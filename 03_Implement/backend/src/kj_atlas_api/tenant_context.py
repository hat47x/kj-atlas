from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    LOCAL_DEFAULT_TENANT_ID,
    TenantMembershipRow,
    TenantRow,
    UserRow,
)


TenantResolutionMethod = Literal[
    "single_tenant_adapter",
    "verified_claim",
    "trusted_host_mapping",
]


@dataclass(frozen=True, slots=True)
class TenantContext:
    tenant_id: str
    membership_id: str | None
    resolved_by: TenantResolutionMethod


LOCAL_DEFAULT_TENANT_CONTEXT = TenantContext(
    tenant_id=LOCAL_DEFAULT_TENANT_ID,
    membership_id=None,
    resolved_by="single_tenant_adapter",
)


def _opaque_membership_id(*, tenant_id: str, user_id: str) -> str:
    digest = sha256(f"{tenant_id}\x00{user_id}".encode("utf-8")).hexdigest()[:24]
    return f"membership-{digest}"


def _deny_inactive_membership() -> None:
    raise HTTPException(
        status_code=403,
        detail={
            "code": "tenant_membership_inactive",
            "message": "Active tenant membership is required.",
        },
    )


def resolve_single_tenant_context(
    *,
    db: Session,
    user_id: str | None,
) -> TenantContext:
    """Resolve the compatibility tenant without accepting client tenant input."""
    if user_id is None:
        return LOCAL_DEFAULT_TENANT_CONTEXT

    user = db.get(UserRow, user_id)
    tenant = db.get(TenantRow, LOCAL_DEFAULT_TENANT_ID)
    membership = db.get(
        TenantMembershipRow,
        (LOCAL_DEFAULT_TENANT_ID, user_id),
    )
    if (
        user is None
        or user.lifecycle_state != "active"
        or tenant is None
        or tenant.lifecycle_state != "active"
        or membership is None
        or membership.lifecycle_state != "active"
    ):
        _deny_inactive_membership()

    return TenantContext(
        tenant_id=LOCAL_DEFAULT_TENANT_ID,
        membership_id=_opaque_membership_id(
            tenant_id=LOCAL_DEFAULT_TENANT_ID,
            user_id=user_id,
        ),
        resolved_by="single_tenant_adapter",
    )
