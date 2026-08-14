from __future__ import annotations

import ast
import inspect
import textwrap
from types import SimpleNamespace

from fastapi import Depends, FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from starlette.routing import Route as StarletteRoute

from kj_atlas_api.active_tenant_session import require_current_tenant_session_version
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app as main_app
from kj_atlas_api.control_plane_auth import require_control_plane_authorization
from kj_atlas_api.routes.docs import _authorize_request
from kj_atlas_api.routes.document_access_admin import _authorize_document_policy_management
from kj_atlas_api.routes.inquiry_bundles import _trusted_session as _inquiry_bundle_trusted_session
from kj_atlas_api.saas_request_context import resolve_trusted_saas_request_session
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


# The prefix-scoped coverage guards above only inspect routes under the four
# prefixes that exist today. A route registered under any other prefix -- the
# Admin, import/share and webhook surfaces this issue still lists as residual --
# would match no prefix at all and therefore be asserted by nothing. The
# contract below inverts that default: every registered route must either
# install a shared tenant-scoped boundary, or be named here with a reason that
# is itself mechanically re-checked.

_TENANT_SCOPED_BOUNDARY_CALLS = frozenset(
    {_authorize_request, _authorize_document_policy_management, _inquiry_bundle_trusted_session}
)

# Route touches no tenant-scoped resource and cannot reach the database.
_NO_TENANT_RESOURCE = "no-tenant-resource"
# Control plane route: authorized by ADR-0072 D1=A+B (control-plane bearer or
# tenant.provision capability) rather than by tenant session. D2=A removed the
# former profile gate that refused these outright on SaaS runtimes, because it
# made SaaS bootstrap impossible (SEC-ADMIN-PLANE-01).
_CONTROL_PLANE_AUTHORIZED = "control-plane-authorized"
# Route issues the opaque version, so it cannot also require it as a header.
_TENANT_SESSION_VERSION_SOURCE = "tenant-session-version-source"
# Route carries the expected version in its request body instead of a header.
_BODY_BORNE_EXPECTED_VERSION = "body-borne-expected-version"
# ADR-0074 BFF OAuth flow that runs before any tenant session exists. Unlike
# _NO_TENANT_RESOURCE it may reach the database (it reads IdP rows and persists
# the minted auth session) but must never touch a tenant-scoped resource.
_PRE_SESSION_OAUTH_FLOW = "pre-session-oauth-flow"

_UNGUARDED_ROUTE_EXEMPTIONS: dict[tuple[str, str], str] = {
    ("GET", "/healthz"): _NO_TENANT_RESOURCE,
    ("GET", "/ai/provider-status"): _NO_TENANT_RESOURCE,
    ("POST", "/admin/provision/hil-rs/a2a3-gate:validate"): _NO_TENANT_RESOURCE,
    ("GET", "/session/bootstrap-policy"): _NO_TENANT_RESOURCE,
    # ADR-0074 BFF: OAuth login flow runs before any tenant session exists.
    ("GET", "/session/login"): _NO_TENANT_RESOURCE,
    # The callback persists the minted auth session, so it may reach the DB but
    # still owns no tenant-scoped resource.
    ("GET", "/session/callback"): _PRE_SESSION_OAUTH_FLOW,
    ("POST", "/session/logout"): _NO_TENANT_RESOURCE,
    ("POST", "/admin/provision/users"): _CONTROL_PLANE_AUTHORIZED,
    # ADR-0063/0064: Platform Control Plane — IdP registration is an admin
    # operation, not a tenant-scoped resource.
    ("POST", "/admin/provision/identity-providers"): _CONTROL_PLANE_AUTHORIZED,
    ("POST", "/admin/provision/tenant-identity-providers"): _CONTROL_PLANE_AUTHORIZED,
    ("GET", "/session/context"): _TENANT_SESSION_VERSION_SOURCE,
    ("POST", "/session/active-tenant"): _BODY_BORNE_EXPECTED_VERSION,
}

# FastAPI registers its own schema and documentation routes as plain Starlette
# routes rather than APIRoute instances. Nothing else may hide there: a mounted
# ASGI sub-application would also skip APIRoute inspection, and with it every
# tenant boundary assertion in this module.
_NON_API_ROUTE_PATHS = frozenset({"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"})


def _flattened_dependency_calls(dependant: object) -> set[object]:
    """Collect every dependency callable reachable from a route's dependant."""
    collected: set[object] = set()
    pending = list(getattr(dependant, "dependencies", ()))
    while pending:
        sub_dependant = pending.pop()
        if sub_dependant.call is not None:
            collected.add(sub_dependant.call)
        pending.extend(sub_dependant.dependencies)
    return collected


