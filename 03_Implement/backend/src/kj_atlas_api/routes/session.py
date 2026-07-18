from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from kj_atlas_api.db import get_db
from kj_atlas_api.saas_request_context import resolve_trusted_saas_request_session
from kj_atlas_api.session_context import (
    KNOWN_EFFECTIVE_CAPABILITIES,
    MAX_SESSION_CAPABILITY_VERSION_LENGTH,
    MAX_SESSION_DISPLAY_NAME_LENGTH,
    MAX_SESSION_IDENTIFIER_LENGTH,
    MAX_SESSION_RESPONSE_BYTES,
    MAX_SESSION_TENANT_COUNT,
    TenantSessionContext,
)
from kj_atlas_api.tenant_context import TenantSummary


router = APIRouter(prefix="/session", tags=["session"])


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


def _tenant_summary(tenant: TenantSummary) -> TenantSessionSummaryResponse:
    return TenantSessionSummaryResponse(
        id=tenant.tenant_id,
        displayName=tenant.display_name,
    )


def _session_response(request_session: TenantSessionContext) -> TenantSessionContextResponse:
    session_response = TenantSessionContextResponse(
        principalId=request_session.principal_id,
        activeTenant=_tenant_summary(request_session.active_tenant),
        availableTenants=[
            _tenant_summary(tenant)
            for tenant in request_session.available_tenants
        ],
        effectiveCapabilities=list(request_session.effective_capabilities),
        capabilityVersion=request_session.capability_version,
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
