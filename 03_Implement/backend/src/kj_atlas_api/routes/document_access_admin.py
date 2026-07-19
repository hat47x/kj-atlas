from __future__ import annotations

import re
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal, cast
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError, model_validator
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kj_atlas_api.auth_context import ResolvedIdentity
from kj_atlas_api.db import get_db
from kj_atlas_api.document_access_metadata_repository import (
    DocumentAccessMetadataEntry,
    document_access_target_exists,
    get_document_access_metadata_row,
    list_document_access_metadata_entries,
)
from kj_atlas_api.models import (
    DocumentAccessAdminAuditEventRow,
    DocumentAccessMetadataRow,
)
from kj_atlas_api.saas_request_context import resolve_trusted_saas_request_session
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_session_precondition import (
    require_tenant_session_request_precondition,
)


router = APIRouter(prefix="/tenant-admin/document-access", tags=["tenant-admin"])

DOCUMENT_POLICY_MANAGE_CAPABILITY = "document.policy.manage"
Visibility = Literal["Public", "Unlisted", "Org", "Restricted"]
BindingStatus = Literal["unconfigured", "not_required", "configured"]
_OPAQUE_POLICY_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class DocumentAccessUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visibility: Visibility
    policyBindingId: str | None = Field(default=None, max_length=128)
    policyVersion: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_policy_binding(self) -> DocumentAccessUpdateRequest:
        if not _OPAQUE_POLICY_VALUE.fullmatch(self.policyVersion):
            raise ValueError("policyVersion must be an opaque canonical identifier")
        if self.policyBindingId is not None and not _OPAQUE_POLICY_VALUE.fullmatch(
            self.policyBindingId
        ):
            raise ValueError("policyBindingId must be an opaque canonical identifier")
        if self.visibility in {"Org", "Restricted"} and self.policyBindingId is None:
            raise ValueError("Org and Restricted require policyBindingId")
        if self.visibility in {"Public", "Unlisted"} and self.policyBindingId is not None:
            raise ValueError("Public and Unlisted must not persist a policy binding")
        return self


class DocumentAccessSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docId: str
    visibility: Visibility
    configured: bool
    bindingStatus: BindingStatus
    policyVersion: str | None
    updatedAt: str | None
    revision: str


class DocumentAccessDetail(DocumentAccessSummary):
    policyBindingId: str | None


class DocumentAccessListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    capabilityVersion: str
    items: list[DocumentAccessSummary]


class DocumentAccessUpdateReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    correlationId: str
    capabilityVersion: str
    recordedAt: str


class DocumentAccessUpdateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item: DocumentAccessDetail
    receipt: DocumentAccessUpdateReceipt


update_request_adapter: TypeAdapter[DocumentAccessUpdateRequest] = TypeAdapter(
    DocumentAccessUpdateRequest
)


