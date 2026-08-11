from collections.abc import Callable
from dataclasses import dataclass
from hashlib import sha256

from sqlalchemy import delete, exists, select, update
from sqlalchemy.orm import aliased
from sqlalchemy.orm import Session

from kj_atlas_api.generation_codec import EncodedGenerationBlob, restore_generation
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


class GenerationGcConflict(RuntimeError):
    pass


class GenerationBlobConflict(RuntimeError):
    pass


class GenerationBlobUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class EphemeralHistoryPruneResult:
    deleted_revision_ids: tuple[str, ...]
    cut_parent_edges: int


def load_database_generation_blob(
    db: Session,
    *,
    tenant: TenantContext,
    content_digest: str,
    max_delta_depth: int = 32,
) -> bytes:
    """Restore and integrity-check an inline generation blob and its delta ancestry."""
    if max_delta_depth < 0:
        raise ValueError("max delta depth must not be negative")
    apply_database_tenant_context(db=db, tenant=tenant)

    def _restore(digest: str, *, remaining_depth: int, ancestors: set[str]) -> bytes:
        if digest in ancestors:
            raise GenerationBlobUnavailable("generation blob delta cycle detected")
        row = db.get(ContentBlobRow, (tenant.tenant_id, digest))
        if (
            row is None
            or row.storage_backend != "database"
            or row.storage_state != "ready"
            or row.payload_bytes is None
        ):
            raise GenerationBlobUnavailable("generation blob is not materialized in database")
        stored_bytes = bytes(row.payload_bytes)
        if len(stored_bytes) != row.stored_byte_size:
            raise GenerationBlobUnavailable("generation blob stored size does not match")
        if row.representation == "full_json":
            if len(stored_bytes) != row.byte_size or sha256(stored_bytes).hexdigest() != digest:
                raise GenerationBlobUnavailable("generation blob integrity verification failed")
            return stored_bytes
        if row.delta_depth > max_delta_depth or remaining_depth < 0:
            raise GenerationBlobUnavailable("generation blob delta depth exceeds policy")
        base_bytes = None
        if row.representation == "gzip_delta":
            if row.base_digest is None or remaining_depth == 0:
                raise GenerationBlobUnavailable("generation blob delta base is unavailable")
            base_bytes = _restore(
                row.base_digest,
                remaining_depth=remaining_depth - 1,
                ancestors=ancestors | {digest},
            )
        encoded = EncodedGenerationBlob(
            content_digest=row.content_digest,
            byte_size=row.byte_size,
            stored_bytes=stored_bytes,
            representation=row.representation,
            base_digest=row.base_digest,
            delta_depth=row.delta_depth,
        )
        try:
            return restore_generation(encoded, base_bytes=base_bytes)
        except ValueError as error:
            raise GenerationBlobUnavailable(
                "generation blob integrity verification failed"
            ) from error

    return _restore(content_digest, remaining_depth=max_delta_depth, ancestors=set())


def save_database_generation_blob(
    db: Session,
    *,
    tenant: TenantContext,
    blob: EncodedGenerationBlob,
    schema_version: str,
    created_at: str,
    max_delta_depth: int = 32,
) -> ContentBlobRow:
    """Persist codec output idempotently without allowing digest metadata collisions."""
    apply_database_tenant_context(db=db, tenant=tenant)
    if len(blob.stored_bytes) == 0 or len(blob.stored_bytes) > 2**31 - 1:
        raise GenerationBlobConflict("generation blob stored size is invalid")
    if blob.delta_depth > max_delta_depth:
        raise GenerationBlobConflict("generation blob delta depth exceeds policy")

    base_bytes = None
    if blob.representation == "gzip_delta":
        if blob.base_digest is None:
            raise GenerationBlobConflict("generation blob delta base is missing")
        base_bytes = load_database_generation_blob(
            db,
            tenant=tenant,
            content_digest=blob.base_digest,
            max_delta_depth=max_delta_depth,
        )
    try:
        restore_generation(blob, base_bytes=base_bytes)
    except ValueError as error:
        raise GenerationBlobConflict("generation blob failed integrity verification") from error

    existing = db.get(ContentBlobRow, (tenant.tenant_id, blob.content_digest))
    expected_shape = (
        "database",
        None,
        blob.representation,
        blob.base_digest,
        blob.delta_depth,
        blob.byte_size,
        len(blob.stored_bytes),
        "ready",
        schema_version,
        bytes(blob.stored_bytes),
    )
    if existing is not None:
        actual_shape = (
            existing.storage_backend,
            existing.locator,
            existing.representation,
            existing.base_digest,
            existing.delta_depth,
            existing.byte_size,
            existing.stored_byte_size,
            existing.storage_state,
            existing.schema_version,
            bytes(existing.payload_bytes) if existing.payload_bytes is not None else None,
        )
        if actual_shape != expected_shape:
            raise GenerationBlobConflict("generation blob digest already has different content")
        return existing

    row = ContentBlobRow(
        tenant_id=tenant.tenant_id,
        content_digest=blob.content_digest,
        storage_backend="database",
        locator=None,
        representation=blob.representation,
        base_digest=blob.base_digest,
        delta_depth=blob.delta_depth,
        byte_size=blob.byte_size,
        stored_byte_size=len(blob.stored_bytes),
        storage_state="ready",
        schema_version=schema_version,
        created_at=created_at,
        payload_bytes=bytes(blob.stored_bytes),
    )
    db.add(row)
    return row


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


