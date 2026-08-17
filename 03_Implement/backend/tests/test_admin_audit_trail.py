"""SEC-ADMIN-PLANE-03: control-plane operation audit trail.

Covers the recording middleware (allowed + denied), the allowlist read API with
cursor pagination, control-plane-only read access, and the no-secrets
guarantee. Recording is fail-open: an audit failure never blocks the operation.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base, AdminAuditEventRow
from kj_atlas_api.settings import settings

_ADMIN_KEY = "control-plane-bootstrap-key"
_BUSINESS_KEY = "business-plane-key"


@contextmanager
def _client(tmp_path) -> Iterator[tuple[TestClient, sessionmaker]]:
    engine = create_engine(f"sqlite:///{tmp_path / 'admin_audit.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            # Point the recording middleware at the test DB.
            client.app.state.admin_audit_session_factory = session_local
            yield client, session_local
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _audit_rows(session_local: sessionmaker) -> list[AdminAuditEventRow]:
    with session_local() as db:  # type: ignore[attr-defined]
        return list(db.query(AdminAuditEventRow).order_by(AdminAuditEventRow.occurred_at))


def _seed_events(client: TestClient, count: int) -> None:
    for index in range(count):
        client.post(
            "/admin/provision/users",
            json={"provider": "oidc", "externalUid": f"u-{index}"},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )


def test_allowed_admin_operation_is_recorded(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    with _client(tmp_path) as (client, session_local):
        response = client.post(
            "/admin/provision/users",
            json={"provider": "oidc", "externalUid": "u-1", "displayName": "A"},
            headers={"X-Admin-Api-Key": _ADMIN_KEY, "X-Request-Id": "trace-admin-1"},
        )
        assert response.status_code == 201

        rows = _audit_rows(session_local)
        assert len(rows) == 1
        row = rows[0]
        assert row.route == "/admin/provision/users"
        assert row.result == "allowed"
        assert row.status_code == 201
        assert row.actor_ref_hash is not None
        assert len(row.actor_ref_hash) == 16
        assert row.request_id is not None


def test_denied_admin_operation_is_recorded(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    with _client(tmp_path) as (client, session_local):
        # Wrong admin key -> 401 control_plane_unauthorized.
        response = client.post(
            "/admin/provision/users",
            json={"provider": "oidc", "externalUid": "u-1"},
            headers={"X-Admin-Api-Key": "wrong-key"},
        )
        assert response.status_code == 401

        rows = _audit_rows(session_local)
        assert len(rows) == 1
        assert rows[0].result == "denied"
        assert rows[0].status_code == 401
        assert rows[0].route == "/admin/provision/users"


def test_audit_trail_never_stores_request_body_or_secrets(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    secret_uid = "super-secret-external-uid"
    with _client(tmp_path) as (client, session_local):
        response = client.post(
            "/admin/provision/users",
            json={"provider": "oidc", "externalUid": secret_uid, "displayName": "A"},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert response.status_code == 201

        rows = _audit_rows(session_local)
        assert len(rows) == 1
        serialized = str(rows[0].__dict__)
        assert secret_uid not in serialized
        assert _ADMIN_KEY not in serialized
        assert "oidc" not in serialized


def test_read_api_returns_allowlist_and_paginates(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    with _client(tmp_path) as (client, _session_local):
        _seed_events(client, 5)

        page = client.get(
            "/admin/provision/audit",
            params={"limit": 3},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert page.status_code == 200
        body = page.json()
        assert len(body["events"]) == 3
        assert body["nextCursor"] is not None
        for event in body["events"]:
            # allowlist: no tenant_id, no body, no secrets.
            assert "tenantId" not in event
            assert "externalUid" not in event

        next_page = client.get(
            "/admin/provision/audit",
            params={"limit": 3, "cursor": body["nextCursor"]},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert next_page.status_code == 200
        next_body = next_page.json()
        assert len(next_body["events"]) == 2
        assert next_body["nextCursor"] is None


def test_read_api_requires_control_plane(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    with _client(tmp_path) as (client, _session_local):
        response = client.get(
            "/admin/provision/audit",
            headers={"X-API-Key": _BUSINESS_KEY},
        )
        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "control_plane_unauthorized"
