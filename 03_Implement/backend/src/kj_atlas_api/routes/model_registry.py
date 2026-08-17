"""AI-MODEL-GOVERNANCE-01 R1/R3: admin-plane model/provider registry + tenant
allowlist management.

Control-plane authorized (require_control_plane_authorization): a business
credential alone cannot register or disable a model. Secrets are accepted as
`api_key_ref` references only -- never a plaintext key.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kj_atlas_api.control_plane_auth import require_control_plane_authorization
from kj_atlas_api.db import get_db
from kj_atlas_api.model_registry_repository import (
    create_model as persist_new_model,
    create_provider as persist_new_provider,
    list_models,
    list_providers,
    list_tenant_allowed_model_ids,
    set_model_lifecycle,
    set_tenant_model_allowlist,
)
from kj_atlas_api.models import TenantRow

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

    @field_validator("apiKeyRef")
    @classmethod
    def _api_key_ref_must_be_a_reference(cls, v: str | None) -> str | None:
        """AI-MODEL-GOVERNANCE-03 AC-4: apiKeyRef must be a reference to an
        allowlisted `KJ_ATLAS_*` env var or a `secret:` secret-manager key --
        never an arbitrary env-var name or a plaintext secret. This keeps
        plaintext keys out of the registry column (DB), so they cannot leak to
        API/logs/audit downstream."""
        if v is None:
            return v
        if re.fullmatch(r"KJ_ATLAS_[A-Z][A-Z0-9_]*", v) or re.fullmatch(r"secret:[A-Za-z0-9._/:-]+", v):
            return v
        raise ValueError(
            "apiKeyRef must reference an allowlisted KJ_ATLAS_* env var or a "
            "'secret:' secret-manager key -- never a plaintext key"
        )


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
    expectedRevision: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


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
    persist_new_provider(
        db,
        provider_id=payload.id,
        provider_kind=payload.providerKind,
        display_name=payload.displayName,
        base_url=payload.baseUrl,
        api_key_ref=payload.apiKeyRef,
        occurred_at=occurred_at,
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "code": "provider_already_exists",
                "message": "A provider with this id already exists.",
            },
        ) from None
    return {"status": "created", "id": payload.id}


@router.post("", status_code=201)
def create_model(payload: RegisterModelRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    """Dynamically register a model under an existing provider."""
    providers = list_providers(db)
    if not any(row.id == payload.providerId for row in providers):
        raise HTTPException(status_code=404, detail="provider not found")
    persist_new_model(
        db,
        model_id=payload.id,
        provider_id=payload.providerId,
        display_name=payload.displayName,
        capabilities=payload.capabilities,
        occurred_at=_now_iso(),
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "code": "model_already_exists",
                "message": "A model with this id already exists.",
            },
        ) from None
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
    _require_active_tenant(db, tenant_id=tenant_id)
    model_ids = sorted(list_tenant_allowed_model_ids(db, tenant_id=tenant_id))
    return {
        "tenantId": tenant_id,
        "modelIds": model_ids,
        "revision": _allowlist_revision(model_ids),
    }


@router.put("/tenants/{tenant_id}/allowlist")
def put_tenant_allowlist(
    tenant_id: str,
    payload: SetTenantAllowlistRequest,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    _require_active_tenant(db, tenant_id=tenant_id, lock_for_update=True)
    current_model_ids = sorted(list_tenant_allowed_model_ids(db, tenant_id=tenant_id))
    current_revision = _allowlist_revision(current_model_ids)
    if payload.expectedRevision is not None and payload.expectedRevision != current_revision:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "model_allowlist_conflict",
                "message": "The tenant model allowlist changed after it was read.",
                "currentRevision": current_revision,
            },
        )
    duplicate_model_ids = sorted(
        model_id for model_id in set(payload.modelIds) if payload.modelIds.count(model_id) > 1
    )
    if duplicate_model_ids:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "duplicate_model_ids",
                "message": "The model allowlist must not contain duplicate model ids.",
                "modelIds": duplicate_model_ids,
            },
        )

    models_by_id = {row.id: row for row in list_models(db)}
    unknown_model_ids = sorted(model_id for model_id in payload.modelIds if model_id not in models_by_id)
    inactive_model_ids = sorted(
        model_id
        for model_id in payload.modelIds
        if model_id in models_by_id and models_by_id[model_id].lifecycle_state != "active"
    )
    if unknown_model_ids or inactive_model_ids:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "invalid_model_allowlist",
                "message": "Every allowlisted model must be registered and active.",
                "unknownModelIds": unknown_model_ids,
                "inactiveModelIds": inactive_model_ids,
            },
        )

    set_tenant_model_allowlist(
        db,
        tenant_id=tenant_id,
        model_ids=payload.modelIds,
        occurred_at=_now_iso(),
    )
    db.commit()
    updated_model_ids = sorted(payload.modelIds)
    return {
        "tenantId": tenant_id,
        "modelIds": updated_model_ids,
        "revision": _allowlist_revision(updated_model_ids),
    }


def _allowlist_revision(model_ids: list[str]) -> str:
    canonical = "\n".join(sorted(model_ids)).encode("utf-8")
    return sha256(canonical).hexdigest()


def _require_active_tenant(
    db: Session,
    *,
    tenant_id: str,
    lock_for_update: bool = False,
) -> TenantRow:
    if lock_for_update:
        tenant = db.scalar(
            select(TenantRow).where(TenantRow.id == tenant_id).with_for_update()
        )
    else:
        tenant = db.get(TenantRow, tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "tenant_not_found", "message": "Tenant not found."},
        )
    if tenant.lifecycle_state != "active":
        raise HTTPException(
            status_code=409,
            detail={"code": "tenant_not_active", "message": "Tenant is not active."},
        )
    return tenant
