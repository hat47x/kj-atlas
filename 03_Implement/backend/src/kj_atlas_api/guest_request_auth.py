"""Request-bound server-owned guest session boundary for ADR-0080."""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from fastapi import HTTPException, Request

from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore

GUEST_AUTH_SESSION_COOKIE = "Kj-Atlas-Guest-Session"
_MAX_GUEST_AUTH_SESSION_COOKIE_LENGTH = 256


@dataclass(frozen=True, slots=True)
class GuestRequestSession:
    tenant_id: str
    guest_principal_id: str
    issuer: str
    subject: str
    session_key_hash: str


def issue_guest_auth_session(
    *,
    store: DatabaseGuestAuthSessionStore,
    hash_key: bytes,
    tenant_id: str,
    guest_principal_id: str,
    issuer: str,
    subject: str,
) -> str:
    """Mint an opaque cookie value only after verified identity binding.

    R2a exposes this as an internal service boundary.  The OAuth/BFF callback
    that supplies the verified ``issuer``/``subject`` is deliberately a later
    slice; callers cannot bypass the store's active-principal identity check.
    """
    raw_session_id = secrets.token_urlsafe(32)
    session_key_hash = derive_session_key_hash(raw_session_id, key=hash_key)
    store.create_guest_auth_session(
        session_key_hash=session_key_hash,
        tenant_id=tenant_id,
        guest_principal_id=guest_principal_id,
        issuer=issuer,
        subject=subject,
    )
    return raw_session_id


def resolve_guest_request_session(*, request: Request) -> GuestRequestSession | None:
    """Resolve the dedicated guest cookie, or return None when it is absent.

    Presence is authoritative: a malformed, unknown, expired or revoked guest
    cookie fails closed instead of falling through to the normal member path.
    """
    raw_session_id = request.cookies.get(GUEST_AUTH_SESSION_COOKIE)
    if raw_session_id is None:
        return None
    if not raw_session_id or len(raw_session_id) > _MAX_GUEST_AUTH_SESSION_COOKIE_LENGTH:
        raise HTTPException(
            status_code=401,
            detail={"code": "guest_session_invalid", "message": "Guest session is invalid."},
        )

    store = getattr(request.app.state, "guest_auth_session_store", None)
    hash_key = getattr(request.app.state, "guest_auth_session_hash_key", None)
    if store is None or hash_key is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "guest_session_unavailable",
                "message": "Guest session persistence is unavailable.",
            },
        )

    session_key_hash = derive_session_key_hash(raw_session_id, key=hash_key)
    resolved = store.resolve_guest_auth_session(session_key_hash=session_key_hash)
    if resolved is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "guest_session_invalid", "message": "Guest session is invalid."},
        )
    return GuestRequestSession(
        tenant_id=resolved.tenant_id,
        guest_principal_id=resolved.guest_principal_id,
        issuer=resolved.issuer,
        subject=resolved.subject,
        session_key_hash=session_key_hash,
    )
