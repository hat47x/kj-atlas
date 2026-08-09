from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text


BACKEND_DIR = Path(__file__).resolve().parents[1]


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


def _column_types(db_path: Path, table_name: str) -> dict[str, str]:
    with sqlite3.connect(db_path) as connection:
        return {row[1]: row[2] for row in connection.execute(f'PRAGMA table_info("{table_name}")')}


def test_portable_text_migration_bounds_keys_but_not_content_objects(tmp_path: Path) -> None:
    db_path = tmp_path / "portable-text.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    tenants = _column_types(db_path, "tenants")
    documents = _column_types(db_path, "documents")
    bundles = _column_types(db_path, "inquiry_bundles")
    assert tenants["id"] == "VARCHAR(128)"
    assert tenants["display_name"] == "VARCHAR(255)"
    assert documents["id"] == "VARCHAR(128)"
    assert documents["payload_json"] == "TEXT"
    assert bundles["journey_id"] == "VARCHAR(256)"
    assert bundles["payload_json"] == "TEXT"


def test_portable_text_migration_downgrade_restores_unbounded_types(tmp_path: Path) -> None:
    db_path = tmp_path / "portable-text-downgrade.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr
    downgrade = _run_alembic(db_path, "downgrade", "20260810_0019")
    assert downgrade.returncode == 0, downgrade.stderr

    tenants = _column_types(db_path, "tenants")
    documents = _column_types(db_path, "documents")
    assert tenants["id"] == "TEXT"
    assert tenants["display_name"] == "TEXT"
    assert documents["payload_json"] == "TEXT"


@pytest.mark.postgres
def test_postgres_portable_text_roundtrip_preserves_rls_policies() -> None:
    database_url = os.getenv("KJ_ATLAS_DATABASE_URL", "")
    if os.getenv("KJ_ATLAS_RUN_PG_TESTS") != "1" or not database_url.startswith("postgresql"):
        pytest.skip("PostgreSQL migration matrix is not configured")

    def run_alembic(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "alembic", *args],
            cwd=BACKEND_DIR,
            check=False,
            text=True,
            capture_output=True,
        )

    upgrade = run_alembic("upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr
    engine = create_engine(database_url)
    with engine.connect() as connection:
        policies_before = connection.scalar(
            text("SELECT COUNT(*) FROM pg_policies WHERE schemaname = current_schema()")
        )
        assert inspect(connection).get_columns("tenants")[0]["type"].length == 128

    downgrade = run_alembic("downgrade", "20260810_0019")
    assert downgrade.returncode == 0, downgrade.stderr
    reupgrade = run_alembic("upgrade", "head")
    assert reupgrade.returncode == 0, reupgrade.stderr
    with engine.connect() as connection:
        policies_after = connection.scalar(
            text("SELECT COUNT(*) FROM pg_policies WHERE schemaname = current_schema()")
        )
    engine.dispose()
    assert policies_before and policies_after == policies_before
