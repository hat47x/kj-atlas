from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from kj_atlas_api.db import get_db
from kj_atlas_api.identity_binding import (
    IdentityMappingConflictError,
    ensure_legacy_identity_provider,
    ensure_user_identity_binding,
    resolve_user_identity,
)
from kj_atlas_api.models import UserIdentityRow, UserRow
from kj_atlas_api.models import A2A3GateValidationRequest, A2A3GateValidationResponse
from kj_atlas_api.reviewer_ref import (
    ReviewerRefResolutionInput,
    build_reviewer_ref_resolver_adapter,
)
from kj_atlas_api.settings import settings
from kj_atlas_api.tenant_foundation import ensure_local_default_membership

router = APIRouter(prefix="/admin/provision", tags=["admin"])

_IDENTITY_CONFLICT_CODE = "identity_already_provisioned_conflict"
_IDENTITY_CONFLICT_MESSAGE = (
    "Identity already provisioned with conflicting profile attributes."
)


class ProvisionUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    externalUid: str
    displayName: str | None = None
    email: str | None = None


class ProvisionUserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    userId: str
    reviewerRef: str = Field(min_length=1, pattern=r"^user:")
    ownerRef: str = Field(min_length=1, pattern=r"^user:")
    provisioned: bool


def _normalize_provider(raw_provider: str) -> str:
    return raw_provider.strip().lower()


def _normalize_external_uid(raw_external_uid: str) -> str:
    return raw_external_uid.strip()


def _normalize_optional_field(raw: str | None) -> str | None:
    if raw is None:
        return None
    normalized = raw.strip()
    return normalized or None

def _resolve_identity_row(*, db: Session, provider: str, external_uid: str) -> UserIdentityRow | None:
    try:
        return resolve_user_identity(
            db=db,
            provider=provider,
            subject=external_uid,
        )
    except IdentityMappingConflictError:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "identity_mapping_conflict",
                "message": "Multiple identity mappings matched the same provider/externalUid pair.",
            },
        ) from None


@router.post("/users", response_model=ProvisionUserResponse, status_code=201)
def provision_user(
    payload: ProvisionUserRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> ProvisionUserResponse:
    reviewer_ref_adapter = build_reviewer_ref_resolver_adapter(
        adapter_name=settings.reviewer_ref_resolver_adapter
    )

    provider = _normalize_provider(payload.provider)
    external_uid = _normalize_external_uid(payload.externalUid)
    display_name = _normalize_optional_field(payload.displayName)
    email = _normalize_optional_field(payload.email)
    if not provider or not external_uid:
        raise HTTPException(
            status_code=400, detail="provider and externalUid must be non-empty"
        )

    identity = _resolve_identity_row(db=db, provider=provider, external_uid=external_uid)
    if identity is not None:
        user_row = db.get(UserRow, identity.user_id)
        if user_row is None:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "identity_user_not_found",
                    "message": "Identity mapping exists but linked user record is missing.",
                },
            )

        if display_name is not None and user_row.display_name not in {
            None,
            display_name,
        }:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": _IDENTITY_CONFLICT_CODE,
                    "message": _IDENTITY_CONFLICT_MESSAGE,
                },
            )
        if email is not None and user_row.email not in {None, email}:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": _IDENTITY_CONFLICT_CODE,
                    "message": _IDENTITY_CONFLICT_MESSAGE,
                },
            )

        user_id = user_row.id
        resolution = reviewer_ref_adapter.resolve(
            ReviewerRefResolutionInput(
                user_id=user_id,
                provider=provider,
                external_uid=external_uid,
                actor_ref=None,
            )
        )
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            identity_binding_changed = ensure_user_identity_binding(
                db=db,
                identity=identity,
                provider=provider,
                subject=external_uid,
                timestamp=now_iso,
            )
        except IdentityMappingConflictError:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "identity_mapping_conflict",
                    "message": "Identity binding conflicts with the provider/subject pair.",
                },
            ) from None
        membership_changed = ensure_local_default_membership(
            db=db,
            user_id=user_id,
            timestamp=now_iso,
        )
        if identity_binding_changed or membership_changed:
            db.commit()
        response.status_code = 200
        return ProvisionUserResponse(
            userId=user_id,
            reviewerRef=resolution.reviewer_ref or f"user:{user_id}",
            ownerRef=resolution.owner_ref or f"user:{user_id}",
            provisioned=False,
        )

    user_id = str(uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    binding = ensure_legacy_identity_provider(
        db=db,
        provider=provider,
        timestamp=now_iso,
    )
    user_row = UserRow(
        id=user_id,
        display_name=display_name,
        email=email,
        lifecycle_state="active",
        created_at=now_iso,
        updated_at=now_iso,
    )
    db.add(user_row)
    db.add(
        UserIdentityRow(
            user_id=user_id,
            provider=provider,
            external_uid=external_uid,
            identity_provider_id=binding.identity_provider_id,
            subject=external_uid,
            created_at=now_iso,
        )
    )
    ensure_local_default_membership(
        db=db,
        user_id=user_id,
        timestamp=now_iso,
    )
    db.commit()

    resolution = reviewer_ref_adapter.resolve(
        ReviewerRefResolutionInput(
            user_id=user_id,
            provider=provider,
            external_uid=external_uid,
            actor_ref=None,
        )
    )
    return ProvisionUserResponse(
        userId=user_id,
        reviewerRef=resolution.reviewer_ref or f"user:{user_id}",
        ownerRef=resolution.owner_ref or f"user:{user_id}",
        provisioned=True,
    )


@router.post("/hil-rs/a2a3-gate:validate", response_model=A2A3GateValidationResponse)
def validate_a2_a3_gate(payload: A2A3GateValidationRequest) -> A2A3GateValidationResponse:
    frozen_values = {
        "freezeContractId": "HIL-RS-02-A1-CONTRACT-FREEZE-v1",
        "schemaVersion": "1.0.0",
        "overridePolicy": "human_dual_control_only",
        "contractLinkLocked": True,
        "sharedResourceFreeze": True,
        "a1Status": "Done",
        "pendingDecisionQueueCount": 0,
        "hasUndefinedContractChangeRequest": False,
        "hasSafeModeRegressionRequest": False,
        "hasShareExportLeakageRelaxationRequest": False,
    }
    payload_dict = payload.model_dump(mode="python")
    go = all(payload_dict[key] == value for key, value in frozen_values.items())
    if not go:
        raise HTTPException(status_code=409, detail="A2/A3 gate invariants violated")
    return A2A3GateValidationResponse(go=True)
