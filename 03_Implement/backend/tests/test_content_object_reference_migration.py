from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from kj_atlas_api.models import LOCAL_DEFAULT_TENANT_ID


BACKEND_DIR = Path(__file__).resolve().parents[1]
TIMESTAMP = "2026-08-09T00:00:00Z"


def _run_alembic(db_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["KJ_ATLAS_DATABASE_URL"] = f"sqlite:///{db_path}"
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_DIR,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


def test_content_reference_migration_enforces_backend_locator_contract(tmp_path: Path) -> None:
    db_path = tmp_path / "content-reference.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")
    values = (
        LOCAL_DEFAULT_TENANT_ID,
        "pending",
        2,
        "0" * 64,
        "document-v1",
        TIMESTAMP,
        TIMESTAMP,
    )
    try:
        con.execute(
            """
            INSERT INTO content_object_references (
                content_id, tenant_id, storage_backend, locator, storage_state,
                byte_size, sha256_digest, schema_version, created_at, updated_at
            ) VALUES ('content-db', ?, 'database', NULL, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        con.execute(
            """
            INSERT INTO content_object_references (
                content_id, tenant_id, storage_backend, locator, storage_state,
                byte_size, sha256_digest, schema_version, created_at, updated_at
            ) VALUES ('content-s3', ?, 's3', 'tenant/content-s3', ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        with pytest.raises(sqlite3.IntegrityError):
            con.execute(
                """
                INSERT INTO content_object_references (
                    content_id, tenant_id, storage_backend, locator, storage_state,
                    byte_size, sha256_digest, schema_version, created_at, updated_at
                ) VALUES ('invalid-s3', ?, 's3', NULL, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
        con.rollback()
    finally:
        con.close()


def test_content_reference_migration_downgrades_cleanly(tmp_path: Path) -> None:
    db_path = tmp_path / "content-reference-downgrade.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr
    downgrade = _run_alembic(db_path, "downgrade", "20260807_0014")
    assert downgrade.returncode == 0, downgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        tables = {
            row[0]
            for row in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert "content_object_references" not in tables
    finally:
        con.close()
