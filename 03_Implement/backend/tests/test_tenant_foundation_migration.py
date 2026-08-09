from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect

from kj_atlas_api.models import Base, LOCAL_DEFAULT_TENANT_ID


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


def test_sqlalchemy_metadata_contains_single_tenant_foundation(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        Base.metadata.create_all(bind=engine)
        inspector = inspect(engine)

        assert {
            "tenants",
            "identity_providers",
            "tenant_identity_providers",
            "tenant_memberships",
        }.issubset(inspector.get_table_names())
        assert "tenant_id" in {column["name"] for column in inspector.get_columns("documents")}
        assert [
            column.name
            for column in Base.metadata.tables["documents"].primary_key.columns
        ] == ["tenant_id", "id"]
        assert "tenant_id" in {
            column["name"] for column in inspector.get_columns("merge_decision_logs")
        }
        identity_columns = {
            column["name"] for column in inspector.get_columns("user_identities")
        }
        assert {"identity_provider_id", "subject"}.issubset(identity_columns)
    finally:
        engine.dispose()


def test_migration_backfills_local_default_tenant_and_membership(tmp_path: Path) -> None:
    db_path = tmp_path / "tenant_backfill.sqlite3"
    upgrade_to_0005 = _run_alembic(db_path, "upgrade", "20260314_0005")
    assert upgrade_to_0005.returncode == 0, upgrade_to_0005.stderr

    con = sqlite3.connect(db_path)
    try:
        con.execute(
            """
            INSERT INTO users (
                id, display_name, lifecycle_state, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            ("user-1", "User 1", "active", "2026-07-16T00:00:00Z", "2026-07-16T00:00:00Z"),
        )
        con.execute(
            "INSERT INTO documents (id, version, updated_at, payload_json) VALUES (?, ?, ?, ?)",
            ("shared-doc", 1, "2026-07-16T00:00:00Z", "{}"),
        )
        con.execute(
            """
            INSERT INTO merge_decision_logs (
                doc_id, decision_id, group_id, snapshot_version, decided_at, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "shared-doc",
                "decision-1",
                "group-1",
                "snapshot-1",
                "2026-07-16T00:00:00Z",
                "{}",
            ),
        )
        con.commit()
    finally:
        con.close()

    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        tenant = con.execute(
            "SELECT id, lifecycle_state FROM tenants WHERE id = ?",
            (LOCAL_DEFAULT_TENANT_ID,),
        ).fetchone()
        membership = con.execute(
            "SELECT tenant_id, user_id, lifecycle_state FROM tenant_memberships"
        ).fetchone()
        document_tenant = con.execute(
            "SELECT tenant_id FROM documents WHERE id = 'shared-doc'"
        ).fetchone()
        log_tenant = con.execute(
            "SELECT tenant_id FROM merge_decision_logs WHERE decision_id = 'decision-1'"
        ).fetchone()

        assert tenant == (LOCAL_DEFAULT_TENANT_ID, "active")
        assert membership == (LOCAL_DEFAULT_TENANT_ID, "user-1", "active")
        assert document_tenant == (LOCAL_DEFAULT_TENANT_ID,)
        assert log_tenant == (LOCAL_DEFAULT_TENANT_ID,)

        con.execute(
            "INSERT INTO documents (id, version, updated_at, payload_json) VALUES (?, ?, ?, ?)",
            ("new-doc", 1, "2026-07-16T00:00:00Z", "{}"),
        )
        con.commit()
        assert con.execute("SELECT tenant_id FROM documents WHERE id = 'new-doc'").fetchone() == (
            LOCAL_DEFAULT_TENANT_ID,
        )
    finally:
        con.close()

    rerun = _run_alembic(db_path, "upgrade", "head")
    assert rerun.returncode == 0, rerun.stderr


def test_migration_downgrade_removes_expand_only_tenant_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "tenant_downgrade.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    downgrade = _run_alembic(db_path, "downgrade", "20260314_0005")
    assert downgrade.returncode == 0, downgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        tables = {
            row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        document_columns = {row[1] for row in con.execute("PRAGMA table_info('documents')")}
        log_columns = {row[1] for row in con.execute("PRAGMA table_info('merge_decision_logs')")}

        assert "tenants" not in tables
        assert "tenant_memberships" not in tables
        assert "tenant_id" not in document_columns
        assert "tenant_id" not in log_columns
    finally:
        con.close()
