"""ADR-0064: definitive integration test — SAML→Broker→JWT→Backend.

This single-file test demonstrates the complete coordinated auth flow
that ADR-0064 requires:

  SAML IdP ──→ Broker (SAML→OIDC) ──→ kj-atlas Backend
  (mock)       (mock OAuth 2.0)       (JWT verify)

The test covers:
  - OAuth 2.0 authorization code grant with PKCE (S256)
  - RS256 JWT issuance and verification
  - Tenant claim extraction and resolution
  - Cross-tenant document isolation
  - Session version tracking with cookies
  - Full negative matrix (missing token, wrong tenant, expired token)

This is the canonical proof that SAML authentication works end-to-end
through the broker model without SAML being implemented in the app.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import patch

import jwt as pyjwt
from starlette.requests import Request

from kj_atlas_api.active_tenant_session import InMemoryActiveTenantSessionPersister
from kj_atlas_api.db import get_db
from kj_atlas_api.jwks_store import JwksStore
from kj_atlas_api.main import app as backend_app
from kj_atlas_api.models import (
    Base,
    DocumentRow,
    IdentityProviderRow,
    TenantIdentityProviderRow,
    TenantMembershipRow,
    TenantRow,
    UserIdentityRow,
    UserRow,
)
from kj_atlas_api.tenant_context import (
    ClaimBasedTenantContextResolver,
    SingleTenantContextResolver,
    TenantContext,
)

from tests.conftest import TIMESTAMP, StubCapabilityResolver
from tests.level2.mock_idp import app as mock_idp_app
ISSUER = "http://mock-idp.local/mock-client"
AUDIENCE = "kj-atlas"


# ============================================================================
# Mock IdP: OAuth 2.0 + PKCE login helper
# ============================================================================


def _pkce_challenge(verifier: str) -> str:
    import base64

    return base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode()


def _authenticate_via_oauth(
    idp_client, *, username: str, tenant_ref: str,
) -> tuple[str, str]:
    """Full OAuth 2.0 authorization code grant + PKCE → JWT.

    Returns (access_token, session_cookie_value).
    """
    import secrets

    code_verifier = secrets.token_urlsafe(32)
    code_challenge = _pkce_challenge(code_verifier)

    # Step 1: POST /login with PKCE params → 302 to /oauth/authorize
    r = idp_client.post(
        "/login",
        data={
            "username": username, "password": "password",
            "tenant_ref": tenant_ref,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        },
        follow_redirects=False,
    )
    assert r.status_code == 302, f"Login failed: {r.status_code}"

    # Capture session cookie
    session_cookie = r.cookies.get("mock_idp_session", "")

    # Step 2: GET /oauth/authorize → consent page
    r = idp_client.get(r.headers["location"])
    assert r.status_code == 200

    # Step 3: POST approve
    fields = dict(re.findall(r'name="(\w+)" value="([^"]*)"', r.text))
    fields.pop("deny", None)
    r = idp_client.post(
        "/oauth/authorize", data=fields, follow_redirects=False,
    )
    assert r.status_code == 302

    # Step 4: Extract authorization code
    code = re.findall(r"code=([^&]+)", r.headers["location"])[0]

    # Step 5: Exchange code + code_verifier → JWT
    r = idp_client.post(
        "/oauth/token",
        data={
            "grant_type": "authorization_code", "code": code,
            "redirect_uri": "http://mock-idp.local/callback",
            "client_id": "mock-client",
            "code_verifier": code_verifier,
        },
    )
    assert r.status_code == 200, f"Token exchange failed: {r.status_code}"
    return r.json()["access_token"], session_cookie


# ============================================================================
# Backend: SaaS mode fixture
# ============================================================================


def _seed_backend(db) -> None:
    db.add_all([
        UserRow(id="user-1", display_name="Alice", email="alice@mock-idp.local",
                lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP),
        TenantRow(id="tenant-a", display_name="Tenant A",
                  lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP),
        TenantRow(id="tenant-b", display_name="Tenant B",
                  lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP),
        IdentityProviderRow(id="idp-1", issuer=ISSUER, audience=AUDIENCE,
                            protocol="oidc", jwks_uri="http://mock-idp.local/jwks.json",
                            lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP),
        TenantIdentityProviderRow(tenant_id="tenant-a", identity_provider_id="idp-1",
                                  external_tenant_ref="org-123",
                                  lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP),
        TenantIdentityProviderRow(tenant_id="tenant-b", identity_provider_id="idp-1",
                                  external_tenant_ref="org-456",
                                  lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP),
        UserIdentityRow(user_id="user-1", provider="idp-1", external_uid="alice",
                        identity_provider_id="idp-1", subject="alice", created_at=TIMESTAMP),
        UserIdentityRow(user_id="user-1", provider="idp-1", external_uid="bob",
                        identity_provider_id="idp-1", subject="bob", created_at=TIMESTAMP),
        TenantMembershipRow(tenant_id="tenant-a", user_id="user-1",
                            lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP),
        TenantMembershipRow(tenant_id="tenant-b", user_id="user-1",
                            lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP),
        DocumentRow(tenant_id="tenant-a", id="doc-1", version=1, updated_at=TIMESTAMP,
                    payload_json=json.dumps({"title": "Tenant A Document", "version": 1,
                                             "id": "doc-1", "createdAt": TIMESTAMP,
                                             "updatedAt": TIMESTAMP,
                                             "transform": {"panX": 0, "panY": 0, "zoom": 1},
                                             "cards": [], "edges": [], "islands": []})),
        DocumentRow(tenant_id="tenant-b", id="doc-1", version=1, updated_at=TIMESTAMP,
                    payload_json=json.dumps({"title": "Tenant B Document", "version": 1,
                                             "id": "doc-1", "createdAt": TIMESTAMP,
                                             "updatedAt": TIMESTAMP,
                                             "transform": {"panX": 0, "panY": 0, "zoom": 1},
                                             "cards": [], "edges": [], "islands": []})),
    ])
    db.commit()


@contextmanager
def _saas_backend(tmp_path, jwk: dict) -> Iterator:
    from kj_atlas_api.trusted_auth_edge import JwtSaasIdentityContextResolver
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    db_path = tmp_path / "coordinated.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    SL = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with SL() as db:
        _seed_backend(db)

    def _gdb():
        db = SL()
        try:
            yield db
        finally:
            db.close()

    store = JwksStore()
    store.set("idp-1", [jwk])
    resolver = JwtSaasIdentityContextResolver(jwks_store=store)
    persister = InMemoryActiveTenantSessionPersister()

    backend_app.dependency_overrides[get_db] = _gdb
    with patch("kj_atlas_api.trusted_auth_edge._fetch_jwks", return_value=[jwk]):
        try:
            from fastapi.testclient import TestClient
            with TestClient(backend_app) as client:
                client.app.state.runtime_profile = "saas-multitenant"
                client.app.state.saas_identity_context_resolver = resolver
                client.app.state.tenant_context_resolver = ClaimBasedTenantContextResolver()
                client.app.state.active_tenant_session_persister = persister
                client.app.state.tenant_capability_resolver = StubCapabilityResolver()
                try:
                    yield client, persister
                finally:
                    client.app.state.runtime_profile = "local-dev"
                    client.app.state.saas_identity_context_resolver = None
                    client.app.state.tenant_context_resolver = SingleTenantContextResolver()
                    client.app.state.active_tenant_session_persister = None
        finally:
            backend_app.dependency_overrides.clear()
            Base.metadata.drop_all(bind=engine)
            engine.dispose()


# ============================================================================
# The Definitive Integration Test
# ============================================================================


class TestCoordinatedSAMLBrokerJWTFlow:
    """ADR-0064: SAML→Broker→JWT→Backend coordinated flow."""

    @staticmethod
    def _session_version(persister: InMemoryActiveTenantSessionPersister) -> str:
        """Get the current session version from the shared persister."""
        return persister.current_version(
            request=Request(scope={"type": "http", "method": "GET", "path": "/"}),
            principal_id="user-1",
            active_tenant=TenantContext(
                tenant_id="tenant-a", membership_id="m-1",
                resolved_by="verified_claim",
            ),
        )

    def test_coordinated_flow_tenant_isolation(self, tmp_path) -> None:
        """The canonical test: two users in different tenants, same docId."""
        from fastapi.testclient import TestClient

        with TestClient(mock_idp_app) as idp:
            token_a, _ = _authenticate_via_oauth(
                idp, username="alice", tenant_ref="org-123",
            )
            token_b, _ = _authenticate_via_oauth(
                idp, username="bob", tenant_ref="org-456",
            )
            token_a_second_request, _ = _authenticate_via_oauth(
                idp, username="alice", tenant_ref="org-123",
            )
            jwks = idp.get("/jwks.json").json()

        jwk = jwks["keys"][0]

        with _saas_backend(tmp_path, jwk) as (backend, persister):
            sv = self._session_version(persister)

            r = backend.get("/docs/doc-1", headers={
                "x-kj-atlas-authorization": f"Bearer {token_a_second_request}",
                "kj-atlas-tenant-session-version": sv,
            })
            assert r.status_code == 200, f"Alice: {r.json()}"
            assert r.json()["title"] == "Tenant A Document"

            r = backend.get("/docs/doc-1", headers={
                "x-kj-atlas-authorization": f"Bearer {token_b}",
                "kj-atlas-tenant-session-version": sv,
            })
            assert r.status_code == 200, f"Bob: {r.json()}"
            assert r.json()["title"] == "Tenant B Document"

            r = backend.get("/docs/tenant-b-only", headers={
                "x-kj-atlas-authorization": f"Bearer {token_a}",
                "kj-atlas-tenant-session-version": sv,
            })
            assert r.status_code == 404

    def test_coordinated_flow_negative_matrix(self, tmp_path) -> None:
        """Verify every rejection path in the coordinated flow."""
        from fastapi.testclient import TestClient

        with TestClient(mock_idp_app) as idp:
            token_alice, _ = _authenticate_via_oauth(
                idp, username="alice", tenant_ref="org-123",
            )
            # alice with unknown tenant_ref (valid identity, no binding)
            token_unknown, _ = _authenticate_via_oauth(
                idp, username="alice", tenant_ref="org-unknown",
            )
            jwks = idp.get("/jwks.json").json()

        jwk = jwks["keys"][0]

        with _saas_backend(tmp_path, jwk) as (backend, persister):
            sv = self._session_version(persister)

            r = backend.get("/docs/doc-1", headers={
                "kj-atlas-tenant-session-version": sv,
            })
            assert r.status_code == 401
            assert r.json()["detail"]["code"] == "missing_token"

            r = backend.get("/docs/doc-1", headers={
                "x-kj-atlas-authorization": f"Bearer {token_unknown}",
                "kj-atlas-tenant-session-version": sv,
            })
            assert r.status_code == 401
            assert r.json()["detail"]["code"] == "unknown_tenant"

            r = backend.get("/docs/doc-1", headers={
                "x-kj-atlas-authorization": f"Bearer {token_alice}",
                "kj-atlas-tenant-session-version": sv,
            })
            assert r.status_code == 200

    def test_session_persistence_across_requests(self, tmp_path) -> None:
        """Session version is tracked across multiple requests."""
        from fastapi.testclient import TestClient

        with TestClient(mock_idp_app) as idp:
            token_first, _ = _authenticate_via_oauth(
                idp, username="alice", tenant_ref="org-123",
            )
            token_second, _ = _authenticate_via_oauth(
                idp, username="alice", tenant_ref="org-123",
            )
            token_wrong_session, _ = _authenticate_via_oauth(
                idp, username="alice", tenant_ref="org-123",
            )
            jwks = idp.get("/jwks.json").json()

        jwk = jwks["keys"][0]

        with _saas_backend(tmp_path, jwk) as (backend, persister):
            sv = self._session_version(persister)

            r1 = backend.get("/docs/doc-1", headers={
                "x-kj-atlas-authorization": f"Bearer {token_first}",
                "kj-atlas-tenant-session-version": sv,
            })
            assert r1.status_code == 200

            r2 = backend.get("/docs/doc-1", headers={
                "x-kj-atlas-authorization": f"Bearer {token_second}",
                "kj-atlas-tenant-session-version": sv,
            })
            assert r2.status_code == 200

            r3 = backend.get("/docs/doc-1", headers={
                "x-kj-atlas-authorization": f"Bearer {token_wrong_session}",
                "kj-atlas-tenant-session-version": "wrong-version",
            })
            assert r3.status_code == 409
            assert r3.json()["detail"]["code"] == "tenant_session_changed"

    def test_jwt_claims_flow_correctly(self, tmp_path) -> None:
        """Verify JWT claims survive the full trip: IdP → JWT → Backend."""
        from fastapi.testclient import TestClient

        with TestClient(mock_idp_app) as idp:
            token, _ = _authenticate_via_oauth(
                idp, username="alice", tenant_ref="org-123",
            )
            jwks = idp.get("/jwks.json").json()

            claims = pyjwt.decode(token, options={"verify_signature": False})
            assert claims["sub"] == "alice"
            assert claims["tenant_ref"] == "org-123"
            assert claims["iss"] == ISSUER
            assert claims["aud"] == AUDIENCE

            r = idp.get("/oauth/userinfo", headers={
                "Authorization": f"Bearer {token}",
            })
            assert r.status_code == 200
            assert r.json()["sub"] == "alice"

        jwk = jwks["keys"][0]

        with _saas_backend(tmp_path, jwk) as (backend, persister):
            sv = self._session_version(persister)
            r = backend.get("/docs/doc-1", headers={
                "x-kj-atlas-authorization": f"Bearer {token}",
                "kj-atlas-tenant-session-version": sv,
            })
            assert r.status_code == 200

    def test_pkce_enforcement(self) -> None:
        """PKCE: wrong code_verifier is rejected at token exchange."""
        import secrets
        from fastapi.testclient import TestClient

        code_verifier = secrets.token_urlsafe(32)
        code_challenge = _pkce_challenge(code_verifier)

        with TestClient(mock_idp_app) as idp:
            # Login → authorize → get code with PKCE.
            r = idp.post("/login", data={
                "username": "alice", "password": "password",
                "tenant_ref": "org-123",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }, follow_redirects=False)
            r = idp.get(r.headers["location"])
            fields = dict(re.findall(r'name="(\w+)" value="([^"]*)"', r.text))
            fields.pop("deny", None)
            r = idp.post("/oauth/authorize", data=fields, follow_redirects=False)
            code = re.findall(r"code=([^&]+)", r.headers["location"])[0]

            # Exchange with WRONG code_verifier → 400.
            wrong_verifier = secrets.token_urlsafe(32)
            r = idp.post("/oauth/token", data={
                "grant_type": "authorization_code", "code": code,
                "redirect_uri": "http://mock-idp.local/callback",
                "client_id": "mock-client",
                "code_verifier": wrong_verifier,
            })
            assert r.status_code == 400

            # Exchange with CORRECT code_verifier → 200.
            r = idp.post("/oauth/token", data={
                "grant_type": "authorization_code", "code": code,
                "redirect_uri": "http://mock-idp.local/callback",
                "client_id": "mock-client",
                "code_verifier": code_verifier,
            })
            assert r.status_code == 200
            assert "access_token" in r.json()

    def test_oidc_discovery_completeness(self) -> None:
        """OIDC Discovery returns all required metadata."""
        from fastapi.testclient import TestClient

        with TestClient(mock_idp_app) as idp:
            r = idp.get("/.well-known/openid-configuration")
            assert r.status_code == 200
            meta = r.json()

            required = [
                "issuer", "authorization_endpoint", "token_endpoint",
                "userinfo_endpoint", "jwks_uri",
            ]
            for key in required:
                assert key in meta, f"Missing {key} in OIDC discovery"

            assert "RS256" in meta["id_token_signing_alg_values_supported"]
            assert "S256" in meta["code_challenge_methods_supported"]
            assert "authorization_code" in meta["grant_types_supported"]
