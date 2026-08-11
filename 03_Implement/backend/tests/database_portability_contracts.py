from __future__ import annotations

from hashlib import sha256

import pytest
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from kj_atlas_api.content_store import ContentBlob
from kj_atlas_api.database_content_store import DatabaseDocumentContentStore
from kj_atlas_api.generation_codec import canonical_json_bytes, encode_generation
from kj_atlas_api.generation_repository import (
    RevisionHeadConflict,
    advance_revision_head,
    load_database_generation_blob,
    save_database_generation_blob,
)
from kj_atlas_api.models import (
    AiGenerationRunRow,
    CanvasRevisionHeadRow,
    CanvasRevisionParentRow,
    CanvasRevisionPinRow,
    CanvasRevisionRow,
    ContentBlobRow,
    DocumentRow,
    TenantRow,
)
from kj_atlas_api.tenant_context import TenantContext


TIMESTAMP = "2026-08-10T00:00:00Z"


def verify_revision_dag_contract(engine: Engine) -> None:
    """Exercise the same revision identity, lineage, and CAS contract on every DB."""
    digest = sha256(b'{"portable":true}').hexdigest()
    tenant = TenantContext(
        tenant_id="tenant-a",
        membership_id="portability-contract",
        resolved_by="verified_claim",
    )

    with Session(engine) as db:
        for tenant_id in ("tenant-a", "tenant-b"):
            if db.get(TenantRow, tenant_id) is None:
                db.add(
                    TenantRow(
                        id=tenant_id,
                        display_name=tenant_id,
                        lifecycle_state="active",
                        created_at=TIMESTAMP,
                        updated_at=TIMESTAMP,
                    )
                )
                db.flush()
            db.add(
                DocumentRow(
                    tenant_id=tenant_id,
                    id="portable-document",
                    version=1,
                    updated_at=TIMESTAMP,
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
                    byte_size=17,
                    stored_byte_size=17,
                    storage_state="ready",
                    schema_version="document-v1",
                    created_at=TIMESTAMP,
                    payload_bytes=b'{"portable":true}',
                )
            )
        db.commit()

        db.add(
            AiGenerationRunRow(
                tenant_id="tenant-a",
                ai_run_id="portable-ai-run",
                task="cluster",
                trace_id="portable-trace",
                input_ir_digest=digest,
                output_digest=digest,
                policy_version="portable-v1",
                safe_mode=True,
                created_at=TIMESTAMP,
                retention_expires_at=None,
            )
        )
        for tenant_id in ("tenant-a", "tenant-b"):
            db.add(
                CanvasRevisionRow(
                    tenant_id=tenant_id,
                    revision_id="portable-base",
                    doc_id="portable-document",
                    content_digest=digest,
                    generation_tier="checkpoint",
                    generation_reason="manual_save",
                    generation_origin="human",
                    actor_ref=None,
                    ai_run_ref=None,
                    source_revision_id=None,
                    created_at=TIMESTAMP,
                )
            )
        db.commit()

        db.add(
            CanvasRevisionRow(
                tenant_id="tenant-a",
                revision_id="portable-proposal",
                doc_id="portable-document",
                content_digest=digest,
                generation_tier="ephemeral",
                generation_reason="ai_proposal",
                generation_origin="ai_proposal",
                actor_ref=None,
                ai_run_ref="portable-ai-run",
                source_revision_id="portable-base",
                created_at=TIMESTAMP,
            )
        )
        db.commit()
        db.add(
            CanvasRevisionParentRow(
                tenant_id="tenant-a",
                revision_id="portable-proposal",
                parent_revision_id="portable-base",
                parent_order=0,
            )
        )
        db.add(
            CanvasRevisionPinRow(
                tenant_id="tenant-a",
                revision_id="portable-base",
                pin_reason="portability-contract",
                created_at=TIMESTAMP,
            )
        )
        db.add(
            CanvasRevisionHeadRow(
                tenant_id="tenant-a",
                doc_id="portable-document",
                head_name="portable-main",
                revision_id="portable-base",
                head_version=1,
                updated_at=TIMESTAMP,
            )
        )
        db.commit()

        assert (
            advance_revision_head(
                db,
                tenant=tenant,
                doc_id="portable-document",
                head_name="portable-main",
                expected_version=1,
                new_revision_id="portable-proposal",
                updated_at=TIMESTAMP,
            )
            == 2
        )
        db.commit()
        with pytest.raises(RevisionHeadConflict):
            advance_revision_head(
                db,
                tenant=tenant,
                doc_id="portable-document",
                head_name="portable-main",
                expected_version=1,
                new_revision_id="portable-base",
                updated_at=TIMESTAMP,
            )

        head = db.scalar(
            select(CanvasRevisionHeadRow).where(
                CanvasRevisionHeadRow.tenant_id == "tenant-a",
                CanvasRevisionHeadRow.doc_id == "portable-document",
                CanvasRevisionHeadRow.head_name == "portable-main",
            )
        )
        assert head is not None
        assert head.revision_id == "portable-proposal"
        assert head.head_version == 2

        tenant_b_revisions = db.scalars(
            select(CanvasRevisionRow.revision_id).where(CanvasRevisionRow.tenant_id == "tenant-b")
        ).all()
        assert tenant_b_revisions == ["portable-base"]

        # Exercise the actual binary LOB, not only its metadata. Deterministic
        # hash material remains larger than 1 MiB after gzip compression.
        large_value = {
            "entropy": "".join(sha256(str(index).encode()).hexdigest() for index in range(30_000))
        }
        large_blob = encode_generation(large_value)
        assert len(large_blob.stored_bytes) > 1024 * 1024
        save_database_generation_blob(
            db,
            tenant=tenant,
            blob=large_blob,
            schema_version="document-v1",
            created_at=TIMESTAMP,
        )
        db.commit()
        assert load_database_generation_blob(
            db,
            tenant=tenant,
            content_digest=large_blob.content_digest,
        ) == canonical_json_bytes(large_value)

        document_store = DatabaseDocumentContentStore(db)
        document_store.save(
            tenant=tenant,
            doc_id="portable-runtime-document",
            version=1,
            updated_at=TIMESTAMP,
            content=ContentBlob.from_text('{"revision":1}'),
        )
        db.commit()
        document_store.save(
            tenant=tenant,
            doc_id="portable-runtime-document",
            version=1,
            updated_at="2026-08-10T00:00:01Z",
            content=ContentBlob.from_text('{"revision":2}'),
        )
        db.commit()
        runtime_head = db.get(
            CanvasRevisionHeadRow,
            ("tenant-a", "portable-runtime-document", "main"),
        )
        assert runtime_head is not None
        assert runtime_head.head_version == 2
        assert (
            document_store.load(
                tenant=tenant,
                doc_id="portable-runtime-document",
            ).content.text
            == '{"revision":2}'
        )
