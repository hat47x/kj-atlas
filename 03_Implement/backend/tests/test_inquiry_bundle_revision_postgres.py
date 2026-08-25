"""DATA-INQUIRY-CONCURRENCY-01 (案A) AC-8: the `inquiry_bundles.revision`
migration round-trip and its atomic CAS methods (update_cas/delete_cas) had
only ever been exercised against SQLite
(test_inquiry_bundle_revision_migration.py). This runs the same round-trip
and a real CAS race against PostgreSQL, the flagship "Verified server DB".

Uses an isolated, throwaway database (never the shared `kj_atlas` database
other `@pytest.mark.postgres` tests in the same CI job depend on being at
head), matching test_postgres_migration_downgrade_matrix.py's pattern.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

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
def test_inquiry_bundle_revision_round_trips_and_cas_races_on_postgres() -> None:
    base_url = os.environ["KJ_ATLAS_DATABASE_URL"]
    url = make_url(base_url)
    isolated_name = f"kj_atlas_dataic01_{uuid4().hex[:16]}"
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
            inspector = inspect(engine)
            columns = {col["name"] for col in inspector.get_columns("inquiry_bundles")}
            assert "revision" in columns

            with engine.connect() as connection:
                connection.execute(
                    text(
                        "INSERT INTO tenants (id, display_name, lifecycle_state, "
                        "created_at, updated_at) VALUES "
                        "('tenant-pg-cas', 'Tenant PG CAS', 'active', :now, :now)"
                    ),
                    {"now": datetime.now(timezone.utc).isoformat()},
                )
                connection.commit()
        finally:
            engine.dispose()

        # Exercise the real store's atomic CAS methods against Postgres --
        # not just raw SQL -- to prove update_cas()/delete_cas() (the
        # single-statement UPDATE/DELETE the issue's AC-3/AC-4 require) work
        # unchanged against this dialect, and that a stale-revision racer
        # loses cleanly.
        from kj_atlas_api.content_store import ContentBlob
        from kj_atlas_api.database_content_store import DatabaseBundleContentStore
        from kj_atlas_api.tenant_context import TenantContext

        factory = sessionmaker(bind=create_engine(isolated_url), class_=Session, expire_on_commit=False)
        tenant = TenantContext(
            tenant_id="tenant-pg-cas", membership_id=None, resolved_by="single_tenant_adapter"
        )
        with factory() as db:
            store = DatabaseBundleContentStore(db)
            store.create(
                tenant=tenant,
                journey_id="journey-pg-cas",
                updated_at=datetime.now(timezone.utc).isoformat(),
                content=ContentBlob.from_text('{"round": 1}'),
            )
            db.commit()

        # Winner: CAS from revision 1 -> 2 succeeds.
        with factory() as db:
            winner_ok = DatabaseBundleContentStore(db).update_cas(
                tenant=tenant,
                journey_id="journey-pg-cas",
                expected_revision=1,
                updated_at=datetime.now(timezone.utc).isoformat(),
                content=ContentBlob.from_text('{"round": 2}'),
            )
            db.commit()
        assert winner_ok is True

        # Loser: a second writer racing on the same stale revision 1 fails
        # closed -- single UPDATE ... WHERE revision = 1 now matches zero rows.
        with factory() as db:
            loser_ok = DatabaseBundleContentStore(db).update_cas(
                tenant=tenant,
                journey_id="journey-pg-cas",
                expected_revision=1,
                updated_at=datetime.now(timezone.utc).isoformat(),
                content=ContentBlob.from_text('{"round": "stale"}'),
            )
            db.commit()
        assert loser_ok is False

        with factory() as db:
            loaded = DatabaseBundleContentStore(db).load(tenant=tenant, journey_id="journey-pg-cas")
        assert loaded is not None
        assert loaded.row.revision == 2
        assert loaded.content.text == '{"round": 2}'

        # delete_cas: a stale revision must not delete; the correct revision must.
        with factory() as db:
            delete_stale = DatabaseBundleContentStore(db).delete_cas(
                tenant=tenant, journey_id="journey-pg-cas", expected_revision=1
            )
            db.commit()
        assert delete_stale is False

        with factory() as db:
            delete_ok = DatabaseBundleContentStore(db).delete_cas(
                tenant=tenant, journey_id="journey-pg-cas", expected_revision=2
            )
            db.commit()
        assert delete_ok is True

        downgrade = _run_alembic(isolated_url, "downgrade", "20260811_0025")
        assert downgrade.returncode == 0, downgrade.stderr

        engine = create_engine(isolated_url)
        try:
            inspector = inspect(engine)
            columns = {col["name"] for col in inspector.get_columns("inquiry_bundles")}
            assert "revision" not in columns
        finally:
            engine.dispose()

        reupgrade = _run_alembic(isolated_url, "upgrade", "head")
        assert reupgrade.returncode == 0, reupgrade.stderr
    finally:
        # See test_postgres_migration_downgrade_matrix.py: a DROP DATABASE
        # issued right after closing a connection can still race Postgres's
        # own backend-process teardown. Retry with a short backoff.
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
