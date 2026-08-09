from collections.abc import Callable

from sqlalchemy import delete, exists, select, update
from sqlalchemy.orm import aliased
from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    CanvasRevisionHeadRow,
    CanvasRevisionParentRow,
    CanvasRevisionPinRow,
    CanvasRevisionRow,
    ContentBlobRow,
    GenerationDeletionAuditEventRow,
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


def delete_ephemeral_gc_candidate(
    db: Session,
    *,
    tenant: TenantContext,
    revision_id: str,
    older_than: str,
    audit_event_id: str,
    executor_ref: str,
    occurred_at: str,
) -> bool:
    apply_database_tenant_context(db=db, tenant=tenant)
    child = aliased(CanvasRevisionParentRow)
    source = aliased(CanvasRevisionRow)
    result = db.execute(
        delete(CanvasRevisionRow).where(
            CanvasRevisionRow.tenant_id == tenant.tenant_id,
            CanvasRevisionRow.revision_id == revision_id,
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
    )
    if result.rowcount != 1:
        return False
    db.add(
        GenerationDeletionAuditEventRow(
            event_id=audit_event_id,
            tenant_id=tenant.tenant_id,
            target_kind="revision",
            target_ref=revision_id,
            storage_backend=None,
            action="revision_gc.delete",
            outcome="deleted",
            executor_ref=executor_ref,
            occurred_at=occurred_at,
        )
    )
    return True


def list_unreferenced_blob_candidates(
    db: Session,
    *,
    tenant: TenantContext,
    older_than: str,
    limit: int = 100,
) -> list[ContentBlobRow]:
    if limit < 1:
        raise ValueError("blob candidate limit must be positive")
    apply_database_tenant_context(db=db, tenant=tenant)
    child_blob = aliased(ContentBlobRow)
    return list(
        db.scalars(
            select(ContentBlobRow)
            .where(
                ContentBlobRow.tenant_id == tenant.tenant_id,
                ContentBlobRow.created_at < older_than,
                ContentBlobRow.storage_state.in_(("ready", "failed", "deleting")),
                ~exists().where(
                    CanvasRevisionRow.tenant_id == ContentBlobRow.tenant_id,
                    CanvasRevisionRow.content_digest == ContentBlobRow.content_digest,
                ),
                ~exists().where(
                    child_blob.tenant_id == ContentBlobRow.tenant_id,
                    child_blob.base_digest == ContentBlobRow.content_digest,
                ),
            )
            .order_by(ContentBlobRow.created_at.asc(), ContentBlobRow.content_digest.asc())
            .limit(limit)
        ).all()
    )


def delete_unreferenced_blob_gc_candidate(
    db: Session,
    *,
    tenant: TenantContext,
    content_digest: str,
    older_than: str,
    audit_event_id: str,
    executor_ref: str,
    occurred_at: str,
    delete_external: Callable[[str, str], bool] | None = None,
) -> bool:
    """Delete one unreferenced blob while holding its DB row lock.

    The caller owns the transaction. Keeping claim, physical deletion, metadata
    deletion, and audit insertion in that transaction prevents a concurrent
    revision FK insert from succeeding after the object has been selected.
    """
    apply_database_tenant_context(db=db, tenant=tenant)
    child_blob = aliased(ContentBlobRow)
    candidate = db.scalar(
        select(ContentBlobRow)
        .where(
            ContentBlobRow.tenant_id == tenant.tenant_id,
            ContentBlobRow.content_digest == content_digest,
            ContentBlobRow.created_at < older_than,
            ContentBlobRow.storage_state.in_(("ready", "failed", "deleting")),
            ~exists().where(
                CanvasRevisionRow.tenant_id == ContentBlobRow.tenant_id,
                CanvasRevisionRow.content_digest == ContentBlobRow.content_digest,
            ),
            ~exists().where(
                child_blob.tenant_id == ContentBlobRow.tenant_id,
                child_blob.base_digest == ContentBlobRow.content_digest,
            ),
        )
        .with_for_update()
    )
    if candidate is None:
        return False

    candidate.storage_state = "deleting"
    db.flush()
    outcome = "deleted"
    try:
        if candidate.storage_backend == "database":
            if candidate.locator is not None:
                raise ValueError("database blob must not have an external locator")
        else:
            if not candidate.locator or delete_external is None:
                raise ValueError("external blob deletion requires a locator and delete adapter")
            if not delete_external(candidate.storage_backend, candidate.locator):
                outcome = "not_found"
    except Exception:
        db.add(
            _blob_deletion_audit(
                event_id=audit_event_id,
                tenant_id=tenant.tenant_id,
                content_digest=content_digest,
                storage_backend=candidate.storage_backend,
                outcome="failed",
                executor_ref=executor_ref,
                occurred_at=occurred_at,
            )
        )
        return False

    result = db.execute(
        delete(ContentBlobRow).where(
            ContentBlobRow.tenant_id == tenant.tenant_id,
            ContentBlobRow.content_digest == content_digest,
            ContentBlobRow.storage_state == "deleting",
            ~exists().where(
                CanvasRevisionRow.tenant_id == ContentBlobRow.tenant_id,
                CanvasRevisionRow.content_digest == ContentBlobRow.content_digest,
            ),
            ~exists().where(
                child_blob.tenant_id == ContentBlobRow.tenant_id,
                child_blob.base_digest == ContentBlobRow.content_digest,
            ),
        )
    )
    if result.rowcount != 1:
        db.add(
            _blob_deletion_audit(
                event_id=audit_event_id,
                tenant_id=tenant.tenant_id,
                content_digest=content_digest,
                storage_backend=candidate.storage_backend,
                outcome="failed",
                executor_ref=executor_ref,
                occurred_at=occurred_at,
            )
        )
        return False
    db.add(
        _blob_deletion_audit(
            event_id=audit_event_id,
            tenant_id=tenant.tenant_id,
            content_digest=content_digest,
            storage_backend=candidate.storage_backend,
            outcome=outcome,
            executor_ref=executor_ref,
            occurred_at=occurred_at,
        )
    )
    return True


def _blob_deletion_audit(
    *,
    event_id: str,
    tenant_id: str,
    content_digest: str,
    storage_backend: str,
    outcome: str,
    executor_ref: str,
    occurred_at: str,
) -> GenerationDeletionAuditEventRow:
    return GenerationDeletionAuditEventRow(
        event_id=event_id,
        tenant_id=tenant_id,
        target_kind="blob",
        target_ref=content_digest,
        storage_backend=storage_backend,
        action="blob_gc.delete",
        outcome=outcome,
        executor_ref=executor_ref,
        occurred_at=occurred_at,
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
