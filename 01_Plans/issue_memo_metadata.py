"""Shared parsing rules for internal issue memo metadata."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


ISSUE_STATUS_ACTIVE = frozenset({"Draft", "Open", "In Progress"})
VALID_ISSUE_STATUSES = ISSUE_STATUS_ACTIVE | {"Done"}
META_RE = re.compile(r"^- (?P<key>[^:]+):\s*(?P<value>.+)$")
BACKLOG_HEADING_RE = re.compile(
    r"^#\s+Issue(?:\s+Draft)?:\s+(?P<backlog>[A-Za-z0-9][A-Za-z0-9-]*)",
    re.MULTILINE,
)


def parse_metadata(lines: Iterable[str]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in lines:
        match = META_RE.match(line)
        if match:
            metadata[match.group("key")] = match.group("value").strip()
    return metadata


def parse_issue_status(metadata: dict[str, str]) -> str:
    return metadata.get("Status", "Unknown").strip()


def parse_backlog_id(text: str, path: Path) -> str:
    match = BACKLOG_HEADING_RE.search(text)
    if match:
        return match.group("backlog")
    return path.stem.removeprefix("issue-")
