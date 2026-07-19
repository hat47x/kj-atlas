from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from kj_atlas_api.tenant_session_precondition import (
    require_tenant_session_request_precondition,
)


def _client(*, runtime_profile: str) -> TestClient:
    app = FastAPI()
    app.state.runtime_profile = runtime_profile

    @app.get("/guarded")
    def guarded(request: Request) -> dict[str, bool]:
        require_tenant_session_request_precondition(
            request=request,
            current_version="trusted-session-v2",
        )
        return {"ok": True}

    return TestClient(app)


def test_single_tenant_runtime_does_not_require_version_header() -> None:
    with _client(runtime_profile="enterprise-production") as client:
        response = client.get("/guarded")

    assert response.status_code == 200


def test_saas_runtime_accepts_exact_current_version() -> None:
    with _client(runtime_profile="saas-multitenant") as client:
        response = client.get(
            "/guarded",
            headers={"KJ-Atlas-Tenant-Session-Version": "trusted-session-v2"},
        )

    assert response.status_code == 200


def test_saas_runtime_rejects_missing_stale_malformed_and_duplicate_versions() -> None:
    requests: tuple[dict[str, object], ...] = (
        {},
        {"headers": {"KJ-Atlas-Tenant-Session-Version": "stale-session-v1"}},
        {"headers": {"KJ-Atlas-Tenant-Session-Version": "contains spaces"}},
        {
            "headers": [
                ("KJ-Atlas-Tenant-Session-Version", "trusted-session-v2"),
                ("KJ-Atlas-Tenant-Session-Version", "trusted-session-v2"),
            ]
        },
    )
    with _client(runtime_profile="saas-multitenant") as client:
        responses = [client.get("/guarded", **kwargs) for kwargs in requests]

    for response in responses:
        assert response.status_code == 409
        assert response.json() == {
            "detail": {
                "code": "tenant_session_changed",
                "message": "Tenant session context changed.",
            }
        }
        assert "stale-session-v1" not in response.text
        assert "trusted-session-v2" not in response.text


def test_unknown_runtime_fails_closed_without_inspecting_header() -> None:
    with _client(runtime_profile="unknown") as client:
        response = client.get(
            "/guarded",
            headers={"KJ-Atlas-Tenant-Session-Version": "trusted-session-v2"},
        )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "runtime_policy_unavailable"
    assert "trusted-session-v2" not in response.text
