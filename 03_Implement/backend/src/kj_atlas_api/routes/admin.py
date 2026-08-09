from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from kj_atlas_api.db import get_db
from kj_atlas_api.identity_binding import (
    IdentityMappingConflictError,
    ensure_legacy_identity_provider,
    ensure_user_identity_binding,
    resolve_user_identity,
)
from kj_atlas_api.models import (
    A2A3GateValidationRequest,
    A2A3GateValidationResponse,
    IdentityProviderRow,
    TenantIdentityProviderRow,
    TenantRow,
    UserIdentityRow,
    UserRow,
)
from kj_atlas_api.persistence_shapes import (
    OIDC_AUDIENCE_MAX_CHARS,
    OIDC_ISSUER_MAX_CHARS,
    URI_MAX_CHARS,
)
from kj_atlas_api.reviewer_ref import (
    ReviewerRefResolutionInput,
    build_reviewer_ref_resolver_adapter,
)
from kj_atlas_api.runtime_bootstrap import resolve_tenant_session_bootstrap_mode
from kj_atlas_api.settings import settings, _validate_trusted_http_endpoint
from kj_atlas_api.tenant_foundation import ensure_local_default_membership

router = APIRouter(prefix="/admin/provision", tags=["admin"])

_IDENTITY_CONFLICT_CODE = "identity_already_provisioned_conflict"
_IDENTITY_CONFLICT_MESSAGE = "Identity already provisioned with conflicting profile attributes."


class ProvisionUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    externalUid: str
    displayName: str | None = None
    email: str | None = None


class ProvisionUserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    userId: str
    reviewerRef: str = Field(min_length=1, pattern=r"^user:")
    ownerRef: str = Field(min_length=1, pattern=r"^user:")
    provisioned: bool


def _normalize_provider(raw_provider: str) -> str:
    return raw_provider.strip().lower()


def _normalize_external_uid(raw_external_uid: str) -> str:
    return raw_external_uid.strip()


def _normalize_optional_field(raw: str | None) -> str | None:
    if raw is None:
        return None
    normalized = raw.strip()
    return normalized or None


def require_single_tenant_provisioning_surface(request: Request) -> None:
    """Keep the legacy local-default provisioning API out of SaaS runtimes."""
    try:
        mode = resolve_tenant_session_bootstrap_mode(request.app.state.runtime_profile)
    except (AttributeError, RuntimeError):
        raise HTTPException(
            status_code=503,
            detail={
                "code": "runtime_policy_unavailable",
                "message": "Runtime policy is unavailable.",
            },
        ) from None
    if mode != "single-tenant":
        raise HTTPException(
            status_code=404,
            detail={
                "code": "strict_provisioning_unavailable",
                "message": "Strict provisioning is unavailable in this runtime.",
            },
        )


def _resolve_identity_row(
    *, db: Session, provider: str, external_uid: str
) -> UserIdentityRow | None:
    try:
        return resolve_user_identity(
            db=db,
            provider=provider,
            subject=external_uid,
        )
    except IdentityMappingConflictError:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "identity_mapping_conflict",
                "message": "Multiple identity mappings matched the same provider/externalUid pair.",
            },
        ) from None


