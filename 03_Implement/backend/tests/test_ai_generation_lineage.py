from hashlib import sha256

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    AiGenerationRunRow,
    Base,
    CanvasRevisionRow,
    ContentBlobRow,
    DocumentRow,
    TenantRow,
)


TIMESTAMP = "2026-08-10T00:00:00Z"
INPUT_DIGEST = sha256(b"redacted input IR").hexdigest()
OUTPUT_DIGEST = sha256(b"{}").hexdigest()


def _engine(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'ai-lineage.sqlite3'}")

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
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
        db.commit()
        for tenant_id in ("tenant-a", "tenant-b"):
            db.add(
                DocumentRow(
                    tenant_id=tenant_id,
                    id="doc",
                    version=1,
                    updated_at=TIMESTAMP,
                    payload_json="{}",
                )
            )
            db.add(
                ContentBlobRow(
                    tenant_id=tenant_id,
                    content_digest=OUTPUT_DIGEST,
                    storage_backend="database",
                    locator=None,
                    representation="full_json",
                    base_digest=None,
                    delta_depth=0,
                    byte_size=2,
                    stored_byte_size=2,
                    storage_state="ready",
                    schema_version="document-v1",
                    created_at=TIMESTAMP,
                )
            )
        db.commit()
    return engine


def _run(tenant_id: str = "tenant-a", *, safe_mode: bool = True) -> AiGenerationRunRow:
    return AiGenerationRunRow(
        tenant_id=tenant_id,
        ai_run_id="run-1",
        task="cluster_cards",
        trace_id="trace-1",
        input_ir_digest=INPUT_DIGEST,
        output_digest=OUTPUT_DIGEST,
        policy_version="ai-generation-v1",
        safe_mode=safe_mode,
        created_at=TIMESTAMP,
        retention_expires_at="2026-09-10T00:00:00Z",
    )


def _revision(*, tenant_id: str = "tenant-a", origin: str, ai_run_ref: str | None):
    return CanvasRevisionRow(
        tenant_id=tenant_id,
        revision_id=f"revision-{origin}",
        doc_id="doc",
        content_digest=OUTPUT_DIGEST,
        generation_tier="checkpoint",
        generation_reason="ai_proposal" if origin == "ai_proposal" else "manual_save",
        generation_origin=origin,
        actor_ref=None,
        ai_run_ref=ai_run_ref,
        source_revision_id=None,
        created_at=TIMESTAMP,
    )


def test_ai_run_links_only_to_same_tenant_ai_proposal(tmp_path) -> None:
    engine = _engine(tmp_path)
    with Session(engine) as db:
        db.add(_run())
        db.commit()
        db.add(_revision(origin="ai_proposal", ai_run_ref="run-1"))
        db.commit()

    invalid = (
        _revision(tenant_id="tenant-b", origin="ai_proposal", ai_run_ref="run-1"),
        _revision(origin="ai_proposal", ai_run_ref=None),
        _revision(origin="human", ai_run_ref="run-1"),
    )
    for row in invalid:
        with Session(engine) as db, pytest.raises(IntegrityError):
            db.add(row)
            db.commit()


def test_ai_run_rejects_disabled_safe_mode(tmp_path) -> None:
    engine = _engine(tmp_path)
    with Session(engine) as db, pytest.raises(IntegrityError):
        db.add(_run(safe_mode=False))
        db.commit()


def test_ai_run_schema_does_not_store_prompt_or_generated_text() -> None:
    columns = set(AiGenerationRunRow.__table__.columns.keys())
    assert not columns.intersection({"prompt", "raw_text", "input_text", "output_text"})
