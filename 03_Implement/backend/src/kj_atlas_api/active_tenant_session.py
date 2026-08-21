from __future__ import annotations

import hmac
import logging
import re
import secrets
from collections.abc import Callable
from threading import Lock
from typing import Protocol, cast

from fastapi import HTTPException, Request, Response

from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthSessionStore, DatabaseSaasAuthStateStore

logger = logging.getLogger(__name__)

MAX_TENANT_SESSION_VERSION_LENGTH = 128
_TENANT_SESSION_VERSION_PATTERN = re.compile(
    rf"[A-Za-z0-9][A-Za-z0-9._~-]{{0,{MAX_TENANT_SESSION_VERSION_LENGTH - 1}}}"
)


class TenantSessionChangedError(Exception):
    """Signal an atomic expected-version mismatch without exposing session state."""


class ActiveTenantSessionPersister(Protocol):
    """Resolve and conditionally update active tenant state in the auth session.

    Implementations own anti-forgery validation and the auth-edge-specific session
    format. ``persist`` must atomically compare the expected version, update the
    selected tenant, and issue a different unpredictable version. Implementations
    must bind state to ``principal_id`` and must not read a tenant identifier from
    request headers, query parameters, or the raw body.
    """

    def current_version(
        self,
        *,
        request: Request,
        principal_id: str,
        active_tenant: TenantContext,
    ) -> str: ...

    def persist(
        self,
        *,
        request: Request,
        response: Response,
        principal_id: str,
        previous_tenant: TenantContext,
        selected_tenant: TenantContext,
        expected_tenant_session_version: str,
    ) -> str: ...

    def clear(self, *, request: Request, response: Response) -> None: ...


def canonical_tenant_session_version(value: object) -> str:
    if not isinstance(value, str) or _TENANT_SESSION_VERSION_PATTERN.fullmatch(value) is None:
        raise ValueError("tenant session version is not canonical")
    return value


def _session_context_unavailable() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "code": "session_context_unavailable",
            "message": "Tenant session context is unavailable.",
        },
    )


def _tenant_session_changed() -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={
            "code": "tenant_session_changed",
            "message": "Tenant session context changed.",
        },
    )


def _active_tenant_update_unavailable() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "code": "active_tenant_update_unavailable",
            "message": "Active tenant update is unavailable.",
        },
    )


def _session_keyed_auth_store(
    request: Request, *, unavailable: Callable[[], HTTPException]
) -> DatabaseSaasAuthSessionStore:
    store = getattr(request.app.state, "saas_auth_session_store", None)
    if store is None:
        raise unavailable()
    return cast(DatabaseSaasAuthSessionStore, store)


def _resolve_session_keyed_version(*, request: Request, auth_session_key_hash: str) -> str:
    """AC-2/AC-3: for a server-owned auth session, tenant_session_version lives
    on the same SaasAuthSessionRow as active_tenant_id -- read it from there so
    the CAS baseline used by a later switch matches the row the switch itself
    updates. AC-6: a store miss (unknown/revoked/expired session) fails closed;
    it must never fall back to the principal-keyed store below.
    """
    store = _session_keyed_auth_store(request, unavailable=_session_context_unavailable)
    try:
        resolved = store.resolve_auth_session(session_key_hash=auth_session_key_hash)
    except Exception:
        logger.warning(
            "auth session store raised resolving active tenant version", exc_info=True
        )
        raise _session_context_unavailable() from None
    if resolved is None:
        raise _session_context_unavailable()
    return canonical_tenant_session_version(resolved.tenant_session_version)


def resolve_active_tenant_session_version(
    *,
    request: Request,
    principal_id: str,
    active_tenant: TenantContext,
    auth_session_key_hash: str | None = None,
) -> str:
    if auth_session_key_hash is not None:
        return _resolve_session_keyed_version(
            request=request, auth_session_key_hash=auth_session_key_hash
        )
    persister = getattr(request.app.state, "active_tenant_session_persister", None)
    if persister is None:
        raise _session_context_unavailable()
    try:
        version = cast(ActiveTenantSessionPersister, persister).current_version(
            request=request,
            principal_id=principal_id,
            active_tenant=active_tenant,
        )
        return canonical_tenant_session_version(version)
    except HTTPException:
        raise
    except Exception:
        logger.warning(
            "active tenant session persister raised resolving current version", exc_info=True
        )
        raise _session_context_unavailable() from None


def require_current_tenant_session_version(
    *,
    current_version: str,
    expected_version: str,
) -> None:
    try:
        current_version = canonical_tenant_session_version(current_version)
        expected_version = canonical_tenant_session_version(expected_version)
    except ValueError:
        raise _tenant_session_changed() from None
    if not hmac.compare_digest(current_version, expected_version):
        raise _tenant_session_changed()


