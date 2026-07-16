from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.document_repository import list_document_rows
from kj_atlas_api.models import UserIdentityRow
from kj_atlas_api.tenant_context import LOCAL_DEFAULT_TENANT_CONTEXT


@dataclass(frozen=True)
class BackfillStats:
    scanned_documents: int = 0
    updated_documents: int = 0
    reviewer_refs_rewritten: int = 0
    owner_refs_rewritten: int = 0


def _resolve_user_ref(mapping: dict[str, str], raw: str) -> str | None:
    user_id = mapping.get(raw)
    if user_id is None:
        return None
    return f"user:{user_id}"


def _rewrite_payload(node: object, mapping: dict[str, str], stats: BackfillStats) -> tuple[object, BackfillStats]:
    if isinstance(node, dict):
        updated: dict[str, object] = {}
        local_stats = stats
        for key, value in node.items():
            next_value, local_stats = _rewrite_payload(value, mapping, local_stats)
            if key == "reviewerRef" and isinstance(value, str):
                replacement = _resolve_user_ref(mapping, value)
                if replacement is not None and replacement != value:
                    next_value = replacement
                    local_stats = BackfillStats(
                        scanned_documents=local_stats.scanned_documents,
                        updated_documents=local_stats.updated_documents,
                        reviewer_refs_rewritten=local_stats.reviewer_refs_rewritten + 1,
                        owner_refs_rewritten=local_stats.owner_refs_rewritten,
                    )
            if key == "ownerRef" and isinstance(value, str):
                replacement = _resolve_user_ref(mapping, value)
                if replacement is not None and replacement != value:
                    next_value = replacement
                    local_stats = BackfillStats(
                        scanned_documents=local_stats.scanned_documents,
                        updated_documents=local_stats.updated_documents,
                        reviewer_refs_rewritten=local_stats.reviewer_refs_rewritten,
                        owner_refs_rewritten=local_stats.owner_refs_rewritten + 1,
                    )
            updated[key] = next_value
        return updated, local_stats

    if isinstance(node, list):
        updated_list = []
        local_stats = stats
        for item in node:
            next_item, local_stats = _rewrite_payload(item, mapping, local_stats)
            updated_list.append(next_item)
        return updated_list, local_stats

    return node, stats


def _load_mapping(mapping_path: Path) -> dict[str, str]:
    payload = json.loads(mapping_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("mapping JSON must be an object")

    mapping: dict[str, str] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("mapping entries must be string -> string")
        normalized_key = key.strip()
        normalized_value = value.strip()
        if not normalized_key or not normalized_value:
            raise ValueError("mapping entries must be non-empty")
        mapping[normalized_key] = normalized_value
    return mapping


def _validated_mapping(db: Session, mapping: dict[str, str]) -> dict[str, str]:
    user_ids = {row.user_id for row in db.query(UserIdentityRow.user_id).distinct()}
    unknown = sorted(user_id for user_id in mapping.values() if user_id not in user_ids)
    if unknown:
        raise ValueError(f"mapping contains unknown users.id values: {', '.join(unknown)}")
    return mapping


def run_backfill(*, database_url: str, mapping_path: Path, dry_run: bool) -> BackfillStats:
    engine = create_engine(database_url)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    try:
        with session_local() as db:
            mapping = _validated_mapping(db, _load_mapping(mapping_path))
            stats = BackfillStats()
            rows = list_document_rows(db, tenant=LOCAL_DEFAULT_TENANT_CONTEXT)
            for row in rows:
                stats = BackfillStats(
                    scanned_documents=stats.scanned_documents + 1,
                    updated_documents=stats.updated_documents,
                    reviewer_refs_rewritten=stats.reviewer_refs_rewritten,
                    owner_refs_rewritten=stats.owner_refs_rewritten,
                )
                payload = json.loads(row.payload_json)
                rewritten, next_stats = _rewrite_payload(payload, mapping, stats)
                if rewritten != payload:
                    next_stats = BackfillStats(
                        scanned_documents=next_stats.scanned_documents,
                        updated_documents=next_stats.updated_documents + 1,
                        reviewer_refs_rewritten=next_stats.reviewer_refs_rewritten,
                        owner_refs_rewritten=next_stats.owner_refs_rewritten,
                    )
                    if not dry_run:
                        row.payload_json = json.dumps(rewritten, ensure_ascii=False)
                stats = next_stats

            if not dry_run:
                db.commit()
            return stats
    finally:
        engine.dispose()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill reviewerRef/ownerRef to user:<users.id>.")
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--mapping-json", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    stats = run_backfill(database_url=args.database_url, mapping_path=args.mapping_json, dry_run=args.dry_run)
    mode = "dry-run" if args.dry_run else "apply"
    print(
        json.dumps(
            {
                "mode": mode,
                "scannedDocuments": stats.scanned_documents,
                "updatedDocuments": stats.updated_documents,
                "reviewerRefsRewritten": stats.reviewer_refs_rewritten,
                "ownerRefsRewritten": stats.owner_refs_rewritten,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
