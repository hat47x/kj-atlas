"""SEC-ADMIN-PLANE-01 / ADR-0072: control-plane authorization and fail-fast.

Covers the negative matrix the issue asks for (AC-2 / AC-7) and the D3=A
production fail-fast (AC-1). The load-bearing assertion is that the
business-plane credential does not reach the control plane: before this change,
`KJ_ATLAS_API_KEY` was the only protection on
`POST /admin/provision/identity-providers`, which registers a trusted JWT issuer
and its JWKS URI -- so a document-API caller could register their own issuer and
then authenticate as any user in any tenant.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.control_plane_auth import (
    ADMIN_API_KEY_HEADER,
    TENANT_PROVISION_CAPABILITY,
)
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base, TenantRow
from kj_atlas_api.session_context import KNOWN_EFFECTIVE_CAPABILITIES
from kj_atlas_api.settings import Settings, settings

TIMESTAMP = "2026-08-13T00:00:00Z"

_ADMIN_KEY = "control-plane-bootstrap-key"
_BUSINESS_KEY = "business-plane-key"

#: One representative route per provisioning surface guarded by ADR-0072 D1.
_CONTROL_PLANE_ROUTES = (
    ("/admin/provision/users", {"provider": "oidc", "externalUid": "u-1"}),
    (
        "/admin/provision/identity-providers",
        {
            "issuer": "https://idp.example.com",
            "audience": "kj-atlas",
            "jwksUri": "https://idp.example.com/jwks",
        },
    ),
    (
        "/admin/provision/tenant-identity-providers",
        {
            "tenantId": "tenant-a",
            "identityProviderId": "idp-1",
            "externalTenantRef": "ext-a",
        },
    ),
    (
        "/admin/provision/hil-rs/a2a3-gate:validate",
        {
            "freezeContractId": "HIL-RS-02-A1-CONTRACT-FREEZE-v1",
            "schemaVersion": "1.0.0",
            "overridePolicy": "human_dual_control_only",
            "contractLinkLocked": True,
            "sharedResourceFreeze": True,
            "a1Status": "Done",
            "pendingDecisionQueueCount": 0,
            "hasUndefinedContractChangeRequest": False,
            "hasSafeModeRegressionRequest": False,
            "hasShareExportLeakageRelaxationRequest": False,
        },
    ),
)


@contextmanager
def _client(tmp_path, *, profile: str | None = None) -> Iterator[TestClient]:
    """A client over its own migrated SQLite file.

    `profile` overrides `app.state.runtime_profile`. It must be applied *after*
    the client starts: `main.py`'s lifespan assigns that attribute from settings
    on startup, so setting it beforehand is silently discarded (two tests here
    initially passed a profile that never took effect and asserted against the
    default `local-dev` behaviour instead).
    """
    engine = create_engine(f"sqlite:///{tmp_path / 'control_plane.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with session_local() as db:
        for tenant_id, name in (("local-default", "Local Default"), ("tenant-a", "Tenant A")):
            db.add(
                TenantRow(
                    id=tenant_id,
                    display_name=name,
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                )
            )
        db.commit()

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            previous_profile = getattr(app.state, "runtime_profile", None)
            if profile is not None:
                app.state.runtime_profile = profile
            try:
                yield client
            finally:
                if profile is not None:
                    app.state.runtime_profile = previous_profile
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


# ---------------------------------------------------------------------------
# AC-2 / AC-7: the business plane must not reach the control plane
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("path", "payload"), _CONTROL_PLANE_ROUTES)
def test_business_plane_key_cannot_reach_control_plane(tmp_path, monkeypatch, path, payload) -> None:
    """The exact escalation SEC-ADMIN-PLANE-01 described must be closed."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    with _client(tmp_path) as client:
        resp = client.post(path, json=payload, headers={"x-api-key": _BUSINESS_KEY})
    assert resp.status_code == 401, resp.text
    assert resp.json()["detail"]["code"] == "control_plane_unauthorized"


