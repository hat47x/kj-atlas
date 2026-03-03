from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from kj_atlas_api.access_control import AuthContext
from kj_atlas_api.models import UserIdentityRow, UserRow
from kj_atlas_api.settings import settings


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


def resolve_identity_context(*, db: Session, request: Request) -> ResolvedIdentity:
    provider = _header(request, settings.auth_provider_field) or "header"
    external_uid = _header(request, settings.auth_subject_field) or _header(request, settings.auth_user_field)
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
        return ResolvedIdentity(user_id=None, reviewer_ref=actor_ref, owner_ref=actor_ref, auth_context=auth)

    identity = (
        db.query(UserIdentityRow)
        .filter(UserIdentityRow.provider == provider, UserIdentityRow.external_uid == external_uid)
        .one_or_none()
    )

    if identity is None:
        if not settings.allow_jit_provisioning:
            raise HTTPException(
                status_code=403,
                detail="Identity not provisioned. Pre-provision via /admin/provision/users before access.",
            )

        user_id = str(uuid4())
        now_iso = _now_iso()
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
            created_at=now_iso,
        )
        db.add(user_row)
        db.add(identity)
        db.commit()
    else:
        user_id = identity.user_id

    reviewer_ref = f"user:{user_id}"
    auth = AuthContext(
        actor_ref=reviewer_ref,
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
    return ResolvedIdentity(user_id=user_id, reviewer_ref=reviewer_ref, owner_ref=reviewer_ref, auth_context=auth)
