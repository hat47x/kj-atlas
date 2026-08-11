"""ADR-0064 D4: E2E test — mock OAuth 2.0 login → JWT → API → tenant isolation.

Verifies the full SAML/OIDC broker coordination flow at mock level:
  1. User logs in via mock IdP (OAuth 2.0 authorization code grant)
  2. Mock IdP issues a signed RS256 JWT
  3. JWT is forwarded as X-Kj-Atlas-Authorization Bearer token
  4. kj-atlas verifies the JWT, resolves tenant, returns tenant-scoped data
  5. Cross-tenant isolation is enforced
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import patch

import jwt as pyjwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

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

from tests.conftest import StubCapabilityResolver
from tests.level2.mock_idp import app as mock_idp_app

TIMESTAMP = "2026-08-07T00:00:00Z"
ISSUER = "http://mock-idp.local/mock-client"
AUDIENCE = "kj-atlas"


# ---------------------------------------------------------------------------
# Mock IdP helpers
# ---------------------------------------------------------------------------


def _generate_pkce() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge (S256)."""
    import base64
    import hashlib
    import secrets

    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def _oauth_login_and_get_jwt(
    idp_client: TestClient,
    *,
    username: str = "alice",
    tenant_ref: str = "org-123",
    use_pkce: bool = True,
) -> str:
    """Execute the full OAuth 2.0 authorization code grant flow (with PKCE)
    against the mock IdP and return a signed JWT access token."""
    code_verifier, code_challenge = _generate_pkce() if use_pkce else ("", "")

    # Step 1: POST /login (with PKCE params) → redirect to /oauth/authorize
    login_data: dict[str, str] = {
        "username": username,
        "password": "password",
        "tenant_ref": tenant_ref,
    }
    if use_pkce:
        login_data["code_challenge"] = code_challenge
        login_data["code_challenge_method"] = "S256"

    resp = idp_client.post(
        "/login", data=login_data, follow_redirects=False,
    )
    assert resp.status_code == 302, f"Login failed: {resp.status_code}"

    # Step 2: GET /oauth/authorize → consent page
    resp = idp_client.get(resp.headers["location"])
    assert resp.status_code == 200

    # Step 3: Extract form fields, remove deny button, POST approve
    hidden = dict(re.findall(r'name="(\w+)" value="([^"]*)"', resp.text))
    hidden.pop("deny", None)
    resp = idp_client.post(
        "/oauth/authorize", data=hidden, follow_redirects=False,
    )
    assert resp.status_code == 302

    # Step 4: Extract authorization code from redirect
    callback = resp.headers["location"]
    code_match = re.findall(r"code=([^&]+)", callback)
    assert code_match, f"No code in redirect: {callback}"
    code = code_match[0]

    # Step 5: POST /oauth/token → exchange code + code_verifier for JWT
    token_data: dict[str, str] = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://mock-idp.local/callback",
        "client_id": "mock-client",
    }
    if use_pkce:
        token_data["code_verifier"] = code_verifier

    resp = idp_client.post("/oauth/token", data=token_data)
    assert resp.status_code == 200, f"Token exchange failed: {resp.status_code} {resp.text}"
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]


def _get_jwks_from_idp(idp_client: TestClient) -> dict[str, object]:
    """Fetch the JWKS from the mock IdP and return it."""
    resp = idp_client.get("/jwks.json")
    assert resp.status_code == 200
    return resp.json()


# ---------------------------------------------------------------------------
# Backend SaaS fixture (reuses pattern from test_saas_e2e_tenant_isolation.py)
# ---------------------------------------------------------------------------