def prune_ephemeral_history_by_reachability(
    db: Session,
    *,
    tenant: TenantContext,
    older_than: str,
    keep_per_root: int,
    executor_ref: str,
    occurred_at: str,
    audit_event_id_for: Callable[[str], str],
) -> EphemeralHistoryPruneResult:
    """Retain the nearest ephemeral ancestors of every durable DAG root.

    All mutations remain in the caller's transaction. A cycle or concurrent
    protection change aborts with ``GenerationGcConflict`` so boundary edge
    cuts cannot commit without their corresponding revision deletions.
    """
    if keep_per_root < 1:
        raise ValueError("ephemeral history retention count must be positive")
    apply_database_tenant_context(db=db, tenant=tenant)
    revisions = list(
        db.scalars(
            select(CanvasRevisionRow)
            .where(CanvasRevisionRow.tenant_id == tenant.tenant_id)
            .with_for_update()
        ).all()
    )
    revision_by_id = {row.revision_id: row for row in revisions}
    parents = list(
        db.scalars(
            select(CanvasRevisionParentRow).where(
                CanvasRevisionParentRow.tenant_id == tenant.tenant_id
            )
        ).all()
    )
    parent_ids_by_child: dict[str, list[str]] = {}
    for edge in parents:
        parent_ids_by_child.setdefault(edge.revision_id, []).append(edge.parent_revision_id)

    roots = {row.revision_id for row in revisions if row.generation_tier != "ephemeral"}
    roots.update(row.source_revision_id for row in revisions if row.source_revision_id)
    roots.update(
        db.scalars(
            select(CanvasRevisionHeadRow.revision_id).where(
                CanvasRevisionHeadRow.tenant_id == tenant.tenant_id
            )
        ).all()
    )
    roots.update(
        db.scalars(
            select(CanvasRevisionPinRow.revision_id).where(
                CanvasRevisionPinRow.tenant_id == tenant.tenant_id
            )
        ).all()
    )

    retained: set[str] = set()
    best_ephemeral_count: dict[str, int] = {}
    pending = [
        (revision_id, 1 if revision_by_id[revision_id].generation_tier == "ephemeral" else 0)
        for revision_id in roots
        if revision_id in revision_by_id
    ]
    while pending:
        revision_id, ephemeral_count = pending.pop()
        previous = best_ephemeral_count.get(revision_id)
        if previous is not None and previous <= ephemeral_count:
            continue
        best_ephemeral_count[revision_id] = ephemeral_count
        if ephemeral_count > keep_per_root:
            continue
        retained.add(revision_id)
        for parent_id in parent_ids_by_child.get(revision_id, ()):
            parent = revision_by_id.get(parent_id)
            if parent is None:
                raise GenerationGcConflict("revision DAG references a missing parent")
            pending.append(
                (
                    parent_id,
                    ephemeral_count + (1 if parent.generation_tier == "ephemeral" else 0),
                )
            )

    candidates = {
        row.revision_id
        for row in revisions
        if row.generation_tier == "ephemeral"
        and row.created_at < older_than
        and row.revision_id not in retained
    }
    children_in_candidates: dict[str, set[str]] = {revision_id: set() for revision_id in candidates}
    for edge in parents:
        if edge.parent_revision_id in candidates and edge.revision_id in candidates:
            children_in_candidates[edge.parent_revision_id].add(edge.revision_id)

    deletion_order: list[str] = []
    remaining = set(candidates)
    while remaining:
        ready = sorted(
            revision_id
            for revision_id in remaining
            if not (children_in_candidates[revision_id] & remaining)
        )
        if not ready:
            raise GenerationGcConflict("revision DAG cycle prevents retention pruning")
        deletion_order.extend(ready)
        remaining.difference_update(ready)

    boundary_edges = [
        edge
        for edge in parents
        if edge.parent_revision_id in candidates and edge.revision_id not in candidates
    ]
    for edge in boundary_edges:
        db.delete(edge)
    db.flush()

    for revision_id in deletion_order:
        db.execute(
            delete(CanvasRevisionParentRow).where(
                CanvasRevisionParentRow.tenant_id == tenant.tenant_id,
                CanvasRevisionParentRow.revision_id == revision_id,
            )
        )
        if not delete_ephemeral_gc_candidate(
            db,
            tenant=tenant,
            revision_id=revision_id,
            older_than=older_than,
            audit_event_id=audit_event_id_for(revision_id),
            executor_ref=executor_ref,
            occurred_at=occurred_at,
        ):
            raise GenerationGcConflict(
                f"revision {revision_id!r} became protected during retention pruning"
            )
        db.flush()
    return EphemeralHistoryPruneResult(
        deleted_revision_ids=tuple(deletion_order),
        cut_parent_edges=len(boundary_edges),
    )


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
