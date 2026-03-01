import json
from hashlib import sha256

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, TypeAdapter
from sqlalchemy.orm import Session

from kj_atlas_api.access_control import (
    AccessDecision,
    AccessRequest,
    AccessResource,
    AuthContext,
    enforce_access,
    normalize_policy_ref,
    parse_csv_header,
    parse_visibility,
    resolve_access_decision,
)
from kj_atlas_api.audit import build_event
from kj_atlas_api.db import get_db
from kj_atlas_api.models import DocumentPayload, DocumentRow

router = APIRouter(prefix="/docs", tags=["docs"])
document_payload_adapter = TypeAdapter(DocumentPayload)



def _authorize_request(
    request: Request,
    *,
    action: str,
    doc_id: str,
    safe_mode: bool,
    read_only: bool,
) -> tuple[AccessRequest, AccessDecision]:
    adapter = getattr(request.app.state, "access_control_adapter", None)
    if adapter is None:
        access_request = AccessRequest(
            action=action,
            safe_mode=safe_mode,
            read_only=read_only,
            auth=AuthContext(actor_ref=request.headers.get("x-actor-ref"), trace_id=request.headers.get("x-trace-id")),
            resource=AccessResource(
                doc_id=doc_id,
                visibility=parse_visibility(request.headers.get("x-doc-visibility")),
                policy_ref=normalize_policy_ref(request.headers.get("x-policy-ref")),
            ),
        )
        decision = AccessDecision(allow=True)
        return access_request, decision

    access_request = AccessRequest(
        action=action,
        safe_mode=safe_mode,
        read_only=read_only,
        auth=AuthContext(
            actor_ref=request.headers.get("x-actor-ref"),
            roles=parse_csv_header(request.headers.get("x-auth-roles")),
            groups=parse_csv_header(request.headers.get("x-auth-groups")),
            trace_id=request.headers.get("x-trace-id"),
        ),
        resource=AccessResource(
            doc_id=doc_id,
            visibility=parse_visibility(request.headers.get("x-doc-visibility")),
            policy_ref=normalize_policy_ref(request.headers.get("x-policy-ref")),
        ),
    )

    fail_safe_mode = getattr(request.app.state, "access_control_fail_safe_mode", "read_only")
    if fail_safe_mode not in {"deny", "read_only"}:
        fail_safe_mode = "read_only"

    decision = resolve_access_decision(adapter=adapter, request=access_request, fail_safe_mode=fail_safe_mode)
    enforce_access(decision, action=action)
    return access_request, decision


def _compute_etag(payload_json: str) -> str:
    return sha256(payload_json.encode("utf-8")).hexdigest()


def _format_etag(etag: str) -> str:
    return f'"{etag}"'


def _parse_if_match(if_match: str) -> set[str]:
    values: set[str] = set()
    for raw_part in if_match.split(","):
        part = raw_part.strip()
        if part.startswith("W/"):
            part = part[2:].strip()
        if part.startswith('"') and part.endswith('"') and len(part) >= 2:
            part = part[1:-1]
        if part:
            values.add(part)
    return values


@router.get("/{doc_id}", response_model=DocumentPayload)
def get_document(
    doc_id: str,
    response: Response,
    request: Request,
    x_read_only: str | None = Header(default=None, alias="X-Read-Only"),
    db: Session = Depends(get_db),
) -> DocumentPayload:
    access_request, decision = _authorize_request(request, action="read", doc_id=doc_id, safe_mode=True, read_only=(x_read_only == "1" or (x_read_only or "").lower() == "true"))

    doc_row = db.get(DocumentRow, doc_id)
    if doc_row is None:
        raise HTTPException(status_code=404, detail="Document not found")

    response.headers["ETag"] = _format_etag(_compute_etag(doc_row.payload_json))
    payload = json.loads(doc_row.payload_json)

    dispatcher = getattr(request.app.state, "audit_dispatcher", None)
    if dispatcher is not None:
        dispatcher.emit(
            build_event(
                event_type="view",
                doc_id=doc_id,
                safe_mode=True,
                actor_ref=request.headers.get("x-actor-ref"),
                metadata={
                    "route": f"/docs/{doc_id}",
                    "method": "GET",
                    "action": access_request.action,
                    "decision_allow": decision.allow,
                    "decision_read_only": decision.read_only,
                    "decision_reason": decision.reason,
                    "visibility": access_request.resource.visibility,
                    "policyRefPresent": access_request.resource.policy_ref is not None,
                    "adapterName": getattr(getattr(request.app.state, "access_control_adapter", None), "name", "none"),
                    "traceId": access_request.auth.trace_id,
                },
            )
        )

    return document_payload_adapter.validate_python(payload)


