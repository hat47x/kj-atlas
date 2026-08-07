from __future__ import annotations

import json
from typing import cast
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from kj_atlas_api.db import get_db
from kj_atlas_api.inquiry_bundle_repository import (
    delete_inquiry_bundle,
    get_inquiry_bundle_row,
)
from kj_atlas_api.models import InquiryBundleDeletionAuditEventRow, InquiryBundleRow
from kj_atlas_api.saas_request_context import resolve_trusted_saas_request_session
from kj_atlas_api.tenant_session_precondition import (
    require_tenant_session_request_precondition,
)


router = APIRouter(prefix="/inquiry-bundles", tags=["inquiry-bundles"])
MAX_INQUIRY_BUNDLE_PAYLOAD_BYTES = 5 * 1024 * 1024
MAX_JOURNEY_ID_LENGTH = 256


def _canonical_journey_id(journey_id: str) -> str:
    if (
        not journey_id
        or len(journey_id) > MAX_JOURNEY_ID_LENGTH
        or journey_id.strip() != journey_id
        or not journey_id.isprintable()
    ):
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_journey_id", "message": "journey_id is required."},
        )
    return journey_id


def _serialize_opaque_payload(payload: object) -> str:
    try:
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_inquiry_bundle", "message": "Inquiry bundle must be JSON."},
        ) from None
    if len(encoded.encode("utf-8")) > MAX_INQUIRY_BUNDLE_PAYLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "inquiry_bundle_too_large",
                "message": "Inquiry bundle exceeds the storage size limit.",
            },
        )
    return encoded


def _trusted_session(*, request: Request, db: Session):
    """Use only server-resolved identity and tenant evidence; never request input."""
    trusted_session = resolve_trusted_saas_request_session(request=request, db=db)
    require_tenant_session_request_precondition(
        request=request,
        current_version=trusted_session.session.tenant_session_version,
    )
    return trusted_session


@router.post("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
def put_inquiry_bundle(
    journey_id: str,
    request: Request,
    payload: object = Body(...),
    db: Session = Depends(get_db),
) -> Response:
    journey_id = _canonical_journey_id(journey_id)
    payload_json = _serialize_opaque_payload(payload)
    trusted_session = _trusted_session(request=request, db=db)
    existing = get_inquiry_bundle_row(
        db, tenant=trusted_session.tenant, journey_id=journey_id
    )
    recorded_at = datetime.now(timezone.utc).isoformat()
    if existing is None:
        db.add(
            InquiryBundleRow(
                tenant_id=trusted_session.tenant.tenant_id,
                journey_id=journey_id,
                payload_json=payload_json,
                updated_at=recorded_at,
            )
        )
    else:
        existing.payload_json = payload_json
        existing.updated_at = recorded_at
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{journey_id}")
def get_inquiry_bundle(
    journey_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> object:
    journey_id = _canonical_journey_id(journey_id)
    trusted_session = _trusted_session(request=request, db=db)
    row = get_inquiry_bundle_row(db, tenant=trusted_session.tenant, journey_id=journey_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Inquiry bundle not found")
    return json.loads(row.payload_json)


@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inquiry_bundle_route(
    journey_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    journey_id = _canonical_journey_id(journey_id)
    trusted_session = _trusted_session(request=request, db=db)
    if not delete_inquiry_bundle(db, tenant=trusted_session.tenant, journey_id=journey_id):
        db.rollback()
        raise HTTPException(status_code=404, detail="Inquiry bundle not found")

    # The row deletion and this deliberately content-free evidence share one DB
    # transaction, so neither can succeed without the other.
    db.add(
        InquiryBundleDeletionAuditEventRow(
            event_id=f"audit-{uuid4()}",
            tenant_id=trusted_session.tenant.tenant_id,
            journey_id=journey_id,
            principal_id=cast(str, trusted_session.identity.user_id),
            action="inquiry_bundle.delete",
            outcome="deleted",
            occurred_at=datetime.now(timezone.utc).isoformat(),
        )
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
