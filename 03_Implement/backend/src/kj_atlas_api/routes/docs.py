import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from kj_atlas_api.db import get_db
from kj_atlas_api.models import DocumentRow, DocumentV1

router = APIRouter(prefix="/docs", tags=["docs"])


@router.get("/{doc_id}", response_model=DocumentV1)
def get_document(doc_id: str, db: Session = Depends(get_db)) -> DocumentV1:
    doc_row = db.get(DocumentRow, doc_id)
    if doc_row is None:
        raise HTTPException(status_code=404, detail="Document not found")

    payload = json.loads(doc_row.payload_json)
    return DocumentV1.model_validate(payload)


@router.put("/{doc_id}", response_model=DocumentV1)
def put_document(doc_id: str, document: DocumentV1, db: Session = Depends(get_db)) -> DocumentV1:
    if document.id != doc_id:
        raise HTTPException(status_code=400, detail="Path doc_id and document.id must match")

    payload_json = document.model_dump_json()
    doc_row = db.get(DocumentRow, doc_id)

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
    return document
