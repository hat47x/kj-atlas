from hashlib import sha256

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.generation_repository import RevisionHeadConflict, advance_revision_head
from kj_atlas_api.models import (
    Base,
    CanvasRevisionHeadRow,
    CanvasRevisionRow,
    ContentBlobRow,
    DocumentRow,
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
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
