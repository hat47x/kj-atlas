from __future__ import annotations

import os
import re
import subprocess
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from kj_atlas_api.database_support import normalize_sync_database_url


def _configured() -> bool:
    return (
        os.getenv("KJ_ATLAS_RUN_PG_TESTS") == "1"
        and bool(os.getenv("KJ_ATLAS_DATABASE_URL"))
        and bool(os.getenv("KJ_ATLAS_TEST_POSTGRES_CONTAINER"))
    )


@pytest.mark.postgres
@pytest.mark.skipif(not _configured(), reason="PostgreSQL backup container is not configured")
def test_postgres_logical_backup_restores_into_isolated_database() -> None:
    database_url = normalize_sync_database_url(os.environ["KJ_ATLAS_DATABASE_URL"])
    container = os.environ["KJ_ATLAS_TEST_POSTGRES_CONTAINER"]
    url = make_url(database_url)
    source_database = url.database or ""
    if not re.fullmatch(r"[A-Za-z0-9_]+", source_database):
        raise ValueError("PostgreSQL test database must use a simple identifier")
    restore_database = f"{source_database}_restore"
    username = url.username or ""
    password = url.password or ""
    suffix = uuid4().hex
    tenant_id = f"backup-tenant-{suffix}"
    document_id = f"backup-document-{suffix}"
    payload = '{"text":"' + ("x" * (1024 * 1024)) + '"}'
    admin_url = url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    source_engine = create_engine(url)

    try:
        with source_engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO tenants "
                    "(id,display_name,lifecycle_state,created_at,updated_at) "
                    "VALUES (:tenant_id,:tenant_id,'active',:timestamp,:timestamp)"
                ),
                {"tenant_id": tenant_id, "timestamp": "2026-08-11T00:00:00Z"},
            )
            connection.execute(
                text(
                    "INSERT INTO documents "
                    "(tenant_id,id,version,updated_at,payload_json) "
                    "VALUES (:tenant_id,:document_id,1,:timestamp,:payload)"
                ),
                {
                    "tenant_id": tenant_id,
                    "document_id": document_id,
                    "timestamp": "2026-08-11T00:00:00Z",
                    "payload": payload,
                },
            )

        with admin_engine.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{restore_database}"'))
            connection.execute(text(f'CREATE DATABASE "{restore_database}"'))

        exported = subprocess.run(
            [
                "docker",
                "exec",
                "-e",
                f"PGPASSWORD={password}",
                container,
                "pg_dump",
                "--format=custom",
                f"--username={username}",
                f"--dbname={source_database}",
            ],
            check=False,
            capture_output=True,
        )
        assert exported.returncode == 0, exported.stderr.decode(errors="replace")
        imported = subprocess.run(
            [
                "docker",
                "exec",
                "-i",
                "-e",
                f"PGPASSWORD={password}",
                container,
                "pg_restore",
                "--exit-on-error",
                "--no-owner",
                f"--username={username}",
                f"--dbname={restore_database}",
            ],
            input=exported.stdout,
            check=False,
            capture_output=True,
        )
        assert imported.returncode == 0, imported.stderr.decode(errors="replace")

        restored_engine = create_engine(url.set(database=restore_database))
        try:
            with restored_engine.connect() as connection:
                restored = connection.execute(
                    text(
                        "SELECT version, length(payload_json) AS payload_length FROM documents "
                        "WHERE tenant_id=:tenant_id AND id=:document_id"
                    ),
                    {"tenant_id": tenant_id, "document_id": document_id},
                ).one()
                assert restored.version == 1
                assert restored.payload_length > 1024 * 1024
                assert connection.scalar(text("SELECT version_num FROM alembic_version"))
        finally:
            restored_engine.dispose()
    finally:
        with source_engine.begin() as connection:
            connection.execute(
                text(
                    "DELETE FROM documents WHERE tenant_id=:tenant_id AND id=:document_id"
                ),
                {"tenant_id": tenant_id, "document_id": document_id},
            )
            connection.execute(
                text("DELETE FROM tenants WHERE id=:tenant_id"),
                {"tenant_id": tenant_id},
            )
        source_engine.dispose()
        with admin_engine.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{restore_database}"'))
        admin_engine.dispose()
