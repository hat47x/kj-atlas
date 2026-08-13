import json
from hashlib import sha256

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.content_store import ContentBlob
from kj_atlas_api.database_content_store import (
    DatabaseAppendOnlyLogContentStore,
    DatabaseBundleContentStore,
    DatabaseDocumentContentStore,
    DocumentRevisionDivergence,
)
from kj_atlas_api.models import (
    Base,
    CanvasRevisionHeadRow,
    CanvasRevisionParentRow,
    CanvasRevisionRow,
    DocumentRow,
    TenantRow,
)
from kj_atlas_api.tenant_context import TenantContext


def _tenant(tenant_id: str) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id=f"membership:{tenant_id}",
        resolved_by="verified_claim",
    )


def _tenant_row(tenant_id: str) -> TenantRow:
    return TenantRow(
        id=tenant_id,
        display_name=tenant_id,
        lifecycle_state="active",
        created_at="2026-08-09T00:00:00Z",
        updated_at="2026-08-09T00:00:00Z",
    )


def test_content_blob_uses_utf8_bytes_for_size_and_digest() -> None:
    blob = ContentBlob.from_text("KJ法")

    assert blob.byte_size == len("KJ法".encode("utf-8"))
    assert blob.sha256_digest == sha256("KJ法".encode("utf-8")).hexdigest()


