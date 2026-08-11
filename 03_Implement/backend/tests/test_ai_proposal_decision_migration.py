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


def test_ai_proposal_decision_migration_upgrade_and_downgrade(tmp_path: Path) -> None:
    db_path = tmp_path / "proposal-decision.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    with sqlite3.connect(db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert "ai_proposal_decision_events" in tables
        assert "ai_proposal_decision_states" in tables
        assert "ai_proposals" in tables
        indexes = {
            row[1] for row in connection.execute("PRAGMA index_list('ai_proposal_decision_events')")
        }
        assert "ix_ai_proposal_decision_events_proposal_order" in indexes

    downgrade = _run_alembic(db_path, "downgrade", "20260811_0022")
    assert downgrade.returncode == 0, downgrade.stderr
    with sqlite3.connect(db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert "ai_proposal_decision_events" not in tables
        assert "ai_proposal_decision_states" not in tables
        assert "ai_proposals" not in tables
