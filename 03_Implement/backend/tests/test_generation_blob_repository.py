from dataclasses import replace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.generation_codec import canonical_json_bytes, encode_generation
from kj_atlas_api.generation_repository import (
    GenerationBlobConflict,
    GenerationBlobUnavailable,
    load_database_generation_blob,
    save_database_generation_blob,
)
from kj_atlas_api.models import Base, ContentBlobRow, TenantRow
from kj_atlas_api.tenant_context import TenantContext


TIMESTAMP = "2026-08-11T00:00:00Z"


def _tenant(tenant_id: str) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id=f"membership-{tenant_id}",
        resolved_by="verified_claim",
    )


@pytest.fixture
def generation_db(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'generation-blobs.sqlite3'}")
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
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_database_blob_roundtrip_is_idempotent_and_tenant_scoped(generation_db) -> None:
    value = {"cards": [{"id": str(index), "text": "observation" * 20} for index in range(100)]}
    encoded = encode_generation(value)
    with Session(generation_db) as db:
        first = save_database_generation_blob(
            db,
            tenant=_tenant("tenant-a"),
            blob=encoded,
            schema_version="document-v1",
            created_at=TIMESTAMP,
        )
        db.commit()
        second = save_database_generation_blob(
            db,
            tenant=_tenant("tenant-a"),
            blob=encoded,
            schema_version="document-v1",
            created_at="ignored-for-idempotency",
        )
        assert second is first
        assert load_database_generation_blob(
            db,
            tenant=_tenant("tenant-a"),
            content_digest=encoded.content_digest,
        ) == canonical_json_bytes(value)
        with pytest.raises(GenerationBlobUnavailable):
            load_database_generation_blob(
                db,
                tenant=_tenant("tenant-b"),
                content_digest=encoded.content_digest,
            )


def test_database_delta_roundtrip_and_integrity_fail_closed(generation_db) -> None:
    base_value = {"cards": [{"id": str(index), "text": "observation" * 20} for index in range(100)]}
    base_bytes = canonical_json_bytes(base_value)
    base = encode_generation(base_value)
    changed_value = {"cards": list(base_value["cards"])}
    changed_value["cards"][50] = {"id": "50", "text": "changed"}
    changed = encode_generation(
        changed_value,
        base_bytes=base_bytes,
        base_digest=base.content_digest,
    )
    assert changed.representation == "gzip_delta"

    with Session(generation_db) as db:
        save_database_generation_blob(
            db,
            tenant=_tenant("tenant-a"),
            blob=base,
            schema_version="document-v1",
            created_at=TIMESTAMP,
        )
        db.flush()
        save_database_generation_blob(
            db,
            tenant=_tenant("tenant-a"),
            blob=changed,
            schema_version="document-v1",
            created_at=TIMESTAMP,
        )
        db.commit()
        assert load_database_generation_blob(
            db,
            tenant=_tenant("tenant-a"),
            content_digest=changed.content_digest,
        ) == canonical_json_bytes(changed_value)

        row = db.get(ContentBlobRow, ("tenant-a", changed.content_digest))
        assert row is not None
        row.payload_bytes = b"tampered"
        row.stored_byte_size = len(row.payload_bytes)
        db.commit()
        with pytest.raises(GenerationBlobUnavailable, match="integrity"):
            load_database_generation_blob(
                db,
                tenant=_tenant("tenant-a"),
                content_digest=changed.content_digest,
            )


def test_database_blob_rejects_invalid_or_conflicting_codec_output(generation_db) -> None:
    encoded = encode_generation({"cards": []})
    with Session(generation_db) as db:
        with pytest.raises(GenerationBlobConflict, match="integrity"):
            save_database_generation_blob(
                db,
                tenant=_tenant("tenant-a"),
                blob=replace(encoded, content_digest="0" * 64),
                schema_version="document-v1",
                created_at=TIMESTAMP,
            )
        save_database_generation_blob(
            db,
            tenant=_tenant("tenant-a"),
            blob=encoded,
            schema_version="document-v1",
            created_at=TIMESTAMP,
        )
        db.commit()
        with pytest.raises(GenerationBlobConflict, match="different content"):
            save_database_generation_blob(
                db,
                tenant=_tenant("tenant-a"),
                blob=encoded,
                schema_version="different-schema",
                created_at=TIMESTAMP,
            )


def test_database_blob_rejects_missing_base_and_detects_delta_cycle(generation_db) -> None:
    base_value = {"cards": [{"id": str(index), "text": "observation" * 20} for index in range(100)]}
    base_bytes = canonical_json_bytes(base_value)
    base = encode_generation(base_value)
    changed_value = {"cards": list(base_value["cards"])}
    changed_value["cards"][50] = {"id": "50", "text": "changed"}
    changed = encode_generation(
        changed_value,
        base_bytes=base_bytes,
        base_digest=base.content_digest,
    )
    assert changed.representation == "gzip_delta"
    with Session(generation_db) as db:
        with pytest.raises(GenerationBlobUnavailable, match="not materialized"):
            save_database_generation_blob(
                db,
                tenant=_tenant("tenant-a"),
                blob=changed,
                schema_version="document-v1",
                created_at=TIMESTAMP,
            )
        save_database_generation_blob(
            db,
            tenant=_tenant("tenant-a"),
            blob=base,
            schema_version="document-v1",
            created_at=TIMESTAMP,
        )
        db.flush()
        save_database_generation_blob(
            db,
            tenant=_tenant("tenant-a"),
            blob=changed,
            schema_version="document-v1",
            created_at=TIMESTAMP,
        )
        db.commit()

        base_row = db.get(ContentBlobRow, ("tenant-a", base.content_digest))
        assert base_row is not None
        base_row.representation = "gzip_delta"
        base_row.base_digest = changed.content_digest
        base_row.delta_depth = 2
        db.commit()
        with pytest.raises(GenerationBlobUnavailable, match="cycle"):
            load_database_generation_blob(
                db,
                tenant=_tenant("tenant-a"),
                content_digest=changed.content_digest,
            )
