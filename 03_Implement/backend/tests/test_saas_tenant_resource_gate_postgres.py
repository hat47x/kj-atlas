"""OPS-SAAS-SCALE-01 AC-6: tenant-scoped resource lookup前のfail-closed境界。"""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.routes.docs import router as docs_router
from tests.test_saas_auth_session_postgres_multi_instance import (
    _build_app,
    _configured,
    _cookie_headers,
    _create_login,
    _isolated_postgres_database,
    _mutation_headers,
    _new_engine,
    _run_alembic,
    _seed_shared_auth_data,
)

TENANT_SESSION_VERSION_HEADER = "KJ-Atlas-Tenant-Session-Version"


class _FailIfReachedDocumentResourceResolver:
    def __init__(self) -> None:
        self.calls = 0

    def resolve(self, **_: object) -> object:
        self.calls += 1
        raise AssertionError("document resource lookup must not run before session precondition")


def _set_database_connections(database_url: str, *, allowed: bool) -> None:
    target_url = make_url(database_url)
    database_name = target_url.database
    if database_name is None or re.fullmatch(r"[a-z0-9_]+", database_name) is None:
        raise ValueError("isolated database name must be a simple identifier")

    admin_engine = create_engine(
        target_url.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
    )
    try:
        with admin_engine.connect() as connection:
            value = "true" if allowed else "false"
            connection.execute(text(f'ALTER DATABASE "{database_name}" WITH ALLOW_CONNECTIONS {value}'))
            if not allowed:
                connection.execute(
                    text(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE datname = :name AND pid <> pg_backend_pid()"
                    ),
                    {"name": database_name},
                )
    finally:
        admin_engine.dispose()


@pytest.mark.postgres
@pytest.mark.skipif(not _configured(), reason="PostgreSQL integration environment is not configured")
def test_stale_or_unavailable_session_stops_before_document_resource_lookup() -> None:
    """Old-tenant and DB-unavailable requests fail before any document lookup."""
    with _isolated_postgres_database() as database_url:
        upgrade = _run_alembic(database_url, "upgrade", "head")
        assert upgrade.returncode == 0, upgrade.stderr

        engine = _new_engine(database_url)
        factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
        database_connections_disabled = False
        try:
            _seed_shared_auth_data(factory)
            app, store = _build_app(factory)
            resource_resolver = _FailIfReachedDocumentResourceResolver()
            app.state.document_access_resource_resolver = resource_resolver
            app.include_router(docs_router)

            raw_session = "ac6-resource-gate-session"
            _create_login(store, raw_session_id=raw_session)

            with TestClient(app) as client:
                before = client.get("/session/context", headers=_cookie_headers(raw_session))
                assert before.status_code == 200, before.text
                version_1 = before.json()["tenantSessionVersion"]

                switched = client.post(
                    "/session/active-tenant",
                    json={
                        "tenantId": "tenant-b",
                        "expectedTenantSessionVersion": version_1,
                    },
                    headers=_mutation_headers(raw_session),
                )
                assert switched.status_code == 200, switched.text
                version_2 = switched.json()["tenantSessionVersion"]
                assert version_2 != version_1

                stale = client.get(
                    "/docs/must-not-load",
                    headers={
                        **_cookie_headers(raw_session),
                        TENANT_SESSION_VERSION_HEADER: version_1,
                    },
                )
                assert stale.status_code == 409, stale.text
                assert stale.json()["detail"]["code"] == "tenant_session_changed"
                assert resource_resolver.calls == 0

                _set_database_connections(database_url, allowed=False)
                database_connections_disabled = True
                unavailable = client.get(
                    "/docs/must-not-load",
                    headers={
                        **_cookie_headers(raw_session),
                        TENANT_SESSION_VERSION_HEADER: version_2,
                    },
                )
                assert unavailable.status_code == 503, unavailable.text
                assert resource_resolver.calls == 0
        finally:
            if database_connections_disabled:
                _set_database_connections(database_url, allowed=True)
            engine.dispose()
