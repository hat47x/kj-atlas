"""Canonical lifecycle values shared by issue triage and validation."""
from __future__ import annotations

ACTIVE_ISSUE_STATUSES = frozenset({"Draft", "Open", "In Progress"})
CANONICAL_ISSUE_STATUSES = ACTIVE_ISSUE_STATUSES | {"Done"}


def parse_issue_status(raw_status: str | None) -> str | None:
    """Return a canonical issue status, without normalizing decorated values."""
    if raw_status is None:
        return None
    status = raw_status.strip()
    return status if status in CANONICAL_ISSUE_STATUSES else None
