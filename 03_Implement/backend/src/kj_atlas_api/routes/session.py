from __future__ import annotations

from dataclasses import replace

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from kj_atlas_api.active_tenant_session import (
    MAX_TENANT_SESSION_VERSION_LENGTH,
    clear_active_tenant_session_cookie,
    persist_active_tenant_selection,
    require_current_tenant_session_version,
)
from kj_atlas_api.db import get_db
from kj_atlas_api.runtime_bootstrap import (
    TenantSessionBootstrapMode,
    resolve_tenant_session_bootstrap_mode,
)
from kj_atlas_api.saas_request_context import resolve_trusted_saas_request_session
from kj_atlas_api.session_context import (
    KNOWN_EFFECTIVE_CAPABILITIES,
    MAX_SESSION_CAPABILITY_VERSION_LENGTH,
    MAX_SESSION_DISPLAY_NAME_LENGTH,
    MAX_SESSION_IDENTIFIER_LENGTH,
    MAX_SESSION_RESPONSE_BYTES,
    MAX_SESSION_TENANT_COUNT,
    TenantSessionContext,
    switch_tenant_session_context,
)
from kj_atlas_api.tenant_context import TenantSummary


router = APIRouter(prefix="/session", tags=["session"])


class TenantSessionBootstrapPolicyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantSessionMode: TenantSessionBootstrapMode


class TenantSessionSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=MAX_SESSION_IDENTIFIER_LENGTH)
    displayName: str = Field(min_length=1, max_length=MAX_SESSION_DISPLAY_NAME_LENGTH)


class TenantSessionContextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principalId: str = Field(min_length=1, max_length=MAX_SESSION_IDENTIFIER_LENGTH)
    activeTenant: TenantSessionSummaryResponse
    availableTenants: list[TenantSessionSummaryResponse] = Field(
        min_length=1,
        max_length=MAX_SESSION_TENANT_COUNT,
    )
    effectiveCapabilities: list[str] = Field(
        max_length=len(KNOWN_EFFECTIVE_CAPABILITIES),
    )
    capabilityVersion: str = Field(
        min_length=1,
        max_length=MAX_SESSION_CAPABILITY_VERSION_LENGTH,
    )
    tenantSessionVersion: str = Field(
        min_length=1,
        max_length=MAX_TENANT_SESSION_VERSION_LENGTH,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._~-]{0,127}$",
    )


class ActiveTenantRequestV1(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    tenantId: str
    expectedTenantSessionVersion: str = Field(
        min_length=1,
        max_length=MAX_TENANT_SESSION_VERSION_LENGTH,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._~-]{0,127}$",
    )


def _tenant_summary(tenant: TenantSummary) -> TenantSessionSummaryResponse:
    return TenantSessionSummaryResponse(
        id=tenant.tenant_id,
        displayName=tenant.display_name,
    )


def _session_response(request_session: TenantSessionContext) -> TenantSessionContextResponse:
    session_response = TenantSessionContextResponse(
        principalId=request_session.principal_id,
        activeTenant=_tenant_summary(request_session.active_tenant),
        availableTenants=[_tenant_summary(tenant) for tenant in request_session.available_tenants],
        effectiveCapabilities=list(request_session.effective_capabilities),
        capabilityVersion=request_session.capability_version,
        tenantSessionVersion=request_session.tenant_session_version,
    )
    if len(session_response.model_dump_json().encode("utf-8")) > MAX_SESSION_RESPONSE_BYTES:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "session_context_unavailable",
                "message": "Tenant session context is unavailable.",
            },
        )
    return session_response


@router.get(
    "/bootstrap-policy",
    response_model=TenantSessionBootstrapPolicyResponse,
)
def get_session_bootstrap_policy(
    request: Request,
    response: Response,
) -> TenantSessionBootstrapPolicyResponse:
    no_cache_headers = {
        "Cache-Control": "no-store",
        "Pragma": "no-cache",
    }
    try:
        policy = TenantSessionBootstrapPolicyResponse(
            tenantSessionMode=resolve_tenant_session_bootstrap_mode(
                request.app.state.runtime_profile
            ),
        )
    except (AttributeError, RuntimeError):
        raise HTTPException(
            status_code=503,
            detail={
                "code": "runtime_policy_unavailable",
                "message": "Runtime policy is unavailable.",
            },
            headers=no_cache_headers,
        ) from None
    response.headers.update(no_cache_headers)
    return policy


@router.post("/logout", status_code=204)
def logout_session(request: Request, response: Response) -> None:
    """Expire the app tenant-session cookie without requiring a live JWT."""
    clear_active_tenant_session_cookie(request=request, response=response)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


@router.get("/context", response_model=TenantSessionContextResponse)
def get_session_context(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TenantSessionContextResponse:
    try:
        trusted_session = resolve_trusted_saas_request_session(
            request=request,
            db=db,
        )
        session_response = _session_response(trusted_session.session)
    except HTTPException as error:
        error.headers = {
            **(error.headers or {}),
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        raise
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return session_response


@router.post("/active-tenant", response_model=TenantSessionContextResponse)
def change_active_tenant(
    payload: ActiveTenantRequestV1,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TenantSessionContextResponse:
    try:
        trusted_session = resolve_trusted_saas_request_session(
            request=request,
            db=db,
        )
        require_current_tenant_session_version(
            current_version=trusted_session.session.tenant_session_version,
            expected_version=payload.expectedTenantSessionVersion,
        )
        selected_session = switch_tenant_session_context(
            db=db,
            principal_id=trusted_session.session.principal_id,
            current_tenant=trusted_session.tenant,
            requested_tenant_id=payload.tenantId,
            capability_resolver=getattr(
                request.app.state,
                "tenant_capability_resolver",
                None,
            ),
            tenant_session_version=trusted_session.session.tenant_session_version,
        )
        # Check the worst-case response size before the auth adapter mutates
        # session state. The opaque version uses an ASCII-only 128-byte bound.
        _session_response(
            replace(
                selected_session,
                tenant_session_version="x" * MAX_TENANT_SESSION_VERSION_LENGTH,
            )
        )
        next_version = persist_active_tenant_selection(
            request=request,
            response=response,
            principal_id=trusted_session.session.principal_id,
            previous_tenant=trusted_session.tenant,
            selected_tenant=selected_session.tenant_context,
            expected_tenant_session_version=payload.expectedTenantSessionVersion,
        )
        session_response = _session_response(
            replace(selected_session, tenant_session_version=next_version)
        )
    except HTTPException as error:
        error.headers = {
            **(error.headers or {}),
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        raise
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return session_response
