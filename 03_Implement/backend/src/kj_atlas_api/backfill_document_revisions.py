from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.content_store import ContentBlob
from kj_atlas_api.database_content_store import DatabaseDocumentContentStore
from kj_atlas_api.database_support import create_verified_database_engine
from kj_atlas_api.models import CanvasRevisionHeadRow, DocumentRow, TenantRow
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


@dataclass(frozen=True)
class DocumentRevisionBackfillStats:
    tenant_id: str
    candidates: int
    materialized: int
    remaining: int
    dry_run: bool


def _tenant(tenant_id: str) -> TenantContext:
    normalized = tenant_id.strip()
    if not normalized or normalized != tenant_id:
        raise ValueError("tenant ID must be non-empty without surrounding whitespace")
    return TenantContext(
        tenant_id=tenant_id,
        membership_id="system:document-revision-backfill",
        resolved_by="verified_claim",
    )


def _candidate_statement(tenant_id: str):
    return (
        select(DocumentRow)
        .outerjoin(
            CanvasRevisionHeadRow,
            (CanvasRevisionHeadRow.tenant_id == DocumentRow.tenant_id)
            & (CanvasRevisionHeadRow.doc_id == DocumentRow.id)
            & (CanvasRevisionHeadRow.head_name == "main"),
        )
        .where(
            DocumentRow.tenant_id == tenant_id,
            CanvasRevisionHeadRow.revision_id.is_(None),
        )
        .order_by(DocumentRow.id.asc())
    )


def _remaining_statement(tenant_id: str):
    return (
        select(func.count())
        .select_from(DocumentRow)
        .outerjoin(
            CanvasRevisionHeadRow,
            (CanvasRevisionHeadRow.tenant_id == DocumentRow.tenant_id)
            & (CanvasRevisionHeadRow.doc_id == DocumentRow.id)
            & (CanvasRevisionHeadRow.head_name == "main"),
        )
        .where(
            DocumentRow.tenant_id == tenant_id,
            CanvasRevisionHeadRow.revision_id.is_(None),
        )
    )


def backfill_document_revisions(
    db: Session,
    *,
    tenant_id: str,
    dry_run: bool,
    limit: int = 100,
) -> DocumentRevisionBackfillStats:
    if limit < 1 or limit > 10_000:
        raise ValueError("backfill limit must be between 1 and 10000")
    tenant = _tenant(tenant_id)
    apply_database_tenant_context(db=db, tenant=tenant)
    if db.get(TenantRow, tenant_id) is None:
        raise ValueError("tenant does not exist")
    candidates = db.scalars(_candidate_statement(tenant_id).limit(limit)).all()
    if dry_run:
        remaining = db.scalar(_remaining_statement(tenant_id))
        return DocumentRevisionBackfillStats(
            tenant_id=tenant_id,
            candidates=len(candidates),
            materialized=0,
            remaining=int(remaining or 0),
            dry_run=True,
        )

    store = DatabaseDocumentContentStore(db)
    for row in candidates:
        store.save(
            tenant=tenant,
            doc_id=row.id,
            version=row.version,
            updated_at=row.updated_at,
            content=ContentBlob.from_text(row.payload_json),
        )
    db.flush()
    remaining = db.scalar(_remaining_statement(tenant_id))
    return DocumentRevisionBackfillStats(
        tenant_id=tenant_id,
        candidates=len(candidates),
        materialized=len(candidates),
        remaining=int(remaining or 0),
        dry_run=False,
    )


def run_backfill(
    *,
    database_url: str,
    tenant_id: str,
    dry_run: bool,
    limit: int,
) -> DocumentRevisionBackfillStats:
    engine = create_verified_database_engine(database_url)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    try:
        with session_local() as db:
            stats = backfill_document_revisions(
                db,
                tenant_id=tenant_id,
                dry_run=dry_run,
                limit=limit,
            )
            if dry_run:
                db.rollback()
            else:
                db.commit()
            return stats
    finally:
        engine.dispose()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize legacy Document rows into the main revision DAG head."
    )
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        stats = run_backfill(
            database_url=args.database_url,
            tenant_id=args.tenant_id,
            dry_run=not args.apply,
            limit=args.limit,
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(asdict(stats), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
