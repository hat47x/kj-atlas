"""OPS-ADMIN-CONCURRENCY-01 AC-6: the tenant model allowlist's row-lock CAS
(`PUT /admin/provision/models/tenants/{tenant_id}/allowlist`) had only ever
been proven with sequential calls (test_model_governance.py), which cannot
distinguish "the lock genuinely blocks a second writer" from "the revision
check alone happens to catch the race". SQLite has no real row-level
locking to test this against; this exercises two real, temporally
overlapping PostgreSQL transactions.

Uses an isolated, throwaway database, matching the pattern established in
test_postgres_migration_downgrade_matrix.py.
"""

from __future__ import annotations

import os
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
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


@pytest.mark.postgres
@pytest.mark.skipif(not _configured(), reason="PostgreSQL matrix is not configured")
def test_two_overlapping_transactions_serialize_on_the_tenant_row_lock() -> None:
    """Writer A acquires the tenant row lock and holds it while writer B's own
    lock acquisition (issued while A is still holding it) blocks. Only after
    A commits does B's SELECT ... FOR UPDATE unblock -- at which point B must
    observe A's write and reject its own stale expectedRevision, proving the
    lock (not just the revision-hash comparison) is what prevents the lost
    update."""
    import subprocess
    import sys

    base_url = os.environ["KJ_ATLAS_DATABASE_URL"]
    url = make_url(base_url)
    isolated_name = f"kj_atlas_opsadmin01_{uuid4().hex[:16]}"
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
        env = os.environ.copy()
        env["KJ_ATLAS_DATABASE_URL"] = isolated_url
        migrate = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=BACKEND_DIR,
            env=env,
            check=False,
            text=True,
            capture_output=True,
        )
        assert migrate.returncode == 0, migrate.stderr

        from kj_atlas_api.model_registry_repository import (
            list_tenant_allowed_model_ids,
            set_tenant_model_allowlist,
        )
        from kj_atlas_api.models import (
            LLMModelRegistryRow,
            LLMProviderRegistryRow,
            TenantRow,
        )
        from kj_atlas_api.routes.model_registry import (
            _allowlist_revision,
            _require_active_tenant,
        )

        now = datetime.now(timezone.utc).isoformat()
        factory = sessionmaker(bind=create_engine(isolated_url), class_=Session, expire_on_commit=False)
        with factory() as db:
            db.add(
                TenantRow(
                    id="tenant-race", display_name="Tenant Race",
                    lifecycle_state="active", created_at=now, updated_at=now,
                )
            )
            db.add(
                LLMProviderRegistryRow(
                    id="p", provider_kind="local", display_name="P",
                    lifecycle_state="active", created_at=now, updated_at=now,
                )
            )
            db.flush()
            for model_id in ("m1", "m2"):
                db.add(
                    LLMModelRegistryRow(
                        id=model_id, provider_id="p", display_name=model_id,
                        lifecycle_state="active", created_at=now, updated_at=now,
                    )
                )
            db.commit()

        with factory() as db:
            initial_revision = _allowlist_revision(
                sorted(list_tenant_allowed_model_ids(db, tenant_id="tenant-race"))
            )

        b_lock_attempted = threading.Event()
        a_committed = threading.Event()
        b_result: dict[str, object] = {}

        def writer_a() -> None:
            with factory() as db:
                _require_active_tenant(db, tenant_id="tenant-race", lock_for_update=True)
                # Hold the row lock open while B's own lock attempt is issued.
                assert b_lock_attempted.wait(timeout=10), "writer B never attempted its lock"
                # A real (if small) window for B's SELECT ... FOR UPDATE to
                # actually reach the server and block, not just enter Python.
                time.sleep(0.3)
                set_tenant_model_allowlist(
                    db, tenant_id="tenant-race", model_ids=["m1"], occurred_at=now
                )
                db.commit()
            a_committed.set()

        def writer_b() -> None:
            with factory() as db:
                b_lock_attempted.set()
                started_waiting_at = time.monotonic()
                _require_active_tenant(db, tenant_id="tenant-race", lock_for_update=True)
                b_result["unblocked_after_a_committed"] = a_committed.is_set()
                b_result["waited_seconds"] = time.monotonic() - started_waiting_at
                current_ids = list_tenant_allowed_model_ids(db, tenant_id="tenant-race")
                b_result["saw_a_write"] = current_ids == {"m1"}
                current_revision = _allowlist_revision(sorted(current_ids))
                b_result["stale_write_would_conflict"] = current_revision != initial_revision
                db.commit()

        thread_a = threading.Thread(target=writer_a)
        thread_b = threading.Thread(target=writer_b)
        thread_a.start()
        # Ensure A has issued its SELECT ... FOR UPDATE before B starts, so
        # B's own attempt is the one that blocks (not a race on who locks
        # first).
        time.sleep(0.2)
        thread_b.start()
        thread_a.join(timeout=15)
        thread_b.join(timeout=15)
        assert not thread_a.is_alive(), "writer A did not finish"
        assert not thread_b.is_alive(), "writer B did not finish"

        # The core claim: B's lock acquisition genuinely blocked until A's
        # commit, not merely raced it and happened to lose on content.
        assert b_result["unblocked_after_a_committed"] is True
        assert b_result["waited_seconds"] >= 0.25
        assert b_result["saw_a_write"] is True
        # Had B gone on to PUT with the revision it read before the race
        # (initial_revision), the route's own comparison would now correctly
        # 409 -- proven directly in test_model_governance.py's sequential
        # test; what this test adds is that the row lock is what forces B to
        # observe A's write in the first place.
        assert b_result["stale_write_would_conflict"] is True

        with factory() as db:
            final_ids = list_tenant_allowed_model_ids(db, tenant_id="tenant-race")
        assert final_ids == {"m1"}
    finally:
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
