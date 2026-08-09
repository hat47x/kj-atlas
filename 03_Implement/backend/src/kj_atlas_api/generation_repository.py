from sqlalchemy import update
from sqlalchemy.orm import Session

from kj_atlas_api.models import CanvasRevisionHeadRow
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


class RevisionHeadConflict(RuntimeError):
    pass


def advance_revision_head(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    head_name: str,
    expected_version: int,
    new_revision_id: str,
    updated_at: str,
) -> int:
    apply_database_tenant_context(db=db, tenant=tenant)
    result = db.execute(
        update(CanvasRevisionHeadRow)
        .where(
            CanvasRevisionHeadRow.tenant_id == tenant.tenant_id,
            CanvasRevisionHeadRow.doc_id == doc_id,
            CanvasRevisionHeadRow.head_name == head_name,
            CanvasRevisionHeadRow.head_version == expected_version,
        )
        .values(
            revision_id=new_revision_id,
            head_version=expected_version + 1,
            updated_at=updated_at,
        )
    )
    if result.rowcount != 1:
        raise RevisionHeadConflict("revision head changed concurrently")
    return expected_version + 1
