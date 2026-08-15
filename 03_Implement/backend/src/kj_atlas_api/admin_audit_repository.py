"""SEC-ADMIN-PLANE-03: local persistence for the control-plane audit trail.

Records /admin/* operations (actor fingerprint, route, operation, target,
result, request id) and provides a bounded, allowlist read path. Recording is
fail-open by contract: callers wrap the insert in try/except and never let an
audit failure block the operation.
"""

from __future__ import annotations

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from kj_atlas_api.models import AdminAuditEventRow

#: Read-path bound so a single response can never grow without limit
#: (SEC-DOC-BOUND-04/05 cursor precedent).
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 500

#: Separator for the composite (occurred_at, event_id) cursor. occurred_at is
#: ISO-8601 (contains ':' / '+') and event_id is hex, so '|' is unambiguous.
_CURSOR_SEPARATOR = "|"


def encode_cursor(occurred_at: str, event_id: str) -> str:
    return f"{occurred_at}{_CURSOR_SEPARATOR}{event_id}"


def decode_cursor(cursor: str) -> tuple[str, str] | None:
    if _CURSOR_SEPARATOR not in cursor:
        return None
    occurred_at, event_id = cursor.split(_CURSOR_SEPARATOR, 1)
    return occurred_at, event_id


def record_admin_audit_event(
    db: Session,
    *,
    event_id: str,
    route: str,
    result: str,
    status_code: int,
    occurred_at: str,
    tenant_id: str | None = None,
    actor_ref_hash: str | None = None,
    operation: str | None = None,
    target: str | None = None,
    request_id: str | None = None,
) -> None:
    """Insert one audit row. Caller owns commit/rollback; never raise here."""
    db.add(
        AdminAuditEventRow(
            event_id=event_id,
            tenant_id=tenant_id,
            actor_ref_hash=actor_ref_hash,
            route=route,
            operation=operation,
            target=target,
            result=result,
            status_code=status_code,
            request_id=request_id,
            occurred_at=occurred_at,
        )
    )


def list_admin_audit_events(
    db: Session,
    *,
    cursor: str | None,
    limit: int,
) -> tuple[list[AdminAuditEventRow], str | None]:
    """Return the most recent `limit` events after `cursor`.

    Order is (occurred_at desc, event_id desc). `cursor` is an opaque composite
    "occurred_at|event_id" from the previous page, decoded and compared
    lexicographically so pagination stays correct even when several events share
    an identical timestamp. Returns `(rows, next_cursor)` where next_cursor is
    None when there are no more pages.
    """
    bounded_limit = max(1, min(limit, MAX_PAGE_SIZE))
    stmt = select(AdminAuditEventRow).order_by(
        AdminAuditEventRow.occurred_at.desc(),
        AdminAuditEventRow.event_id.desc(),
    )
    decoded = decode_cursor(cursor) if cursor is not None else None
    if decoded is not None:
        cursor_occurred_at, cursor_event_id = decoded
        stmt = stmt.where(
            or_(
                AdminAuditEventRow.occurred_at < cursor_occurred_at,
                and_(
                    AdminAuditEventRow.occurred_at == cursor_occurred_at,
                    AdminAuditEventRow.event_id < cursor_event_id,
                ),
            )
        )
    stmt = stmt.limit(bounded_limit + 1)
    rows = list(db.scalars(stmt))
    has_more = len(rows) > bounded_limit
    page = rows[:bounded_limit]
    next_cursor = encode_cursor(page[-1].occurred_at, page[-1].event_id) if has_more else None
    return page, next_cursor
