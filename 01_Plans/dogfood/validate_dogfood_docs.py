#!/usr/bin/env python3
"""Validate structural integrity of kj-atlas dogfood documents (R1-R6).

Checks each doc_kj_atlas_dogfood_r*.json:
- parses as JSON with the expected top-level keys
- island.cardIds all resolve to real cards
- edge fromId/toId resolve to cards or islands
- readingOrder items resolve to cards or islands
- at least one narrative is present

Also syntax-checks the lightweight cognitive-dogfood experiment helper scripts.
It does not score or validate any future arm result.

Exit 0 = all documents/tools structurally valid. Exit 1 = any issue found.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DOGFOOD_DIR = Path(__file__).parent
GLOB = "doc_kj_atlas_dogfood_r*.json"
COGNITIVE_TOOL_FILES = (
    "validate_cognitive_run_records.py",
    "build_cognitive_blind_package.py",
)


def validate_one(path: Path) -> list[str]:
    issues: list[str] = []
    d = json.loads(path.read_text(encoding="utf-8"))
    doc_id = d.get("id", path.stem)

    card_ids = {c["id"] for c in d.get("cards", [])}
    island_ids = {i["id"] for i in d.get("islands", [])}
    valid_endpoints = card_ids | island_ids

    for island in d.get("islands", []):
        missing = [cid for cid in island["cardIds"] if cid not in card_ids]
        if missing:
            issues.append(f"{doc_id}: island {island['id']} missing cards {missing}")

    for edge in d.get("edges", []):
        for ref in ("fromId", "toId"):
            if edge.get(ref) not in valid_endpoints:
                issues.append(f"{doc_id}: edge {edge['id']} unknown {ref}={edge.get(ref)}")

    for item in d.get("readingOrder", []):
        if item not in valid_endpoints:
            issues.append(f"{doc_id}: readingOrder unknown {item}")

    if not d.get("narratives"):
        issues.append(f"{doc_id}: no narratives")

    return issues


def validate_cognitive_tools() -> list[str]:
    issues: list[str] = []
    for filename in COGNITIVE_TOOL_FILES:
        path = DOGFOOD_DIR / filename
        if not path.is_file():
            issues.append(f"{filename}: missing cognitive dogfood helper")
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            issues.append(
                f"{filename}: syntax error at line {exc.lineno}: {exc.msg}"
            )
    return issues


def main() -> int:
    files = sorted(DOGFOOD_DIR.glob(GLOB))
    if not files:
        print(f"ERROR: no dogfood docs matched {GLOB}", file=sys.stderr)
        return 1

    all_issues: list[str] = []
    for path in files:
        try:
            all_issues.extend(validate_one(path))
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            all_issues.append(f"{path.name}: invalid document ({exc})")

    all_issues.extend(validate_cognitive_tools())

    for path in files:
        d = json.loads(path.read_text(encoding="utf-8"))
        print(
            f"  {path.name}: {len(d['cards'])}C/{len(d['edges'])}E/"
            f"{len(d['islands'])}I/{len(d['narratives'])}N"
        )

    for filename in COGNITIVE_TOOL_FILES:
        status = "present" if (DOGFOOD_DIR / filename).is_file() else "missing"
        print(f"  {filename}: {status} / syntax-check")

    if all_issues:
        print(f"\nISSUES FOUND ({len(all_issues)}):")
        for issue in all_issues:
            print(f"  - {issue}")
        return 1

    print("\nALL DOGFOOD DOCUMENTS/TOOLS STRUCTURALLY VALID ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