def test_database_content_stores_preserve_semantics_and_tenant_scope(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'content-store.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    tenant_a = _tenant("tenant-a")
    tenant_b = _tenant("tenant-b")

    try:
        with session_local() as db:
            db.add_all([_tenant_row("tenant-a"), _tenant_row("tenant-b")])
            db.commit()

            documents = DatabaseDocumentContentStore(db)
            bundles = DatabaseBundleContentStore(db)
            logs = DatabaseAppendOnlyLogContentStore(db)

            document_a = documents.save(
                tenant=tenant_a,
                doc_id="shared",
                version=1,
                updated_at="2026-08-09T00:00:00Z",
                content=ContentBlob.from_text('{"owner":"a"}'),
            )
            documents.save(
                tenant=tenant_b,
                doc_id="shared",
                version=1,
                updated_at="2026-08-09T00:00:00Z",
                content=ContentBlob.from_text('{"owner":"b"}'),
            )
            bundles.replace(
                tenant=tenant_a,
                journey_id="journey",
                updated_at="2026-08-09T00:00:00Z",
                content=ContentBlob.from_text('{"round":1}'),
            )
            logs.append(
                tenant=tenant_a,
                doc_id="shared",
                decision_id="decision-1",
                group_id="group-1",
                snapshot_version="snapshot-1",
                decided_at="2026-08-09T00:00:00Z",
                content=ContentBlob.from_text('{"decision":"keep"}'),
            )
            assert document_a.row.id == "shared"
            db.commit()

            head_a = db.get(CanvasRevisionHeadRow, ("tenant-a", "shared", "main"))
            head_b = db.get(CanvasRevisionHeadRow, ("tenant-b", "shared", "main"))
            assert head_a is not None and head_a.head_version == 1
            assert head_b is not None and head_b.head_version == 1

            assert documents.load(tenant=tenant_a, doc_id="shared").content.text == '{"owner":"a"}'
            assert documents.load(tenant=tenant_b, doc_id="shared").content.text == '{"owner":"b"}'
            assert bundles.load(tenant=tenant_b, journey_id="journey") is None
            assert logs.list_by_group(tenant=tenant_b, doc_id="shared", group_id="group-1") == []
            assert (
                len(
                    logs.list_by_snapshot(
                        tenant=tenant_a, doc_id="shared", snapshot_version="snapshot-1"
                    )
                )
                == 1
            )

            replaced = bundles.replace(
                tenant=tenant_a,
                journey_id="journey",
                updated_at="2026-08-09T00:01:00Z",
                content=ContentBlob.from_text('{"round":2}'),
            )
            assert replaced.content.text == '{"round":2}'
            assert bundles.delete(tenant=tenant_a, journey_id="journey") is True
            assert bundles.delete(tenant=tenant_a, journey_id="journey") is False
            db.rollback()
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_document_store_materializes_legacy_parent_and_detects_divergence(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'document-revisions.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    tenant = _tenant("tenant-a")
    try:
        with session_local() as db:
            db.add(_tenant_row("tenant-a"))
            db.add(
                DocumentRow(
                    tenant_id="tenant-a",
                    id="legacy",
                    version=1,
                    updated_at="2026-08-09T00:00:00Z",
                    payload_json='{ "value": 1 }',
                )
            )
            db.commit()

            store = DatabaseDocumentContentStore(db)
            store.save(
                tenant=tenant,
                doc_id="legacy",
                version=1,
                updated_at="2026-08-09T00:00:00Z",
                content=ContentBlob.from_text('{ "value": 1 }'),
            )
            db.commit()
            initial_head = db.get(CanvasRevisionHeadRow, ("tenant-a", "legacy", "main"))
            assert initial_head is not None
            assert initial_head.head_version == 1
            assert db.scalar(select(func.count()).select_from(CanvasRevisionRow)) == 1
            assert store.load(tenant=tenant, doc_id="legacy").content.text == '{"value":1}'

            store.save(
                tenant=tenant,
                doc_id="legacy",
                version=1,
                updated_at="2026-08-09T00:01:00Z",
                content=ContentBlob.from_text('{"value":2}'),
            )
            db.commit()
            head = db.get(CanvasRevisionHeadRow, ("tenant-a", "legacy", "main"))
            assert head is not None
            assert head.head_version == 2
            assert db.scalar(select(func.count()).select_from(CanvasRevisionRow)) == 2
            assert db.scalar(select(func.count()).select_from(CanvasRevisionParentRow)) == 1

            # Canonically identical no-op writes do not create another revision.
            store.save(
                tenant=tenant,
                doc_id="legacy",
                version=1,
                updated_at="2026-08-09T00:01:00Z",
                content=ContentBlob.from_text('{"value":2}'),
            )
            db.commit()
            assert db.scalar(select(func.count()).select_from(CanvasRevisionRow)) == 2

            row = db.get(DocumentRow, ("tenant-a", "legacy"))
            assert row is not None
            row.payload_json = '{"value":3}'
            db.commit()
            with pytest.raises(DocumentRevisionDivergence, match="differs"):
                store.load(tenant=tenant, doc_id="legacy")
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_database_store_leaves_transaction_control_to_the_caller(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'transaction-control.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    tenant = _tenant("tenant-a")

    try:
        with session_local() as db:
            db.add(_tenant_row("tenant-a"))
            db.commit()
            DatabaseDocumentContentStore(db).save(
                tenant=tenant,
                doc_id="rolled-back",
                version=1,
                updated_at="2026-08-09T00:00:00Z",
                content=ContentBlob.from_text("{}"),
            )
            db.rollback()

        with session_local() as db:
            assert (
                DatabaseDocumentContentStore(db).load(tenant=tenant, doc_id="rolled-back") is None
            )
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_bundle_cas_is_atomic_and_revision_is_tenant_scoped(tmp_path) -> None:
    # DATA-INQUIRY-CONCURRENCY-01 (案A): create/update_cas/delete_cas use a
    # server-owned revision and single atomic statements (AC-3, AC-4, AC-7).
    engine = create_engine(f"sqlite:///{tmp_path / 'bundle-cas.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    tenant_a = _tenant("tenant-a")
    tenant_b = _tenant("tenant-b")

    try:
        with session_local() as db:
            db.add_all([_tenant_row("tenant-a"), _tenant_row("tenant-b")])
            db.commit()

        # create() starts the server-owned revision at 1.
        with session_local() as db:
            DatabaseBundleContentStore(db).create(
                tenant=tenant_a,
                journey_id="same-id",
                updated_at="2026-08-13T00:00:00Z",
                content=ContentBlob.from_text('{"round":1}'),
            )
            db.commit()

        # A stale expected revision is a no-op (single UPDATE matches 0 rows).
        with session_local() as db:
            store = DatabaseBundleContentStore(db)
            assert store.update_cas(
                tenant=tenant_a,
                journey_id="same-id",
                expected_revision=99,
                updated_at="2026-08-13T00:01:00Z",
                content=ContentBlob.from_text('{"round":"stale"}'),
            ) is False
            db.rollback()

        # The correct expected revision wins and bumps the revision.
        with session_local() as db:
            store = DatabaseBundleContentStore(db)
            assert store.update_cas(
                tenant=tenant_a,
                journey_id="same-id",
                expected_revision=1,
                updated_at="2026-08-13T00:02:00Z",
                content=ContentBlob.from_text('{"round":2}'),
            ) is True
            db.commit()

        with session_local() as db:
            loaded = DatabaseBundleContentStore(db).load(
                tenant=tenant_a, journey_id="same-id"
            )
            assert loaded is not None
            assert loaded.row.revision == 2
            assert json.loads(loaded.row.payload_json) == {"round": 2}

        # AC-4: two writers holding the same old revision — only one wins and
        # the loser changes no payload, audit, or revision.
        with session_local() as db:
            assert DatabaseBundleContentStore(db).update_cas(
                tenant=tenant_a,
                journey_id="same-id",
                expected_revision=2,
                updated_at="2026-08-13T00:03:00Z",
                content=ContentBlob.from_text('{"round":"winner"}'),
            ) is True
            db.commit()
        with session_local() as db:
            assert DatabaseBundleContentStore(db).update_cas(
                tenant=tenant_a,
                journey_id="same-id",
                expected_revision=2,
                updated_at="2026-08-13T00:04:00Z",
                content=ContentBlob.from_text('{"round":"loser"}'),
            ) is False
            db.rollback()

        with session_local() as db:
            loaded = DatabaseBundleContentStore(db).load(
                tenant=tenant_a, journey_id="same-id"
            )
            assert loaded is not None
            assert loaded.row.revision == 3
            assert json.loads(loaded.row.payload_json) == {"round": "winner"}

        # AC-7: the same journey id in tenant B keeps its own revision counter;
        # tenant A's CAS operations never touch tenant B's row.
        with session_local() as db:
            b_store = DatabaseBundleContentStore(db)
            b_store.create(
                tenant=tenant_b,
                journey_id="same-id",
                updated_at="2026-08-13T00:05:00Z",
                content=ContentBlob.from_text('{"owner":"b"}'),
            )
            db.commit()
        with session_local() as db:
            store = DatabaseBundleContentStore(db)
            assert store.update_cas(
                tenant=tenant_a,
                journey_id="same-id",
                expected_revision=3,
                updated_at="2026-08-13T00:06:00Z",
                content=ContentBlob.from_text('{"round":"next"}'),
            ) is True
            db.commit()
        with session_local() as db:
            assert (
                DatabaseBundleContentStore(db)
                .load(tenant=tenant_b, journey_id="same-id")
                .row.revision
                == 1
            )
            assert json.loads(
                DatabaseBundleContentStore(db)
                .load(tenant=tenant_b, journey_id="same-id")
                .row.payload_json
            ) == {"owner": "b"}

        # CAS delete: a correct revision deletes; a stale revision is a no-op.
        with session_local() as db:
            store = DatabaseBundleContentStore(db)
            assert store.delete_cas(
                tenant=tenant_b, journey_id="same-id", expected_revision=1
            ) is True
            assert store.delete_cas(
                tenant=tenant_a, journey_id="same-id", expected_revision=999
            ) is False
            db.commit()
        with session_local() as db:
            assert (
                DatabaseBundleContentStore(db).load(tenant=tenant_b, journey_id="same-id")
                is None
            )
            assert (
                DatabaseBundleContentStore(db).load(tenant=tenant_a, journey_id="same-id")
                is not None
            )
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
