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


def _insert_document(con: sqlite3.Connection, doc_id: str) -> None:
    con.execute(
        """
        INSERT INTO documents (tenant_id, id, version, updated_at, payload_json)
        VALUES (?, ?, 1, ?, '{}')
        """,
        (LOCAL_DEFAULT_TENANT_ID, doc_id, TIMESTAMP),
    )
    con.commit()


def test_migration_creates_tenant_document_policy_constraints(tmp_path: Path) -> None:
    db_path = tmp_path / "document-access-metadata.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        primary_key_columns = {
            row[1]: row[5]
            for row in con.execute("PRAGMA table_info('document_access_metadata')")
            if row[5] > 0
        }
        assert primary_key_columns == {"tenant_id": 1, "doc_id": 2}
        foreign_key_pairs = {
            (row[3], row[4])
            for row in con.execute("PRAGMA foreign_key_list('document_access_metadata')")
            if row[2] == "documents"
        }
        assert foreign_key_pairs == {("tenant_id", "tenant_id"), ("doc_id", "id")}

        _insert_document(con, "doc-1")
        con.execute(
            """
            INSERT INTO document_access_metadata (
                tenant_id, doc_id, visibility, policy_binding_id, policy_version, updated_at
            ) VALUES (?, 'doc-1', 'Org', 'binding-1', 'policy-v1', ?)
            """,
            (LOCAL_DEFAULT_TENANT_ID, TIMESTAMP),
        )
        con.commit()

        with pytest.raises(sqlite3.IntegrityError):
            con.execute(
                """
                INSERT INTO document_access_metadata (
                    tenant_id, doc_id, visibility, policy_binding_id, policy_version, updated_at
                ) VALUES (?, 'missing-doc', 'Public', NULL, 'policy-v1', ?)
                """,
                (LOCAL_DEFAULT_TENANT_ID, TIMESTAMP),
            )
        con.rollback()

        _insert_document(con, "doc-invalid")
        with pytest.raises(sqlite3.IntegrityError):
            con.execute(
                """
                INSERT INTO document_access_metadata (
                    tenant_id, doc_id, visibility, policy_binding_id, policy_version, updated_at
                ) VALUES (?, 'doc-invalid', 'Restricted', NULL, 'policy-v1', ?)
                """,
                (LOCAL_DEFAULT_TENANT_ID, TIMESTAMP),
            )
        con.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            con.execute(
                """
                INSERT INTO document_access_metadata (
                    tenant_id, doc_id, visibility, policy_binding_id, policy_version, updated_at
                ) VALUES (?, 'doc-invalid', 'Invalid', NULL, 'policy-v1', ?)
                """,
                (LOCAL_DEFAULT_TENANT_ID, TIMESTAMP),
            )
    finally:
        con.close()


def test_migration_downgrade_removes_access_metadata_table(tmp_path: Path) -> None:
    db_path = tmp_path / "document-access-metadata-downgrade.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    downgrade = _run_alembic(db_path, "downgrade", "20260717_0009")
    assert downgrade.returncode == 0, downgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        tables = {
            row[0]
            for row in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert "document_access_metadata" not in tables
    finally:
        con.close()
