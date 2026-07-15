#!/usr/bin/env python3
"""Validate active issue memo metadata consistency.

Checks active memo files discovered from their own `Status` metadata. README is
an entry point, not a second status registry.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PLANS_DIR = Path(__file__).resolve().parents[1]
if str(PLANS_DIR) not in sys.path:
    sys.path.insert(0, str(PLANS_DIR))

from issue_memo_metadata import (  # noqa: E402
    ISSUE_STATUS_ACTIVE,
    VALID_ISSUE_STATUSES,
    parse_backlog_id,
    parse_issue_status,
    parse_metadata,
)

ALLOWED_VERIFICATION_LEVELS = {"docs-check", "unit", "integration", "e2e"}
REQUIRED_FIELDS = [
    "- Type:",
    "- Status:",
    "- Lifecycle:",
    "- Source Issue:",
    "- Priority:",
    "- Scope:",
    "- Related ADR/Spec:",
    "- Expected verification level:",
]


@dataclass(frozen=True)
class ActiveMemoRow:
    backlog: str
    memo: str
    status: str
    source: str


def parse_active_rows(readme_text: str) -> list[ActiveMemoRow]:
    rows: list[ActiveMemoRow] = []
    in_active_section = False
    for line in readme_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_active_section = stripped == "## Active issue memos"
            continue

        if not in_active_section:
            continue

        if "issue-" not in stripped or not stripped.startswith("|"):
            continue

        cols = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cols) != 4:
            continue
        if cols[0] == "Backlog ID":
            continue

        rows.append(
            ActiveMemoRow(
                backlog=cols[0],
                memo=cols[1].strip("`"),
                status=cols[2],
                source=cols[3],
            )
        )
    return rows


def discover_active_rows(root: Path) -> list[ActiveMemoRow]:
    rows: list[ActiveMemoRow] = []
    for memo_path in sorted(root.glob("issue-*.md")):
        text = memo_path.read_text(encoding="utf-8")
        metadata = parse_metadata(text.splitlines()[:20])
        status = parse_issue_status(metadata)
        if status not in ISSUE_STATUS_ACTIVE:
            continue
        rows.append(
            ActiveMemoRow(
                backlog=parse_backlog_id(text, memo_path),
                memo=memo_path.name,
                status=status,
                source=metadata.get("Source Issue", ""),
            )
        )
    return rows



def extract_dependency_paths(memo_text: str) -> list[str]:
    lines = memo_text.splitlines()
    in_dependencies = False
    refs: list[str] = []
    heading_re = re.compile(r"^##+\s+(?:\d+\)\s*)?(?:依存関係|Dependencies)")
    section_re = re.compile(r"^##+\s+")
    for line in lines:
        stripped = line.strip()
        if heading_re.match(stripped):
            in_dependencies = True
            continue
        if in_dependencies and section_re.match(stripped):
            break
        if not in_dependencies:
            continue
        refs.extend(re.findall(r"`([^`]*issue-[^`]+\.md)`", line))
    return refs


def extract_field_value(memo_text: str, field_name: str) -> str | None:
    return parse_metadata(memo_text.splitlines()).get(field_name)


def extract_verification_level(memo_text: str) -> str | None:
    match = re.search(r"^- Expected verification level:\s*`([^`]+)`", memo_text, re.M)
    if not match:
        return None
    return match.group(1).strip()


def validate_rows(root: Path, rows: Iterable[ActiveMemoRow]) -> list[str]:
    errors: list[str] = []
    for row in rows:
        memo_path = root / row.memo
        if not memo_path.exists():
            errors.append(f"missing memo file: {row.memo}")
            continue

        text = memo_path.read_text(encoding="utf-8")
        for field in REQUIRED_FIELDS:
            if field not in text:
                errors.append(f"{row.memo}: missing field {field}")

        level = extract_verification_level(text)
        if level and level not in ALLOWED_VERIFICATION_LEVELS:
            errors.append(
                f"{row.memo}: invalid Expected verification level `{level}` "
                f"(allowed: {sorted(ALLOWED_VERIFICATION_LEVELS)})"
            )

        memo_status = extract_field_value(text, "Status")
        memo_source = extract_field_value(text, "Source Issue")
        memo_priority = extract_field_value(text, "Priority")

        if row.status not in ISSUE_STATUS_ACTIVE:
            errors.append(
                f"{row.memo}: invalid active status `{row.status}` (allowed: {sorted(ISSUE_STATUS_ACTIVE)})"
            )

        if memo_status and memo_status not in ISSUE_STATUS_ACTIVE:
            errors.append(
                f"{row.memo}: invalid Status `{memo_status}` (allowed: {sorted(ISSUE_STATUS_ACTIVE)})"
            )

        if memo_priority is None or not memo_priority.strip():
            errors.append(f"{row.memo}: missing or empty Priority value")

        for dep in extract_dependency_paths(text):
            dep_path = root / Path(dep).name
            if not dep_path.exists():
                errors.append(f"{row.memo}: dependency path not found `{dep}`")

        if row.status != "Draft" and row.source == "TBD":
            errors.append(
                f"{row.memo}: status is {row.status} but Source Issue is TBD in index"
            )

        if memo_status and memo_source:
            if memo_status != row.status or memo_source != row.source:
                errors.append(
                    f"{row.memo}: index status/source mismatch "
                    f"(index=({row.status}, {row.source}), memo=({memo_status}, {memo_source}))"
                )

    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    seen_backlogs: dict[str, str] = {}
    for memo_path in sorted(root.glob("issue-*.md")):
        text = memo_path.read_text(encoding="utf-8")
        metadata = parse_metadata(text.splitlines()[:20])
        status = parse_issue_status(metadata)
        if status not in VALID_ISSUE_STATUSES:
            errors.append(
                f"{memo_path.name}: invalid Status `{status}` "
                f"(allowed: {sorted(VALID_ISSUE_STATUSES)})"
            )

        if status in ISSUE_STATUS_ACTIVE:
            backlog = parse_backlog_id(text, memo_path)
            normalized_backlog = backlog.casefold()
            previous = seen_backlogs.get(normalized_backlog)
            if previous:
                errors.append(
                    f"{memo_path.name}: duplicate Backlog ID `{backlog}` also used by {previous}"
                )
            else:
                seen_backlogs[normalized_backlog] = memo_path.name

    errors.extend(validate_rows(root, discover_active_rows(root)))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory that contains issues README and memo files",
    )
    args = parser.parse_args()

    errors = validate(args.root)
    if errors:
        print("validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    rows = discover_active_rows(args.root)
    print(f"ok: validated {len(rows)} active issue memos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
