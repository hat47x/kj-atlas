from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from kj_atlas_api.db import get_db
from kj_atlas_api.saas_request_context import resolve_trusted_saas_request_session
from kj_atlas_api.tenant_context import TenantSummary


router = APIRouter(prefix="/session", tags=["session"])


class TenantSessionSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    displayName: str


class TenantSessionContextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principalId: str
    activeTenant: TenantSessionSummaryResponse
    availableTenants: list[TenantSessionSummaryResponse]
    effectiveCapabilities: list[str]
    capabilityVersion: str


def _tenant_summary(tenant: TenantSummary) -> TenantSessionSummaryResponse:
    return TenantSessionSummaryResponse(
        id=tenant.tenant_id,
        displayName=tenant.display_name,
    )


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
    except HTTPException as error:
        error.headers = {
            **(error.headers or {}),
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        raise
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return TenantSessionContextResponse(
        principalId=trusted_session.session.principal_id,
        activeTenant=_tenant_summary(trusted_session.session.active_tenant),
        availableTenants=[
            _tenant_summary(tenant)
            for tenant in trusted_session.session.available_tenants
        ],
        effectiveCapabilities=list(
            trusted_session.session.effective_capabilities
        ),
        capabilityVersion=trusted_session.session.capability_version,
    )