@pytest.mark.parametrize(("path", "payload"), _CONTROL_PLANE_ROUTES)
def test_missing_credential_is_rejected(tmp_path, monkeypatch, path, payload) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", None)
    with _client(tmp_path) as client:
        resp = client.post(path, json=payload)
    assert resp.status_code == 401, resp.text


@pytest.mark.parametrize(("path", "payload"), _CONTROL_PLANE_ROUTES)
def test_wrong_admin_credential_is_rejected(tmp_path, monkeypatch, path, payload) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", None)
    with _client(tmp_path) as client:
        resp = client.post(path, json=payload, headers={ADMIN_API_KEY_HEADER: "wrong"})
    assert resp.status_code == 401, resp.text


def test_admin_credential_reaches_the_control_plane(tmp_path, monkeypatch) -> None:
    """Stage A must actually work -- this is the bootstrap path."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", None)
    path, payload = _CONTROL_PLANE_ROUTES[1]
    with _client(tmp_path) as client:
        resp = client.post(path, json=payload, headers={ADMIN_API_KEY_HEADER: _ADMIN_KEY})
    assert resp.status_code < 400, resp.text


@pytest.mark.parametrize(("path", "payload"), _CONTROL_PLANE_ROUTES)
def test_admin_credential_alone_reaches_control_plane_when_business_key_also_set(tmp_path, monkeypatch, path, payload) -> None:
    """SEC-ADMIN-PLANE-02 (D-a): when BOTH keys are configured, the control-plane
    credential ALONE must not be blocked at the auth layer for /admin/provision/*.
    The business-plane key must not be a prerequisite for the control plane —
    re-coupling them would defeat ADR-0072's separation. Fixed by the /admin/*
    bypass in require_api_key.

    The claim is specifically about AUTH: any status other than 401/403 (e.g. a
    201 success, or a 404/422 business-logic rejection like an unknown
    identityProviderId) proves the request passed both the middleware and
    require_control_plane_authorization and reached the route handler."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    with _client(tmp_path) as client:
        resp = client.post(path, json=payload, headers={ADMIN_API_KEY_HEADER: _ADMIN_KEY})
    assert resp.status_code not in (401, 403), resp.text


def test_rejection_does_not_reveal_whether_a_key_is_configured(tmp_path, monkeypatch) -> None:
    """The 401 body must be identical for wrong-key and unconfigured-key."""
    path, payload = _CONTROL_PLANE_ROUTES[1]

    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    with _client(tmp_path) as client:
        wrong = client.post(path, json=payload, headers={ADMIN_API_KEY_HEADER: "wrong"})

    monkeypatch.setattr(settings, "admin_api_key", None)
    with _client(tmp_path, profile="enterprise-production") as client:
        unconfigured = client.post(path, json=payload, headers={ADMIN_API_KEY_HEADER: "wrong"})

    assert wrong.status_code == unconfigured.status_code == 401
    assert wrong.json() == unconfigured.json()
    assert _ADMIN_KEY not in wrong.text


def test_admin_credential_is_never_echoed(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    path, payload = _CONTROL_PLANE_ROUTES[1]
    with _client(tmp_path) as client:
        resp = client.post(path, json=payload, headers={ADMIN_API_KEY_HEADER: "wrong-but-secret"})
    assert "wrong-but-secret" not in resp.text
    assert _ADMIN_KEY not in resp.text


# ---------------------------------------------------------------------------
# D2=A: the surface is reachable on SaaS (it used to 404 there)
# ---------------------------------------------------------------------------


def test_control_plane_is_reachable_on_saas_profile(tmp_path, monkeypatch) -> None:
    """SEC-ADMIN-PLANE-01 課題2: SaaS could not bootstrap at all.

    The former guard returned 404 for any non-single-tenant profile while the
    startup warning instructed the operator to call that same endpoint.
    """
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    path, payload = _CONTROL_PLANE_ROUTES[1]
    with _client(tmp_path, profile="saas-multitenant") as client:
        resp = client.post(path, json=payload, headers={ADMIN_API_KEY_HEADER: _ADMIN_KEY})
    assert resp.status_code != 404, resp.text
    assert resp.status_code < 400, resp.text


def test_unknown_runtime_profile_does_not_fall_through_to_open(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", None)
    path, payload = _CONTROL_PLANE_ROUTES[1]
    with _client(tmp_path, profile="not-a-profile") as client:
        resp = client.post(path, json=payload)
    assert resp.status_code == 503, resp.text
    assert resp.json()["detail"]["code"] == "runtime_policy_unavailable"


def test_local_dev_stays_open_when_unconfigured(tmp_path, monkeypatch) -> None:
    """Zero-configuration local use must not regress."""
    monkeypatch.setattr(settings, "admin_api_key", None)
    path, payload = _CONTROL_PLANE_ROUTES[1]
    with _client(tmp_path, profile="local-dev") as client:
        resp = client.post(path, json=payload)
    assert resp.status_code < 400, resp.text


def test_provision_capability_is_a_known_capability() -> None:
    assert TENANT_PROVISION_CAPABILITY in KNOWN_EFFECTIVE_CAPABILITIES


# ---------------------------------------------------------------------------
# AC-1 / D3=A: production profiles fail fast without authentication
# ---------------------------------------------------------------------------


def _settings_env(profile: str, **overrides: str) -> dict[str, str]:
    env = {
        "KJ_ATLAS_RUNTIME_PROFILE": profile,
        "KJ_ATLAS_DATABASE_URL": "sqlite:///./kj_atlas.db",
        "KJ_ATLAS_LLM_PROVIDER": "none",
    }
    env.update(overrides)
    return env


@pytest.mark.parametrize("profile", ["enterprise-production", "saas-multitenant"])
def test_production_profile_without_control_plane_key_fails_fast(monkeypatch, profile) -> None:
    for key, value in _settings_env(profile).items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("KJ_ATLAS_ADMIN_API_KEY", raising=False)
    monkeypatch.setenv("KJ_ATLAS_API_KEY", _BUSINESS_KEY)

    with pytest.raises(ValueError, match="KJ_ATLAS_ADMIN_API_KEY"):
        Settings()


def test_enterprise_production_without_business_key_fails_fast(monkeypatch) -> None:
    """The original P0: this profile started fully unauthenticated at defaults."""
    for key, value in _settings_env("enterprise-production").items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("KJ_ATLAS_ADMIN_API_KEY", _ADMIN_KEY)
    monkeypatch.delenv("KJ_ATLAS_API_KEY", raising=False)

    with pytest.raises(ValueError, match="KJ_ATLAS_API_KEY"):
        Settings()


def test_production_profile_with_both_keys_constructs(monkeypatch) -> None:
    for key, value in _settings_env("enterprise-production").items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("KJ_ATLAS_ADMIN_API_KEY", _ADMIN_KEY)
    monkeypatch.setenv("KJ_ATLAS_API_KEY", _BUSINESS_KEY)

    built = Settings()
    assert built.admin_api_key == _ADMIN_KEY
    assert built.api_key == _BUSINESS_KEY


@pytest.mark.parametrize("profile", ["local-dev", "evaluation"])
def test_non_production_profiles_still_construct_without_any_key(monkeypatch, profile) -> None:
    for key, value in _settings_env(profile).items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("KJ_ATLAS_ADMIN_API_KEY", raising=False)
    monkeypatch.delenv("KJ_ATLAS_API_KEY", raising=False)

    built = Settings()
    assert built.admin_api_key is None


def test_control_plane_key_must_be_canonical(monkeypatch) -> None:
    for key, value in _settings_env("local-dev").items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("KJ_ATLAS_ADMIN_API_KEY", "has whitespace")

    with pytest.raises(ValueError, match="canonical bearer"):
        Settings()


def test_startup_warning_names_the_control_plane_credential() -> None:
    """AC-4: the warning previously named an endpoint that 404'd on this profile."""
    source = (
        os.path.join(os.path.dirname(__file__), "..", "src", "kj_atlas_api", "trusted_saas_runtime.py")
    )
    with open(source, encoding="utf-8") as handle:
        text = handle.read()
    assert "X-Admin-Api-Key" in text
    assert "KJ_ATLAS_ADMIN_API_KEY" in text
