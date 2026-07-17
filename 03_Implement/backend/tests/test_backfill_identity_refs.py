from __future__ import annotations

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.backfill_identity_refs import run_backfill
from kj_atlas_api.models import (
    Base,
    DocumentRow,
    LOCAL_DEFAULT_TENANT_ID,
    UserIdentityRow,
    UserRow,
)


def test_backfill_identity_refs_dry_run_then_apply(tmp_path) -> None:
    db_path = tmp_path / "backfill.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    payload = {
        "id": "doc-backfill",
        "reviewers": [{"reviewerRef": "user:sso:sub:alice"}],
        "reviewEvents": [{"reviewerRef": "user:sso:sub:alice", "target": {"kind": "card", "id": "c1"}}],
        "cards": [{"id": "card-1", "ownerRef": "user:sso:sub:alice", "text": "hello", "x": 0, "y": 0}],
        "edges": [],
    }

    with session_local() as db:
        db.add(
            UserRow(
                id="u-1",
                display_name="Alice",
                email="alice@example.com",
                lifecycle_state="active",
                created_at="2026-03-03T00:00:00Z",
                updated_at="2026-03-03T00:00:00Z",
            )
        )
        db.add(
            UserIdentityRow(
                user_id="u-1",
                provider="sso",
                external_uid="alice",
                created_at="2026-03-03T00:00:00Z",
            )
        )
        db.add(
            DocumentRow(
                id="doc-backfill",
                version=1,
                updated_at="2026-03-03T00:00:00Z",
                payload_json=json.dumps(payload),
            )
        )
        db.commit()

    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps({"user:sso:sub:alice": "u-1"}), encoding="utf-8")

    dry_stats = run_backfill(
        database_url=f"sqlite:///{db_path}",
        mapping_path=mapping_path,
        dry_run=True,
    )
    assert dry_stats.updated_documents == 1
    assert dry_stats.reviewer_refs_rewritten == 2
    assert dry_stats.owner_refs_rewritten == 1

    with session_local() as db:
        persisted = json.loads(
            db.get(DocumentRow, (LOCAL_DEFAULT_TENANT_ID, "doc-backfill")).payload_json
        )
        assert persisted["reviewers"][0]["reviewerRef"] == "user:sso:sub:alice"

    apply_stats = run_backfill(
        database_url=f"sqlite:///{db_path}",
        mapping_path=mapping_path,
        dry_run=False,
    )
    assert apply_stats.updated_documents == 1

    with session_local() as db:
        persisted = json.loads(
            db.get(DocumentRow, (LOCAL_DEFAULT_TENANT_ID, "doc-backfill")).payload_json
        )
        assert persisted["reviewers"][0]["reviewerRef"] == "user:u-1"
        assert persisted["reviewEvents"][0]["reviewerRef"] == "user:u-1"
        assert persisted["cards"][0]["ownerRef"] == "user:u-1"

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
