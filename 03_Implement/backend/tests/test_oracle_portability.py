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
from sqlalchemy.orm import Session

from kj_atlas_api.models import DocumentRow
from tests.database_portability_contracts import verify_revision_dag_contract


BACKEND_DIR = Path(__file__).resolve().parents[1]
TIMESTAMP = "2026-08-10T00:00:00Z"


def _configured_url(name: str) -> str | None:
    if os.getenv("KJ_ATLAS_RUN_ORACLE_TESTS") != "1":
        return None
    return os.getenv(name)


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


def _reset_schema(database_url: str, admin_url: str) -> None:
    username = make_url(database_url).username or ""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,29}", username):
        raise ValueError("Oracle test user must use a simple identifier")
    password = make_url(database_url).password or ""
    engine = create_engine(admin_url)
    with engine.begin() as connection:
        try:
            connection.execute(text(f'DROP USER "{username.upper()}" CASCADE'))
        except Exception as error:
            if "ORA-01918" not in str(error):
                raise
        connection.execute(text(f'CREATE USER "{username.upper()}" IDENTIFIED BY "{password}"'))
        connection.execute(
            text(f'GRANT CONNECT, RESOURCE, UNLIMITED TABLESPACE TO "{username.upper()}"')
        )
    engine.dispose()


def _drop_schema(database_url: str, admin_url: str) -> None:
    username = (make_url(database_url).username or "").upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,29}", username):
        raise ValueError("Oracle test user must use a simple identifier")
    engine = create_engine(admin_url)
    with engine.begin() as connection:
        try:
            connection.execute(text(f'DROP USER "{username}" CASCADE'))
        except Exception as error:
            if "ORA-01918" not in str(error):
                raise
    engine.dispose()


def _expect_integrity_error(database_url: str, statement: str) -> None:
    engine = create_engine(database_url)
    try:
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text(statement), {"timestamp": TIMESTAMP})
    finally:
        engine.dispose()


def _verify_data_pump_restore(database_url: str, admin_url: str) -> None:
    container = os.environ["KJ_ATLAS_TEST_ORACLE_CONTAINER"]
    source = (make_url(database_url).username or "").upper()
    restored = f"{source}_RESTORE"
    admin = make_url(admin_url)
    admin_user = admin.username or ""
    admin_password = admin.password or ""
    service = admin.query.get("service_name", "FREEPDB1")
    dump_name = "kj_atlas_portability.dmp"

    export = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "expdp",
            f"{admin_user}/{admin_password}@{service}",
            f"schemas={source}",
            "directory=DATA_PUMP_DIR",
            f"dumpfile={dump_name}",
            "logfile=kj_atlas_portability_exp.log",
            "reuse_dumpfiles=yes",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert export.returncode == 0, export.stdout + export.stderr

    restored_url = make_url(database_url).set(username=restored.lower())
    _drop_schema(restored_url.render_as_string(hide_password=False), admin_url)
    imported = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "impdp",
            f"{admin_user}/{admin_password}@{service}",
            "directory=DATA_PUMP_DIR",
            f"dumpfile={dump_name}",
            "logfile=kj_atlas_portability_imp.log",
            f"remap_schema={source}:{restored}",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert imported.returncode == 0, imported.stdout + imported.stderr

    restored_engine = create_engine(restored_url.render_as_string(hide_password=False))
    with restored_engine.connect() as connection:
        count, largest = connection.execute(
            text("SELECT COUNT(*), MAX(DBMS_LOB.GETLENGTH(payload_json)) FROM documents")
        ).one()
    restored_engine.dispose()
    assert count == 2
    assert largest > 1024 * 1024


@pytest.mark.oracle
@pytest.mark.skipif(
    _configured_url("KJ_ATLAS_TEST_ORACLE_URL") is None,
    reason="Oracle matrix is not configured",
)
def test_oracle_promotion_matrix() -> None:
    database_url = _configured_url("KJ_ATLAS_TEST_ORACLE_URL")
    admin_url = _configured_url("KJ_ATLAS_TEST_ORACLE_ADMIN_URL")
    assert database_url is not None
    assert admin_url is not None
    assert make_url(database_url).get_backend_name() == "oracle"
    _reset_schema(database_url, admin_url)

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
                "('tenant-a','shared',1,:timestamp,:payload)"
            ),
            {"timestamp": TIMESTAMP, "payload": large_payload},
        )
        connection.execute(
            text(
                "INSERT INTO documents "
                "(tenant_id,id,version,updated_at,payload_json) VALUES "
                "('tenant-b','shared',1,:timestamp,'{}')"
            ),
            {"timestamp": TIMESTAMP},
        )
        connection.execute(
            text(
                "INSERT INTO documents "
                "(tenant_id,id,version,updated_at,payload_json) VALUES "
                "('tenant-a','only-a',1,:timestamp,'{}')"
            ),
            {"timestamp": TIMESTAMP},
        )
        connection.execute(
            text(
                "INSERT INTO users "
                "(id,display_name,email,lifecycle_state,created_at,updated_at) "
                "VALUES ('user-a','User A',NULL,'active',:timestamp,:timestamp)"
            ),
            {"timestamp": TIMESTAMP},
        )
        connection.execute(
            text(
                "INSERT INTO user_identities "
                "(id,user_id,provider,external_uid,created_at) "
                "VALUES (1,'user-a','OIDC','Subject-A',:timestamp)"
            ),
            {"timestamp": TIMESTAMP},
        )

    with Session(engine) as session:
        document = session.get(
            DocumentRow,
            {"tenant_id": "tenant-a", "id": "shared"},
        )
        assert document is not None
        assert len(document.payload_json) > 1024 * 1024

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
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM tenants WHERE id='rolled-back'")) == 0
    engine.dispose()

    _expect_integrity_error(
        database_url,
        "INSERT INTO merge_decision_logs "
        "(tenant_id,doc_id,decision_id,group_id,snapshot_version,decided_at,payload_json) "
        "VALUES ('tenant-b','only-a','decision-x','group-x','snapshot-x',:timestamp,'{}')",
    )
    _expect_integrity_error(
        database_url,
        "INSERT INTO user_identities "
        "(id,user_id,provider,external_uid,created_at) "
        "VALUES (2,'user-a','oidc','subject-a',:timestamp)",
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

    _verify_data_pump_restore(database_url, admin_url)
    engine = create_engine(database_url)
    verify_revision_dag_contract(engine)
    engine.dispose()
