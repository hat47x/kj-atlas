from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from kj_atlas_api.tenant_context import TenantContext


POSTGRESQL_TENANT_SETTING = "kj_atlas.tenant_id"


def apply_database_tenant_context(
    *,
    db: Session,
    tenant: TenantContext,
) -> None:
    """Set transaction-local PostgreSQL context; SQLite remains single-tenant only."""
    tenant_id = tenant.tenant_id.strip()
    if not tenant_id:
        raise ValueError("tenant_id must be non-empty")

    if db.get_bind().dialect.name != "postgresql":
        return

    db.execute(
        text(
            "SELECT set_config('kj_atlas.tenant_id', :tenant_id, true)"
        ),
        {"tenant_id": tenant_id},
    )