@router.post(
    "/users",
    response_model=ProvisionUserResponse,
    status_code=201,
    dependencies=[Depends(require_single_tenant_provisioning_surface)],
)
def provision_user(
    payload: ProvisionUserRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> ProvisionUserResponse:
    reviewer_ref_adapter = build_reviewer_ref_resolver_adapter(
        adapter_name=settings.reviewer_ref_resolver_adapter
    )

    provider = _normalize_provider(payload.provider)
    external_uid = _normalize_external_uid(payload.externalUid)
    display_name = _normalize_optional_field(payload.displayName)
    email = _normalize_optional_field(payload.email)
    if not provider or not external_uid:
        raise HTTPException(status_code=400, detail="provider and externalUid must be non-empty")

    identity = _resolve_identity_row(db=db, provider=provider, external_uid=external_uid)
    if identity is not None:
        user_row = db.get(UserRow, identity.user_id)
        if user_row is None:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "identity_user_not_found",
                    "message": "Identity mapping exists but linked user record is missing.",
                },
            )

        if display_name is not None and user_row.display_name not in {
            None,
            display_name,
        }:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": _IDENTITY_CONFLICT_CODE,
                    "message": _IDENTITY_CONFLICT_MESSAGE,
                },
            )
        if email is not None and user_row.email not in {None, email}:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": _IDENTITY_CONFLICT_CODE,
                    "message": _IDENTITY_CONFLICT_MESSAGE,
                },
            )

        user_id = user_row.id
        resolution = reviewer_ref_adapter.resolve(
            ReviewerRefResolutionInput(
                user_id=user_id,
                provider=provider,
                external_uid=external_uid,
                actor_ref=None,
            )
        )
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            identity_binding_changed = ensure_user_identity_binding(
                db=db,
                identity=identity,
                provider=provider,
                subject=external_uid,
                timestamp=now_iso,
            )
        except IdentityMappingConflictError:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "identity_mapping_conflict",
                    "message": "Identity binding conflicts with the provider/subject pair.",
                },
            ) from None
        membership_changed = ensure_local_default_membership(
            db=db,
            user_id=user_id,
            timestamp=now_iso,
        )
        if identity_binding_changed or membership_changed:
            db.commit()
        response.status_code = 200
        return ProvisionUserResponse(
            userId=user_id,
            reviewerRef=resolution.reviewer_ref or f"user:{user_id}",
            ownerRef=resolution.owner_ref or f"user:{user_id}",
            provisioned=False,
        )

    user_id = str(uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    binding = ensure_legacy_identity_provider(
        db=db,
        provider=provider,
        timestamp=now_iso,
    )
    user_row = UserRow(
        id=user_id,
        display_name=display_name,
        email=email,
        lifecycle_state="active",
        created_at=now_iso,
        updated_at=now_iso,
    )
    db.add(user_row)
    db.add(
        UserIdentityRow(
            user_id=user_id,
            provider=provider,
            external_uid=external_uid,
            identity_provider_id=binding.identity_provider_id,
            subject=external_uid,
            created_at=now_iso,
        )
    )
    ensure_local_default_membership(
        db=db,
        user_id=user_id,
        timestamp=now_iso,
    )
    db.commit()

    resolution = reviewer_ref_adapter.resolve(
        ReviewerRefResolutionInput(
            user_id=user_id,
            provider=provider,
            external_uid=external_uid,
            actor_ref=None,
        )
    )
    return ProvisionUserResponse(
        userId=user_id,
        reviewerRef=resolution.reviewer_ref or f"user:{user_id}",
        ownerRef=resolution.owner_ref or f"user:{user_id}",
        provisioned=True,
    )


@router.post("/hil-rs/a2a3-gate:validate", response_model=A2A3GateValidationResponse)
def validate_a2_a3_gate(payload: A2A3GateValidationRequest) -> A2A3GateValidationResponse:
    frozen_values = {
        "freezeContractId": "HIL-RS-02-A1-CONTRACT-FREEZE-v1",
        "schemaVersion": "1.0.0",
        "overridePolicy": "human_dual_control_only",
        "contractLinkLocked": True,
        "sharedResourceFreeze": True,
        "a1Status": "Done",
        "pendingDecisionQueueCount": 0,
        "hasUndefinedContractChangeRequest": False,
        "hasSafeModeRegressionRequest": False,
        "hasShareExportLeakageRelaxationRequest": False,
    }
    payload_dict = payload.model_dump(mode="python")
    go = all(payload_dict[key] == value for key, value in frozen_values.items())
    if not go:
        raise HTTPException(status_code=409, detail="A2/A3 gate invariants violated")
    return A2A3GateValidationResponse(go=True)


# ---------------------------------------------------------------------------
# ADR-0063 D9-1 / ADR-0064: Identity Provider registration (Platform Control Plane)
# ---------------------------------------------------------------------------


_VALID_PROTOCOLS_V1 = frozenset({"oidc"})


class RegisterIdentityProviderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issuer: str = Field(min_length=1, max_length=OIDC_ISSUER_MAX_CHARS)
    audience: str = Field(min_length=1, max_length=OIDC_AUDIENCE_MAX_CHARS)
    protocol: str = "oidc"
    jwksUri: str | None = Field(
        default=None,
        max_length=URI_MAX_CHARS,
        validation_alias="jwksUri",
    )


class RegisterIdentityProviderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identityProviderId: str
    issuer: str
    audience: str
    protocol: str
    jwksUri: str | None = None


class RegisterTenantIdentityProviderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str = Field(min_length=1)
    identityProviderId: str = Field(min_length=1)
    externalTenantRef: str | None = None


class RegisterTenantIdentityProviderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str
    identityProviderId: str
    externalTenantRef: str | None = None


@router.post(
    "/identity-providers",
    response_model=RegisterIdentityProviderResponse,
    status_code=201,
    dependencies=[Depends(require_single_tenant_provisioning_surface)],
)
def register_identity_provider(
    payload: RegisterIdentityProviderRequest,
    db: Session = Depends(get_db),
) -> RegisterIdentityProviderResponse:
    """ADR-0063 D9-1: register a trusted identity provider (broker / IdP).

    Validates the JWKS URI against the trusted-HTTP-endpoint contract.
    Protocol v1 accepts 'oidc' only.
    """
    issuer = payload.issuer.strip()
    audience = payload.audience.strip()
    protocol = payload.protocol.strip().lower()

    if protocol not in _VALID_PROTOCOLS_V1:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "unsupported_protocol",
                "message": f"Protocol must be one of: {', '.join(sorted(_VALID_PROTOCOLS_V1))}",
            },
        )

    if payload.jwksUri is not None:
        jwks_uri = payload.jwksUri.strip()
        if not jwks_uri:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "invalid_jwks_uri",
                    "message": "jwksUri must be non-empty if provided.",
                },
            )
        try:
            _validate_trusted_http_endpoint(
                endpoint=jwks_uri,
                endpoint_key="jwksUri",
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "invalid_jwks_uri",
                    "message": str(exc),
                },
            ) from None
    else:
        jwks_uri = None

    # Check for duplicate issuer+audience.
    existing = (
        db.query(IdentityProviderRow)
        .filter(
            IdentityProviderRow.issuer == issuer,
            IdentityProviderRow.audience == audience,
        )
        .one_or_none()
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "identity_provider_exists",
                "message": "An identity provider with this issuer+audience already exists.",
            },
        )

    provider_id = f"idp-{uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    db.add(
        IdentityProviderRow(
            id=provider_id,
            issuer=issuer,
            audience=audience,
            protocol=protocol,
            jwks_uri=jwks_uri,
            lifecycle_state="active",
            created_at=now_iso,
            updated_at=now_iso,
        )
    )
    db.commit()
    return RegisterIdentityProviderResponse(
        identityProviderId=provider_id,
        issuer=issuer,
        audience=audience,
        protocol=protocol,
        jwksUri=jwks_uri,
    )


