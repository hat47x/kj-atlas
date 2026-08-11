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


def test_external_proposal_provenance_migration_upgrade_and_downgrade(tmp_path: Path) -> None:
    db_path = tmp_path / "external-proposal.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr
    with sqlite3.connect(db_path) as connection:
        proposal_columns = {
            row[1] for row in connection.execute("PRAGMA table_info('ai_proposals')")
        }
        event_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info('ai_proposal_decision_events')")
        }
        assert {"origin", "task_id", "proposal_fingerprint", "provenance_level"} <= proposal_columns
        assert {"proposal_origin", "provenance_level"} <= event_columns
        task_columns = {
            row[1] for row in connection.execute("PRAGMA table_info('external_agent_tasks')")
        }
        assert {"tenant_id", "task_id", "doc_id", "source_bundle_hash"} <= task_columns

    downgrade = _run_alembic(db_path, "downgrade", "20260811_0023")
    assert downgrade.returncode == 0, downgrade.stderr
