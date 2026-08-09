from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect

from kj_atlas_api.models import Base

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _index_names(database_url: str) -> set[str]:
    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        return {index["name"] for index in inspector.get_indexes("merge_decision_logs")}
    finally:
        engine.dispose()


def test_merge_decision_log_indexes_defined_in_sqlalchemy_metadata(tmp_path) -> None:
    db_path = tmp_path / "schema_indexes.sqlite3"
    database_url = f"sqlite:///{db_path}"

    engine = create_engine(database_url)
    try:
        Base.metadata.create_all(bind=engine)
    finally:
        engine.dispose()

    index_names = _index_names(database_url)
    assert "ix_merge_decision_logs_doc_group_id" in index_names
    assert "ix_merge_decision_logs_doc_snapshot_id" in index_names


def test_merge_decision_log_indexes_created_by_alembic_upgrade_head(tmp_path) -> None:
    db_path = tmp_path / "migration_indexes.sqlite3"
    env = os.environ.copy()
    env["KJ_ATLAS_DATABASE_URL"] = f"sqlite:///{db_path}"

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        cwd=BACKEND_DIR,
        env=env,
    )

    index_names = _index_names(env["KJ_ATLAS_DATABASE_URL"])
    assert "ix_merge_decision_logs_doc_group_id" in index_names
    assert "ix_merge_decision_logs_doc_snapshot_id" in index_names
