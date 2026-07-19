from __future__ import annotations

import ast
import inspect
import textwrap
from types import SimpleNamespace

from fastapi import Depends, FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app as main_app
from kj_atlas_api.tenant_session_precondition import (
    require_tenant_scoped_api_precondition,
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


def test_tenant_scoped_dependency_rejects_stale_version_before_endpoint(
    monkeypatch,
) -> None:
    app = FastAPI()
    app.state.runtime_profile = "saas-multitenant"
    app.dependency_overrides[get_db] = lambda: object()
    endpoint_called = False

    monkeypatch.setattr(
        "kj_atlas_api.tenant_session_precondition.resolve_trusted_saas_request_session",
        lambda **_: SimpleNamespace(
            session=SimpleNamespace(tenant_session_version="trusted-session-v2")
        ),
    )

    @app.post(
        "/guarded",
        dependencies=[Depends(require_tenant_scoped_api_precondition)],
    )
    def guarded() -> dict[str, bool]:
        nonlocal endpoint_called
        endpoint_called = True
        return {"ok": True}

    with TestClient(app) as client:
        response = client.post(
            "/guarded",
            headers={"KJ-Atlas-Tenant-Session-Version": "stale-session-v1"},
        )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "tenant_session_changed"
    assert endpoint_called is False


def test_all_tenant_content_ai_and_context_routes_install_precondition() -> None:
    tenant_content_routes = [
        route
        for route in main_app.routes
        if isinstance(route, APIRoute)
        and route.path.startswith(("/ai/", "/context/"))
        and route.path != "/ai/provider-status"
    ]

    assert tenant_content_routes
    for route in tenant_content_routes:
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_tenant_scoped_api_precondition in dependency_calls, route.path


def test_all_document_and_document_admin_routes_use_shared_authorization_boundaries() -> None:
    route_boundaries = {
        "/docs/": "_authorize_request",
        "/tenant-admin/document-access": "_authorize_document_policy_management",
    }

    for path_prefix, boundary_call in route_boundaries.items():
        routes = [
            route
            for route in main_app.routes
            if isinstance(route, APIRoute) and route.path.startswith(path_prefix)
        ]
        assert routes, path_prefix
        for route in routes:
            endpoint_tree = ast.parse(textwrap.dedent(inspect.getsource(route.endpoint)))
            called_functions = {
                node.func.id
                for node in ast.walk(endpoint_tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            assert boundary_call in called_functions, route.path
