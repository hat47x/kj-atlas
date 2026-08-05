#!/usr/bin/env python3
"""Validate active issue memo metadata consistency.

Checks active memo files discovered from their own `Status` metadata. README is
an entry point, not a second status registry.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from .issue_memo_status import (
        ACTIVE_ISSUE_STATUSES,
        CANONICAL_ISSUE_STATUSES,
        parse_issue_status,
    )
except ImportError:  # Direct script execution from 01_Plans/issues/.
    from issue_memo_status import (
        ACTIVE_ISSUE_STATUSES,
        CANONICAL_ISSUE_STATUSES,
        parse_issue_status,
    )

ALLOWED_VERIFICATION_LEVELS = {"docs-check", "unit", "integration", "e2e"}
REQUIRED_FIELDS = [
    "- Type:",
    "- Status:",
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
        status = parse_issue_status(extract_field_value(text, "Status"))
        if status not in ACTIVE_ISSUE_STATUSES:
            continue
        rows.append(
            ActiveMemoRow(
                backlog=memo_path.stem.removeprefix("issue-"),
                memo=memo_path.name,
                status=status,
                source=extract_field_value(text, "Source Issue") or "",
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
    pattern = rf"^- {re.escape(field_name)}:\s*(.+)$"
    match = re.search(pattern, memo_text, re.M)
    if not match:
        return None
    return match.group(1).strip()


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

        if row.status not in ACTIVE_ISSUE_STATUSES:
            errors.append(
                f"{row.memo}: invalid active status `{row.status}` (allowed: {sorted(ACTIVE_ISSUE_STATUSES)})"
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


def validate_status_contract(root: Path) -> list[str]:
    errors: list[str] = []
    requirement_paths: dict[str, list[str]] = {}

    for memo_path in sorted(root.glob("issue-*.md")):
        text = memo_path.read_text(encoding="utf-8")
        raw_status = extract_field_value(text, "Status")
        status = parse_issue_status(raw_status)
        if raw_status is None:
            errors.append(f"{memo_path.name}: missing Status metadata")
            continue
        if status is None:
            errors.append(
                f"{memo_path.name}: invalid Status `{raw_status}` "
                f"(allowed: {sorted(CANONICAL_ISSUE_STATUSES)})"
            )
            continue
        if status not in ACTIVE_ISSUE_STATUSES:
            continue

        requirement_id = extract_field_value(text, "RequirementID")
        if requirement_id:
            canonical_id = requirement_id.strip().strip("`")
            requirement_paths.setdefault(canonical_id, []).append(memo_path.name)

    for requirement_id, memo_names in sorted(requirement_paths.items()):
        if len(memo_names) > 1:
            errors.append(
                f"duplicate active RequirementID `{requirement_id}`: {', '.join(memo_names)}"
            )

    return errors


def validate(root: Path) -> list[str]:
    return validate_status_contract(root) + validate_rows(root, discover_active_rows(root))


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
