from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response
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
    provisioned: bool


def _normalize_optional_field(raw: str | None) -> str | None:
    if raw is None:
        return None
    normalized = raw.strip()
    return normalized or None


@router.post("/users", response_model=ProvisionUserResponse, status_code=201)
def provision_user(
    payload: ProvisionUserRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> ProvisionUserResponse:
    provider = payload.provider.strip()
    external_uid = payload.externalUid.strip()
    display_name = _normalize_optional_field(payload.displayName)
    email = _normalize_optional_field(payload.email)
    if not provider or not external_uid:
        raise HTTPException(status_code=400, detail="provider and externalUid must be non-empty")

    identity = (
        db.query(UserIdentityRow)
        .filter(UserIdentityRow.provider == provider, UserIdentityRow.external_uid == external_uid)
        .one_or_none()
    )
    if identity is not None:
        user_row = db.get(UserRow, identity.user_id)
        if user_row is None:
            raise HTTPException(status_code=409, detail={"code": "identity_user_not_found"})

        if display_name is not None and user_row.display_name not in {None, display_name}:
            raise HTTPException(status_code=409, detail={"code": "identity_already_provisioned_conflict"})
        if email is not None and user_row.email not in {None, email}:
            raise HTTPException(status_code=409, detail={"code": "identity_already_provisioned_conflict"})

        user_id = user_row.id
        reviewer_ref = f"user:{user_id}"
        response.status_code = 200
        return ProvisionUserResponse(userId=user_id, reviewerRef=reviewer_ref, ownerRef=reviewer_ref, provisioned=False)

    user_id = str(uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
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
            created_at=now_iso,
        )
    )
    db.commit()

    reviewer_ref = f"user:{user_id}"
    return ProvisionUserResponse(userId=user_id, reviewerRef=reviewer_ref, ownerRef=reviewer_ref, provisioned=True)