def _endpoint_called_objects(route: APIRoute) -> set[object]:
    """Objects actually CALLED in the endpoint body, resolved through the
    endpoint's own module globals.

    Deliberately requires ast.Call, not just ast.Name: a bare reference to an
    identifier (an unused local, a debug-log argument, a name mentioned only
    inside a dead branch) proves nothing was invoked. Resolving through
    __globals__ rather than matching the literal spelling also means an
    aliased import (`from x import get_db as _session_factory`) still
    resolves to the same underlying object -- the alias cannot hide a call
    from this check the way a name-string comparison would let it.
    """
    endpoint_tree = ast.parse(textwrap.dedent(inspect.getsource(route.endpoint)))
    called_names = {
        node.func.id
        for node in ast.walk(endpoint_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    endpoint_globals = route.endpoint.__globals__
    return {endpoint_globals[name] for name in called_names if name in endpoint_globals}


def _registered_api_routes() -> dict[tuple[str, str], APIRoute]:
    registered: dict[tuple[str, str], APIRoute] = {}
    for route in main_app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods:
            key = (method, route.path)
            # A silent dict overwrite here would let a second route registered
            # under an already-used (method, path) hide the first from every
            # check below, while Starlette's actual dispatch serves whichever
            # route was registered FIRST -- the opposite of what got audited.
            assert key not in registered, (
                f"duplicate route registration for {key}: "
                f"{registered.get(key)} and {route} both claim it"
            )
            registered[key] = route
    return registered


def _installs_tenant_scoped_boundary(route: APIRoute) -> bool:
    if require_tenant_scoped_api_precondition in _flattened_dependency_calls(route.dependant):
        return True
    return bool(_TENANT_SCOPED_BOUNDARY_CALLS & _endpoint_called_objects(route))


def _exempt_routes(reason: str) -> dict[tuple[str, str], APIRoute]:
    registered = _registered_api_routes()
    return {
        route_key: registered[route_key]
        for route_key, route_reason in _UNGUARDED_ROUTE_EXEMPTIONS.items()
        if route_reason == reason
    }


def test_every_registered_route_is_tenant_guarded_or_explicitly_exempt() -> None:
    registered = _registered_api_routes()
    assert registered

    unguarded = {
        route_key
        for route_key, route in registered.items()
        if not _installs_tenant_scoped_boundary(route)
    }

    # Set equality both ways: a newly registered route that skips the shared
    # boundary fails until it is classified, and a stale exemption fails once
    # the route it excused is guarded or removed.
    assert unguarded == set(_UNGUARDED_ROUTE_EXEMPTIONS)


def test_no_non_api_routes_escape_the_authorization_contract() -> None:
    non_api_routes = [route for route in main_app.routes if not isinstance(route, APIRoute)]

    for route in non_api_routes:
        assert type(route) is StarletteRoute, route
    assert {route.path for route in non_api_routes} == _NON_API_ROUTE_PATHS


def test_no_tenant_resource_exemptions_cannot_reach_the_database() -> None:
    exempt_routes = _exempt_routes(_NO_TENANT_RESOURCE)
    assert exempt_routes

    for route_key, route in exempt_routes.items():
        assert get_db not in _flattened_dependency_calls(route.dependant), route_key
        assert get_db not in _endpoint_called_objects(route), route_key


def test_pre_session_oauth_flow_exemptions_use_the_database_without_a_tenant_boundary() -> None:
    exempt_routes = _exempt_routes(_PRE_SESSION_OAUTH_FLOW)
    assert exempt_routes

    for route_key, route in exempt_routes.items():
        # Distinguishes from _NO_TENANT_RESOURCE: the OAuth callback reads IdP
        # rows and persists the minted auth session, so get_db is expected.
        assert get_db in _flattened_dependency_calls(route.dependant), route_key
        assert not _installs_tenant_scoped_boundary(route), route_key


def test_control_plane_exemption_requires_control_plane_authorization() -> None:
    exempt_routes = _exempt_routes(_CONTROL_PLANE_AUTHORIZED)
    assert exempt_routes

    for route_key, route in exempt_routes.items():
        dependency_calls = _flattened_dependency_calls(route.dependant)
        assert require_control_plane_authorization in dependency_calls, route_key


def test_session_route_exemptions_resolve_the_trusted_session_themselves() -> None:
    version_source_routes = _exempt_routes(_TENANT_SESSION_VERSION_SOURCE)
    body_borne_routes = _exempt_routes(_BODY_BORNE_EXPECTED_VERSION)
    assert version_source_routes
    assert body_borne_routes

    for route_key, route in {**version_source_routes, **body_borne_routes}.items():
        assert resolve_trusted_saas_request_session in _endpoint_called_objects(route), route_key

    for route_key, route in body_borne_routes.items():
        assert require_current_tenant_session_version in _endpoint_called_objects(route), route_key
