from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from kj_atlas_api.tenant_context import TenantContext


POSTGRESQL_TENANT_SETTING = "kj_atlas.tenant_id"


def apply_database_tenant_id(
    *,
    db: Session,
    tenant_id: str,
) -> None:
    """Set transaction-local tenant scope without implying membership.

    Normal authenticated user paths should keep using
    ``apply_database_tenant_context``. ADR-0080 guest admission uses this
    lower-level primitive because guest principals deliberately do not become
    ``TenantMembershipRow`` entries.
    """
    normalized_tenant_id = tenant_id.strip()
    if not normalized_tenant_id:
        raise ValueError("tenant_id must be non-empty")

    if db.get_bind().dialect.name != "postgresql":
        return

    db.execute(
        text("SELECT set_config('kj_atlas.tenant_id', :tenant_id, true)"),
        {"tenant_id": normalized_tenant_id},
    )


def apply_database_tenant_context(
    *,
    db: Session,
    tenant: TenantContext,
) -> None:
    """Set transaction-local PostgreSQL context from trusted tenant evidence."""
    apply_database_tenant_id(db=db, tenant_id=tenant.tenant_id)
