from __future__ import annotations

import json
import shutil
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import _normalize_database_url, get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base


@contextmanager
def _sqlite_client_for_file(db_path: Path, *, create_schema: bool) -> Iterator[TestClient]:
    engine = create_engine(_normalize_database_url(f"sqlite:///{db_path}"))
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    if create_schema:
        Base.metadata.create_all(bind=engine)

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _recovery_document_payload(doc_id: str) -> dict:
    return {
        "version": 2,
        "id": doc_id,
        "title": "data-maintenance recovery rehearsal",
        "createdAt": "2026-05-24T00:00:00Z",
        "updatedAt": "2026-05-24T00:05:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {"id": "card-1", "text": "復旧演習の前提", "x": 0, "y": 0, "textReviewed": True},
            {"id": "card-2", "text": "判断ログと一緒に戻す", "x": 200, "y": 0, "textReviewed": False},
        ],
        "edges": [
            {"id": "edge-1", "fromId": "card-1", "toId": "card-2", "type": "related"},
        ],
        "islands": [],
        "mergeSuggestionDecisions": [
            {
                "id": "embedded-decision-1",
                "groupId": "group-recovery",
                "decision": "defer",
                "decidedAt": "2026-05-24T00:04:00Z",
                "cardIds": ["card-1", "card-2"],
                "mergedTextDraft": "復旧演習の前提と判断ログ",
                "editedText": "復旧演習の前提と判断ログ",
                "rationale": "operator rehearsal fixture",
            }
        ],
    }


def _merge_decision_record(*, decision_id: str, action: str) -> dict:
    return {
        "decisionId": decision_id,
        "groupId": "group-recovery",
        "action": action,
        "selectedCardIds": ["card-1", "card-2"],
        "note": "data maintenance recovery rehearsal",
        "decidedBy": "reviewer:opaque-maint",
        "decidedAt": "2026-05-24T00:06:00Z",
        "snapshotVersion": "snap-recovery-1",
    }


def test_sqlite_backup_restore_rehearsal_preserves_document_and_merge_decisions(tmp_path: Path) -> None:
    source_db = tmp_path / "source.sqlite3"
    backup_db = tmp_path / "backup.sqlite3"
    restored_db = tmp_path / "restored.sqlite3"
    doc_id = "doc-data-maint-recovery"

    with _sqlite_client_for_file(source_db, create_schema=True) as client:
        put_response = client.put(f"/docs/{doc_id}", json=_recovery_document_payload(doc_id))
        assert put_response.status_code == 200
        assert put_response.json()["version"] == 2

        for decision_id, action in (("decision-restore-1", "accept"), ("decision-restore-2", "partial")):
            append_response = client.post(
                f"/docs/{doc_id}/merge-decision-logs",
                json={"record": _merge_decision_record(decision_id=decision_id, action=action)},
            )
            assert append_response.status_code == 201

        before_backup = client.get(f"/docs/{doc_id}/merge-decision-logs/restore/snap-recovery-1")
        assert before_backup.status_code == 200
        assert [entry["decisionId"] for entry in before_backup.json()] == [
            "decision-restore-1",
            "decision-restore-2",
        ]

    assert source_db.exists()
    shutil.copy2(source_db, backup_db)
    assert backup_db.stat().st_size > 0
    shutil.copy2(backup_db, restored_db)

    with _sqlite_client_for_file(restored_db, create_schema=False) as restored_client:
        restored_doc = restored_client.get(f"/docs/{doc_id}")
        assert restored_doc.status_code == 200
        restored_payload = restored_doc.json()
        assert restored_payload["version"] == 2
        assert restored_payload["id"] == doc_id
        assert restored_payload["title"] == "data-maintenance recovery rehearsal"
        assert [card["id"] for card in restored_payload["cards"]] == ["card-1", "card-2"]

        restored_logs = restored_client.get(f"/docs/{doc_id}/merge-decision-logs/restore/snap-recovery-1")
        assert restored_logs.status_code == 200
        assert [entry["action"] for entry in restored_logs.json()] == ["accept", "partial"]

    with sqlite3.connect(restored_db) as connection:
        doc_row = connection.execute(
            "select version, payload_json from documents where id = ?",
            (doc_id,),
        ).fetchone()
        assert doc_row is not None
        assert doc_row[0] == 2
        assert json.loads(doc_row[1])["id"] == doc_id

        log_count = connection.execute(
            "select count(*) from merge_decision_logs where doc_id = ? and snapshot_version = ?",
            (doc_id, "snap-recovery-1"),
        ).fetchone()[0]
        assert log_count == 2
