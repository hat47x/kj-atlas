from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from tests.database_portability_contracts import verify_revision_dag_contract


BACKEND_DIR = Path(__file__).resolve().parents[1]
TIMESTAMP = "2026-08-10T00:00:00Z"


def _configured_url() -> str | None:
    if os.getenv("KJ_ATLAS_RUN_MSSQL_TESTS") != "1":
        return None
    return os.getenv("KJ_ATLAS_TEST_MSSQL_URL")


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


def _master_url(database_url: str) -> str:
    return make_url(database_url).set(database="master").render_as_string(hide_password=False)


def _reset_database(database_url: str) -> None:
    url = make_url(database_url)
    database = url.database or ""
    if not re.fullmatch(r"[A-Za-z0-9_]+", database):
        raise ValueError("SQL Server test database must use a simple identifier")
    engine = create_engine(_master_url(database_url), isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        connection.execute(
            text(
                f"IF DB_ID('{database}') IS NOT NULL BEGIN "
                f"ALTER DATABASE [{database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
                f"DROP DATABASE [{database}]; END"
            )
        )
        connection.execute(
            text(f"CREATE DATABASE [{database}] COLLATE Latin1_General_100_CI_AS_SC_UTF8")
        )
    engine.dispose()


def _expect_integrity_error(database_url: str, statement: str) -> None:
    engine = create_engine(database_url)
    try:
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text(statement), {"timestamp": TIMESTAMP})
    finally:
        engine.dispose()


def _verify_backup_restore(database_url: str) -> None:
    url = make_url(database_url)
    database = url.database or ""
    restore_database = f"{database}_restore"
    backup_path = f"/var/opt/mssql/data/{database}-portability.bak"
    engine = create_engine(_master_url(database_url), isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        connection.execute(
            text(f"BACKUP DATABASE [{database}] TO DISK = N'{backup_path}' WITH INIT, COPY_ONLY")
        )
        connection.execute(
            text(
                f"IF DB_ID('{restore_database}') IS NOT NULL BEGIN "
                f"ALTER DATABASE [{restore_database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
                f"DROP DATABASE [{restore_database}]; END"
            )
        )
        connection.execute(
            text(
                f"RESTORE DATABASE [{restore_database}] FROM DISK = N'{backup_path}' WITH "
                f"MOVE '{database}' TO '/var/opt/mssql/data/{restore_database}.mdf', "
                f"MOVE '{database}_log' TO '/var/opt/mssql/data/{restore_database}_log.ldf'"
            )
        )
    engine.dispose()

    restored_url = url.set(database=restore_database).render_as_string(hide_password=False)
    restored = create_engine(restored_url)
    with restored.connect() as connection:
        count, largest = connection.execute(
            text("SELECT COUNT(*), MAX(LEN(payload_json)) FROM documents")
        ).one()
    restored.dispose()
    assert count == 2
    assert largest > 1024 * 1024


@pytest.mark.mssql
@pytest.mark.skipif(_configured_url() is None, reason="SQL Server matrix is not configured")
def test_mssql_promotion_matrix() -> None:
    database_url = _configured_url()
    assert database_url is not None
    assert make_url(database_url).get_backend_name() == "mssql"
    _reset_database(database_url)

    upgrade = _run_alembic(database_url, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    engine = create_engine(database_url, pool_size=1, max_overflow=0)
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
                    "SELECT LEN(payload_json) FROM documents "
                    "WHERE tenant_id='tenant-a' AND id='shared'"
                )
            )
            > 1024 * 1024
        )

    transaction = engine.connect()
    rollback = transaction.begin()
    transaction.execute(
        text(
            "INSERT INTO tenants "
            "(id,display_name,lifecycle_state,created_at,updated_at) "
            "VALUES ('rolled-back','rolled-back','active',:timestamp,:timestamp)"
        ),
        {"timestamp": TIMESTAMP},
    )
    rollback.rollback()
    transaction.close()
    with engine.connect() as reused_connection:
        assert (
            reused_connection.scalar(text("SELECT COUNT(*) FROM tenants WHERE id='rolled-back'"))
            == 0
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
    engine = create_engine(database_url)
    verify_revision_dag_contract(engine)
    engine.dispose()
