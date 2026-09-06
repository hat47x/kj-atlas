from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.db import _normalize_database_url
from kj_atlas_api.guest_admission_models import GuestPrincipalRow
from kj_atlas_api.guest_auth_session_models import GuestAuthSessionRow
from kj_atlas_api.guest_redeem import DatabaseGuestRedeemStateStore, VerifiedGuestIdentity
from kj_atlas_api.guest_redeem_state_models import GuestRedeemStateRow
from kj_atlas_api.models import TenantRow
from kj_atlas_api.tenant_db_guard import apply_database_tenant_id

RUN_RLS_TESTS_ENV = "KJ_ATLAS_RUN_PG_RLS_TESTS"
ADMIN_DATABASE_URL_ENV = "KJ_ATLAS_DATABASE_URL"
RUNTIME_DATABASE_URL_ENV = "KJ_ATLAS_TEST_POSTGRES_RUNTIME_DATABASE_URL"
BACKEND_DIR = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 7, 1, 0, tzinfo=timezone.utc)
ISSUER = "https://personal-idp.example.test"
STATE_HASH_KEY = b"postgres-guest-redeem-state-key-01"
SESSION_HASH_KEY = b"postgres-guest-session-key-00001"


@pytest.fixture(scope="module")
def postgres_guest_redeem_engines() -> Iterator[tuple[Engine, Engine]]:
    if os.getenv(RUN_RLS_TESTS_ENV) != "1":
        pytest.skip(f"set {RUN_RLS_TESTS_ENV}=1 to exercise PostgreSQL guest redeem state")
    admin_url = os.getenv(ADMIN_DATABASE_URL_ENV, "")
    runtime_url = os.getenv(RUNTIME_DATABASE_URL_ENV, "")
    if not admin_url.startswith("postgresql") or not runtime_url.startswith("postgresql"):
        pytest.fail("guest redeem verification requires PostgreSQL admin and runtime URLs")

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
def test_pre_tenant_redeem_state_returns_to_forced_rls_and_redeems_atomically(
    postgres_guest_redeem_engines: tuple[Engine, Engine],
) -> None:
    admin_engine, runtime_engine = postgres_guest_redeem_engines
    suffix = uuid4().hex
    tenant_id = f"guest-redeem-{suffix}"
    principal_id = f"principal-{suffix}"
    subject = f"subject-{suffix}"

    with admin_engine.connect() as connection:
        redeem_posture = connection.execute(
            text(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE relname = 'guest_redeem_states'"
            )
        ).one()
        principal_posture = connection.execute(
            text(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE relname = 'guest_principals'"
            )
        ).one()
    assert tuple(redeem_posture) == (False, False)
    assert tuple(principal_posture) == (True, True)

    with Session(admin_engine) as db:
        db.add(
            TenantRow(
                id=tenant_id,
                display_name=tenant_id,
                lifecycle_state="active",
                created_at=NOW.isoformat(),
                updated_at=NOW.isoformat(),
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
                status="pending",
                verification_method="personal_account",
                verified_issuer=None,
                verified_subject=None,
                created_by="host-admin",
                created_at=NOW.isoformat(),
                expires_at=(NOW + timedelta(hours=2)).isoformat(),
                redeemed_at=None,
                revoked_at=None,
            )
        )
        db.commit()

    runtime_factory = sessionmaker(bind=runtime_engine, class_=Session, expire_on_commit=False)
    store = DatabaseGuestRedeemStateStore(runtime_factory)
    raw_state = ""
    try:
        with Session(runtime_engine) as db:
            assert db.get(GuestPrincipalRow, (tenant_id, principal_id)) is None

        raw_state = store.issue_redeem_state(
            tenant_id=tenant_id,
            guest_principal_id=principal_id,
            hash_key=STATE_HASH_KEY,
            now=NOW,
        )
        challenge = store.resolve_challenge(
            raw_state=raw_state,
            hash_key=STATE_HASH_KEY,
            now=NOW,
        )
        assert challenge.tenant_id == tenant_id
        assert challenge.guest_principal_id == principal_id
        assert challenge.verification_method == "personal_account"

        raw_session_id = store.redeem_verified_identity(
            raw_state=raw_state,
            hash_key=STATE_HASH_KEY,
            session_hash_key=SESSION_HASH_KEY,
            identity=VerifiedGuestIdentity(issuer=ISSUER, subject=subject),
            now=NOW,
        )
        session_hash = derive_session_key_hash(raw_session_id, key=SESSION_HASH_KEY)

        with Session(admin_engine) as db:
            state = db.scalar(
                select(GuestRedeemStateRow).where(GuestRedeemStateRow.tenant_id == tenant_id)
            )
            assert state is not None and state.consumed_at is not None
            session_row = db.get(GuestAuthSessionRow, session_hash)
            assert session_row is not None
            assert session_row.tenant_id == tenant_id
            assert session_row.guest_principal_id == principal_id
        with Session(admin_engine) as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_id)
            principal = db.get(GuestPrincipalRow, (tenant_id, principal_id))
            assert principal is not None
            assert principal.status == "active"
            assert principal.verified_issuer == ISSUER
            assert principal.verified_subject == subject

        with pytest.raises(Exception):
            store.redeem_verified_identity(
                raw_state=raw_state,
                hash_key=STATE_HASH_KEY,
                session_hash_key=SESSION_HASH_KEY,
                identity=VerifiedGuestIdentity(issuer=ISSUER, subject=subject),
                now=NOW,
            )
    finally:
        with Session(admin_engine) as db:
            db.execute(delete(GuestAuthSessionRow).where(GuestAuthSessionRow.tenant_id == tenant_id))
            db.execute(delete(GuestRedeemStateRow).where(GuestRedeemStateRow.tenant_id == tenant_id))
            db.commit()
        with Session(admin_engine) as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_id)
            db.execute(delete(GuestPrincipalRow).where(GuestPrincipalRow.tenant_id == tenant_id))
            db.commit()
        with Session(admin_engine) as db:
            db.execute(delete(TenantRow).where(TenantRow.id == tenant_id))
            db.commit()
