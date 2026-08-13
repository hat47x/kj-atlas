"""ADR-0074 / SAAS-TENANT-SESSION-BINDING-01: mock IdP harness prep.

Covers the three gaps recorded against tests/level2/mock_idp.py before it
can exercise the ADR-0074 "Acceptance Gate回答案③" (per-broker logout
connection scope):

  1. Issued JWTs now carry a `sid` claim, stable across every token minted
     within the same mock IdP login session.
  2. /oauth/token now supports confidential-client verification, opt-in per
     client_id via /admin/register-client-secret -- unregistered client_ids
     (including "mock-client", every existing caller) are unaffected.
  3. /admin/trigger-backchannel-logout builds a spec-shaped OIDC Logout
     Token (Back-Channel Logout 1.0) and best-effort delivers it to a URI
     registered via /admin/register-backchannel-logout-uri.
"""

from __future__ import annotations

import json
import re
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from tests.level2 import mock_idp
from tests.level2.mock_idp import app as mock_idp_app


def _generate_pkce() -> tuple[str, str]:
    import base64
    import hashlib
    import secrets

    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def _login_and_get_code(idp_client: TestClient, *, username: str = "alice") -> str:
    """Drive /login -> /oauth/authorize (approve) and return the auth code.
    Leaves the mock_idp_session cookie set on idp_client for the caller to
    reuse across further authorize calls in the same "browser session"."""
    resp = idp_client.post(
        "/login",
        data={"username": username, "password": "password", "tenant_ref": "org-123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    return _authorize_from_redirect(idp_client, resp.headers["location"])


def _reauthorize_with_existing_session(idp_client: TestClient) -> str:
    """GET /login with an existing mock_idp_session cookie already set:
    recognized-session redirect straight to /oauth/authorize (mirrors a
    second app in the same browser session requesting its own token,
    without re-submitting credentials)."""
    resp = idp_client.get("/login", follow_redirects=False)
    assert resp.status_code == 302
    return _authorize_from_redirect(idp_client, resp.headers["location"])


def _authorize_from_redirect(idp_client: TestClient, authorize_url: str) -> str:
    resp = idp_client.get(authorize_url)
    assert resp.status_code == 200
    hidden = dict(re.findall(r'name="(\w+)" value="([^"]*)"', resp.text))
    hidden.pop("deny", None)
    resp = idp_client.post("/oauth/authorize", data=hidden, follow_redirects=False)
    assert resp.status_code == 302
    code_match = re.findall(r"code=([^&]+)", resp.headers["location"])
    assert code_match
    return code_match[0]


def _exchange_code(
    idp_client: TestClient,
    code: str,
    *,
    client_id: str = "mock-client",
    client_secret: str | None = None,
) -> object:
    data: dict[str, str] = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://mock-idp.local/callback",
        "client_id": client_id,
    }
    if client_secret is not None:
        data["client_secret"] = client_secret
    return idp_client.post("/oauth/token", data=data)


@pytest.fixture(autouse=True)
def _reset_admin_registrations() -> Iterator[None]:
    """Each test gets a clean slate: registering a secret/URI in one test
    must not leak into another (they share module-level dicts)."""
    mock_idp._registered_client_secrets.clear()
    mock_idp._registered_backchannel_logout_uris.clear()
    yield
    mock_idp._registered_client_secrets.clear()
    mock_idp._registered_backchannel_logout_uris.clear()


@pytest.fixture
def idp_client() -> Iterator[TestClient]:
    with TestClient(mock_idp_app) as client:
        yield client


# ---------------------------------------------------------------------------
# 1. sid claim
# ---------------------------------------------------------------------------


def test_issued_token_carries_a_sid_claim(idp_client: TestClient) -> None:
    code = _login_and_get_code(idp_client)
    resp = _exchange_code(idp_client, code)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    claims = pyjwt.decode(token, options={"verify_signature": False}, algorithms=["RS256"])
    assert isinstance(claims.get("sid"), str)
    assert claims["sid"]


def test_sid_is_stable_across_tokens_from_the_same_login_session(idp_client: TestClient) -> None:
    # A second authorization against the *same* mock_idp_session cookie
    # (recognized by GET /login, no re-submitted credentials) must yield the
    # same sid, since a real OP's `sid` names the IdP login session, not the
    # individual token. Re-POSTing /login instead would mint a fresh mock
    # session -- that's test_sid_differs_across_independent_login_sessions.
    code_a = _login_and_get_code(idp_client)
    token_a = _exchange_code(idp_client, code_a).json()["access_token"]

    code_b = _reauthorize_with_existing_session(idp_client)
    token_b = _exchange_code(idp_client, code_b).json()["access_token"]

    sid_a = pyjwt.decode(token_a, options={"verify_signature": False}, algorithms=["RS256"])["sid"]
    sid_b = pyjwt.decode(token_b, options={"verify_signature": False}, algorithms=["RS256"])["sid"]
    assert sid_a == sid_b


def test_sid_differs_across_independent_login_sessions() -> None:
    with TestClient(mock_idp_app) as client_a, TestClient(mock_idp_app) as client_b:
        code_a = _login_and_get_code(client_a)
        token_a = _exchange_code(client_a, code_a).json()["access_token"]
        code_b = _login_and_get_code(client_b)
        token_b = _exchange_code(client_b, code_b).json()["access_token"]

    sid_a = pyjwt.decode(token_a, options={"verify_signature": False}, algorithms=["RS256"])["sid"]
    sid_b = pyjwt.decode(token_b, options={"verify_signature": False}, algorithms=["RS256"])["sid"]
    assert sid_a != sid_b


# ---------------------------------------------------------------------------
# 2. Opt-in confidential-client verification
# ---------------------------------------------------------------------------


def test_unregistered_client_id_stays_public_client_no_secret_required(
    idp_client: TestClient,
) -> None:
    code = _login_and_get_code(idp_client)
    resp = _exchange_code(idp_client, code, client_id="mock-client")
    assert resp.status_code == 200


def test_registered_client_id_rejects_token_exchange_without_secret(idp_client: TestClient) -> None:
    idp_client.post(
        "/admin/register-client-secret",
        data={"client_id": "mock-confidential-client", "client_secret": "s3cret"},
    )
    code = _login_and_get_code(idp_client)
    resp = _exchange_code(idp_client, code, client_id="mock-confidential-client")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "invalid_client"


def test_registered_client_id_rejects_wrong_secret(idp_client: TestClient) -> None:
    idp_client.post(
        "/admin/register-client-secret",
        data={"client_id": "mock-confidential-client", "client_secret": "s3cret"},
    )
    code = _login_and_get_code(idp_client)
    resp = _exchange_code(
        idp_client, code, client_id="mock-confidential-client", client_secret="wrong"
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "invalid_client"


def test_registered_client_id_succeeds_with_correct_secret(idp_client: TestClient) -> None:
    idp_client.post(
        "/admin/register-client-secret",
        data={"client_id": "mock-confidential-client", "client_secret": "s3cret"},
    )
    code = _login_and_get_code(idp_client)
    resp = _exchange_code(
        idp_client, code, client_id="mock-confidential-client", client_secret="s3cret"
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 3. Back-Channel Logout
# ---------------------------------------------------------------------------


def _decode_logout_token_unverified(token: str) -> dict[str, object]:
    return pyjwt.decode(token, options={"verify_signature": False}, algorithms=["RS256"])


def test_logout_token_requires_sub_or_sid(idp_client: TestClient) -> None:
    resp = idp_client.post("/admin/trigger-backchannel-logout", data={"client_id": "mock-client"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "sub_or_sid_required"


def test_logout_token_has_the_spec_shaped_events_claim_and_no_nonce(idp_client: TestClient) -> None:
    resp = idp_client.post(
        "/admin/trigger-backchannel-logout",
        data={"client_id": "mock-client", "sub": "alice", "sid": "session-123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["delivery"] == {"attempted": False, "ok": False}  # no URI registered

    claims = _decode_logout_token_unverified(body["logout_token"])
    assert claims["events"] == {"http://schemas.openid.net/event/backchannel-logout": {}}
    assert claims["sub"] == "alice"
    assert claims["sid"] == "session-123"
    assert "nonce" not in claims
    assert claims["aud"] == "mock-client"


def test_logout_token_is_verifiable_against_the_mock_idps_own_jwks(idp_client: TestClient) -> None:
    jwks = idp_client.get("/jwks.json").json()
    jwk = jwks["keys"][0]
    public_key = pyjwt.algorithms.RSAAlgorithm.from_jwk(jwk)

    resp = idp_client.post(
        "/admin/trigger-backchannel-logout",
        data={"client_id": "mock-client", "sid": "session-verify"},
    )
    token = resp.json()["logout_token"]

    # Must not raise: a genuinely mis-signed token would fail here.
    claims = pyjwt.decode(token, public_key, algorithms=["RS256"], audience="mock-client")
    assert claims["sid"] == "session-verify"


def test_backchannel_logout_delivers_to_the_registered_uri(idp_client: TestClient) -> None:
    # Real local HTTP server (same pattern as
    # test_access_control_adapter_contracts.py's http-adapter test): the mock
    # IdP's trigger endpoint uses a real httpx.Client, so a same-process ASGI
    # app can't be wired in directly -- it needs an actual socket to POST to.
    received: dict[str, object] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length)
            from urllib.parse import parse_qs

            received["path"] = self.path
            received["form"] = {k: v[0] for k, v in parse_qs(body.decode("utf-8")).items()}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received"}).encode("utf-8"))

        def log_message(self, format, *args):  # noqa: A003, ANN001
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        idp_client.post(
            "/admin/register-backchannel-logout-uri",
            data={
                "client_id": "mock-client",
                "uri": f"http://127.0.0.1:{server.server_port}/rp/backchannel-logout",
            },
        )
        resp = idp_client.post(
            "/admin/trigger-backchannel-logout",
            data={"client_id": "mock-client", "sid": "session-delivery"},
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert resp.status_code == 200
    body = resp.json()
    assert body["delivery"] == {"attempted": True, "ok": True, "status_code": 200}
    assert received["path"] == "/rp/backchannel-logout"
    delivered_claims = _decode_logout_token_unverified(received["form"]["logout_token"])
    assert delivered_claims["sid"] == "session-delivery"


def test_backchannel_logout_reports_failed_delivery_without_raising(idp_client: TestClient) -> None:
    idp_client.post(
        "/admin/register-backchannel-logout-uri",
        data={"client_id": "mock-client", "uri": "http://127.0.0.1:1/unreachable"},
    )
    resp = idp_client.post(
        "/admin/trigger-backchannel-logout",
        data={"client_id": "mock-client", "sid": "session-unreachable"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["delivery"]["attempted"] is True
    assert body["delivery"]["ok"] is False
    assert "error" in body["delivery"]
    # The token itself must still come back even though delivery failed --
    # callers implementing ADR-0074 decision 6's full-session-revocation
    # fallback need it regardless of whether the push succeeded.
    assert body["logout_token"]
