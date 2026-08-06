from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.access_control import (
    AccessControlInvalidPolicyError,
    AccessControlUnreachableError,
    AccessDecision,
    AuthContext,
)
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import LOCAL_DEFAULT_TENANT_ID, Base
from kj_atlas_api.tenant_context import TenantContext


class DenyAllAdapter:
    name = "deny-all"

    def authorize(self, request):  # noqa: ANN001
        return AccessDecision(allow=False, reason=f"blocked:{request.action}")


class AllowAllAdapter:
    name = "allow-all"

    def authorize(self, request):  # noqa: ANN001
        return AccessDecision(allow=True)


class UnreachableAdapter:
    name = "unreachable"

    def authorize(self, request):  # noqa: ANN001
        raise AccessControlUnreachableError("timeout")


class InvalidPolicyAdapter:
    name = "invalid-policy"

    def authorize(self, request):  # noqa: ANN001
        raise AccessControlInvalidPolicyError("bad signature")


class CrashAdapter:
    name = "crash"

    def authorize(self, request):  # noqa: ANN001
        raise RuntimeError("unexpected adapter exception")


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
        "islands": [],
    }


def test_adapter_unset_keeps_existing_docs_roundtrip(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = None
        put_resp = client.put("/docs/doc-compat", json=_sample_payload("doc-compat"))
        assert put_resp.status_code == 200

        get_resp = client.get("/docs/doc-compat")
        assert get_resp.status_code == 200


def test_tenant_scoped_profile_denies_read_when_adapter_is_missing(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Same request as the roundtrip above -- adapter unset, document present in
    # the caller's own tenant -- so a 404 or a tenant-boundary reason cannot be
    # mistaken for the denial under test. Only the runtime profile differs.
    monkeypatch.setattr(
        "kj_atlas_api.routes.docs.resolve_trusted_saas_request_session",
        lambda **_: SimpleNamespace(
            identity=SimpleNamespace(
                auth_context=AuthContext(actor_ref="user-1", user_id="user-1"),
            ),
            tenant=TenantContext(
                tenant_id=LOCAL_DEFAULT_TENANT_ID,
                membership_id="membership-1",
                resolved_by="verified_claim",
            ),
            session=SimpleNamespace(tenant_session_version="session-v2"),
        ),
    )

    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = None
        seed_resp = client.put(
            "/docs/doc-adapter-missing",
            json=_sample_payload("doc-adapter-missing"),
        )
        assert seed_resp.status_code == 200

        original_runtime_profile = client.app.state.runtime_profile
        try:
            client.app.state.runtime_profile = "saas-multitenant"
            read_resp = client.get(
                "/docs/doc-adapter-missing",
                headers={"KJ-Atlas-Tenant-Session-Version": "session-v2"},
            )
            write_resp = client.put(
                "/docs/doc-adapter-missing",
                json=_sample_payload("doc-adapter-missing"),
                headers={"KJ-Atlas-Tenant-Session-Version": "session-v2"},
            )
        finally:
            client.app.state.runtime_profile = original_runtime_profile

    assert read_resp.status_code == 403
    assert read_resp.json()["detail"] == "Access denied: adapter_missing"
    assert "access-test" not in read_resp.text
    assert "alpha" not in read_resp.text
    assert write_resp.status_code == 403
    assert write_resp.json()["detail"] == "Access denied: adapter_missing"


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


def test_fail_safe_visibility_header_is_trimmed_before_policy_ref_guard(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.get(
            "/docs/doc-restricted-trimmed",
            headers={"x-doc-visibility": "  Restricted  "},
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


def test_fail_safe_unreachable_policy_ref_blocks_export_with_reason(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = UnreachableAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.post(
            "/docs/doc-unreachable/export-audit",
            json={"safeMode": False, "exportKind": "bundle"},
            headers={"x-doc-visibility": "Restricted", "x-policy-ref": "org-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: policy_ref_unreachable"


def test_fail_safe_invalid_policy_ref_blocks_write_with_reason(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = InvalidPolicyAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.put(
            "/docs/doc-invalid",
            json=_sample_payload("doc-invalid"),
            headers={"x-doc-visibility": "Org", "x-policy-ref": "org-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: policy_ref_invalid"


def test_fail_safe_adapter_exception_blocks_read_with_reason(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = CrashAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.get(
            "/docs/doc-crash",
            headers={"x-doc-visibility": "Org", "x-policy-ref": "org-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: adapter_error"


def test_safe_mode_priority_blocks_export_before_adapter_allow(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"

        response = client.post(
            "/docs/doc-safe-mode/export-audit",
            json={"safeMode": True, "exportKind": "bundle"},
            headers={"x-doc-visibility": "Public", "x-policy-ref": "public-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: safe_mode"


def test_read_only_priority_blocks_write_before_adapter_allow(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"

        response = client.put(
            "/docs/doc-read-only",
            json=_sample_payload("doc-read-only"),
            headers={"x-read-only": "true", "x-doc-visibility": "Public", "x-policy-ref": "public-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: read_only"


@pytest.mark.parametrize("visibility", ["Public", "Unlisted", "Org", "Restricted"])
def test_safe_mode_and_read_only_priority_remains_stronger_than_visibility_label(tmp_path, visibility: str) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"

        export_resp = client.post(
            "/docs/doc-priority/export-audit",
            json={"safeMode": True, "exportKind": "bundle"},
            headers={"x-doc-visibility": visibility, "x-policy-ref": "policy-v1"},
        )
        write_resp = client.put(
            "/docs/doc-priority",
            json=_sample_payload("doc-priority"),
            headers={"x-read-only": "true", "x-doc-visibility": visibility, "x-policy-ref": "policy-v1"},
        )

    assert export_resp.status_code == 403
    assert export_resp.json()["detail"] == "Access denied: safe_mode"
    assert write_resp.status_code == 403
    assert write_resp.json()["detail"] == "Access denied: read_only"


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
