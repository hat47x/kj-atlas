from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError


BACKEND_DIR = Path(__file__).resolve().parents[1]
TIMESTAMP = "2026-08-10T00:00:00Z"


def _configured_urls() -> list[str]:
    if os.getenv("KJ_ATLAS_RUN_MYSQL_TESTS") != "1":
        return []
    return [
        value
        for key in ("KJ_ATLAS_TEST_MYSQL_URL", "KJ_ATLAS_TEST_MARIADB_URL")
        if (value := os.getenv(key))
    ]


def _run_alembic(url: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["KJ_ATLAS_DATABASE_URL"] = url
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_DIR,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


def _reset_schema(url: str) -> None:
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table_name in inspect(connection).get_table_names():
            connection.execute(text(f"DROP TABLE `{table_name}`"))
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    engine.dispose()


def _expect_integrity_error(url: str, statement: str) -> None:
    engine = create_engine(url)
    try:
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text(statement), {"timestamp": TIMESTAMP})
    finally:
        engine.dispose()


def _verify_backup_restore(database_url: str) -> None:
    url = make_url(database_url)
    backend = url.get_backend_name()
    database = url.database or ""
    if not re.fullmatch(r"[A-Za-z0-9_]+", database):
        raise ValueError("MySQL family test database must use a simple identifier")
    restore_database = f"{database}_restore"
    container_env = {
        "mysql": "KJ_ATLAS_TEST_MYSQL_CONTAINER",
        "mariadb": "KJ_ATLAS_TEST_MARIADB_CONTAINER",
    }
    container = os.environ[container_env[backend]]
    dump_command = "mysqldump" if backend == "mysql" else "mariadb-dump"
    client_command = "mysql" if backend == "mysql" else "mariadb"
    username = url.username or ""
    password = url.password or ""
    credential_args = ["-e", f"MYSQL_PWD={password}", container]

    server_engine = create_engine(url.set(database=None))
    with server_engine.begin() as connection:
        connection.execute(text(f"DROP DATABASE IF EXISTS `{restore_database}`"))
        connection.execute(text(f"CREATE DATABASE `{restore_database}`"))
    server_engine.dispose()

    exported = subprocess.run(
        [
            "docker",
            "exec",
            *credential_args,
            dump_command,
            f"--user={username}",
            "--single-transaction",
            "--skip-lock-tables",
            database,
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
            *credential_args,
            client_command,
            f"--user={username}",
            restore_database,
        ],
        input=exported.stdout,
        check=False,
        capture_output=True,
    )
    assert imported.returncode == 0, imported.stderr.decode(errors="replace")

    restored = create_engine(url.set(database=restore_database))
    with restored.connect() as connection:
        count, largest = connection.execute(
            text("SELECT COUNT(*), MAX(CHAR_LENGTH(payload_json)) FROM documents")
        ).one()
    restored.dispose()
    assert count == 2
    assert largest > 1024 * 1024


@pytest.mark.mysql
@pytest.mark.parametrize("database_url", _configured_urls())
def test_mysql_family_promotion_matrix(database_url: str) -> None:
    backend = make_url(database_url).get_backend_name()
    assert backend in {"mysql", "mariadb"}
    _reset_schema(database_url)

    upgrade = _run_alembic(database_url, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    engine = create_engine(database_url)
    large_payload = '{"text":"' + ("x" * (1024 * 1024)) + '"}'
    with engine.begin() as connection:
        for tenant_id in ("tenant-a", "tenant-b"):
            connection.execute(
                text(
                    "INSERT INTO tenants "
                    "(id,display_name,lifecycle_state,created_at,updated_at) "
                    "VALUES (:tenant_id,:tenant_id,'active',:timestamp,:timestamp)"
                ),
                {"tenant_id": tenant_id, "timestamp": TIMESTAMP},
            )
        connection.execute(
            text(
                "INSERT INTO documents "
                "(tenant_id,id,version,updated_at,payload_json) VALUES "
                "('tenant-a','shared',1,:timestamp,:payload),"
                "('tenant-b','shared',1,:timestamp,'{}'),"
                "('tenant-a','only-a',1,:timestamp,'{}')"
            ),
            {"timestamp": TIMESTAMP, "payload": large_payload},
        )
        connection.execute(
            text(
                "INSERT INTO identity_providers "
                "(id,issuer,audience,lifecycle_state,protocol,jwks_uri,created_at,updated_at) "
                "VALUES ('idp-a','https://issuer.example','Audience','active','oidc',NULL,"
                ":timestamp,:timestamp)"
            ),
            {"timestamp": TIMESTAMP},
        )
        assert (
            connection.scalar(
                text(
                    "SELECT CHAR_LENGTH(payload_json) FROM documents "
                    "WHERE tenant_id='tenant-a' AND id='shared'"
                )
            )
            > 1024 * 1024
        )
    engine.dispose()

    _expect_integrity_error(
        database_url,
        "INSERT INTO merge_decision_logs "
        "(tenant_id,doc_id,decision_id,group_id,snapshot_version,decided_at,payload_json) "
        "VALUES ('tenant-b','only-a','decision-x','group-x','snapshot-x',:timestamp,'{}')",
    )
    _expect_integrity_error(
        database_url,
        "INSERT INTO identity_providers "
        "(id,issuer,audience,lifecycle_state,protocol,jwks_uri,created_at,updated_at) "
        "VALUES ('idp-b','HTTPS://ISSUER.EXAMPLE','audience','active','oidc',NULL,"
        ":timestamp,:timestamp)",
    )

    blocked = _run_alembic(database_url, "downgrade", "20260717_0007")
    assert blocked.returncode != 0
    assert "duplicate docId" in blocked.stderr

    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM documents WHERE tenant_id='tenant-b' AND id='shared'"))
    engine.dispose()
    downgrade = _run_alembic(database_url, "downgrade", "20260717_0007")
    assert downgrade.returncode == 0, downgrade.stderr
    reupgrade = _run_alembic(database_url, "upgrade", "head")
    assert reupgrade.returncode == 0, reupgrade.stderr

    _verify_backup_restore(database_url)
