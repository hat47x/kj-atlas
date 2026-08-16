"""AI-MODEL-GOVERNANCE-01 R1/R3: admin-plane model/provider registry + tenant
allowlist management.

Control-plane authorized (require_control_plane_authorization): a business
credential alone cannot register or disable a model. Secrets are accepted as
`api_key_ref` references only -- never a plaintext key.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from kj_atlas_api.control_plane_auth import require_control_plane_authorization
from kj_atlas_api.db import get_db
from kj_atlas_api.model_registry_repository import (
    list_models,
    list_providers,
    list_tenant_allowed_model_ids,
    register_model,
    register_provider,
    set_model_lifecycle,
    set_tenant_model_allowlist,
)

router = APIRouter(
    prefix="/admin/provision/models",
    tags=["admin"],
    dependencies=[Depends(require_control_plane_authorization)],
)

_MODEL_ID_PATTERN = r"^[A-Za-z0-9._:/-]{1,256}$"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RegisterProviderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    providerKind: str = Field(min_length=1, max_length=64)
    displayName: str = Field(min_length=1, max_length=256)
    baseUrl: str | None = Field(default=None, max_length=2048)
    # Reference only (env var / secret-manager key), never a plaintext value.
    apiKeyRef: str | None = Field(default=None, max_length=256)


class RegisterModelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=_MODEL_ID_PATTERN)
    providerId: str = Field(min_length=1, max_length=128)
    displayName: str = Field(min_length=1, max_length=256)
    capabilities: str | None = Field(default=None, max_length=256)


class SetModelLifecycleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lifecycleState: str = Field(pattern="^(active|disabled)$")


class SetTenantAllowlistRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modelIds: list[str] = Field(max_length=500)


class ProviderItem(BaseModel):
    id: str
    providerKind: str
    displayName: str
    lifecycleState: str


class ModelItem(BaseModel):
    id: str
    providerId: str
    displayName: str
    capabilities: str | None = None
    lifecycleState: str


class RegistryListResponse(BaseModel):
    providers: list[ProviderItem]
    models: list[ModelItem]


@router.get("", response_model=RegistryListResponse)
def list_model_registry(db: Session = Depends(get_db)) -> RegistryListResponse:
    """List registered providers and models (admin UI/CLI)."""
    return RegistryListResponse(
        providers=[
            ProviderItem(
                id=row.id,
                providerKind=row.provider_kind,
                displayName=row.display_name,
                lifecycleState=row.lifecycle_state,
            )
            for row in list_providers(db)
        ],
        models=[
            ModelItem(
                id=row.id,
                providerId=row.provider_id,
                displayName=row.display_name,
                capabilities=row.capabilities,
                lifecycleState=row.lifecycle_state,
            )
            for row in list_models(db)
        ],
    )


@router.post("/providers", status_code=201)
def create_provider(payload: RegisterProviderRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    """Dynamically register a new model service (provider)."""
    occurred_at = _now_iso()
    register_provider(
        db,
        provider_id=payload.id,
        provider_kind=payload.providerKind,
        display_name=payload.displayName,
        base_url=payload.baseUrl,
        api_key_ref=payload.apiKeyRef,
        occurred_at=occurred_at,
    )
    db.commit()
    return {"status": "created", "id": payload.id}


@router.post("", status_code=201)
def create_model(payload: RegisterModelRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    """Dynamically register a model under an existing provider."""
    providers = list_providers(db)
    if not any(row.id == payload.providerId for row in providers):
        raise HTTPException(status_code=404, detail="provider not found")
    register_model(
        db,
        model_id=payload.id,
        provider_id=payload.providerId,
        display_name=payload.displayName,
        capabilities=payload.capabilities,
        occurred_at=_now_iso(),
    )
    db.commit()
    return {"status": "created", "id": payload.id}


@router.patch("/{model_id}")
def update_model_lifecycle(
    model_id: str,
    payload: SetModelLifecycleRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Disable/enable a model. Disabled models are fail-closed on call."""
    occurred_at = _now_iso()
    changed = set_model_lifecycle(db, model_id=model_id, lifecycle_state=payload.lifecycleState, occurred_at=occurred_at)
    if not changed:
        raise HTTPException(status_code=404, detail="model not found")
    db.commit()
    return {"status": "updated", "id": model_id}


@router.get("/tenants/{tenant_id}/allowlist")
def get_tenant_allowlist(tenant_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    model_ids = sorted(list_tenant_allowed_model_ids(db, tenant_id=tenant_id))
    return {"tenantId": tenant_id, "modelIds": model_ids}


@router.put("/tenants/{tenant_id}/allowlist")
def put_tenant_allowlist(
    tenant_id: str,
    payload: SetTenantAllowlistRequest,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    set_tenant_model_allowlist(db, tenant_id=tenant_id, model_ids=payload.modelIds, occurred_at=_now_iso())
    db.commit()
    return {"tenantId": tenant_id, "modelIds": sorted(payload.modelIds)}
