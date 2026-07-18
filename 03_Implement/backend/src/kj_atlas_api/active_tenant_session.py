from __future__ import annotations

from typing import Protocol, cast

from fastapi import HTTPException, Request, Response

from kj_atlas_api.tenant_context import TenantContext


class ActiveTenantSessionPersister(Protocol):
    """Persist a server-validated tenant selection in the trusted auth session.

    Implementations own anti-forgery validation and the auth-edge-specific session
    format. They must bind the selected tenant to ``principal_id`` and must not read
    a tenant identifier from request headers, query parameters, or the raw body.
    """

    def persist(
        self,
        *,
        request: Request,
        response: Response,
        principal_id: str,
        previous_tenant: TenantContext,
        selected_tenant: TenantContext,
    ) -> None:
        ...


def _active_tenant_update_unavailable() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "code": "active_tenant_update_unavailable",
            "message": "Active tenant update is unavailable.",
        },
    )


def persist_active_tenant_selection(
    *,
    request: Request,
    response: Response,
    principal_id: str,
    previous_tenant: TenantContext,
    selected_tenant: TenantContext,
) -> None:
    persister = getattr(request.app.state, "active_tenant_session_persister", None)
    if persister is None:
        raise _active_tenant_update_unavailable()
    try:
        cast(ActiveTenantSessionPersister, persister).persist(
            request=request,
            response=response,
            principal_id=principal_id,
            previous_tenant=previous_tenant,
            selected_tenant=selected_tenant,
        )
    except HTTPException:
        raise
    except Exception:
        raise _active_tenant_update_unavailable() from None
