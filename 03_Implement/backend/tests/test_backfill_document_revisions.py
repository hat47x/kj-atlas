from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.backfill_document_revisions import backfill_document_revisions
from kj_atlas_api.models import Base, CanvasRevisionHeadRow, DocumentRow, TenantRow


TIMESTAMP = "2026-08-11T00:00:00Z"


def test_document_revision_backfill_is_scoped_batched_and_idempotent(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'document-revision-backfill.sqlite3'}")
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as db:
            for tenant_id in ("tenant-a", "tenant-b"):
                db.add(
                    TenantRow(
                        id=tenant_id,
                        display_name=tenant_id,
                        lifecycle_state="active",
                        created_at=TIMESTAMP,
                        updated_at=TIMESTAMP,
                    )
                )
                for index in range(2):
                    db.add(
                        DocumentRow(
                            tenant_id=tenant_id,
                            id=f"doc-{index}",
                            version=1,
                            updated_at=TIMESTAMP,
                            payload_json=f'{{"tenant":"{tenant_id}","index":{index}}}',
                        )
                    )
            db.commit()

            dry_run = backfill_document_revisions(
                db,
                tenant_id="tenant-a",
                dry_run=True,
                limit=1,
            )
            assert dry_run.candidates == 1
            assert dry_run.materialized == 0
            assert dry_run.remaining == 2
            assert db.get(CanvasRevisionHeadRow, ("tenant-a", "doc-0", "main")) is None

            first = backfill_document_revisions(
                db,
                tenant_id="tenant-a",
                dry_run=False,
                limit=1,
            )
            db.commit()
            assert first.materialized == 1
            assert first.remaining == 1
            assert db.get(CanvasRevisionHeadRow, ("tenant-a", "doc-0", "main")) is not None
            assert db.get(CanvasRevisionHeadRow, ("tenant-b", "doc-0", "main")) is None

            second = backfill_document_revisions(
                db,
                tenant_id="tenant-a",
                dry_run=False,
                limit=100,
            )
            db.commit()
            assert second.materialized == 1
            assert second.remaining == 0

            complete = backfill_document_revisions(
                db,
                tenant_id="tenant-a",
                dry_run=False,
            )
            assert complete.materialized == 0
            assert complete.remaining == 0
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
