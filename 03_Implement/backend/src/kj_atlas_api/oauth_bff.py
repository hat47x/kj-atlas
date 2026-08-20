"""SAAS-TENANT-SESSION-BINDING-01 AC-1 (ADR-0074 decisions 1/2/3): BFF OAuth
login. GET /session/login starts an authorization-code+PKCE flow against the
broker; GET /session/callback exchanges the code, verifies the returned
token against the same JWKS pipeline the bearer path uses
(trusted_auth_edge.py), and mints a server-owned Kj-Atlas-Auth-Session
cookie. ADR-0074 decisions 2/5 and 回答案2 define the cookie attributes and
the anti-CSRF contract this flow must satisfy.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode, urlsplit

import jwt
from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from kj_atlas_api.active_tenant_session import _new_session_version, tenant_session_cookie_is_secure
from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.oauth_broker_client import (
    OauthBrokerInvalidResponseError,
    OauthBrokerUnavailableError,
    exchange_code_for_tokens,
)
from kj_atlas_api.settings import settings
from kj_atlas_api.tenant_context import VerifiedTenantClaim
from kj_atlas_api.trusted_auth_edge import (
    JwtIdentityError,
    _fetch_jwks,
    _jwt_algorithms,
    _normalize_audience,
    _resolve_identity_provider,
    _resolve_subject_to_user_id,
    _resolve_tenant_claim,
    _verify_jwt,
)

logger = logging.getLogger(__name__)

_AUTH_SESSION_COOKIE = "Kj-Atlas-Auth-Session"
_OAUTH_PENDING_COOKIE = "Kj-Atlas-Oauth-Pending"
_OAUTH_PENDING_PATH = "/session"
_OAUTH_PENDING_MAX_AGE_SECONDS = 300
_AUTH_SESSION_MAX_AGE_SECONDS = 3600
_MAX_NEXT_PATH_LENGTH = 512


def _oauth_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _validate_next_path(raw: str | None) -> str:
    """Same-origin only -- anything else is discarded in favor of "/" rather
    than rejecting the login attempt outright (open-redirect guard)."""
    if not raw or len(raw) > _MAX_NEXT_PATH_LENGTH:
        return "/"
    if "\r" in raw or "\n" in raw:
        return "/"
    if not raw.startswith("/") or raw.startswith("//"):
        return "/"
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return "/"
    return raw


def _generate_pkce_pair() -> tuple[str, str]:
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


@dataclass(frozen=True, slots=True)
class _PendingLogin:
    state: str
    code_verifier: str
    next_path: str


def _parse_pending_cookie(raw: str | None) -> _PendingLogin | None:
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    state = payload.get("state")
    code_verifier = payload.get("code_verifier")
    next_path = payload.get("next")
    if not isinstance(state, str) or not state:
        return None
    if not isinstance(code_verifier, str) or not code_verifier:
        return None
    if not isinstance(next_path, str) or not next_path:
        return None
    return _PendingLogin(state=state, code_verifier=code_verifier, next_path=next_path)


def initiate_login(*, request: Request, next_query: str | None) -> RedirectResponse:
    """GET /session/login: start an authorization-code+PKCE flow (ADR-0074 decision 1)."""
    authorize_endpoint = settings.saas_oauth_broker_http_authorize_endpoint
    client_id = settings.saas_oauth_broker_http_client_id
    redirect_uri = settings.saas_oauth_broker_http_redirect_uri
    if not authorize_endpoint or not client_id or not redirect_uri:
        raise _oauth_error(503, "oauth_login_unavailable", "OAuth login is not configured.")

    state = secrets.token_urlsafe(32)
    code_verifier, code_challenge = _generate_pkce_pair()
    next_path = _validate_next_path(next_query)

    pending_payload = json.dumps(
        {"state": state, "code_verifier": code_verifier, "next": next_path}
    )
    query = urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    )
    redirect = RedirectResponse(url=f"{authorize_endpoint}?{query}", status_code=302)
    redirect.set_cookie(
        key=_OAUTH_PENDING_COOKIE,
        value=pending_payload,
        httponly=True,
        secure=tenant_session_cookie_is_secure(request.app.state.runtime_profile),
        samesite="lax",
        max_age=_OAUTH_PENDING_MAX_AGE_SECONDS,
        path=_OAUTH_PENDING_PATH,
    )
    return redirect


def _verify_broker_identity(*, db: Session, token: str) -> tuple[str, VerifiedTenantClaim]:
    """Mirrors JwtSaasIdentityContextResolver's bearer-path verification
    (trusted_auth_edge.py) so a broker-issued token gets the exact same
    JWKS/signature/issuer/audience/tenant-claim rigor as a live bearer token.
    """
    try:
        claims_unverified: dict[str, object] = jwt.decode(
            token,
            options={"verify_signature": False},
            algorithms=list(_jwt_algorithms()),
        )
    except jwt.PyJWTError:
        raise JwtIdentityError(status_code=401, code="invalid_token") from None

    issuer = claims_unverified.get("iss")
    if not isinstance(issuer, str):
        raise JwtIdentityError(status_code=401, code="invalid_token")
    aud_values = _normalize_audience(claims_unverified.get("aud"))
    if not aud_values:
        raise JwtIdentityError(status_code=401, code="invalid_token")

    provider = None
    matched_audience = ""
    for aud in aud_values:
        provider = _resolve_identity_provider(db, issuer, aud)
        if provider is not None:
            matched_audience = aud
            break
    if provider is None:
        raise JwtIdentityError(status_code=401, code="unknown_provider")

    keys = _fetch_jwks(provider.jwks_uri)
    verified = _verify_jwt(token, keys, issuer, matched_audience)

    subject = verified.get("sub")
    if not isinstance(subject, str):
        raise JwtIdentityError(status_code=401, code="invalid_token")

    user_id = _resolve_subject_to_user_id(db, provider.id, subject)
    if user_id is None:
        raise JwtIdentityError(status_code=403, code="identity_not_provisioned")

    verified_tenant_claim = _resolve_tenant_claim(
        db=db,
        verified_claims=verified,
        provider=provider,
        subject=subject,
    )
    return user_id, verified_tenant_claim


def handle_callback(
    *,
    request: Request,
    db: Session,
    code: str | None,
    state: str | None,
    error: str | None,
) -> RedirectResponse:
    """GET /session/callback: exchange the code, verify the token, and mint the
    auth-session cookie (ADR-0074 decisions 1/2)."""
    pending = _parse_pending_cookie(request.cookies.get(_OAUTH_PENDING_COOKIE))
    if pending is None:
        raise _oauth_error(400, "oauth_login_not_pending", "No pending OAuth login was found.")
    if error is not None:
        raise _oauth_error(400, "oauth_broker_denied", "The identity broker denied the login request.")
    if not state or not hmac.compare_digest(state, pending.state):
        raise _oauth_error(400, "oauth_state_mismatch", "The OAuth state parameter did not match.")
    if not code:
        raise _oauth_error(400, "oauth_login_not_pending", "No authorization code was returned.")

    config = getattr(request.app.state, "saas_oauth_broker_config", None)
    if config is None:
        raise _oauth_error(503, "oauth_broker_unavailable", "The OAuth broker is not configured.")

    try:
        tokens = exchange_code_for_tokens(
            config=config, code=code, code_verifier=pending.code_verifier
        )
    except OauthBrokerInvalidResponseError:
        raise _oauth_error(
            400, "oauth_broker_rejected", "The identity broker rejected the code exchange."
        ) from None
    except OauthBrokerUnavailableError:
        raise _oauth_error(503, "oauth_broker_unavailable", "The identity broker is unavailable.") from None

    token_to_verify = tokens.id_token or tokens.access_token
    try:
        user_id, verified_tenant_claim = _verify_broker_identity(db=db, token=token_to_verify)
    except JwtIdentityError:
        raise _oauth_error(401, "oauth_token_invalid", "The broker-issued token failed verification.") from None

    auth_session_store = getattr(request.app.state, "saas_auth_session_store", None)
    auth_state_store = getattr(request.app.state, "saas_auth_state_store", None)
    hash_key = getattr(request.app.state, "saas_auth_session_hash_key", None)
    if auth_session_store is None or auth_state_store is None or hash_key is None:
        raise _oauth_error(503, "session_persist_unavailable", "Session persistence is unavailable.")

    tenant_session_version = auth_state_store.current_or_create_session_version(
        principal_id=user_id,
        new_version=_new_session_version(),
    )

    raw_session_id = secrets.token_urlsafe(32)
    session_key_hash = derive_session_key_hash(raw_session_id, key=hash_key)
    try:
        auth_session_store.create_auth_session(
            session_key_hash=session_key_hash,
            principal_id=user_id,
            issuer=verified_tenant_claim.issuer,
            subject=verified_tenant_claim.subject,
            active_tenant_id=verified_tenant_claim.tenant_id,
            tenant_session_version=tenant_session_version,
        )
    except Exception:
        logger.warning("oauth callback: failed to persist auth session", exc_info=True)
        raise _oauth_error(503, "session_persist_unavailable", "Failed to persist the auth session.") from None

    redirect = RedirectResponse(url=pending.next_path, status_code=302)
    redirect.delete_cookie(
        key=_OAUTH_PENDING_COOKIE,
        httponly=True,
        secure=tenant_session_cookie_is_secure(request.app.state.runtime_profile),
        samesite="lax",
        path=_OAUTH_PENDING_PATH,
    )
    redirect.set_cookie(
        key=_AUTH_SESSION_COOKIE,
        value=raw_session_id,
        httponly=True,
        secure=tenant_session_cookie_is_secure(request.app.state.runtime_profile),
        samesite="strict",
        max_age=_AUTH_SESSION_MAX_AGE_SECONDS,
        path="/",
    )
    return redirect


def revoke_auth_session_cookie(*, request: Request, response: Response) -> None:
    """ADR-0074 decision 6: logout revokes the session that was presented.

    Revoking the row without clearing the cookie would keep re-presenting a
    dead credential; clearing the cookie without revoking the row would leave
    a live session that any retained copy of the cookie could still use. Both
    happen here, and the cookie is cleared even when the store is unconfigured,
    since clearing is always safe.
    """
    raw_session_id = request.cookies.get(_AUTH_SESSION_COOKIE)
    store = getattr(request.app.state, "saas_auth_session_store", None)
    hash_key = getattr(request.app.state, "saas_auth_session_hash_key", None)
    if raw_session_id and store is not None and hash_key is not None:
        store.revoke_auth_session(
            session_key_hash=derive_session_key_hash(raw_session_id, key=hash_key)
        )
    response.delete_cookie(
        key=_AUTH_SESSION_COOKIE,
        httponly=True,
        secure=tenant_session_cookie_is_secure(request.app.state.runtime_profile),
        samesite="strict",
        path="/",
    )
