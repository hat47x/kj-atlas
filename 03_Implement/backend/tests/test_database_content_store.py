from hashlib import sha256

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.content_store import ContentBlob
from kj_atlas_api.database_content_store import (
    DatabaseAppendOnlyLogContentStore,
    DatabaseBundleContentStore,
    DatabaseDocumentContentStore,
)
from kj_atlas_api.models import Base, TenantRow
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
            assert document_a.row in db.new
            db.commit()

            assert documents.load(tenant=tenant_a, doc_id="shared").content.text == '{"owner":"a"}'
            assert documents.load(tenant=tenant_b, doc_id="shared").content.text == '{"owner":"b"}'
            assert bundles.load(tenant=tenant_b, journey_id="journey") is None
            assert logs.list_by_group(
                tenant=tenant_b, doc_id="shared", group_id="group-1"
            ) == []
            assert len(
                logs.list_by_snapshot(
                    tenant=tenant_a, doc_id="shared", snapshot_version="snapshot-1"
                )
            ) == 1

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
            assert DatabaseDocumentContentStore(db).load(
                tenant=tenant, doc_id="rolled-back"
            ) is None
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