def _persist_session_keyed_selection(
    *,
    request: Request,
    auth_session_key_hash: str,
    selected_tenant: TenantContext,
    expected_tenant_session_version: str,
) -> str:
    """AC-2/AC-3: CAS-write the switch onto the same SaasAuthSessionRow the
    cookie-fallback identity resolver reads active_tenant_id from, so the very
    next request (which rebuilds VerifiedTenantClaim from that row) sees the
    new tenant without needing a reissued token. No separate version cookie
    is set here -- the presented Kj-Atlas-Auth-Session cookie is already the
    binding, and the new version is returned in the JSON body like the
    principal-keyed path.
    """
    store = _session_keyed_auth_store(request, unavailable=_active_tenant_update_unavailable)
    expected = canonical_tenant_session_version(expected_tenant_session_version)
    new_version = canonical_tenant_session_version(_new_session_version())
    try:
        rotated = store.rotate_active_tenant(
            session_key_hash=auth_session_key_hash,
            expected_version=expected,
            new_active_tenant_id=selected_tenant.tenant_id,
            new_version=new_version,
        )
    except Exception:
        logger.warning("auth session store raised persisting active tenant", exc_info=True)
        raise _active_tenant_update_unavailable() from None
    if not rotated:
        raise _tenant_session_changed()
    return new_version


def persist_active_tenant_selection(
    *,
    request: Request,
    response: Response,
    principal_id: str,
    previous_tenant: TenantContext,
    selected_tenant: TenantContext,
    expected_tenant_session_version: str,
    auth_session_key_hash: str | None = None,
) -> str:
    if auth_session_key_hash is not None:
        return _persist_session_keyed_selection(
            request=request,
            auth_session_key_hash=auth_session_key_hash,
            selected_tenant=selected_tenant,
            expected_tenant_session_version=expected_tenant_session_version,
        )
    persister = getattr(request.app.state, "active_tenant_session_persister", None)
    if persister is None:
        raise _active_tenant_update_unavailable()
    try:
        next_version = cast(ActiveTenantSessionPersister, persister).persist(
            request=request,
            response=response,
            principal_id=principal_id,
            previous_tenant=previous_tenant,
            selected_tenant=selected_tenant,
            expected_tenant_session_version=expected_tenant_session_version,
        )
        next_version = canonical_tenant_session_version(next_version)
        if hmac.compare_digest(expected_tenant_session_version, next_version):
            raise ValueError("tenant session version did not change")
        return next_version
    except TenantSessionChangedError:
        raise _tenant_session_changed() from None
    except HTTPException:
        raise
    except Exception:
        logger.warning("active tenant session persister raised persisting selection", exc_info=True)
        raise _active_tenant_update_unavailable() from None


def _new_session_version() -> str:
    """Generate a token accepted by the stricter header/cookie canonical form."""
    # token_urlsafe may start with '-' or '_', while our canonical external
    # representation deliberately starts with an alphanumeric character.
    # Rejection sampling preserves the token format and essentially all entropy.
    while True:
        candidate = secrets.token_urlsafe(32)
        if _TENANT_SESSION_VERSION_PATTERN.fullmatch(candidate) is not None:
            return candidate


def tenant_session_cookie_is_secure(runtime_profile: str) -> bool:
    """Only the explicitly local HTTP profile may emit a non-Secure cookie."""
    return runtime_profile.strip().lower() != "local-dev"


