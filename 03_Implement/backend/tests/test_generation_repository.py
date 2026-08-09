from hashlib import sha256

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.generation_repository import (
    RevisionHeadConflict,
    advance_revision_head,
    delete_unreferenced_blob_gc_candidate,
    delete_ephemeral_gc_candidate,
    list_ephemeral_gc_candidates,
    list_unreferenced_blob_candidates,
)
from kj_atlas_api.models import (
    Base,
    CanvasRevisionHeadRow,
    CanvasRevisionParentRow,
    CanvasRevisionPinRow,
    CanvasRevisionRow,
    ContentBlobRow,
    DocumentRow,
    GenerationDeletionAuditEventRow,
    TenantRow,
)
from kj_atlas_api.tenant_context import TenantContext


def _tenant(tenant_id: str) -> TenantContext:
    return TenantContext(tenant_id=tenant_id, membership_id=None, resolved_by="verified_claim")


def test_revision_head_compare_and_swap_is_tenant_scoped(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'generation.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(engine)
    digest = sha256(b"{}").hexdigest()
    timestamp = "2026-08-09T00:00:00Z"
    try:
        with session_local() as db:
            for tenant_id in ("tenant-a", "tenant-b"):
                db.add(
                    TenantRow(
                        id=tenant_id,
                        display_name=tenant_id,
                        lifecycle_state="active",
                        created_at=timestamp,
                        updated_at=timestamp,
                    )
                )
                db.add(
                    DocumentRow(
                        tenant_id=tenant_id,
                        id="doc",
                        version=1,
                        updated_at=timestamp,
                        payload_json="{}",
                    )
                )
                db.add(
                    ContentBlobRow(
                        tenant_id=tenant_id,
                        content_digest=digest,
                        storage_backend="database",
                        locator=None,
                        representation="full_json",
                        base_digest=None,
                        delta_depth=0,
                        byte_size=2,
                        stored_byte_size=2,
                        storage_state="ready",
                        schema_version="document-v1",
                        created_at=timestamp,
                    )
                )
                for revision_id in ("rev-1", "rev-2"):
                    db.add(
                        CanvasRevisionRow(
                            tenant_id=tenant_id,
                            revision_id=revision_id,
                            doc_id="doc",
                            content_digest=digest,
                            generation_tier="checkpoint",
                            generation_reason="manual_save",
                            generation_origin="human",
                            actor_ref=None,
                            ai_run_ref=None,
                            source_revision_id=None,
                            created_at=timestamp,
                        )
                    )
                db.add(
                    CanvasRevisionHeadRow(
                        tenant_id=tenant_id,
                        doc_id="doc",
                        head_name="main",
                        revision_id="rev-1",
                        head_version=1,
                        updated_at=timestamp,
                    )
                )
            db.commit()

            assert (
                advance_revision_head(
                    db,
                    tenant=_tenant("tenant-a"),
                    doc_id="doc",
                    head_name="main",
                    expected_version=1,
                    new_revision_id="rev-2",
                    updated_at=timestamp,
                )
                == 2
            )
            with pytest.raises(RevisionHeadConflict, match="concurrently"):
                advance_revision_head(
                    db,
                    tenant=_tenant("tenant-a"),
                    doc_id="doc",
                    head_name="main",
                    expected_version=1,
                    new_revision_id="rev-1",
                    updated_at=timestamp,
                )
            tenant_b = db.get(CanvasRevisionHeadRow, ("tenant-b", "doc", "main"))
            assert tenant_b is not None
            assert tenant_b.revision_id == "rev-1"
            assert tenant_b.head_version == 1

            for revision_id in ("old-free", "old-pinned", "old-parent"):
                db.add(
                    CanvasRevisionRow(
                        tenant_id="tenant-a",
                        revision_id=revision_id,
                        doc_id="doc",
                        content_digest=digest,
                        generation_tier="ephemeral",
                        generation_reason="autosave",
                        generation_origin="system",
                        actor_ref=None,
                        ai_run_ref=None,
                        source_revision_id=None,
                        created_at="2026-07-01T00:00:00Z",
                    )
                )
            db.add(
                CanvasRevisionPinRow(
                    tenant_id="tenant-a",
                    revision_id="old-pinned",
                    pin_reason="user",
                    created_at=timestamp,
                )
            )
            db.add(
                CanvasRevisionParentRow(
                    tenant_id="tenant-a",
                    revision_id="rev-2",
                    parent_revision_id="old-parent",
                    parent_order=0,
                )
            )
            db.commit()
            assert [
                row.revision_id
                for row in list_ephemeral_gc_candidates(
                    db,
                    tenant=_tenant("tenant-a"),
                    older_than="2026-08-01T00:00:00Z",
                )
            ] == ["old-free"]
            assert (
                delete_ephemeral_gc_candidate(
                    db,
                    tenant=_tenant("tenant-a"),
                    revision_id="old-pinned",
                    older_than="2026-08-01T00:00:00Z",
                    audit_event_id="audit-protected",
                    executor_ref="system:gc",
                    occurred_at=timestamp,
                )
                is False
            )
            assert (
                delete_ephemeral_gc_candidate(
                    db,
                    tenant=_tenant("tenant-a"),
                    revision_id="old-free",
                    older_than="2026-08-01T00:00:00Z",
                    audit_event_id="audit-revision",
                    executor_ref="system:gc",
                    occurred_at=timestamp,
                )
                is True
            )
            db.flush()
            revision_audit = db.get(GenerationDeletionAuditEventRow, "audit-revision")
            assert revision_audit is not None
            assert revision_audit.target_ref == "old-free"
            assert revision_audit.outcome == "deleted"
            assert db.get(GenerationDeletionAuditEventRow, "audit-protected") is None

            orphan_digest = sha256(b"orphan").hexdigest()
            db.add(
                ContentBlobRow(
                    tenant_id="tenant-a",
                    content_digest=orphan_digest,
                    storage_backend="database",
                    locator=None,
                    representation="full_json",
                    base_digest=None,
                    delta_depth=0,
                    byte_size=6,
                    stored_byte_size=6,
                    storage_state="failed",
                    schema_version="document-v1",
                    created_at="2026-07-01T00:00:00Z",
                )
            )
            db.commit()
            assert [
                row.content_digest
                for row in list_unreferenced_blob_candidates(
                    db,
                    tenant=_tenant("tenant-a"),
                    older_than="2026-08-01T00:00:00Z",
                )
            ] == [orphan_digest]
            assert delete_unreferenced_blob_gc_candidate(
                db,
                tenant=_tenant("tenant-a"),
                content_digest=orphan_digest,
                older_than="2026-08-01T00:00:00Z",
                audit_event_id="audit-blob",
                executor_ref="system:gc",
                occurred_at=timestamp,
            )
            db.flush()
            blob_audit = db.get(GenerationDeletionAuditEventRow, "audit-blob")
            assert blob_audit is not None
            assert blob_audit.target_ref == orphan_digest
            assert blob_audit.outcome == "deleted"
            assert db.get(ContentBlobRow, ("tenant-a", orphan_digest)) is None

            external_digest = sha256(b"external orphan").hexdigest()
            failed_digest = sha256(b"failed external orphan").hexdigest()
            for content_digest, backend, locator in (
                (external_digest, "nas", "tenants/a/content/external.json"),
                (failed_digest, "s3", "tenants/a/content/failed.json"),
            ):
                db.add(
                    ContentBlobRow(
                        tenant_id="tenant-a",
                        content_digest=content_digest,
                        storage_backend=backend,
                        locator=locator,
                        representation="gzip_json",
                        base_digest=None,
                        delta_depth=0,
                        byte_size=15,
                        stored_byte_size=15,
                        storage_state="ready",
                        schema_version="document-v1",
                        created_at="2026-07-01T00:00:00Z",
                    )
                )
            db.commit()

            deleted: list[tuple[str, str]] = []

            def _delete_external(backend: str, locator: str) -> bool:
                deleted.append((backend, locator))
                return True

            assert delete_unreferenced_blob_gc_candidate(
                db,
                tenant=_tenant("tenant-a"),
                content_digest=external_digest,
                older_than="2026-08-01T00:00:00Z",
                audit_event_id="audit-external-blob",
                executor_ref="system:gc",
                occurred_at=timestamp,
                delete_external=_delete_external,
            )
            db.flush()
            assert deleted == [("nas", "tenants/a/content/external.json")]
            assert db.get(ContentBlobRow, ("tenant-a", external_digest)) is None

            def _fail_delete(_backend: str, _locator: str) -> bool:
                raise OSError("storage unavailable")

            assert not delete_unreferenced_blob_gc_candidate(
                db,
                tenant=_tenant("tenant-a"),
                content_digest=failed_digest,
                older_than="2026-08-01T00:00:00Z",
                audit_event_id="audit-failed-blob",
                executor_ref="system:gc",
                occurred_at=timestamp,
                delete_external=_fail_delete,
            )
            db.flush()
            failed_blob = db.get(ContentBlobRow, ("tenant-a", failed_digest))
            assert failed_blob is not None
            assert failed_blob.storage_state == "deleting"
            failed_audit = db.get(GenerationDeletionAuditEventRow, "audit-failed-blob")
            assert failed_audit is not None
            assert failed_audit.outcome == "failed"
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
