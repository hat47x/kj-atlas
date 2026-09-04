"""OPS-SAAS-SCALE-01: PostgreSQL上の認証session正本を複数app instanceで検証する。

SQLite上でstore objectを2つ作るだけでは、実運用の水平スケール境界は確認できない。
このtestは隔離PostgreSQL databaseへ実migrationを適用し、別々のSQLAlchemy engineを持つ
2つ以上のFastAPI instanceから同じBFF auth sessionをHTTPで利用する。
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text, update
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.active_tenant_session import DatabaseActiveTenantSessionPersister
from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.db import _normalize_database_url, get_db
from kj_atlas_api.jwks_store import JwksStore
from kj_atlas_api.models import (
    IdentityProviderRow,
    SaasAuthSessionRow,
    TenantIdentityProviderRow,
    TenantMembershipRow,
    TenantRow,
    UserIdentityRow,
    UserRow,
)
from kj_atlas_api.routes.session import router as session_router
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthSessionStore, DatabaseSaasAuthStateStore
from kj_atlas_api.session_csrf import (
    AUTH_SESSION_COOKIE,
    BffCsrfProtectionMiddleware,
    CSRF_HEADER,
    derive_session_csrf_token,
)
from kj_atlas_api.tenant_context import ClaimBasedTenantContextResolver
from kj_atlas_api.trusted_auth_edge import JwtSaasIdentityContextResolver
from tests.conftest import StubCapabilityResolver

BACKEND_DIR = Path(__file__).resolve().parents[1]
RUN_PG_TESTS_ENV = "KJ_ATLAS_RUN_PG_TESTS"
DATABASE_URL_ENV = "KJ_ATLAS_DATABASE_URL"
POSTGRES_CONTAINER_ENV = "KJ_ATLAS_TEST_POSTGRES_CONTAINER"
HASH_KEY = b"ops-saas-scale-postgres-key-0123456789"
ROTATED_HASH_KEY = b"ops-saas-scale-rotated-key-987654321"
ISSUER = "https://broker.example.test/issuer"
AUDIENCE = "kj-atlas"
TIMESTAMP = "2026-09-04T00:00:00Z"


def _configured() -> bool:
    return (
        os.getenv(RUN_PG_TESTS_ENV) == "1"
        and bool(os.getenv(DATABASE_URL_ENV))
        and bool(os.getenv(POSTGRES_CONTAINER_ENV))
    )


def _run_alembic(database_url: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env[DATABASE_URL_ENV] = database_url
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_DIR,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


@contextmanager
def _isolated_postgres_database():
    base_url = make_url(os.environ[DATABASE_URL_ENV])
    database_name = f"kj_atlas_ops_scale_{uuid4().hex[:16]}"
    if not re.fullmatch(r"[a-z0-9_]+", database_name):
        raise ValueError("isolated database name must be a simple identifier")

    admin_url = base_url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    finally:
        admin_engine.dispose()

    isolated_url = base_url.set(database=database_name).render_as_string(hide_password=False)
    try:
        yield isolated_url
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
                            {"name": database_name},
                        )
                        connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
                    last_error = None
                    break
                except OperationalError as error:
                    last_error = error
            if last_error is not None:
                raise last_error
        finally:
            admin_engine.dispose()


def _new_engine(database_url: str) -> Engine:
    return create_engine(
        _normalize_database_url(database_url),
        pool_size=1,
        max_overflow=0,
    )


def _seed_shared_auth_data(factory: sessionmaker[Session]) -> None:
    with factory() as db:
        db.add_all(
            [
                UserRow(
                    id="user-1",
                    display_name="User One",
                    email="user-1@example.test",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                TenantRow(
                    id="tenant-a",
                    display_name="Tenant A",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                TenantRow(
                    id="tenant-b",
                    display_name="Tenant B",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                IdentityProviderRow(
                    id="idp-1",
                    issuer=ISSUER,
                    audience=AUDIENCE,
                    protocol="oidc",
                    jwks_uri="https://broker.example.test/jwks.json",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                TenantIdentityProviderRow(
                    tenant_id="tenant-a",
                    identity_provider_id="idp-1",
                    external_tenant_ref="external-a",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                TenantIdentityProviderRow(
                    tenant_id="tenant-b",
                    identity_provider_id="idp-1",
                    external_tenant_ref="external-b",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                UserIdentityRow(
                    user_id="user-1",
                    provider="idp-1",
                    external_uid="subject-1",
                    identity_provider_id="idp-1",
                    subject="subject-1",
                    created_at=TIMESTAMP,
                ),
                TenantMembershipRow(
                    tenant_id="tenant-a",
                    user_id="user-1",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                TenantMembershipRow(
                    tenant_id="tenant-b",
                    user_id="user-1",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
            ]
        )
        db.commit()


def _build_app(
    factory: sessionmaker[Session],
    *,
    hash_key: bytes = HASH_KEY,
) -> tuple[FastAPI, DatabaseSaasAuthSessionStore]:
    auth_store = DatabaseSaasAuthSessionStore(factory)
    principal_store = DatabaseSaasAuthStateStore(factory)

    app = FastAPI()
    app.state.runtime_profile = "saas-multitenant"
    app.state.saas_auth_session_store = auth_store
    app.state.saas_auth_session_hash_key = hash_key
    app.state.saas_identity_context_resolver = JwtSaasIdentityContextResolver(
        jwks_store=JwksStore(),
        auth_session_store=auth_store,
        auth_session_hash_key=hash_key,
    )
    app.state.tenant_context_resolver = ClaimBasedTenantContextResolver()
    app.state.tenant_capability_resolver = StubCapabilityResolver()
    app.state.active_tenant_session_persister = DatabaseActiveTenantSessionPersister(
        store=principal_store,
        secure_cookie=False,
    )

    def _get_test_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    app.include_router(session_router)
    app.add_middleware(BffCsrfProtectionMiddleware)
    return app, auth_store


def _cookie_headers(raw_session_id: str) -> dict[str, str]:
    return {"Cookie": f"{AUTH_SESSION_COOKIE}={raw_session_id}"}


def _mutation_headers(raw_session_id: str, *, key: bytes = HASH_KEY) -> dict[str, str]:
    return {
        **_cookie_headers(raw_session_id),
        "Origin": "http://testserver",
        CSRF_HEADER: derive_session_csrf_token(raw_session_id, key=key),
    }


def _create_login(
    store: DatabaseSaasAuthSessionStore,
    *,
    raw_session_id: str,
    tenant_id: str = "tenant-a",
    version: str = "version-1",
) -> str:
    key_hash = derive_session_key_hash(raw_session_id, key=HASH_KEY)
    store.create_auth_session(
        session_key_hash=key_hash,
        principal_id="user-1",
        issuer=ISSUER,
        subject="subject-1",
        active_tenant_id=tenant_id,
        tenant_session_version=version,
    )
    return key_hash


@pytest.mark.postgres
@pytest.mark.skipif(not _configured(), reason="PostgreSQL integration environment is not configured")
def test_auth_session_is_shared_across_two_http_app_instances_and_survives_restart() -> None:
    """AC-4/5/6/7: real PostgreSQL + separate app/engine instances.

    The same login session crosses app instances, CAS invalidates a stale tab,
    independent logins of one principal remain independent, expiry/revocation
    propagate through the shared database, and a newly created app instance sees
    the existing session. A hash-key rotation intentionally invalidates cookies
    minted under the previous key instead of guessing or falling back.
    """
    with _isolated_postgres_database() as database_url:
        # AC-7: exercise the auth-session migration itself on PostgreSQL, not SQLite.
        upgrade = _run_alembic(database_url, "upgrade", "20260813_0027")
        assert upgrade.returncode == 0, upgrade.stderr
        migration_engine = _new_engine(database_url)
        try:
            assert inspect(migration_engine).has_table("saas_auth_sessions")
        finally:
            migration_engine.dispose()

        downgrade = _run_alembic(database_url, "downgrade", "20260813_0026")
        assert downgrade.returncode == 0, downgrade.stderr
        migration_engine = _new_engine(database_url)
        try:
            assert not inspect(migration_engine).has_table("saas_auth_sessions")
        finally:
            migration_engine.dispose()

        reupgrade = _run_alembic(database_url, "upgrade", "head")
        assert reupgrade.returncode == 0, reupgrade.stderr

        engine_a = _new_engine(database_url)
        engine_b = _new_engine(database_url)
        factory_a = sessionmaker(bind=engine_a, class_=Session, expire_on_commit=False)
        factory_b = sessionmaker(bind=engine_b, class_=Session, expire_on_commit=False)
        try:
            _seed_shared_auth_data(factory_a)
            app_a, store_a = _build_app(factory_a)
            app_b, _ = _build_app(factory_b)

            raw_shared = "shared-browser-session"
            raw_other = "independent-browser-session"
            shared_hash = _create_login(store_a, raw_session_id=raw_shared)
            other_hash = _create_login(store_a, raw_session_id=raw_other)

            with TestClient(app_a) as client_a, TestClient(app_b) as client_b:
                before = client_b.get("/session/context", headers=_cookie_headers(raw_shared))
                assert before.status_code == 200, before.text
                assert before.json()["activeTenant"]["id"] == "tenant-a"
                version_1 = before.json()["tenantSessionVersion"]

                switched = client_a.post(
                    "/session/active-tenant",
                    json={
                        "tenantId": "tenant-b",
                        "expectedTenantSessionVersion": version_1,
                    },
                    headers=_mutation_headers(raw_shared),
                )
                assert switched.status_code == 200, switched.text
                version_2 = switched.json()["tenantSessionVersion"]
                assert version_2 != version_1
                assert switched.json()["activeTenant"]["id"] == "tenant-b"

                # A second app instance resolves the same shared row immediately.
                observed = client_b.get("/session/context", headers=_cookie_headers(raw_shared))
                assert observed.status_code == 200, observed.text
                assert observed.json()["activeTenant"]["id"] == "tenant-b"
                assert observed.json()["tenantSessionVersion"] == version_2

                # A stale tab routed to another worker fails before any requested
                # tenant switch can be applied.
                stale = client_b.post(
                    "/session/active-tenant",
                    json={
                        "tenantId": "tenant-a",
                        "expectedTenantSessionVersion": version_1,
                    },
                    headers=_mutation_headers(raw_shared),
                )
                assert stale.status_code == 409, stale.text
                assert stale.json()["detail"]["code"] == "tenant_session_changed"

                # A distinct login of the same principal keeps its own tenant/version.
                independent = client_b.get(
                    "/session/context", headers=_cookie_headers(raw_other)
                )
                assert independent.status_code == 200, independent.text
                assert independent.json()["activeTenant"]["id"] == "tenant-a"
                assert independent.json()["tenantSessionVersion"] == "version-1"

                # Logout on app A revokes only the presented shared session.
                logged_out = client_a.post(
                    "/session/logout", headers=_mutation_headers(raw_shared)
                )
                assert logged_out.status_code == 204, logged_out.text
                revoked_elsewhere = client_b.get(
                    "/session/context", headers=_cookie_headers(raw_shared)
                )
                assert revoked_elsewhere.status_code == 401, revoked_elsewhere.text
                assert revoked_elsewhere.json()["detail"]["code"] == "session_invalid"
                still_live = client_b.get(
                    "/session/context", headers=_cookie_headers(raw_other)
                )
                assert still_live.status_code == 200, still_live.text

            # A fresh app/engine instance after a rolling restart still resolves
            # the independent login from PostgreSQL.
            engine_c = _new_engine(database_url)
            factory_c = sessionmaker(bind=engine_c, class_=Session, expire_on_commit=False)
            try:
                app_c, _ = _build_app(factory_c)
                with TestClient(app_c) as client_c:
                    after_restart = client_c.get(
                        "/session/context", headers=_cookie_headers(raw_other)
                    )
                    assert after_restart.status_code == 200, after_restart.text
                    assert after_restart.json()["activeTenant"]["id"] == "tenant-a"
            finally:
                engine_c.dispose()

            # Expiry written through one engine is observed by a separately
            # constructed app instance; the revoked shared session stays revoked.
            raw_expiring = "idle-expiring-session"
            expiring_hash = _create_login(store_a, raw_session_id=raw_expiring)
            with factory_a() as db:
                db.execute(
                    update(SaasAuthSessionRow)
                    .where(SaasAuthSessionRow.session_key_hash == expiring_hash)
                    .values(
                        last_used_at=(
                            datetime.now(timezone.utc) - timedelta(minutes=61)
                        ).isoformat()
                    )
                )
                db.commit()
            with TestClient(app_b) as client_b:
                expired = client_b.get(
                    "/session/context", headers=_cookie_headers(raw_expiring)
                )
                assert expired.status_code == 401, expired.text
                assert expired.json()["detail"]["code"] == "session_invalid"

            # Key rotation is fail-closed: a worker using a new hash key cannot
            # reinterpret a cookie minted under the old key as another session.
            engine_d = _new_engine(database_url)
            factory_d = sessionmaker(bind=engine_d, class_=Session, expire_on_commit=False)
            try:
                app_d, _ = _build_app(factory_d, hash_key=ROTATED_HASH_KEY)
                with TestClient(app_d) as client_d:
                    rotated_key = client_d.get(
                        "/session/context", headers=_cookie_headers(raw_other)
                    )
                    assert rotated_key.status_code == 401, rotated_key.text
                    assert rotated_key.json()["detail"]["code"] == "session_invalid"
            finally:
                engine_d.dispose()

            # Keep explicit evidence that the two principal-equal sessions were
            # distinct database rows throughout the test.
            with factory_a() as db:
                shared_row = db.get(SaasAuthSessionRow, shared_hash)
                other_row = db.get(SaasAuthSessionRow, other_hash)
                assert shared_row is not None and shared_row.revoked_at is not None
                assert other_row is not None and other_row.revoked_at is None
        finally:
            engine_b.dispose()
            engine_a.dispose()
