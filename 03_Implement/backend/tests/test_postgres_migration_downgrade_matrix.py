"""DX-CI-PG-02: PostgreSQL-specific alembic downgrade() branches were never
executed against a real PostgreSQL server.

`20260717_0007` through `20260720_0012` each carry dialect-specific downgrade
code (RLS policy management, "constraint-ddl" strategy DDL, named foreign-key
drops), but every existing downgrade test for these six migrations hardcodes
`_run_alembic()`'s `KJ_ATLAS_DATABASE_URL` to `sqlite:///...`. Sibling database
engines (Oracle, MySQL family, MSSQL, CockroachDB) each have a dedicated
portability test that runs a real downgrade; PostgreSQL -- the flagship
database, with a service already running in CI -- did not.

This test runs on an isolated, throwaway database (never the shared `kj_atlas`
database other `@pytest.mark.postgres` tests in the same CI job depend on
being at head) so a mid-run downgrade here cannot disturb them.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _configured() -> bool:
    return (
        os.getenv("KJ_ATLAS_RUN_PG_TESTS") == "1"
        and bool(os.getenv("KJ_ATLAS_DATABASE_URL"))
        and bool(os.getenv("KJ_ATLAS_TEST_POSTGRES_CONTAINER"))
    )


def _run_alembic(database_url: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["KJ_ATLAS_DATABASE_URL"] = database_url
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_DIR,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


@pytest.mark.postgres
@pytest.mark.skipif(not _configured(), reason="PostgreSQL matrix is not configured")
def test_postgres_downgrade_matrix_runs_the_rls_and_constraint_ddl_branches() -> None:
    """A single `downgrade 20260716_0006` runs 0012 through 0007's downgrade()
    in sequence, so one hop exercises all six migrations' PostgreSQL-specific
    code without six separate test functions."""
    base_url = os.environ["KJ_ATLAS_DATABASE_URL"]
    url = make_url(base_url)
    isolated_name = f"kj_atlas_dxcipg02_{uuid4().hex[:16]}"
    if not re.fullmatch(r"[a-z0-9_]+", isolated_name):
        raise ValueError("isolated database name must be a simple identifier")
    admin_url = url.set(database="postgres")

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{isolated_name}"'))
    finally:
        admin_engine.dispose()

    isolated_url = url.set(database=isolated_name).render_as_string(hide_password=False)
    try:
        upgrade = _run_alembic(isolated_url, "upgrade", "head")
        assert upgrade.returncode == 0, upgrade.stderr

        engine = create_engine(isolated_url)
        try:
            with engine.connect() as connection:
                # Sanity check: we are actually on the postgres RLS branch (0009)
                # before downgrading it away, or the assertions below are vacuous.
                rls_enabled = connection.execute(
                    text("SELECT relrowsecurity FROM pg_class WHERE relname = 'documents'")
                ).scalar_one()
                assert rls_enabled is True
                policy_count = connection.execute(
                    text("SELECT count(*) FROM pg_policies WHERE tablename = 'documents'")
                ).scalar_one()
                assert policy_count == 1
        finally:
            engine.dispose()

        downgrade = _run_alembic(isolated_url, "downgrade", "20260716_0006")
        assert downgrade.returncode == 0, downgrade.stderr

        engine = create_engine(isolated_url)
        try:
            inspector = inspect(engine)
            with engine.connect() as connection:
                # 20260717_0009: RLS disabled and policies dropped (postgres-only
                # branch -- sqlite's downgrade is a no-op by dialect check).
                rls_enabled = connection.execute(
                    text("SELECT relrowsecurity FROM pg_class WHERE relname = 'documents'")
                ).scalar_one()
                assert rls_enabled is False
                policy_count = connection.execute(
                    text(
                        "SELECT count(*) FROM pg_policies "
                        "WHERE tablename IN ('documents', 'merge_decision_logs')"
                    )
                ).scalar_one()
                assert policy_count == 0

            # 20260717_0010 / 0011: both document_access_* tables (and, with
            # them, their postgres-only policy/RLS cleanup) are gone.
            assert not inspector.has_table("document_access_metadata")
            assert not inspector.has_table("document_access_admin_audit_events")

            # 20260717_0008: the "constraint-ddl" strategy branch (postgres's
            # counterpart to sqlite's table-rebuild) restored the pre-tenant-key
            # primary key on documents.
            document_pk = inspector.get_pk_constraint("documents")
            assert document_pk["constrained_columns"] == ["id"]

            # 20260717_0007: identity_provider_id/subject and their named
            # foreign key were dropped back off user_identities via the
            # non-sqlite branch (`if bind.dialect.name != "sqlite":`).
            user_identity_columns = {
                column["name"] for column in inspector.get_columns("user_identities")
            }
            assert "identity_provider_id" not in user_identity_columns
            assert "subject" not in user_identity_columns
        finally:
            engine.dispose()

        # 20260720_0012's downgrade (a named FK drop on
        # document_access_admin_audit_events) already had to succeed above --
        # returncode == 0 on the downgrade call is its only observable
        # evidence, since 0011's downgrade drops that same table moments later.

        reupgrade = _run_alembic(isolated_url, "upgrade", "head")
        assert reupgrade.returncode == 0, reupgrade.stderr
    finally:
        # Observed in practice: right after an assertion failure closes the
        # inspecting connection, a DROP DATABASE issued immediately afterward
        # can still race Postgres's own backend-process teardown and fail with
        # "database is being accessed by other users" even though
        # pg_terminate_backend was just asked to end that session. Retry with
        # a short backoff rather than leak the isolated database.
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        try:
            last_error: Exception | None = None
            for attempt in range(5):
                if attempt:
                    time.sleep(0.5 * attempt)
                try:
                    with admin_engine.connect() as connection:
                        connection.execute(
                            text(
                                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                                "WHERE datname = :name AND pid <> pg_backend_pid()"
                            ),
                            {"name": isolated_name},
                        )
                        connection.execute(text(f'DROP DATABASE IF EXISTS "{isolated_name}"'))
                    last_error = None
                    break
                except OperationalError as error:
                    last_error = error
            if last_error is not None:
                raise last_error
        finally:
            admin_engine.dispose()
