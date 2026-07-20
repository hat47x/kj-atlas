from __future__ import annotations

import hmac
import logging
import re
from typing import Protocol, cast

from fastapi import HTTPException, Request, Response

from kj_atlas_api.tenant_context import TenantContext

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
    ) -> str:
        ...

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
        ...


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


def resolve_active_tenant_session_version(
    *,
    request: Request,
    principal_id: str,
    active_tenant: TenantContext,
) -> str:
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
        logger.warning("Failed to resolve current tenant session version", exc_info=True)
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


def persist_active_tenant_selection(
    *,
    request: Request,
    response: Response,
    principal_id: str,
    previous_tenant: TenantContext,
    selected_tenant: TenantContext,
    expected_tenant_session_version: str,
) -> str:
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
        logger.warning("Failed to advance tenant session version", exc_info=True)
        raise _active_tenant_update_unavailable() from None