def _error(*, status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def _authorize_document_policy_management(
    *,
    request: Request,
    db: Session,
) -> tuple[ResolvedIdentity, TenantContext, str]:
    trusted_session = resolve_trusted_saas_request_session(
        request=request,
        db=db,
    )
    require_tenant_session_request_precondition(
        request=request,
        current_version=trusted_session.session.tenant_session_version,
    )
    if (
        DOCUMENT_POLICY_MANAGE_CAPABILITY
        not in trusted_session.session.effective_capabilities
    ):
        raise _error(
            status_code=403,
            code="document_policy_manage_required",
            message="Document policy management capability is required.",
        )
    return (
        trusted_session.identity,
        trusted_session.tenant,
        trusted_session.session.capability_version,
    )


def _metadata_revision(
    *,
    tenant_id: str,
    doc_id: str,
    metadata: DocumentAccessMetadataRow | None,
) -> str:
    values = [tenant_id, doc_id, "unconfigured"]
    if metadata is not None:
        values = [
            tenant_id,
            doc_id,
            "configured",
            metadata.visibility,
            metadata.policy_binding_id or "",
            metadata.policy_version,
            metadata.updated_at,
        ]
    return sha256("\x00".join(values).encode("utf-8")).hexdigest()


def _binding_status(
    metadata: DocumentAccessMetadataRow | None,
) -> BindingStatus:
    if metadata is None:
        return "unconfigured"
    if metadata.visibility in {"Public", "Unlisted"}:
        return "not_required"
    return "configured"


def _summary(
    *,
    tenant_id: str,
    entry: DocumentAccessMetadataEntry,
) -> DocumentAccessSummary:
    metadata = entry.metadata
    visibility: Visibility = "Restricted"
    if metadata is not None:
        visibility = cast(Visibility, metadata.visibility)
    return DocumentAccessSummary(
        docId=entry.doc_id,
        visibility=visibility,
        configured=metadata is not None,
        bindingStatus=_binding_status(metadata),
        policyVersion=metadata.policy_version if metadata is not None else None,
        updatedAt=metadata.updated_at if metadata is not None else None,
        revision=_metadata_revision(
            tenant_id=tenant_id,
            doc_id=entry.doc_id,
            metadata=metadata,
        ),
    )


def _detail(
    *,
    tenant_id: str,
    doc_id: str,
    metadata: DocumentAccessMetadataRow | None,
) -> DocumentAccessDetail:
    summary = _summary(
        tenant_id=tenant_id,
        entry=DocumentAccessMetadataEntry(doc_id=doc_id, metadata=metadata),
    )
    return DocumentAccessDetail(
        **summary.model_dump(),
        policyBindingId=metadata.policy_binding_id if metadata is not None else None,
    )


def _etag(revision: str) -> str:
    return f'"{revision}"'


def _if_match_accepts(if_match: str, revision: str) -> bool:
    for raw_value in if_match.split(","):
        value = raw_value.strip()
        if value.startswith("W/"):
            value = value[2:].strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        if value == revision:
            return True
    return False


def _conflict() -> HTTPException:
    return _error(
        status_code=409,
        code="document_access_conflict",
        message="Document access settings changed. Reload before saving.",
    )


@router.get("", response_model=DocumentAccessListResponse)
def list_document_access_settings(
    request: Request,
    db: Session = Depends(get_db),
) -> DocumentAccessListResponse:
    _, tenant, capability_version = _authorize_document_policy_management(
        request=request,
        db=db,
    )
    entries = list_document_access_metadata_entries(db, tenant=tenant)
    return DocumentAccessListResponse(
        capabilityVersion=capability_version,
        items=[_summary(tenant_id=tenant.tenant_id, entry=entry) for entry in entries],
    )


@router.get("/{doc_id}", response_model=DocumentAccessDetail)
def get_document_access_settings(
    doc_id: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> DocumentAccessDetail:
    _, tenant, _ = _authorize_document_policy_management(request=request, db=db)
    if not document_access_target_exists(db, tenant=tenant, doc_id=doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    metadata = get_document_access_metadata_row(db, tenant=tenant, doc_id=doc_id)
    detail = _detail(
        tenant_id=tenant.tenant_id,
        doc_id=doc_id,
        metadata=metadata,
    )
    response.headers["ETag"] = _etag(detail.revision)
    return detail


@router.put("/{doc_id}", response_model=DocumentAccessUpdateResponse)
def put_document_access_settings(
    doc_id: str,
    request: Request,
    response: Response,
    payload: object = Body(...),
    if_match: str | None = Header(default=None, alias="If-Match"),
    db: Session = Depends(get_db),
) -> DocumentAccessUpdateResponse:
    identity, tenant, capability_version = _authorize_document_policy_management(
        request=request,
        db=db,
    )
    try:
        update_request = update_request_adapter.validate_python(payload)
    except ValidationError:
        raise _error(
            status_code=422,
            code="invalid_document_access_settings",
            message="Document access settings are invalid.",
        ) from None

    if not document_access_target_exists(db, tenant=tenant, doc_id=doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    current = get_document_access_metadata_row(db, tenant=tenant, doc_id=doc_id)
    current_revision = _metadata_revision(
        tenant_id=tenant.tenant_id,
        doc_id=doc_id,
        metadata=current,
    )
    if if_match is None:
        raise _error(
            status_code=428,
            code="document_access_precondition_required",
            message="If-Match is required for document access settings.",
        )
    if not _if_match_accepts(if_match, current_revision):
        raise _conflict()

    recorded_at = datetime.now(timezone.utc).isoformat()
    correlation_id = f"document-access-{uuid4()}"
    next_metadata = DocumentAccessMetadataRow(
        tenant_id=tenant.tenant_id,
        doc_id=doc_id,
        visibility=update_request.visibility,
        policy_binding_id=update_request.policyBindingId,
        policy_version=update_request.policyVersion,
        updated_at=recorded_at,
    )

    try:
        if current is None:
            db.add(next_metadata)
            db.flush()
            db.expunge(next_metadata)
        else:
            conditions = [
                DocumentAccessMetadataRow.tenant_id == tenant.tenant_id,
                DocumentAccessMetadataRow.doc_id == doc_id,
                DocumentAccessMetadataRow.visibility == current.visibility,
                DocumentAccessMetadataRow.policy_version == current.policy_version,
                DocumentAccessMetadataRow.updated_at == current.updated_at,
            ]
            if current.policy_binding_id is None:
                conditions.append(DocumentAccessMetadataRow.policy_binding_id.is_(None))
            else:
                conditions.append(
                    DocumentAccessMetadataRow.policy_binding_id
                    == current.policy_binding_id
                )
            result = db.execute(
                update(DocumentAccessMetadataRow)
                .where(*conditions)
                .values(
                    visibility=next_metadata.visibility,
                    policy_binding_id=next_metadata.policy_binding_id,
                    policy_version=next_metadata.policy_version,
                    updated_at=next_metadata.updated_at,
                )
                .execution_options(synchronize_session=False)
            )
            if result.rowcount != 1:
                db.rollback()
                raise _conflict()

        db.add(
            DocumentAccessAdminAuditEventRow(
                event_id=f"audit-{uuid4()}",
                tenant_id=tenant.tenant_id,
                principal_id=cast(str, identity.user_id),
                doc_id=doc_id,
                action="document.policy.update",
                decision="allowed",
                policy_version=update_request.policyVersion,
                capability_version=capability_version,
                correlation_id=correlation_id,
                occurred_at=recorded_at,
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _conflict() from None

    detail = _detail(
        tenant_id=tenant.tenant_id,
        doc_id=doc_id,
        metadata=next_metadata,
    )
    response.headers["ETag"] = _etag(detail.revision)
    return DocumentAccessUpdateResponse(
        item=detail,
        receipt=DocumentAccessUpdateReceipt(
            correlationId=correlation_id,
            capabilityVersion=capability_version,
            recordedAt=recorded_at,
        ),
    )
