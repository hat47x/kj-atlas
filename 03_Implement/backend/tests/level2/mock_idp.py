"""ADR-0064 D4: Level 2 mock IdP with OAuth 2.0 + PKCE + RS256 JWT.

Provides a complete mock OAuth 2.0 / OIDC identity provider with PKCE.

Browser flow:
  GET  /login                      — HTML login form
  POST /login                      — validate credentials, set session cookie,
                                     redirect to /oauth/authorize
  GET  /oauth/authorize            — consent page (checks session cookie)
  POST /oauth/authorize            — issue authorization code (stores PKCE
                                     code_challenge), redirect

API flow:
  POST /oauth/token                — exchange code + code_verifier for JWT
  GET  /oauth/userinfo             — return claims from Bearer token
  GET  /.well-known/openid-configuration — OIDC Discovery

Legacy (ADR-0063 D9-7):
  POST /oidc/token                 — direct JWT issuance (no OAuth flow)
  GET  /jwks.json                  — ephemeral public key
  GET  /healthz                    — liveness

Test-only admin (ADR-0074 SAAS-TENANT-SESSION-BINDING-01 harness prep):
  POST /admin/register-client-secret         — opt in a client_id to
                                               confidential-client verification
  POST /admin/register-backchannel-logout-uri — where to POST Logout Tokens
  POST /admin/trigger-backchannel-logout      — build+send a Logout Token
                                               (OIDC Back-Channel Logout 1.0)
"""

from __future__ import annotations

import hashlib
import secrets
import time
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import Cookie, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from .jwt_signer import EphemeralSigningKey

app = FastAPI(title="kj-atlas mock idp")

_SIGNING_KEY = EphemeralSigningKey(kid="mock-idp-level2")
_MOCK_BASE = "http://mock-idp.local"

# In-memory stores.
_pending_codes: dict[str, dict[str, object]] = {}  # code → {claims, code_challenge}
_mock_sessions: dict[str, dict[str, str]] = {}  # session_id → {username, tenant_ref}
# Test harness opt-in stores (ADR-0074 prep). Empty by default so existing
# public-client + PKCE callers (e.g. test_saas_oauth_login_e2e.py) see no
# behavior change: a client_id only gets confidential-client / back-channel
# logout treatment once a test explicitly registers it.
_registered_client_secrets: dict[str, str] = {}  # client_id → secret
_registered_backchannel_logout_uris: dict[str, str] = {}  # client_id → RP URI


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _new_session() -> str:
    sid = secrets.token_urlsafe(32)
    _mock_sessions[sid] = {}
    return sid


