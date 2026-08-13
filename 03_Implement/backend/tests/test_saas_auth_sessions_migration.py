from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from kj_atlas_api.models import LOCAL_DEFAULT_TENANT_ID

BACKEND_DIR = Path(__file__).resolve().parents[1]
TIMESTAMP = "2026-08-13T00:00:00Z"


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


def _insert_session(
    con: sqlite3.Connection,
    *,
    session_key_hash: str,
    active_tenant_id: str | None,
    principal_id: str = "principal-1",
    issuer: str = "https://broker.example/realm",
    subject: str = "subject-1",
) -> None:
    con.execute(
        """
        INSERT INTO saas_auth_sessions (
            session_key_hash, principal_id, issuer, subject, active_tenant_id,
            tenant_session_version, created_at, last_used_at, absolute_expires_at, revoked_at
        ) VALUES (?, ?, ?, ?, ?, 'version-1', ?, ?, ?, NULL)
        """,
        (
            session_key_hash,
            principal_id,
            issuer,
            subject,
            active_tenant_id,
            TIMESTAMP,
            TIMESTAMP,
            TIMESTAMP,
        ),
    )


def test_migration_creates_saas_auth_sessions_table(tmp_path: Path) -> None:
    db_path = tmp_path / "saas-auth-sessions.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        primary_key_columns = {
            row[1]: row[5]
            for row in con.execute("PRAGMA table_info('saas_auth_sessions')")
            if row[5] > 0
        }
        assert primary_key_columns == {"session_key_hash": 1}

        columns = {row[1]: row[3] for row in con.execute("PRAGMA table_info('saas_auth_sessions')")}
        # row[3] is `notnull`: 1 means NOT NULL.
        assert columns == {
            "session_key_hash": 1,
            "principal_id": 1,
            "issuer": 1,
            "subject": 1,
            "active_tenant_id": 0,
            "tenant_session_version": 1,
            "created_at": 1,
            "last_used_at": 1,
            "absolute_expires_at": 1,
            "revoked_at": 0,
        }

        foreign_key_pairs = {
            (row[3], row[4])
            for row in con.execute("PRAGMA foreign_key_list('saas_auth_sessions')")
            if row[2] == "tenants"
        }
        assert foreign_key_pairs == {("active_tenant_id", "id")}

        index_names = {row[1] for row in con.execute("PRAGMA index_list('saas_auth_sessions')")}
        assert {
            "ix_saas_auth_sessions_principal_id",
            "ix_saas_auth_sessions_issuer_subject",
        } <= index_names

        # active_tenant_id may reference an existing tenant...
        _insert_session(con, session_key_hash="hash-a", active_tenant_id=LOCAL_DEFAULT_TENANT_ID)
        # ...or be NULL (a login before any tenant has been selected).
        _insert_session(
            con, session_key_hash="hash-b", active_tenant_id=None, principal_id="principal-2"
        )
        con.commit()

        with pytest.raises(sqlite3.IntegrityError):
            _insert_session(con, session_key_hash="hash-c", active_tenant_id="no-such-tenant")
        con.rollback()

        # session_key_hash is the primary key: a second row with the same
        # hash (e.g. a hash collision or a caller that forgot to hash) must
        # be rejected, not silently overwrite the existing session.
        with pytest.raises(sqlite3.IntegrityError):
            _insert_session(
                con, session_key_hash="hash-a", active_tenant_id=LOCAL_DEFAULT_TENANT_ID
            )
        con.rollback()
    finally:
        con.close()


def test_migration_downgrade_removes_saas_auth_sessions_table(tmp_path: Path) -> None:
    db_path = tmp_path / "saas-auth-sessions-downgrade.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    downgrade = _run_alembic(db_path, "downgrade", "20260813_0026")
    assert downgrade.returncode == 0, downgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        tables = {
            row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert "saas_auth_sessions" not in tables
        # The table it's expanding alongside must be untouched by this
        # migration's downgrade.
        assert "saas_tenant_sessions" in tables
    finally:
        con.close()
