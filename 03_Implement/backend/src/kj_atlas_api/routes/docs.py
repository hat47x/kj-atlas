import json
from hashlib import sha256

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from pydantic import TypeAdapter
from sqlalchemy.orm import Session

from kj_atlas_api.db import get_db
from kj_atlas_api.models import DocumentPayload, DocumentRow

router = APIRouter(prefix="/docs", tags=["docs"])
document_payload_adapter = TypeAdapter(DocumentPayload)


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
def get_document(doc_id: str, response: Response, db: Session = Depends(get_db)) -> DocumentPayload:
    doc_row = db.get(DocumentRow, doc_id)
    if doc_row is None:
        raise HTTPException(status_code=404, detail="Document not found")

    response.headers["ETag"] = _format_etag(_compute_etag(doc_row.payload_json))
    payload = json.loads(doc_row.payload_json)
    return document_payload_adapter.validate_python(payload)


@router.put("/{doc_id}", response_model=DocumentPayload)
def put_document(
    doc_id: str,
    document: DocumentPayload,
    response: Response,
    if_match: str | None = Header(default=None, alias="If-Match"),
    db: Session = Depends(get_db),
) -> DocumentPayload:
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