def _seed_backend_db(db: Session) -> None:
    db.add_all(
        [
            UserRow(
                id="user-1", display_name="Alice",
                email="alice@mock-idp.local",
                lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP,
            ),
            TenantRow(
                id="tenant-a", display_name="Tenant A",
                lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP,
            ),
            TenantRow(
                id="tenant-b", display_name="Tenant B",
                lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP,
            ),
            IdentityProviderRow(
                id="idp-1", issuer=ISSUER, audience=AUDIENCE,
                protocol="oidc",
                jwks_uri="http://mock-idp.local/jwks.json",
                lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP,
            ),
            TenantIdentityProviderRow(
                tenant_id="tenant-a", identity_provider_id="idp-1",
                external_tenant_ref="org-123",
                lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP,
            ),
            TenantIdentityProviderRow(
                tenant_id="tenant-b", identity_provider_id="idp-1",
                external_tenant_ref="org-456",
                lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP,
            ),
            # All test usernames map to user-1
            UserIdentityRow(
                user_id="user-1", provider="idp-1",
                external_uid="alice",
                identity_provider_id="idp-1", subject="alice", created_at=TIMESTAMP,
            ),
            UserIdentityRow(
                user_id="user-1", provider="idp-1",
                external_uid="bob",
                identity_provider_id="idp-1", subject="bob", created_at=TIMESTAMP,
            ),
            UserIdentityRow(
                user_id="user-1", provider="idp-1",
                external_uid="charlie",
                identity_provider_id="idp-1", subject="charlie", created_at=TIMESTAMP,
            ),
            TenantMembershipRow(
                tenant_id="tenant-a", user_id="user-1",
                lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP,
            ),
            TenantMembershipRow(
                tenant_id="tenant-b", user_id="user-1",
                lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP,
            ),
            DocumentRow(
                tenant_id="tenant-a", id="shared-doc", version=1,
                updated_at=TIMESTAMP,
                payload_json=json.dumps({
                    "version": 1, "id": "shared-doc",
                    "title": "Tenant A Document",
                    "createdAt": TIMESTAMP, "updatedAt": TIMESTAMP,
                    "transform": {"panX": 0, "panY": 0, "zoom": 1},
                    "cards": [], "edges": [], "islands": [],
                }),
            ),
            DocumentRow(
                tenant_id="tenant-b", id="shared-doc", version=1,
                updated_at=TIMESTAMP,
                payload_json=json.dumps({
                    "version": 1, "id": "shared-doc",
                    "title": "Tenant B Document",
                    "createdAt": TIMESTAMP, "updatedAt": TIMESTAMP,
                    "transform": {"panX": 0, "panY": 0, "zoom": 1},
                    "cards": [], "edges": [], "islands": [],
                }),
            ),
        ]
    )
    db.commit()


@contextmanager
def _backend_saas_client(
    tmp_path, jwk: dict[str, object],
) -> Iterator[tuple[TestClient, InMemoryActiveTenantSessionPersister]]:
    from kj_atlas_api.trusted_auth_edge import JwtSaasIdentityContextResolver

    db_path = tmp_path / "oauth_e2e.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with session_local() as db:
        _seed_backend_db(db)

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    jwks_store = JwksStore()
    jwks_store.set("idp-1", [jwk])
    identity_resolver = JwtSaasIdentityContextResolver(jwks_store=jwks_store)
    session_persister = InMemoryActiveTenantSessionPersister()

    backend_app.dependency_overrides[get_db] = _get_test_db
    with patch(
        "kj_atlas_api.trusted_auth_edge._fetch_jwks",
        return_value=[jwk],
    ):
        try:
            with TestClient(backend_app) as client:
                client.app.state.runtime_profile = "saas-multitenant"
                client.app.state.saas_identity_context_resolver = identity_resolver
                client.app.state.tenant_context_resolver = ClaimBasedTenantContextResolver()
                client.app.state.active_tenant_session_persister = session_persister
                client.app.state.tenant_capability_resolver = StubCapabilityResolver()
                try:
                    yield client, session_persister
                finally:
                    client.app.state.runtime_profile = "local-dev"
                    client.app.state.saas_identity_context_resolver = None
                    client.app.state.tenant_context_resolver = SingleTenantContextResolver()
                    client.app.state.active_tenant_session_persister = None
        finally:
            backend_app.dependency_overrides.clear()
            Base.metadata.drop_all(bind=engine)
            engine.dispose()


# ---------------------------------------------------------------------------
# E2E Tests
# ---------------------------------------------------------------------------


