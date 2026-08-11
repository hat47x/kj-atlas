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
"""

from __future__ import annotations

import hashlib
import secrets
import time
from urllib.parse import urlencode

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
) -> RedirectResponse:
    """Issue authorization code. Store PKCE code_challenge for later
    verification at /oauth/token."""
    if deny:
        params = urlencode({"error": "access_denied", "state": state})
        return RedirectResponse(url=f"{redirect_uri}?{params}", status_code=302)

    code = secrets.token_urlsafe(32)
    entry: dict[str, object] = {
        "sub": username,
        "tenant_ref": tenant_ref,
        "scope": scope,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "exp": time.time() + 600,
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
    code_verifier: str | None = Form(None),
) -> dict[str, object]:
    """Exchange an authorization code for a short-lived JWT."""
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="unsupported grant_type")

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
