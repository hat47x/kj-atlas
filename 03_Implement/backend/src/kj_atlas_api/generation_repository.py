from sqlalchemy import exists, select, update
from sqlalchemy.orm import aliased
from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    CanvasRevisionHeadRow,
    CanvasRevisionParentRow,
    CanvasRevisionPinRow,
    CanvasRevisionRow,
)
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


class RevisionHeadConflict(RuntimeError):
    pass


def list_ephemeral_gc_candidates(
    db: Session,
    *,
    tenant: TenantContext,
    older_than: str,
    limit: int = 100,
) -> list[CanvasRevisionRow]:
    if limit < 1:
        raise ValueError("GC candidate limit must be positive")
    apply_database_tenant_context(db=db, tenant=tenant)
    child = aliased(CanvasRevisionParentRow)
    source = aliased(CanvasRevisionRow)
    return list(
        db.scalars(
            select(CanvasRevisionRow)
            .where(
                CanvasRevisionRow.tenant_id == tenant.tenant_id,
                CanvasRevisionRow.generation_tier == "ephemeral",
                CanvasRevisionRow.created_at < older_than,
                ~exists().where(
                    CanvasRevisionHeadRow.tenant_id == CanvasRevisionRow.tenant_id,
                    CanvasRevisionHeadRow.revision_id == CanvasRevisionRow.revision_id,
                ),
                ~exists().where(
                    child.tenant_id == CanvasRevisionRow.tenant_id,
                    child.parent_revision_id == CanvasRevisionRow.revision_id,
                ),
                ~exists().where(
                    source.tenant_id == CanvasRevisionRow.tenant_id,
                    source.source_revision_id == CanvasRevisionRow.revision_id,
                ),
                ~exists().where(
                    CanvasRevisionPinRow.tenant_id == CanvasRevisionRow.tenant_id,
                    CanvasRevisionPinRow.revision_id == CanvasRevisionRow.revision_id,
                ),
            )
            .order_by(CanvasRevisionRow.created_at.asc(), CanvasRevisionRow.revision_id.asc())
            .limit(limit)
        ).all()
    )


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
