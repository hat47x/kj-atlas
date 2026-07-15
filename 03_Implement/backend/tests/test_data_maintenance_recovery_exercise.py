from __future__ import annotations

import shutil
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base


@contextmanager
def _sqlite_client(db_path: Path, *, create_schema: bool) -> Iterator[TestClient]:
    engine = create_engine(f"sqlite:///{db_path}")
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


def _backup_sqlite_database(source: Path, destination: Path) -> None:
    with sqlite3.connect(source) as source_connection:
        with sqlite3.connect(destination) as destination_connection:
            source_connection.backup(destination_connection)


def _recovery_document(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "data maintenance recovery exercise",
        "createdAt": "2026-05-25T00:00:00Z",
        "updatedAt": "2026-05-25T00:01:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {
                "id": "card-reviewed",
                "text": "Reviewed recovery note",
                "x": 0,
                "y": 0,
                "claimType": "fact",
                "textReviewed": True,
            },
            {
                "id": "card-unreviewed",
                "text": "Unreviewed recovery note",
                "x": 180,
                "y": 40,
                "claimType": "hypothesis",
                "textReviewed": False,
            },
        ],
        "edges": [
            {
                "id": "edge-1",
                "fromId": "card-reviewed",
                "toId": "card-unreviewed",
                "type": "related",
            }
        ],
        "islands": [
            {
                "id": "island-recovery",
                "cardIds": ["card-reviewed", "card-unreviewed"],
                "shape": {"kind": "rect"},
                "title": "Recovery scope",
            }
        ],
        "mergeSuggestionDecisions": [
            {
                "id": "embedded-decision-1",
                "groupId": "group-recovery",
                "decision": "defer",
                "decidedAt": "2026-05-25T00:02:00Z",
                "cardIds": ["card-reviewed", "card-unreviewed"],
                "mergedTextDraft": "Reviewed recovery note / Unreviewed recovery note",
                "editedText": "Reviewed recovery note / Unreviewed recovery note",
                "rationale": "backup restore exercise",
            }
        ],
    }


def _decision_record(*, decision_id: str, action: str) -> dict:
    return {
        "decisionId": decision_id,
        "groupId": "group-recovery",
        "action": action,
        "selectedCardIds": ["card-reviewed", "card-unreviewed"],
        "note": "DATA-MAINT-02 recovery exercise",
        "decidedBy": "reviewer:opaque-data-maint",
        "decidedAt": "2026-05-25T00:03:00Z",
        "snapshotVersion": "snapshot-recovery-1",
    }


def test_sqlite_backup_restore_exercise_preserves_document_logs_and_safe_export_gate(
    tmp_path: Path,
) -> None:
    source_db = tmp_path / "source.sqlite3"
    backup_db = tmp_path / "backup.sqlite3"
    restored_db = tmp_path / "restored.sqlite3"
    doc_id = "doc-data-maint-recovery"

    with _sqlite_client(source_db, create_schema=True) as client:
        put_response = client.put(f"/docs/{doc_id}", json=_recovery_document(doc_id))
        assert put_response.status_code == 200

        first_log = client.post(
            f"/docs/{doc_id}/merge-decision-logs",
            json={"record": _decision_record(decision_id="decision-1", action="accept")},
        )
        assert first_log.status_code == 201

        second_log = client.post(
            f"/docs/{doc_id}/merge-decision-logs",
            json={"record": _decision_record(decision_id="decision-2", action="partial")},
        )
        assert second_log.status_code == 201

    _backup_sqlite_database(source_db, backup_db)
    shutil.copy2(backup_db, restored_db)

    with _sqlite_client(restored_db, create_schema=False) as client:
        loaded = client.get(f"/docs/{doc_id}")
        assert loaded.status_code == 200
        loaded_json = loaded.json()
        assert loaded_json["version"] == 1
        assert loaded_json["id"] == doc_id
        assert loaded_json["cards"][0]["textReviewed"] is True
        assert loaded_json["cards"][1]["textReviewed"] is False
        assert loaded_json["mergeSuggestionDecisions"][0]["groupId"] == "group-recovery"

        by_group = client.get(f"/docs/{doc_id}/merge-decision-logs/by-group/group-recovery")
        assert by_group.status_code == 200
        assert [entry["decisionId"] for entry in by_group.json()] == ["decision-1", "decision-2"]

        restored_logs = client.get(
            f"/docs/{doc_id}/merge-decision-logs/restore/snapshot-recovery-1"
        )
        assert restored_logs.status_code == 200
        assert [entry["action"] for entry in restored_logs.json()] == ["accept", "partial"]

        safe_mode_export = client.post(
            f"/docs/{doc_id}/export-audit",
            json={"safeMode": True, "exportKind": "bundle"},
        )
        assert safe_mode_export.status_code == 403
        assert safe_mode_export.json()["detail"] == "Access denied: safe_mode"
