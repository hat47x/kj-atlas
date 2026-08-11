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


def test_blob_payload_migration_fails_closed_for_legacy_ready_metadata(tmp_path: Path) -> None:
    db_path = tmp_path / "blob-payload-upgrade.sqlite3"
    initial = _run_alembic(db_path, "upgrade", "20260810_0020")
    assert initial.returncode == 0, initial.stderr
    digest = "a" * 64
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT INTO content_blobs "
            "(tenant_id,content_digest,storage_backend,locator,representation,base_digest,"
            "delta_depth,byte_size,stored_byte_size,storage_state,schema_version,created_at) "
            "VALUES ('local-default',?,'database',NULL,'full_json',NULL,0,2,2,'ready',"
            "'document-v1','2026-08-11T00:00:00Z')",
            (digest,),
        )

    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr
    with sqlite3.connect(db_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(content_blobs)")}
        state, payload = connection.execute(
            "SELECT storage_state,payload_bytes FROM content_blobs WHERE content_digest=?",
            (digest,),
        ).fetchone()
        assert "payload_bytes" in columns
        assert state == "failed"
        assert payload is None


def test_blob_payload_location_constraint_and_downgrade(tmp_path: Path) -> None:
    db_path = tmp_path / "blob-payload-shape.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr
    with sqlite3.connect(db_path) as connection:
        for digest, backend, locator, state, payload in (
            ("b" * 64, "database", None, "ready", None),
            ("c" * 64, "s3", "tenant/key", "ready", b"{}"),
            ("d" * 64, "s3", None, "ready", None),
        ):
            try:
                connection.execute(
                    "INSERT INTO content_blobs "
                    "(tenant_id,content_digest,storage_backend,locator,representation,base_digest,"
                    "delta_depth,byte_size,stored_byte_size,storage_state,schema_version,created_at,"
                    "payload_bytes) VALUES "
                    "('local-default',?,?,?,'full_json',NULL,0,2,2,?,'document-v1',"
                    "'2026-08-11T00:00:00Z',?)",
                    (digest, backend, locator, state, payload),
                )
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError(
                    f"invalid blob location shape was accepted: {backend}/{locator}/{state}"
                )

        connection.execute(
            "INSERT INTO content_blobs "
            "(tenant_id,content_digest,storage_backend,locator,representation,base_digest,"
            "delta_depth,byte_size,stored_byte_size,storage_state,schema_version,created_at,"
            "payload_bytes) VALUES "
            "('local-default',?,'database',NULL,'full_json',NULL,0,2,2,'ready',"
            "'document-v1','2026-08-11T00:00:00Z',?)",
            ("e" * 64, b"{}"),
        )

    downgrade = _run_alembic(db_path, "downgrade", "20260810_0020")
    assert downgrade.returncode == 0, downgrade.stderr
    with sqlite3.connect(db_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(content_blobs)")}
    assert "payload_bytes" not in columns
