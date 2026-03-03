from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from kj_atlas_api.db import get_db
from kj_atlas_api.models import UserIdentityRow, UserRow

router = APIRouter(prefix="/admin/provision", tags=["admin"])


class ProvisionUserRequest(BaseModel):
    provider: str
    externalUid: str
    displayName: str | None = None
    email: str | None = None


class ProvisionUserResponse(BaseModel):
    userId: str
    reviewerRef: str
    ownerRef: str


@router.post("/users", response_model=ProvisionUserResponse)
def provision_user(payload: ProvisionUserRequest, db: Session = Depends(get_db)) -> ProvisionUserResponse:
    provider = payload.provider.strip()
    external_uid = payload.externalUid.strip()
    if not provider or not external_uid:
        raise HTTPException(status_code=400, detail="provider and externalUid must be non-empty")

    identity = (
        db.query(UserIdentityRow)
        .filter(UserIdentityRow.provider == provider, UserIdentityRow.external_uid == external_uid)
        .one_or_none()
    )
    if identity is not None:
        user_id = identity.user_id
        reviewer_ref = f"user:{user_id}"
        return ProvisionUserResponse(userId=user_id, reviewerRef=reviewer_ref, ownerRef=reviewer_ref)

    user_id = str(uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    user_row = UserRow(
        id=user_id,
        display_name=payload.displayName.strip() if payload.displayName else None,
        email=payload.email.strip() if payload.email else None,
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
            created_at=now_iso,
        )
    )
    db.commit()

    reviewer_ref = f"user:{user_id}"
    return ProvisionUserResponse(userId=user_id, reviewerRef=reviewer_ref, ownerRef=reviewer_ref)
