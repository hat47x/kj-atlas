from __future__ import annotations

import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

from kj_atlas_api.models import LOCAL_DEFAULT_TENANT_ID


BACKEND_DIR = Path(__file__).resolve().parents[1]
TIMESTAMP = "2026-07-17T00:00:00Z"


def _run_alembic(db_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["KJ_ATLAS_DATABASE_URL"] = f"sqlite:///{db_path}"
    return subprocess.run(
        ["alembic", *args],
        cwd=BACKEND_DIR,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


def _upgrade_to_0007(db_path: Path) -> None:
    upgrade = _run_alembic(db_path, "upgrade", "20260717_0007")
    assert upgrade.returncode == 0, upgrade.stderr


def _insert_tenant(con: sqlite3.Connection, tenant_id: str) -> None:
    con.execute(
        """
        INSERT INTO tenants (
            id, display_name, lifecycle_state, created_at, updated_at
        ) VALUES (?, ?, 'active', ?, ?)
        """,
        (tenant_id, tenant_id, TIMESTAMP, TIMESTAMP),
    )


def _insert_document(
    con: sqlite3.Connection,
    *,
    tenant_id: str,
    doc_id: str,
) -> None:
    con.execute(
        """
        INSERT INTO documents (
            tenant_id, id, version, updated_at, payload_json
        ) VALUES (?, ?, 1, ?, '{}')
        """,
        (tenant_id, doc_id, TIMESTAMP),
    )


def test_migration_allows_same_doc_id_per_tenant_and_enforces_log_fk(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "tenant_document_key.sqlite3"
    _upgrade_to_0007(db_path)

    con = sqlite3.connect(db_path)
    try:
        _insert_document(
            con,
            tenant_id=LOCAL_DEFAULT_TENANT_ID,
            doc_id="shared-doc",
        )
        con.execute(
            """
            INSERT INTO merge_decision_logs (
                tenant_id, doc_id, decision_id, group_id,
                snapshot_version, decided_at, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, '{}')
            """,
            (
                LOCAL_DEFAULT_TENANT_ID,
                "shared-doc",
                "shared-decision",
                "group-1",
                "snapshot-1",
                TIMESTAMP,
            ),
        )
        con.commit()
    finally:
        con.close()

    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        primary_key_columns = {
            row[1]: row[5]
            for row in con.execute("PRAGMA table_info('documents')")
            if row[5] > 0
        }
        assert primary_key_columns == {"tenant_id": 1, "id": 2}

        foreign_keys = list(
            con.execute("PRAGMA foreign_key_list('merge_decision_logs')")
        )
        composite_pairs = {
            (row[3], row[4])
            for row in foreign_keys
            if row[2] == "documents"
        }
        assert composite_pairs == {("tenant_id", "tenant_id"), ("doc_id", "id")}

        _insert_tenant(con, "tenant-b")
        _insert_document(con, tenant_id="tenant-b", doc_id="shared-doc")
        con.execute(
            """
            INSERT INTO merge_decision_logs (
                tenant_id, doc_id, decision_id, group_id,
                snapshot_version, decided_at, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, '{}')
            """,
            (
                "tenant-b",
                "shared-doc",
                "shared-decision",
                "group-1",
                "snapshot-1",
                TIMESTAMP,
            ),
        )
        con.commit()
        assert con.execute(
            "SELECT COUNT(*) FROM documents WHERE id = 'shared-doc'"
        ).fetchone() == (2,)
        assert con.execute(
            """
            SELECT COUNT(*) FROM merge_decision_logs
            WHERE doc_id = 'shared-doc' AND decision_id = 'shared-decision'
            """
        ).fetchone() == (2,)

        con.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(sqlite3.IntegrityError):
            con.execute(
                """
                INSERT INTO merge_decision_logs (
                    tenant_id, doc_id, decision_id, group_id,
                    snapshot_version, decided_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, '{}')
                """,
                (
                    "tenant-b",
                    "missing-doc",
                    "orphan-decision",
                    "group-1",
                    "snapshot-1",
                    TIMESTAMP,
                ),
            )
    finally:
        con.close()


def test_downgrade_refuses_duplicate_doc_ids_then_restores_global_key(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "tenant_document_key_downgrade.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        _insert_tenant(con, "tenant-b")
        _insert_document(
            con,
            tenant_id=LOCAL_DEFAULT_TENANT_ID,
            doc_id="duplicate-doc",
        )
        _insert_document(con, tenant_id="tenant-b", doc_id="duplicate-doc")
        con.commit()
    finally:
        con.close()

    blocked = _run_alembic(db_path, "downgrade", "20260717_0007")
    assert blocked.returncode != 0
    assert "duplicate docId values exist" in blocked.stderr

    con = sqlite3.connect(db_path)
    try:
        con.execute(
            "DELETE FROM documents WHERE tenant_id = ? AND id = ?",
            ("tenant-b", "duplicate-doc"),
        )
        con.commit()
    finally:
        con.close()

    downgrade = _run_alembic(db_path, "downgrade", "20260717_0007")
    assert downgrade.returncode == 0, downgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        primary_key_columns = {
            row[1]: row[5]
            for row in con.execute("PRAGMA table_info('documents')")
            if row[5] > 0
        }
        indexes = {
            row[1] for row in con.execute("PRAGMA index_list('documents')")
        }
        assert primary_key_columns == {"id": 1}
        assert "ix_documents_tenant_id_id" in indexes
    finally:
        con.close()
