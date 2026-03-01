from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.access_control import AccessDecision
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base


class DenyAllAdapter:
    name = "deny-all"

    def authorize(self, request):  # noqa: ANN001
        return AccessDecision(allow=False, reason=f"blocked:{request.action}")


class AllowAllAdapter:
    name = "allow-all"

    def authorize(self, request):  # noqa: ANN001
        return AccessDecision(allow=True)


class ErrorAdapter:
    name = "error"

    def __init__(self, message: str):
        self._message = message

    def authorize(self, request):  # noqa: ANN001
        raise RuntimeError(self._message)


@contextmanager
def _sqlite_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "docs_access_control.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
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
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _sample_payload(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "access-test",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 0, "y": 0}],
        "edges": [],
    }


def test_adapter_unset_keeps_existing_docs_roundtrip(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = None
        put_resp = client.put("/docs/doc-compat", json=_sample_payload("doc-compat"))
        assert put_resp.status_code == 200

        get_resp = client.get("/docs/doc-compat")
        assert get_resp.status_code == 200


def test_fail_safe_deny_when_policy_ref_missing_for_restricted_visibility(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.get(
            "/docs/doc-restricted",
            headers={"x-doc-visibility": "Restricted"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: policy_ref_missing"


def test_fail_safe_read_only_blocks_write_export_but_allows_read(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"
        client.put("/docs/doc-ro", json=_sample_payload("doc-ro"))

        read_resp = client.get(
            "/docs/doc-ro",
            headers={"x-doc-visibility": "Restricted"},
        )
        write_resp = client.put(
            "/docs/doc-ro",
            json=_sample_payload("doc-ro"),
            headers={"x-doc-visibility": "Restricted"},
        )
        export_resp = client.post(
            "/docs/doc-ro/export-audit",
            json={"safeMode": True, "exportKind": "bundle"},
            headers={"x-doc-visibility": "Restricted"},
        )

    assert read_resp.status_code == 200
    assert write_resp.status_code == 403
    assert export_resp.status_code == 403


def test_adapter_denial_prevents_role_header_privilege_escalation(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = DenyAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"

        response = client.put(
            "/docs/doc-escalation",
            json=_sample_payload("doc-escalation"),
            headers={
                "x-auth-roles": "admin,superuser",
                "x-auth-groups": "security",
                "x-doc-visibility": "Org",
                "x-policy-ref": "policy-org-1",
            },
        )

    assert response.status_code == 403
    assert "blocked:write" in response.json()["detail"]


def test_adapter_runtime_error_enforces_fail_safe_for_restricted_visibility(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = ErrorAdapter("policy_ref_unreachable:timeout")
        client.app.state.access_control_fail_safe_mode = "read_only"
        client.put("/docs/doc-fs", json=_sample_payload("doc-fs"))

        read_resp = client.get(
            "/docs/doc-fs",
            headers={"x-doc-visibility": "Restricted", "x-policy-ref": "policy-1"},
        )
        write_resp = client.put(
            "/docs/doc-fs",
            json=_sample_payload("doc-fs"),
            headers={"x-doc-visibility": "Restricted", "x-policy-ref": "policy-1"},
        )

    assert read_resp.status_code == 200
    assert write_resp.status_code == 403
    assert write_resp.json()["detail"] == "Access denied: policy_ref_unreachable"


def test_adapter_runtime_error_is_fail_open_for_public_visibility(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = ErrorAdapter("adapter exploded")
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.put(
            "/docs/doc-public",
            json=_sample_payload("doc-public"),
            headers={"x-doc-visibility": "Public"},
        )

    assert response.status_code == 200
