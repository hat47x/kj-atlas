from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from urllib.parse import urlsplit

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from kj_atlas_api.active_tenant_session import tenant_session_cookie_is_secure
from kj_atlas_api.trusted_auth_edge import _extract_bearer_token

AUTH_SESSION_COOKIE = "Kj-Atlas-Auth-Session"
CSRF_COOKIE = "Kj-Atlas-Csrf"
CSRF_HEADER = "X-Kj-Atlas-Csrf"
CSRF_TOKEN_MAX_AGE_SECONDS = 3600
_MAX_AUTH_SESSION_COOKIE_LENGTH = 256
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})
_CSRF_DOMAIN_SEPARATOR = b"kj-atlas-session-csrf-v1\x00"


@dataclass(frozen=True, slots=True)
class CsrfFailure:
    status_code: int
    code: str
    message: str


def derive_session_csrf_token(raw_session_id: str, *, key: bytes) -> str:
    if (
        not raw_session_id
        or len(raw_session_id) > _MAX_AUTH_SESSION_COOKIE_LENGTH
        or raw_session_id.strip() != raw_session_id
        or any(not character.isprintable() for character in raw_session_id)
    ):
        raise ValueError("auth session cookie is not canonical")
    return hmac.new(
        key,
        _CSRF_DOMAIN_SEPARATOR + raw_session_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def set_session_csrf_cookie(
    *, response: Response, raw_session_id: str, key: bytes, runtime_profile: str
) -> None:
    response.set_cookie(
        key=CSRF_COOKIE,
        value=derive_session_csrf_token(raw_session_id, key=key),
        httponly=False,
        secure=tenant_session_cookie_is_secure(runtime_profile),
        samesite="strict",
        max_age=CSRF_TOKEN_MAX_AGE_SECONDS,
        path="/",
    )


def clear_session_csrf_cookie(*, response: Response, runtime_profile: str) -> None:
    response.delete_cookie(
        key=CSRF_COOKIE,
        httponly=False,
        secure=tenant_session_cookie_is_secure(runtime_profile),
        samesite="strict",
        path="/",
    )


def _same_origin_host(request: Request) -> bool:
    origin = request.headers.get("origin")
    host = request.headers.get("host")
    if (
        origin is None
        or host is None
        or not origin
        or not host
        or origin.strip() != origin
        or host.strip() != host
        or len(origin) > 2048
        or len(host) > 255
        or any(not character.isprintable() for character in origin + host)
    ):
        return False
    parsed = urlsplit(origin)
    try:
        parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        return False
    return (
        parsed.netloc.lower() == host.lower()
        and parsed.scheme.lower() == request.url.scheme.lower()
    )


def validate_bff_csrf_request(request: Request, *, key: bytes | None) -> CsrfFailure | None:
    if request.method.upper() in _SAFE_METHODS:
        return None
    # The trusted auth edge gives an explicitly-present bearer credential
    # priority over the BFF cookie. Preserve that compatibility boundary until
    # the separate SPA bearer cutover is completed.
    if _extract_bearer_token(request) is not None:
        return None

    raw_session_id = request.cookies.get(AUTH_SESSION_COOKIE)
    if not raw_session_id:
        # No BFF credential: leave normal authentication/authorization to the
        # route. This middleware is not a replacement auth mechanism.
        return None
    if key is None:
        return CsrfFailure(
            503,
            "csrf_protection_unavailable",
            "Session request protection is unavailable.",
        )
    try:
        expected = derive_session_csrf_token(raw_session_id, key=key)
    except ValueError:
        return CsrfFailure(403, "csrf_validation_failed", "Request validation failed.")

    if not _same_origin_host(request):
        return CsrfFailure(403, "csrf_validation_failed", "Request validation failed.")
    presented = request.headers.get(CSRF_HEADER)
    if (
        presented is None
        or len(presented) != 64
        or any(character not in "0123456789abcdef" for character in presented)
        or not hmac.compare_digest(presented, expected)
    ):
        return CsrfFailure(403, "csrf_validation_failed", "Request validation failed.")
    return None


class BffCsrfProtectionMiddleware(BaseHTTPMiddleware):
    """ADR-0074 decision 5: protect unsafe BFF-cookie requests globally.

    SameSite=Strict remains the first browser boundary. For any unsafe request
    that actually relies on the BFF cookie, this middleware also requires a
    same-origin Origin/Host pair and a session-bound synchronizer header.
    """

    async def dispatch(self, request: Request, call_next):
        failure = validate_bff_csrf_request(
            request,
            key=getattr(request.app.state, "saas_auth_session_hash_key", None),
        )
        if failure is not None:
            return JSONResponse(
                status_code=failure.status_code,
                content={"detail": {"code": failure.code, "message": failure.message}},
                headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
            )
        return await call_next(request)
