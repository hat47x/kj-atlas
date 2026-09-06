from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.db import _normalize_database_url
from kj_atlas_api.guest_admission_models import GuestPrincipalRow
from kj_atlas_api.guest_auth_session_models import GuestAuthSessionRow
from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore
from kj_atlas_api.models import TenantRow
from kj_atlas_api.tenant_db_guard import apply_database_tenant_id

RUN_RLS_TESTS_ENV = "KJ_ATLAS_RUN_PG_RLS_TESTS"
ADMIN_DATABASE_URL_ENV = "KJ_ATLAS_DATABASE_URL"
RUNTIME_DATABASE_URL_ENV = "KJ_ATLAS_TEST_POSTGRES_RUNTIME_DATABASE_URL"
BACKEND_DIR = Path(__file__).resolve().parents[1]
TS = "2026-09-06T12:00:00Z"
ISSUER = "https://guest-idp.example.test"


@pytest.fixture(scope="module")
def postgres_guest_auth_engines() -> Iterator[tuple[Engine, Engine]]:
    if os.getenv(RUN_RLS_TESTS_ENV) != "1":
        pytest.skip(f"set {RUN_RLS_TESTS_ENV}=1 to exercise PostgreSQL guest auth sessions")
    admin_url = os.getenv(ADMIN_DATABASE_URL_ENV, "")
    runtime_url = os.getenv(RUNTIME_DATABASE_URL_ENV, "")
    if not admin_url.startswith("postgresql") or not runtime_url.startswith("postgresql"):
        pytest.fail("guest auth verification requires PostgreSQL admin and runtime URLs")

    migration_env = os.environ.copy()
    migration_env[ADMIN_DATABASE_URL_ENV] = admin_url
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env=migration_env,
        check=True,
    )
    admin_engine = create_engine(_normalize_database_url(admin_url))
    runtime_engine = create_engine(_normalize_database_url(runtime_url), pool_size=1, max_overflow=0)
    try:
        yield admin_engine, runtime_engine
    finally:
        runtime_engine.dispose()
        admin_engine.dispose()


@pytest.mark.postgres
def test_pre_tenant_guest_session_resolves_then_returns_to_forced_rls(
    postgres_guest_auth_engines: tuple[Engine, Engine],
) -> None:
    admin_engine, runtime_engine = postgres_guest_auth_engines
    suffix = uuid4().hex
    tenant_id = f"guest-auth-{suffix}"
    principal_id = f"principal-{suffix}"
    subject = f"subject-{suffix}"
    session_hash = uuid4().hex + uuid4().hex

    with admin_engine.connect() as connection:
        session_posture = connection.execute(
            text(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE relname = 'guest_auth_sessions'"
            )
        ).one()
        principal_posture = connection.execute(
            text(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE relname = 'guest_principals'"
            )
        ).one()
    assert tuple(session_posture) == (False, False)
    assert tuple(principal_posture) == (True, True)

    with Session(admin_engine) as db:
        db.add(
            TenantRow(
                id=tenant_id,
                display_name=tenant_id,
                lifecycle_state="active",
                created_at=TS,
                updated_at=TS,
            )
        )
        db.commit()
    with Session(admin_engine) as db:
        apply_database_tenant_id(db=db, tenant_id=tenant_id)
        db.add(
            GuestPrincipalRow(
                tenant_id=tenant_id,
                guest_principal_id=principal_id,
                invited_email=f"{principal_id}@example.test",
                status="active",
                verification_method="personal_account",
                verified_issuer=ISSUER,
                verified_subject=subject,
                created_by="host-admin",
                created_at=TS,
                expires_at="2026-09-07T12:00:00Z",
                redeemed_at=TS,
                revoked_at=None,
            )
        )
        db.commit()

    runtime_factory = sessionmaker(bind=runtime_engine, class_=Session, expire_on_commit=False)
    store = DatabaseGuestAuthSessionStore(runtime_factory)
    try:
        # The restricted runtime role starts without tenant context.  The store
        # first resolves/creates pre-tenant session state, then applies the
        # tenant scope before touching FORCE-RLS guest_principals.
        store.create_guest_auth_session(
            session_key_hash=session_hash,
            tenant_id=tenant_id,
            guest_principal_id=principal_id,
            issuer=ISSUER,
            subject=subject,
        )
        resolved = store.resolve_guest_auth_session(session_key_hash=session_hash)
        assert resolved is not None
        assert resolved.tenant_id == tenant_id
        assert resolved.guest_principal_id == principal_id

        with Session(runtime_engine) as db:
            assert db.get(GuestPrincipalRow, (tenant_id, principal_id)) is None

        with Session(admin_engine) as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_id)
            principal = db.get(GuestPrincipalRow, (tenant_id, principal_id))
            assert principal is not None
            principal.status = "revoked"
            principal.revoked_at = "2026-09-06T13:00:00Z"
            db.commit()

        assert store.resolve_guest_auth_session(session_key_hash=session_hash) is None
    finally:
        with Session(admin_engine) as db:
            db.execute(
                delete(GuestAuthSessionRow).where(
                    GuestAuthSessionRow.session_key_hash == session_hash
                )
            )
            db.commit()
        with Session(admin_engine) as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_id)
            db.execute(
                delete(GuestPrincipalRow).where(GuestPrincipalRow.tenant_id == tenant_id)
            )
            db.commit()
        with Session(admin_engine) as db:
            db.execute(delete(TenantRow).where(TenantRow.id == tenant_id))
            db.commit()
