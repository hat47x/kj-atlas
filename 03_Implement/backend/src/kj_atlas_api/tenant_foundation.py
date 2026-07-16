from __future__ import annotations

from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    LOCAL_DEFAULT_TENANT_ID,
    TenantMembershipRow,
    TenantRow,
)


LOCAL_DEFAULT_TENANT_DISPLAY_NAME = "Local workspace"


def ensure_local_default_membership(
    *,
    db: Session,
    user_id: str,
    timestamp: str,
) -> bool:
    """Maintain the single-tenant compatibility rows until scoped repositories land."""
    changed = False

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
        changed = True

    membership = db.get(
        TenantMembershipRow,
        (LOCAL_DEFAULT_TENANT_ID, user_id),
    )
    if membership is None:
        db.add(
            TenantMembershipRow(
                tenant_id=LOCAL_DEFAULT_TENANT_ID,
                user_id=user_id,
                lifecycle_state="active",
                created_at=timestamp,
                updated_at=timestamp,
            )
        )
        changed = True

    return changed