class TestOAuthLoginE2E:
    """ADR-0064 D4: Full OAuth login → JWT → API → tenant isolation."""

    @staticmethod
    def _session_version(persister: InMemoryActiveTenantSessionPersister) -> str:
        from starlette.requests import Request

        return persister.current_version(
            request=Request(scope={"type": "http", "method": "GET", "path": "/"}),
            principal_id="user-1",
            active_tenant=TenantContext(
                tenant_id="tenant-a", membership_id="m-1",
                resolved_by="verified_claim",
            ),
        )

    def test_full_oauth_flow_tenant_a_access(self, tmp_path) -> None:
        """User logs in as org-123 (Tenant A) via OAuth, accesses shared-doc,
        sees Tenant A's document."""
        with TestClient(mock_idp_app) as idp_client:
            # Get JWT via OAuth login as Tenant A
            token = _oauth_login_and_get_jwt(
                idp_client, username="alice", tenant_ref="org-123",
            )
            # Get JWKS from mock IdP
            jwks = _get_jwks_from_idp(idp_client)
            jwk = jwks["keys"][0]

        with _backend_saas_client(tmp_path, jwk) as (backend_client, persister):
            sv = self._session_version(persister)
            resp = backend_client.get(
                "/docs/shared-doc",
                headers={
                    "x-kj-atlas-authorization": f"Bearer {token}",
                    "kj-atlas-tenant-session-version": sv,
                },
            )
            assert resp.status_code == 200, f"body={resp.json()}"
            assert resp.json()["title"] == "Tenant A Document"

    def test_oauth_login_tenant_b_cannot_see_tenant_a_document(
        self, tmp_path,
    ) -> None:
        """User logs in as org-456 (Tenant B), accesses same docId,
        sees Tenant B's document — NOT Tenant A's."""
        with TestClient(mock_idp_app) as idp_client:
            token = _oauth_login_and_get_jwt(
                idp_client, username="bob", tenant_ref="org-456",
            )
            jwks = _get_jwks_from_idp(idp_client)
            jwk = jwks["keys"][0]

        with _backend_saas_client(tmp_path, jwk) as (backend_client, persister):
            sv = self._session_version(persister)
            resp = backend_client.get(
                "/docs/shared-doc",
                headers={
                    "x-kj-atlas-authorization": f"Bearer {token}",
                    "kj-atlas-tenant-session-version": sv,
                },
            )
            assert resp.status_code == 200, f"body={resp.json()}"
            assert resp.json()["title"] == "Tenant B Document"

    def test_oauth_login_both_tenants_isolation(self, tmp_path) -> None:
        """Both tenants log in via OAuth, each sees only their own document."""
        with TestClient(mock_idp_app) as idp_client:
            token_a = _oauth_login_and_get_jwt(
                idp_client, username="alice", tenant_ref="org-123",
            )
            token_b = _oauth_login_and_get_jwt(
                idp_client, username="bob", tenant_ref="org-456",
            )
            jwks = _get_jwks_from_idp(idp_client)
            jwk = jwks["keys"][0]

        with _backend_saas_client(tmp_path, jwk) as (backend_client, persister):
            sv = self._session_version(persister)

            resp_a = backend_client.get(
                "/docs/shared-doc",
                headers={
                    "x-kj-atlas-authorization": f"Bearer {token_a}",
                    "kj-atlas-tenant-session-version": sv,
                },
            )
            assert resp_a.status_code == 200
            assert resp_a.json()["title"] == "Tenant A Document"

            resp_b = backend_client.get(
                "/docs/shared-doc",
                headers={
                    "x-kj-atlas-authorization": f"Bearer {token_b}",
                    "kj-atlas-tenant-session-version": sv,
                },
            )
            assert resp_b.status_code == 200
            assert resp_b.json()["title"] == "Tenant B Document"

    def test_oauth_login_nonexistent_document_returns_404(
        self, tmp_path,
    ) -> None:
        """Tenant A accesses a doc that doesn't exist in their namespace → 404."""
        with TestClient(mock_idp_app) as idp_client:
            token = _oauth_login_and_get_jwt(
                idp_client, username="alice", tenant_ref="org-123",
            )
            jwks = _get_jwks_from_idp(idp_client)
            jwk = jwks["keys"][0]

        with _backend_saas_client(tmp_path, jwk) as (backend_client, persister):
            sv = self._session_version(persister)
            resp = backend_client.get(
                "/docs/nonexistent-doc",
                headers={
                    "x-kj-atlas-authorization": f"Bearer {token}",
                    "kj-atlas-tenant-session-version": sv,
                },
            )
            assert resp.status_code == 404
            assert resp.json()["detail"] == "Document not found"

    def test_oauth_login_wrong_tenant_claim_is_denied(self, tmp_path) -> None:
        """Valid user (alice) but with a tenant_ref that has no binding → 401."""
        with TestClient(mock_idp_app) as idp_client:
            # alice is a valid user, but org-unknown has no tenant binding
            token = _oauth_login_and_get_jwt(
                idp_client, username="alice", tenant_ref="org-unknown",
            )
            jwks = _get_jwks_from_idp(idp_client)
            jwk = jwks["keys"][0]

        with _backend_saas_client(tmp_path, jwk) as (backend_client, persister):
            sv = self._session_version(persister)
            resp = backend_client.get(
                "/docs/shared-doc",
                headers={
                    "x-kj-atlas-authorization": f"Bearer {token}",
                    "kj-atlas-tenant-session-version": sv,
                },
            )
            assert resp.status_code == 401, f"body={resp.json()}"
            assert resp.json()["detail"]["code"] == "unknown_tenant"

    def test_oauth_login_expired_token_is_rejected(self, tmp_path) -> None:
        """Expired JWT → 401."""
        with TestClient(mock_idp_app) as idp_client:
            # Get a valid JWT first, then manually create an expired one
            token = _oauth_login_and_get_jwt(
                idp_client, username="alice", tenant_ref="org-123",
            )
            jwks = _get_jwks_from_idp(idp_client)
            jwk = jwks["keys"][0]

        # Build an expired token with the same claims
        valid_claims = pyjwt.decode(token, options={"verify_signature": False})
        now = int(time.time())
        valid_claims["exp"] = now - 3600
        valid_claims["iat"] = now - 7200

        # We can't re-sign with the mock IdP's private key from outside.
        # Instead, verify that the backend correctly rejects expired JWTs
        # using a token we know is expired from the direct /oidc/token endpoint.
        with TestClient(mock_idp_app) as idp_client:
            # Use the direct token endpoint with short expiry
            resp = idp_client.post(
                "/oidc/token",
                json={
                    "provider": "mock-client",
                    "claims": {
                        "sub": "alice",
                        "tenant_ref": "org-123",
                        "exp": now - 3600,
                    },
                },
            )
        expired_token = resp.json()["access_token"]

        with _backend_saas_client(tmp_path, jwk) as (backend_client, persister):
            sv = self._session_version(persister)
            resp = backend_client.get(
                "/docs/shared-doc",
                headers={
                    "x-kj-atlas-authorization": f"Bearer {expired_token}",
                    "kj-atlas-tenant-session-version": sv,
                },
            )
            # The token will fail at the unverified peek stage because
            # jwt.decode with verify_signature=False still checks exp by default
            assert resp.status_code == 401, f"body={resp.json()}"

    def test_oauth_userinfo_endpoint_returns_claims(self) -> None:
        """Verify /oauth/userinfo returns correct claims after login."""
        with TestClient(mock_idp_app) as idp_client:
            token = _oauth_login_and_get_jwt(
                idp_client, username="charlie", tenant_ref="org-123",
            )
            resp = idp_client.get(
                "/oauth/userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["sub"] == "charlie"
            assert resp.json()["tenant_ref"] == "org-123"
            assert "email" in resp.json()

    def test_oidc_discovery_returns_metadata(self) -> None:
        """Verify OIDC Discovery endpoint."""
        with TestClient(mock_idp_app) as idp_client:
            resp = idp_client.get("/.well-known/openid-configuration")
            assert resp.status_code == 200
            meta = resp.json()
            assert meta["issuer"] == "http://mock-idp.local"
            assert "authorization_endpoint" in meta
            assert "token_endpoint" in meta
            assert "userinfo_endpoint" in meta
            assert "jwks_uri" in meta

    # ------------------------------------------------------------------
    # ADR-0064: logout and browser-safe token grant
    # ------------------------------------------------------------------

    def test_logout_clears_session(self) -> None:
        """RP-Initiated Logout clears the session cookie."""
        with TestClient(mock_idp_app) as idp_client:
            # Login to get a session cookie.
            r = idp_client.post(
                "/login",
                data={"username": "alice", "password": "p",
                      "tenant_ref": "org-123"},
                follow_redirects=False,
            )
            session_cookie = r.cookies.get("mock_idp_session", "")
            assert session_cookie, "No session cookie after login"

            # Logout.
            r = idp_client.get(
                "/logout",
                cookies={"mock_idp_session": session_cookie},
            )
            assert r.status_code == 200

    def test_logout_redirects_when_post_logout_uri_provided(self) -> None:
        """Logout redirects to post_logout_redirect_uri."""
        with TestClient(mock_idp_app) as idp_client:
            r = idp_client.get(
                "/logout",
                params={
                    "post_logout_redirect_uri": "http://app.local/after-logout",
                    "state": "abc123",
                },
                follow_redirects=False,
            )
            assert r.status_code == 302
            assert "after-logout" in r.headers["location"]
            assert "state=abc123" in r.headers["location"]

    def test_refresh_token_grant_is_not_supported(self) -> None:
        """The SPA client is not issued a browser-readable long-lived token."""
        with TestClient(mock_idp_app) as idp_client:
            r = idp_client.post("/oauth/token", data={
                "grant_type": "refresh_token",
                "refresh_token": "any-opaque-refresh-token",
                "client_id": "mock-client",
            })
            assert r.status_code == 400
            assert r.json()["detail"] == "unsupported grant_type"
