#!/usr/bin/env python3
"""Validate active issue memo metadata consistency.

Checks:
- Active table rows in `README.md` resolve to existing memo files.
- Active memo files contain required metadata fields.
- Active table status/source consistency (`Draft` only when Source Issue is TBD).
- `Expected verification level` value is one of the allowed values.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

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
    readme_path = root / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")
    rows = parse_active_rows(readme_text)
    return validate_rows(root, rows)


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

    rows = parse_active_rows((args.root / "README.md").read_text(encoding="utf-8"))
    print(f"ok: validated {len(rows)} active issue memos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
