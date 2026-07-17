from __future__ import annotations

import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

from kj_atlas_api.identity_binding import legacy_identity_provider_binding
from kj_atlas_api.models import LOCAL_DEFAULT_TENANT_ID


BACKEND_DIR = Path(__file__).resolve().parents[1]


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


def _seed_identity(db_path: Path) -> None:
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            """
            INSERT INTO users (
                id, display_name, lifecycle_state, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                "user-1",
                "User 1",
                "active",
                "2026-07-17T00:00:00Z",
                "2026-07-17T00:00:00Z",
            ),
        )
        con.execute(
            """
            INSERT INTO user_identities (
                user_id, provider, external_uid, created_at
            ) VALUES (?, ?, ?, ?)
            """,
            ("user-1", " OIDC ", "subject-1", "2026-07-17T00:00:00Z"),
        )
        con.commit()
    finally:
        con.close()


def test_migration_backfills_identity_provider_and_subject(tmp_path: Path) -> None:
    db_path = tmp_path / "identity_binding.sqlite3"
    upgrade_to_0006 = _run_alembic(db_path, "upgrade", "20260716_0006")
    assert upgrade_to_0006.returncode == 0, upgrade_to_0006.stderr
    _seed_identity(db_path)

    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    expected = legacy_identity_provider_binding("oidc")
    con = sqlite3.connect(db_path)
    try:
        identity = con.execute(
            """
            SELECT identity_provider_id, subject
            FROM user_identities
            WHERE user_id = 'user-1'
            """
        ).fetchone()
        provider = con.execute(
            """
            SELECT issuer, audience, lifecycle_state
            FROM identity_providers
            WHERE id = ?
            """,
            (expected.identity_provider_id,),
        ).fetchone()
        tenant_binding = con.execute(
            """
            SELECT lifecycle_state
            FROM tenant_identity_providers
            WHERE tenant_id = ? AND identity_provider_id = ?
            """,
            (LOCAL_DEFAULT_TENANT_ID, expected.identity_provider_id),
        ).fetchone()

        assert identity == (expected.identity_provider_id, "subject-1")
        assert provider == (expected.issuer, expected.audience, "active")
        assert tenant_binding == ("active",)

        with pytest.raises(sqlite3.IntegrityError):
            con.execute(
                """
                INSERT INTO user_identities (
                    user_id, provider, external_uid,
                    identity_provider_id, subject, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "user-1",
                    "different-provider-label",
                    "different-legacy-uid",
                    expected.identity_provider_id,
                    "subject-1",
                    "2026-07-17T00:00:00Z",
                ),
            )
    finally:
        con.close()

    rerun = _run_alembic(db_path, "upgrade", "head")
    assert rerun.returncode == 0, rerun.stderr


def test_migration_downgrade_removes_expand_columns_and_legacy_bindings(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "identity_binding_downgrade.sqlite3"
    upgrade_to_0006 = _run_alembic(db_path, "upgrade", "20260716_0006")
    assert upgrade_to_0006.returncode == 0, upgrade_to_0006.stderr
    _seed_identity(db_path)
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    downgrade = _run_alembic(db_path, "downgrade", "20260716_0006")
    assert downgrade.returncode == 0, downgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        columns = {row[1] for row in con.execute("PRAGMA table_info('user_identities')")}
        provider_count = con.execute(
            "SELECT COUNT(*) FROM identity_providers WHERE id LIKE 'idp-legacy-%'"
        ).fetchone()
        binding_count = con.execute(
            """
            SELECT COUNT(*) FROM tenant_identity_providers
            WHERE identity_provider_id LIKE 'idp-legacy-%'
            """
        ).fetchone()

        assert "identity_provider_id" not in columns
        assert "subject" not in columns
        assert provider_count == (0,)
        assert binding_count == (0,)
    finally:
        con.close()
