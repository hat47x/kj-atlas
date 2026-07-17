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


def test_migration_creates_minimal_tenant_scoped_admin_audit_table(tmp_path: Path) -> None:
    db_path = tmp_path / "document-access-admin-audit.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        columns = {
            row[1]
            for row in con.execute(
                "PRAGMA table_info('document_access_admin_audit_events')"
            )
        }
        assert columns == {
            "event_id",
            "tenant_id",
            "principal_id",
            "doc_id",
            "action",
            "decision",
            "policy_version",
            "capability_version",
            "correlation_id",
            "occurred_at",
        }
        assert not columns.intersection(
            {"policy_binding_id", "policy_ref", "token", "secret", "title", "content"}
        )

        con.execute(
            """
            INSERT INTO document_access_admin_audit_events (
                event_id, tenant_id, principal_id, doc_id, action, decision,
                policy_version, capability_version, correlation_id, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "audit-1",
                LOCAL_DEFAULT_TENANT_ID,
                "user-1",
                "doc-1",
                "document.policy.update",
                "allowed",
                "policy-v1",
                "capability-v1",
                "correlation-1",
                TIMESTAMP,
            ),
        )
        con.commit()

        with pytest.raises(sqlite3.IntegrityError):
            con.execute(
                """
                INSERT INTO document_access_admin_audit_events (
                    event_id, tenant_id, principal_id, doc_id, action, decision,
                    policy_version, capability_version, correlation_id, occurred_at
                ) VALUES ('audit-2', ?, 'user-1', 'doc-1', 'document.read',
                          'allowed', 'policy-v1', 'capability-v1', 'correlation-2', ?)
                """,
                (LOCAL_DEFAULT_TENANT_ID, TIMESTAMP),
            )
        con.rollback()
    finally:
        con.close()


def test_migration_downgrade_removes_only_admin_audit_table(tmp_path: Path) -> None:
    db_path = tmp_path / "document-access-admin-audit-downgrade.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    downgrade = _run_alembic(db_path, "downgrade", "20260717_0010")
    assert downgrade.returncode == 0, downgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        tables = {
            row[0]
            for row in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert "document_access_admin_audit_events" not in tables
        assert "document_access_metadata" in tables
    finally:
        con.close()