@router.put("/{doc_id}", response_model=DocumentPayload)
def put_document(
    doc_id: str,
    document: DocumentPayload,
    response: Response,
    request: Request,
    if_match: str | None = Header(default=None, alias="If-Match"),
    x_read_only: str | None = Header(default=None, alias="X-Read-Only"),
    db: Session = Depends(get_db),
) -> DocumentPayload:
    _authorize_request(request, action="write", doc_id=doc_id, safe_mode=True, read_only=(x_read_only == "1" or (x_read_only or "").lower() == "true"))

    if document.id != doc_id:
        raise HTTPException(status_code=400, detail="Path doc_id and document.id must match")

    payload_json = document.model_dump_json()
    doc_row = db.get(DocumentRow, doc_id)

    if if_match is not None:
        if doc_row is None:
            raise HTTPException(status_code=409, detail="ETag mismatch")

        current_etag = _compute_etag(doc_row.payload_json)
        expected_etags = _parse_if_match(if_match)
        if "*" not in expected_etags and current_etag not in expected_etags:
            raise HTTPException(status_code=409, detail="ETag mismatch")

    if doc_row is None:
        doc_row = DocumentRow(
            id=doc_id,
            version=document.version,
            updated_at=document.updatedAt.isoformat(),
            payload_json=payload_json,
        )
        db.add(doc_row)
    else:
        doc_row.version = document.version
        doc_row.updated_at = document.updatedAt.isoformat()
        doc_row.payload_json = payload_json

    db.commit()
    response.headers["ETag"] = _format_etag(_compute_etag(payload_json))
    return document


class ExportAuditPayload(BaseModel):
    safeMode: bool = True
    exportKind: str = "bundle"


@router.post("/{doc_id}/export-audit")
def post_export_audit(
    doc_id: str,
    payload: ExportAuditPayload,
    request: Request,
    x_read_only: str | None = Header(default=None, alias="X-Read-Only"),
) -> dict[str, str]:
    access_request, decision = _authorize_request(request, action="export", doc_id=doc_id, safe_mode=payload.safeMode, read_only=(x_read_only == "1" or (x_read_only or "").lower() == "true"))
    dispatcher = getattr(request.app.state, "audit_dispatcher", None)
    if dispatcher is not None:
        dispatcher.emit(
            build_event(
                event_type="export",
                doc_id=doc_id,
                safe_mode=payload.safeMode,
                actor_ref=request.headers.get("x-actor-ref"),
                metadata={
                    "route": f"/docs/{doc_id}/export-audit",
                    "method": "POST",
                    "exportKind": payload.exportKind,
                    "action": access_request.action,
                    "decision_allow": decision.allow,
                    "decision_read_only": decision.read_only,
                    "decision_reason": decision.reason,
                    "visibility": access_request.resource.visibility,
                    "policyRefPresent": access_request.resource.policy_ref is not None,
                    "adapterName": getattr(getattr(request.app.state, "access_control_adapter", None), "name", "none"),
                    "traceId": access_request.auth.trace_id,
                },
            )
        )

    return {"status": "accepted"}