def _b64url(data: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _compute_code_challenge(code_verifier: str) -> str:
    """S256 PKCE: code_challenge = base64url(sha256(code_verifier))."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return _b64url(digest)


def _issue_jwt(*, provider: str, claims: dict[str, object]) -> dict[str, object]:
    now = int(time.time())
    c = dict(claims)
    issuer = c.pop("iss", f"{_MOCK_BASE}/{provider}")
    audience = c.pop("aud", "kj-atlas")
    subject = c.pop("sub", c.get("email", "mock-subject"))
    tenant_ref = c.pop("tenant_ref", c.get("tenant_ref", "mock-org"))

    payload: dict[str, object] = {
        "iss": issuer,
        "aud": audience,
        "sub": subject,
        "tenant_ref": tenant_ref,
        "iat": now - 60,
        "exp": now + 3600,
        "jti": secrets.token_urlsafe(24),
        **c,
    }
    token = jwt.encode(
        payload,
        _SIGNING_KEY.private_key_pem,
        algorithm="RS256",
        headers={"kid": _SIGNING_KEY.kid},
    )
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 3600,
        # id_token: claims dict for backward compat with mock SP.
        # The JWT string is in access_token.
        "id_token": {
            "iss": issuer,
            "aud": audience,
            "sub": subject,
            "tenant_ref": tenant_ref,
            **c,
        },
    }


# ---------------------------------------------------------------------------
# Legacy: direct JWT issuance (ADR-0063)
# ---------------------------------------------------------------------------


class IssueTokenRequest(BaseModel):
    provider: str
    claims: dict[str, object]


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "mock-idp", "kid": _SIGNING_KEY.kid}


@app.get("/jwks.json")
def jwks() -> dict[str, object]:
    return {"keys": [_SIGNING_KEY.public_jwk()]}


@app.post("/oidc/token")
def issue_token(request: IssueTokenRequest) -> dict[str, object]:
    return _issue_jwt(provider=request.provider, claims=request.claims)


# ---------------------------------------------------------------------------
# OIDC Discovery
# ---------------------------------------------------------------------------


@app.get("/.well-known/openid-configuration")
def openid_configuration() -> dict[str, object]:
    return {
        "issuer": _MOCK_BASE,
        "authorization_endpoint": f"{_MOCK_BASE}/oauth/authorize",
        "token_endpoint": f"{_MOCK_BASE}/oauth/token",
        "userinfo_endpoint": f"{_MOCK_BASE}/oauth/userinfo",
        "jwks_uri": f"{_MOCK_BASE}/jwks.json",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email"],
        "code_challenge_methods_supported": ["S256"],
    }


# ---------------------------------------------------------------------------
# Login (with session cookie)
# ---------------------------------------------------------------------------


@app.get("/login", response_class=HTMLResponse)
def login_page(
    redirect_uri: str | None = None,
    state: str | None = None,
    code_challenge: str | None = None,
    code_challenge_method: str | None = None,
    session_id: str | None = Cookie(default=None, alias="mock_idp_session"),
) -> str:
    """HTML login form. If already authenticated via session cookie, skip."""
    if session_id and session_id in _mock_sessions:
        sess = _mock_sessions[session_id]
        params = {
            "response_type": "code",
            "client_id": "mock-client",
            "scope": "openid profile email",
            "username": sess.get("username", "alice"),
            "tenant_ref": sess.get("tenant_ref", "org-123"),
        }
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        else:
            params["redirect_uri"] = f"{_MOCK_BASE}/callback"
        if state:
            params["state"] = state
        if code_challenge:
            params["code_challenge"] = code_challenge
        if code_challenge_method:
            params["code_challenge_method"] = code_challenge_method
        authz_url = f"/oauth/authorize?{urlencode(params)}"
        return RedirectResponse(url=authz_url, status_code=302)

    fields = ""
    for name, value in [
        ("redirect_uri", redirect_uri),
        ("state", state),
        ("code_challenge", code_challenge),
        ("code_challenge_method", code_challenge_method),
    ]:
        if value:
            fields += f'<input type="hidden" name="{name}" value="{value}">\n'

    return f"""<!DOCTYPE html>
<html><head><title>Mock IdP Login</title></head>
<body>
<h1>Mock IdP Login</h1>
<form method="post" action="/login">
  <label>Username: <input name="username" value="alice"></label><br>
  <label>Password: <input name="password" type="password" value="password"></label><br>
  <label>Tenant: <select name="tenant_ref">
    <option value="org-123">Org 123 (Tenant A)</option>
    <option value="org-456">Org 456 (Tenant B)</option>
  </select></label><br>
  {fields}
  <button type="submit">Sign in</button>
</form>
</body></html>"""


@app.post("/login")
def login_submit(
    username: str = Form(...),
    password: str = Form(""),
    tenant_ref: str = Form("org-123"),
    redirect_uri: str | None = Form(None),
    state: str | None = Form(None),
    code_challenge: str | None = Form(None),
    code_challenge_method: str | None = Form(None),
) -> RedirectResponse:
    """Accept any non-empty credentials. Set session cookie, redirect to
    /oauth/authorize carrying PKCE parameters through."""
    if not username.strip():
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create mock session.
    sid = _new_session()
    _mock_sessions[sid] = {
        "username": username.strip(),
        "tenant_ref": tenant_ref.strip(),
    }

    params: dict[str, str] = {
        "response_type": "code",
        "client_id": "mock-client",
        "scope": "openid profile email",
        "username": username.strip(),
        "tenant_ref": tenant_ref.strip(),
    }
    if redirect_uri:
        params["redirect_uri"] = redirect_uri
    else:
        params["redirect_uri"] = f"{_MOCK_BASE}/callback"
    if state:
        params["state"] = state
    else:
        params["state"] = secrets.token_urlsafe(16)
    if code_challenge:
        params["code_challenge"] = code_challenge
    if code_challenge_method:
        params["code_challenge_method"] = code_challenge_method

    authorize_url = f"/oauth/authorize?{urlencode(params)}"
    redirect = RedirectResponse(url=authorize_url, status_code=302)
    redirect.set_cookie(
        key="mock_idp_session",
        value=sid,
        httponly=True,
        max_age=3600,
        samesite="lax",
    )
    return redirect


# ---------------------------------------------------------------------------
# OAuth 2.0 Authorization (with PKCE)
# ---------------------------------------------------------------------------


@app.get("/oauth/authorize", response_class=HTMLResponse)
def authorize_page(
    response_type: str = "code",
    client_id: str = "mock-client",
    redirect_uri: str = f"{_MOCK_BASE}/callback",
    scope: str = "openid",
    state: str = "",
    username: str = "alice",
    tenant_ref: str = "org-123",
    code_challenge: str | None = None,
    code_challenge_method: str | None = None,
) -> str:
    """Mock consent page. Displays requested scopes and forwards PKCE params."""
    challenge_info = ""
    if code_challenge:
        challenge_info = f"<li>PKCE: S256 (challenge: {code_challenge[:20]}...)</li>"

    return f"""<!DOCTYPE html>
<html><head><title>Mock IdP — Authorize</title></head>
<body>
<h1>Authorize Application</h1>
<p>Client <strong>{client_id}</strong> requests access to:</p>
<ul>
  <li>Scopes: {scope}</li>
  <li>Redirect: {redirect_uri}</li>
  {challenge_info}
</ul>
<p>Signed in as <strong>{username}</strong> (tenant: {tenant_ref})</p>
<form method="post" action="/oauth/authorize">
  <input type="hidden" name="response_type" value="{response_type}">
  <input type="hidden" name="client_id" value="{client_id}">
  <input type="hidden" name="redirect_uri" value="{redirect_uri}">
  <input type="hidden" name="scope" value="{scope}">
  <input type="hidden" name="state" value="{state}">
  <input type="hidden" name="username" value="{username}">
  <input type="hidden" name="tenant_ref" value="{tenant_ref}">
  <input type="hidden" name="code_challenge" value="{code_challenge or ""}">
  <input type="hidden" name="code_challenge_method" value="{code_challenge_method or ""}">
  <button type="submit" name="approve" value="true">Approve</button>
  <button type="submit" name="deny" value="true">Deny</button>
</form>
</body></html>"""


@app.post("/oauth/authorize")
def authorize_approve(
    response_type: str = Form("code"),
    client_id: str = Form("mock-client"),
    redirect_uri: str = Form(f"{_MOCK_BASE}/callback"),
    scope: str = Form("openid"),
    state: str = Form(""),
    username: str = Form("alice"),
    tenant_ref: str = Form("org-123"),
    code_challenge: str = Form(""),
    code_challenge_method: str = Form(""),
    approve: str | None = Form(None),
    deny: str | None = Form(None),
    session_id: str | None = Cookie(default=None, alias="mock_idp_session"),
) -> RedirectResponse:
    """Issue authorization code. Store PKCE code_challenge for later
    verification at /oauth/token."""
    if deny:
        params = urlencode({"error": "access_denied", "state": state})
        return RedirectResponse(url=f"{redirect_uri}?{params}", status_code=302)

    code = secrets.token_urlsafe(32)
    # The OIDC `sid` claim identifies this IdP login session so a later
    # back-channel Logout Token can name it. Reuse the mock_idp_session
    # cookie's id (the login already minted one via _new_session()) when
    # present so every token from the same browser session shares one sid;
    # fall back to a fresh id for token-endpoint-only callers with no cookie.
    sid = session_id or secrets.token_urlsafe(16)
    entry: dict[str, object] = {
        "sub": username,
        "tenant_ref": tenant_ref,
        "scope": scope,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "exp": time.time() + 600,
        "sid": sid,
    }
    # Store PKCE challenge if provided.
    if code_challenge and code_challenge_method.upper() == "S256":
        entry["code_challenge"] = code_challenge

    _pending_codes[code] = entry

    params = urlencode({"code": code, "state": state})
    return RedirectResponse(url=f"{redirect_uri}?{params}", status_code=302)


# ---------------------------------------------------------------------------
# Token endpoint (with PKCE verification)
# ---------------------------------------------------------------------------


@app.post("/oauth/token")
def token_exchange(
    grant_type: str = Form(...),
    code: str | None = Form(None),
    redirect_uri: str = Form(f"{_MOCK_BASE}/callback"),
    client_id: str = Form("mock-client"),
    client_secret: str | None = Form(None),
    code_verifier: str | None = Form(None),
) -> dict[str, object]:
    """Exchange an authorization code for a short-lived JWT."""
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="unsupported grant_type")

    # Confidential-client verification is opt-in: only a client_id a test
    # has registered a secret for (see /admin/register-client-secret) is
    # held to it. Unregistered client_ids -- including the default
    # "mock-client" every existing test uses -- keep today's public-client
    # + PKCE behavior unchanged.
    expected_secret = _registered_client_secrets.get(client_id)
    if expected_secret is not None:
        if not client_secret or not secrets.compare_digest(client_secret, expected_secret):
            raise HTTPException(status_code=401, detail="invalid_client")

    # Authorization code grant (with PKCE).
    if not code:
        raise HTTPException(status_code=400, detail="missing_code")

    pending = _pending_codes.get(code)
    if pending is None:
        raise HTTPException(status_code=400, detail="invalid_grant")

    if time.time() > float(pending["exp"]):
        del _pending_codes[code]
        raise HTTPException(status_code=400, detail="code_expired")

    stored_challenge = pending.get("code_challenge")
    if stored_challenge is not None:
        if not code_verifier:
            raise HTTPException(status_code=400, detail="missing_code_verifier")
        expected = _compute_code_challenge(code_verifier)
        if not secrets.compare_digest(expected, str(stored_challenge)):
            raise HTTPException(status_code=400, detail="invalid_code_verifier")

    del _pending_codes[code]

    claims: dict[str, object] = {
        "sub": str(pending["sub"]),
        "tenant_ref": str(pending["tenant_ref"]),
        "email": f"{pending['sub']}@mock-idp.local",
        "name": str(pending["sub"]).title(),
        "sid": str(pending["sid"]),
    }
    result = _issue_jwt(provider=str(pending["client_id"]), claims=claims)
    result["scope"] = pending.get("scope", "openid")
    return result


# ---------------------------------------------------------------------------
# Logout (RP-Initiated Logout)
# ---------------------------------------------------------------------------


@app.get("/logout")
def logout(
    id_token_hint: str | None = None,
    post_logout_redirect_uri: str | None = None,
    state: str | None = None,
    session_id: str | None = Cookie(default=None, alias="mock_idp_session"),
):
    """RP-Initiated Logout: clear session and optionally redirect."""
    if session_id:
        _mock_sessions.pop(session_id, None)

    if post_logout_redirect_uri:
        params = f"?state={state}" if state else ""
        response: object = RedirectResponse(
            url=f"{post_logout_redirect_uri}{params}",
            status_code=302,
        )
    else:
        response = HTMLResponse(
            content="<!DOCTYPE html><html><body><h1>Logged out</h1></body></html>",
            status_code=200,
        )
    response.delete_cookie(key="mock_idp_session")  # type: ignore[union-attr]
    return response  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Back-Channel Logout (OIDC Back-Channel Logout 1.0) -- test-only admin API
#
# Real IdPs push a Logout Token to a Relying Party's registered
# backchannel_logout_uri when a session ends elsewhere (SSO logout, admin
# revocation). This mock has no persistent client registration, so tests
# register a target URI and a client_secret explicitly via the /admin
# endpoints below, then call /admin/trigger-backchannel-logout to have the
# mock build a spec-shaped Logout Token and (best-effort) POST it -- mirroring
# how a Broker like Keycloak would notify kj-atlas's BFF.
# ---------------------------------------------------------------------------


def _issue_logout_token(*, issuer: str, audience: str, sub: str | None, sid: str | None) -> str:
    """Build a signed OIDC Logout Token (Back-Channel Logout 1.0 draft §3).

    Must carry the `events` claim naming the backchannel-logout event, at
    least one of sub/sid, and must NOT carry `nonce` (the spec forbids it to
    keep Logout Tokens from being mistaken for ID Tokens).
    """
    now = int(time.time())
    payload: dict[str, object] = {
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "jti": secrets.token_urlsafe(24),
        "events": {"http://schemas.openid.net/event/backchannel-logout": {}},
    }
    if sub is not None:
        payload["sub"] = sub
    if sid is not None:
        payload["sid"] = sid
    return jwt.encode(
        payload,
        _SIGNING_KEY.private_key_pem,
        algorithm="RS256",
        headers={"kid": _SIGNING_KEY.kid},
    )


@app.post("/admin/register-client-secret")
def register_client_secret(
    client_id: str = Form(...), client_secret: str = Form(...)
) -> dict[str, str]:
    """Test-only: opt a client_id into confidential-client verification at
    /oauth/token. Unregistered client_ids stay public-client (unchanged)."""
    if not client_id.strip() or not client_secret.strip():
        raise HTTPException(status_code=400, detail="client_id_and_secret_required")
    _registered_client_secrets[client_id] = client_secret
    return {"status": "registered", "client_id": client_id}


@app.post("/admin/register-backchannel-logout-uri")
def register_backchannel_logout_uri(
    client_id: str = Form(...), uri: str = Form(...)
) -> dict[str, str]:
    """Test-only: where trigger-backchannel-logout should POST Logout Tokens
    for this client_id."""
    if not client_id.strip() or not uri.strip():
        raise HTTPException(status_code=400, detail="client_id_and_uri_required")
    _registered_backchannel_logout_uris[client_id] = uri
    return {"status": "registered", "client_id": client_id, "uri": uri}


@app.post("/admin/trigger-backchannel-logout")
def trigger_backchannel_logout(
    client_id: str = Form("mock-client"),
    sub: str | None = Form(None),
    sid: str | None = Form(None),
) -> dict[str, object]:
    """Test-only: build a Logout Token and attempt delivery to the URI
    registered for client_id. Always returns the token (callers that want to
    assert on delivery failure -- e.g. the ADR-0074 decision-6 fallback to
    full-session revocation when back-channel logout can't reach the RP --
    can register an unreachable/no URI and inspect delivery.ok themselves)."""
    if not sub and not sid:
        raise HTTPException(status_code=400, detail="sub_or_sid_required")

    logout_token = _issue_logout_token(
        issuer=f"{_MOCK_BASE}/{client_id}",
        audience=client_id,
        sub=sub,
        sid=sid,
    )

    uri = _registered_backchannel_logout_uris.get(client_id)
    if uri is None:
        return {"logout_token": logout_token, "delivery": {"attempted": False, "ok": False}}

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(uri, data={"logout_token": logout_token})
        return {
            "logout_token": logout_token,
            "delivery": {
                "attempted": True,
                "ok": response.status_code == 200,
                "status_code": response.status_code,
            },
        }
    except httpx.HTTPError as exc:
        return {
            "logout_token": logout_token,
            "delivery": {"attempted": True, "ok": False, "error": str(exc)},
        }


# ---------------------------------------------------------------------------
# UserInfo
# ---------------------------------------------------------------------------


@app.get("/oauth/userinfo")
def userinfo(request: Request) -> dict[str, object]:
    """Return claims from the Bearer token."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing_token")
    token = auth_header[7:].strip()

    try:
        unverified: dict[str, object] = jwt.decode(
            token,
            options={"verify_signature": False},
            algorithms=["RS256"],
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid_token") from None

    return {
        "sub": unverified.get("sub"),
        "email": unverified.get("email"),
        "name": unverified.get("name"),
        "tenant_ref": unverified.get("tenant_ref"),
    }
