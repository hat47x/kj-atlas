from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from sqlalchemy import func
from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    LOCAL_DEFAULT_TENANT_ID,
    IdentityProviderRow,
    TenantIdentityProviderRow,
    TenantRow,
    UserIdentityRow,
)
from kj_atlas_api.tenant_foundation import LOCAL_DEFAULT_TENANT_DISPLAY_NAME


LEGACY_IDENTITY_PROVIDER_AUDIENCE = "kj-atlas-single-tenant"


@dataclass(frozen=True, slots=True)
class LegacyIdentityProviderBinding:
    identity_provider_id: str
    issuer: str
    audience: str


class IdentityMappingConflictError(RuntimeError):
    pass


def normalize_provider(raw_provider: str) -> str:
    return raw_provider.strip().lower()


def legacy_identity_provider_binding(provider: str) -> LegacyIdentityProviderBinding:
    normalized_provider = normalize_provider(provider)
    if not normalized_provider:
        raise ValueError("provider must be non-empty")
    digest = sha256(normalized_provider.encode("utf-8")).hexdigest()[:24]
    identity_provider_id = f"idp-legacy-{digest}"
    return LegacyIdentityProviderBinding(
        identity_provider_id=identity_provider_id,
        issuer=f"urn:kj-atlas:legacy-provider:{digest}",
        audience=LEGACY_IDENTITY_PROVIDER_AUDIENCE,
    )


def ensure_legacy_identity_provider(
    *,
    db: Session,
    provider: str,
    timestamp: str,
) -> LegacyIdentityProviderBinding:
    """Create the compatibility IdP binding used before verified issuer resolution lands."""
    binding = legacy_identity_provider_binding(provider)

    tenant = db.get(TenantRow, LOCAL_DEFAULT_TENANT_ID)
    if tenant is None:
        db.add(
            TenantRow(
                id=LOCAL_DEFAULT_TENANT_ID,
                display_name=LOCAL_DEFAULT_TENANT_DISPLAY_NAME,
                lifecycle_state="active",
                created_at=timestamp,
                updated_at=timestamp,
            )
        )

    identity_provider = db.get(IdentityProviderRow, binding.identity_provider_id)
    if identity_provider is None:
        db.add(
            IdentityProviderRow(
                id=binding.identity_provider_id,
                issuer=binding.issuer,
                audience=binding.audience,
                lifecycle_state="active",
                created_at=timestamp,
                updated_at=timestamp,
            )
        )
    elif (
        identity_provider.issuer != binding.issuer
        or identity_provider.audience != binding.audience
    ):
        raise RuntimeError("legacy identity provider identifier collision")

    tenant_binding = db.get(
        TenantIdentityProviderRow,
        (LOCAL_DEFAULT_TENANT_ID, binding.identity_provider_id),
    )
    if tenant_binding is None:
        db.add(
            TenantIdentityProviderRow(
                tenant_id=LOCAL_DEFAULT_TENANT_ID,
                identity_provider_id=binding.identity_provider_id,
                lifecycle_state="active",
                created_at=timestamp,
                updated_at=timestamp,
            )
        )

    # Make the tenant visible to the following membership lookup in the same
    # transaction. Session.get() does not reliably match a pending composite
    # graph before it has been flushed.
    db.flush()
    return binding


def resolve_user_identity(
    *,
    db: Session,
    provider: str,
    subject: str,
) -> UserIdentityRow | None:
    """Prefer the structured IdP binding while retaining a bounded legacy fallback."""
    binding = legacy_identity_provider_binding(provider)
    structured_matches = (
        db.query(UserIdentityRow)
        .filter(
            UserIdentityRow.identity_provider_id == binding.identity_provider_id,
            UserIdentityRow.subject == subject,
        )
        .limit(2)
        .all()
    )
    legacy_matches = (
        db.query(UserIdentityRow)
        .filter(
            func.lower(UserIdentityRow.provider) == normalize_provider(provider),
            UserIdentityRow.external_uid == subject,
        )
        .limit(2)
        .all()
    )
    matched_by_id = {
        row.id: row
        for row in [*structured_matches, *legacy_matches]
    }
    if len(matched_by_id) > 1:
        raise IdentityMappingConflictError
    return next(iter(matched_by_id.values()), None)


def ensure_user_identity_binding(
    *,
    db: Session,
    identity: UserIdentityRow,
    provider: str,
    subject: str,
    timestamp: str,
) -> bool:
    """Fill expand columns on a legacy row without overwriting conflicting bindings."""
    binding = ensure_legacy_identity_provider(
        db=db,
        provider=provider,
        timestamp=timestamp,
    )
    if identity.identity_provider_id is None and identity.subject is None:
        identity.identity_provider_id = binding.identity_provider_id
        identity.subject = subject
        return True
    if (
        identity.identity_provider_id != binding.identity_provider_id
        or identity.subject != subject
    ):
        raise IdentityMappingConflictError
    return False
