from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

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


def test_inquiry_bundle_revision_migration_upgrade_and_downgrade(tmp_path: Path) -> None:
    # DATA-INQUIRY-CONCURRENCY-01 (案A) AC-8: SQLite migration round-trip for
    # the server-owned `revision` column.
    db_path = tmp_path / "inquiry-bundle-revision.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    with sqlite3.connect(db_path) as connection:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info('inquiry_bundles')")
        }
        assert "revision" in columns

        # Pre-existing rows are back-filled to revision 1 via server_default.
        connection.execute(
            "INSERT INTO inquiry_bundles (tenant_id, journey_id, payload_json, updated_at) "
            "VALUES ('tenant-a', 'j1', '{}', 'now')"
        )
        connection.commit()
        revision = connection.execute(
            "SELECT revision FROM inquiry_bundles WHERE journey_id = 'j1'"
        ).fetchone()[0]
        assert revision == 1

    downgrade = _run_alembic(db_path, "downgrade", "20260811_0025")
    assert downgrade.returncode == 0, downgrade.stderr
    with sqlite3.connect(db_path) as connection:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info('inquiry_bundles')")
        }
        assert "revision" not in columns