@router.post(
    "/tenant-identity-providers",
    response_model=RegisterTenantIdentityProviderResponse,
    status_code=201,
    dependencies=[Depends(require_single_tenant_provisioning_surface)],
)
def register_tenant_identity_provider(
    payload: RegisterTenantIdentityProviderRequest,
    db: Session = Depends(get_db),
) -> RegisterTenantIdentityProviderResponse:
    """ADR-0063 D8: link a tenant to an identity provider with an external
    tenant reference (mapping the broker's organization claim to tenants.id).
    """
    tenant_id = payload.tenantId.strip()
    provider_id = payload.identityProviderId.strip()
    external_ref = payload.externalTenantRef.strip() if payload.externalTenantRef else None
    if external_ref == "":
        external_ref = None

    # Verify tenant exists.
    tenant = db.get(TenantRow, tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "tenant_not_found",
                "message": "Tenant does not exist.",
            },
        )

    # Verify identity provider exists.
    provider = db.get(IdentityProviderRow, provider_id)
    if provider is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "identity_provider_not_found",
                "message": "Identity provider does not exist.",
            },
        )

    # Check for duplicate (identity_provider_id, external_tenant_ref).
    existing = db.get(TenantIdentityProviderRow, (tenant_id, provider_id))
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "tenant_identity_provider_exists",
                "message": "This tenant is already linked to this identity provider.",
            },
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    db.add(
        TenantIdentityProviderRow(
            tenant_id=tenant_id,
            identity_provider_id=provider_id,
            external_tenant_ref=external_ref,
            lifecycle_state="active",
            created_at=now_iso,
            updated_at=now_iso,
        )
    )
    db.commit()
    return RegisterTenantIdentityProviderResponse(
        tenantId=tenant_id,
        identityProviderId=provider_id,
        externalTenantRef=external_ref,
    )
    return A2A3GateValidationResponse(go=True)
