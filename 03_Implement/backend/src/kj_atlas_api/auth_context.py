from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from kj_atlas_api.access_control import AuthContext
from kj_atlas_api.identity_binding import (
    IdentityMappingConflictError,
    ensure_legacy_identity_provider,
    ensure_user_identity_binding,
    resolve_user_identity,
)
from kj_atlas_api.models import UserIdentityRow, UserRow
from kj_atlas_api.reviewer_ref import (
    ReviewerRefResolutionInput,
    build_reviewer_ref_resolver_adapter,
)
from kj_atlas_api.settings import settings
from kj_atlas_api.tenant_foundation import ensure_local_default_membership


@dataclass(frozen=True)
class ResolvedIdentity:
    user_id: str | None
    reviewer_ref: str | None
    owner_ref: str | None
    auth_context: AuthContext


def _header(request: Request, header_name: str) -> str | None:
    value = request.headers.get(header_name)
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_provider(raw_provider: str | None) -> str:
    if raw_provider is None:
        return "header"
    return raw_provider.strip().lower() or "header"


def _resolve_identity_row(*, db: Session, provider: str, external_uid: str) -> UserIdentityRow | None:
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


def resolve_identity_context(*, db: Session, request: Request) -> ResolvedIdentity:
    reviewer_ref_adapter = build_reviewer_ref_resolver_adapter(
        adapter_name=settings.reviewer_ref_resolver_adapter
    )
    provider = _normalize_provider(_header(request, settings.auth_provider_field))
    external_uid = _header(request, settings.auth_subject_field) or _header(
        request, settings.auth_user_field
    )
    display_name = _header(request, settings.auth_name_field)
    email = _header(request, settings.auth_email_field)

    amr = _header(request, "x-auth-amr")
    acr = _header(request, "x-auth-acr")
    aal = _header(request, "x-auth-aal")
    auth_time = _header(request, "x-auth-time")

    if external_uid is None:
        actor_ref = _header(request, "x-actor-ref")
        auth = AuthContext(
            actor_ref=actor_ref,
            user_id=None,
            provider=None,
            external_uid=None,
            roles=(),
            groups=(),
            trace_id=_header(request, "x-trace-id"),
            amr=amr,
            acr=acr,
            aal=aal,
            auth_time=auth_time,
        )
        resolution = reviewer_ref_adapter.resolve(
            ReviewerRefResolutionInput(
                user_id=None,
                provider=None,
                external_uid=None,
                actor_ref=actor_ref,
            )
        )
        return ResolvedIdentity(
            user_id=None,
            reviewer_ref=resolution.reviewer_ref,
            owner_ref=resolution.owner_ref,
            auth_context=auth,
        )

    identity = _resolve_identity_row(db=db, provider=provider, external_uid=external_uid)

    if identity is None:
        if not settings.allow_jit_provisioning:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "identity_not_provisioned",
                    "message": "Identity not provisioned. Pre-provision via /admin/provision/users before access.",
                },
            )

        user_id = str(uuid4())
        now_iso = _now_iso()
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
        identity = UserIdentityRow(
            user_id=user_id,
            provider=provider,
            external_uid=external_uid,
            identity_provider_id=binding.identity_provider_id,
            subject=external_uid,
            created_at=now_iso,
        )
        db.add(user_row)
        db.add(identity)
        ensure_local_default_membership(
            db=db,
            user_id=user_id,
            timestamp=now_iso,
        )
        db.commit()
    else:
        user_id = identity.user_id
        now_iso = _now_iso()
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
                    "message": "Identity binding conflicts with the verified provider/subject pair.",
                },
            ) from None
        membership_changed = ensure_local_default_membership(
            db=db,
            user_id=user_id,
            timestamp=now_iso,
        )
        if identity_binding_changed or membership_changed:
            db.commit()

    resolution = reviewer_ref_adapter.resolve(
        ReviewerRefResolutionInput(
            user_id=user_id,
            provider=provider,
            external_uid=external_uid,
            actor_ref=None,
        )
    )

    auth = AuthContext(
        actor_ref=resolution.reviewer_ref,
        user_id=user_id,
        provider=provider,
        external_uid=external_uid,
        roles=(),
        groups=(),
        trace_id=_header(request, "x-trace-id"),
        amr=amr,
        acr=acr,
        aal=aal,
        auth_time=auth_time,
    )
    return ResolvedIdentity(
        user_id=user_id,
        reviewer_ref=resolution.reviewer_ref,
        owner_ref=resolution.owner_ref,
        auth_context=auth,
    )
