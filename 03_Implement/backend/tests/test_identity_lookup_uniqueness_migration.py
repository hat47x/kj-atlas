from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from kj_atlas_api.models import UserIdentityRow

BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_user_identity_model_declares_case_insensitive_lookup_index() -> None:
    index = next(
        candidate
        for candidate in UserIdentityRow.__table__.indexes
        if candidate.name == "uq_user_identities_provider_lower_external_uid"
    )

    assert index.unique is True
    assert [str(expression) for expression in index.expressions] == [
        "lower(provider)",
        "lower(external_uid)",
    ]


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


def test_migration_rejects_case_insensitive_external_uid_duplicates(tmp_path: Path) -> None:
    db_path = tmp_path / "dupe_external_uid.sqlite3"

    upgrade_to_0004 = _run_alembic(db_path, "upgrade", "20260313_0004")
    assert upgrade_to_0004.returncode == 0, upgrade_to_0004.stderr

    con = sqlite3.connect(db_path)
    try:
        con.execute(
            "INSERT INTO users (id, display_name, lifecycle_state, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ("u-1", "Alice", "active", "2026-03-14T00:00:00Z", "2026-03-14T00:00:00Z"),
        )
        con.execute(
            "INSERT INTO users (id, display_name, lifecycle_state, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ("u-2", "Bob", "active", "2026-03-14T00:00:00Z", "2026-03-14T00:00:00Z"),
        )
        con.execute(
            "INSERT INTO user_identities (user_id, provider, external_uid, created_at) VALUES (?, ?, ?, ?)",
            ("u-1", "sso", "Alice", "2026-03-14T00:00:00Z"),
        )
        con.execute(
            "INSERT INTO user_identities (user_id, provider, external_uid, created_at) VALUES (?, ?, ?, ?)",
            ("u-2", "SSO", "alice", "2026-03-14T00:00:00Z"),
        )
        con.commit()
    finally:
        con.close()

    blocked_upgrade = _run_alembic(db_path, "upgrade", "head")
    assert blocked_upgrade.returncode != 0
    assert "Detected case-insensitive duplicates in user_identities" in blocked_upgrade.stderr


def test_migration_is_idempotent_when_index_already_exists(tmp_path: Path) -> None:
    """inspector.get_indexes() cannot see this expression index on SQLite
    (SAWarning: "Skipped unsupported reflection of expression-based
    index ..."), so the existence check that guarded op.create_index() used
    to always report the index missing. On a database where the index was
    already created by some other means, upgrading to head then failed with
    "index ... already exists" instead of skipping the create. Query
    sqlite_master directly to detect it instead.
    """
    db_path = tmp_path / "preexisting_identity_idx.sqlite3"

    upgrade_to_0004 = _run_alembic(db_path, "upgrade", "20260313_0004")
    assert upgrade_to_0004.returncode == 0, upgrade_to_0004.stderr

    con = sqlite3.connect(db_path)
    try:
        con.execute(
            "CREATE UNIQUE INDEX uq_user_identities_provider_lower_external_uid "
            "ON user_identities (lower(provider), lower(external_uid))"
        )
        con.commit()
    finally:
        con.close()

    upgrade_to_head = _run_alembic(db_path, "upgrade", "head")
    assert upgrade_to_head.returncode == 0, upgrade_to_head.stderr


def test_migration_downgrade_drops_case_insensitive_index(tmp_path: Path) -> None:
    db_path = tmp_path / "downgrade_identity_idx.sqlite3"

    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        idx_names = {row[1] for row in con.execute("PRAGMA index_list('user_identities')")}
        assert "uq_user_identities_provider_lower_external_uid" in idx_names
    finally:
        con.close()

    downgrade = _run_alembic(db_path, "downgrade", "20260313_0004")
    assert downgrade.returncode == 0, downgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        idx_names = {row[1] for row in con.execute("PRAGMA index_list('user_identities')")}
        assert "uq_user_identities_provider_lower_external_uid" not in idx_names
    finally:
        con.close()