class InMemoryActiveTenantSessionPersister:
    """ADR-0063 D9-6: thread-safe in-memory session persister for saas-multitenant.

    Stores per-principal session versions in a dict. persist() atomically
    compares the expected version before issuing a new one, and sets a
    session cookie (Kj-Atlas-Tenant-Session-Version) on the response.

    ADR-0064 D4: cookie-based session for mock/OAuth login flow.

    Production upgrade path (ADR-0064 Phase 3): Replace with a Redis or
    database-backed implementation that:
    - Persists sessions across process restarts
    - Supports horizontal scaling (shared session store)
    - Signs/encrypts the session cookie (currently plain token_urlsafe)
    - Adds CSRF token binding (currently SameSite=strict cookie only)
    """

    _COOKIE_KEY = "Kj-Atlas-Tenant-Session-Version"

    def __init__(self, *, secure_cookie: bool = False) -> None:
        self._sessions: dict[str, str] = {}
        self._lock = Lock()
        self._secure_cookie = secure_cookie

    def current_version(
        self,
        *,
        request: Request,
        principal_id: str,
        active_tenant: TenantContext,
    ) -> str:
        with self._lock:
            stored_version = self._sessions.get(principal_id)
            if stored_version is not None:
                try:
                    canonical_tenant_session_version(stored_version)
                except ValueError:
                    # Rotate legacy/corrupted in-memory state instead of fixing
                    # the principal in a permanent 503 loop until restart.
                    stored_version = _new_session_version()
                    self._sessions[principal_id] = stored_version
            # ADR-0064: try to read existing session from cookie first.
            try:
                cookie_version = request.cookies.get(self._COOKIE_KEY)
                if cookie_version and stored_version is not None:
                    if hmac.compare_digest(cookie_version, stored_version):
                        return stored_version
            except (KeyError, AttributeError):
                pass
            if stored_version is None:
                stored_version = _new_session_version()
                self._sessions[principal_id] = stored_version
            return stored_version

    def persist(
        self,
        *,
        request: Request,
        response: Response,
        principal_id: str,
        previous_tenant: TenantContext,
        selected_tenant: TenantContext,
        expected_tenant_session_version: str,
    ) -> str:
        with self._lock:
            current = self._sessions.get(principal_id)
            if current is not None and not hmac.compare_digest(
                current, expected_tenant_session_version
            ):
                raise TenantSessionChangedError("tenant session version mismatch")
            # Validate before mutating server state or issuing the cookie. This
            # keeps a faulty future generator from persisting a poison version.
            new_version = canonical_tenant_session_version(_new_session_version())
            self._sessions[principal_id] = new_version
            # ADR-0064 D4: set session cookie on the response.
            response.set_cookie(
                key=self._COOKIE_KEY,
                value=new_version,
                httponly=True,
                secure=self._secure_cookie,
                samesite="strict",
                max_age=3600,
                path="/",
            )
            return new_version

    def clear(self, *, request: Request, response: Response) -> None:
        """Invalidate a presented version and expire its browser binding."""
        cookie_version = request.cookies.get(self._COOKIE_KEY)
        if cookie_version:
            with self._lock:
                matching_principals = [
                    principal_id
                    for principal_id, version in self._sessions.items()
                    if hmac.compare_digest(cookie_version, version)
                ]
                for principal_id in matching_principals:
                    del self._sessions[principal_id]
        response.delete_cookie(
            key=self._COOKIE_KEY,
            httponly=True,
            secure=self._secure_cookie,
            samesite="strict",
            path="/",
        )


class DatabaseActiveTenantSessionPersister:
    """Cluster-wide tenant-session version persistence for SaaS runtimes."""

    _COOKIE_KEY = InMemoryActiveTenantSessionPersister._COOKIE_KEY

    def __init__(
        self,
        *,
        store: DatabaseSaasAuthStateStore,
        secure_cookie: bool = True,
    ) -> None:
        self._store = store
        self._secure_cookie = secure_cookie

    def current_version(
        self,
        *,
        request: Request,
        principal_id: str,
        active_tenant: TenantContext,
    ) -> str:
        version = self._store.current_or_create_session_version(
            principal_id=principal_id,
            new_version=_new_session_version(),
        )
        return canonical_tenant_session_version(version)

    def persist(
        self,
        *,
        request: Request,
        response: Response,
        principal_id: str,
        previous_tenant: TenantContext,
        selected_tenant: TenantContext,
        expected_tenant_session_version: str,
    ) -> str:
        expected = canonical_tenant_session_version(expected_tenant_session_version)
        new_version = canonical_tenant_session_version(_new_session_version())
        if not self._store.rotate_session_version(
            principal_id=principal_id,
            expected_version=expected,
            new_version=new_version,
        ):
            raise TenantSessionChangedError("tenant session version mismatch")
        response.set_cookie(
            key=self._COOKIE_KEY,
            value=new_version,
            httponly=True,
            secure=self._secure_cookie,
            samesite="strict",
            max_age=3600,
            path="/",
        )
        return new_version

    def clear(self, *, request: Request, response: Response) -> None:
        cookie_version = request.cookies.get(self._COOKIE_KEY)
        if cookie_version:
            try:
                canonical_tenant_session_version(cookie_version)
            except ValueError:
                pass
            else:
                self._store.clear_session_version(session_version=cookie_version)
        response.delete_cookie(
            key=self._COOKIE_KEY,
            httponly=True,
            secure=self._secure_cookie,
            samesite="strict",
            path="/",
        )


def clear_active_tenant_session_cookie(*, request: Request, response: Response) -> None:
    persister = getattr(request.app.state, "active_tenant_session_persister", None)
    if persister is None:
        raise _active_tenant_update_unavailable()
    try:
        cast(ActiveTenantSessionPersister, persister).clear(
            request=request,
            response=response,
        )
    except HTTPException:
        raise
    except Exception:
        logger.warning(
            "active tenant session persister raised clearing cookie",
            exc_info=True,
        )
        raise _active_tenant_update_unavailable() from None
