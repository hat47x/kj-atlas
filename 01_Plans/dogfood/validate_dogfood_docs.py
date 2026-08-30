#!/usr/bin/env python3
"""Validate structural integrity of kj-atlas dogfood documents and helpers.

Checks each doc_kj_atlas_dogfood_r*.json:
- parses as JSON with the expected top-level keys
- island.cardIds all resolve to real cards
- edge fromId/toId resolve to cards or islands
- readingOrder items resolve to cards or islands
- at least one narrative is present

Also:
- syntax-checks the lightweight cognitive-dogfood experiment helper scripts
- validates the Case 001 Round 1 frozen product-source manifest shape
- validates the Case 001 frozen canonical skill manifest shape

It does not score or validate any future arm result.

Exit 0 = all documents/tools structurally valid. Exit 1 = any issue found.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath

DOGFOOD_DIR = Path(__file__).parent
GLOB = "doc_kj_atlas_dogfood_r*.json"
COGNITIVE_TOOL_FILES = (
    "validate_cognitive_run_records.py",
    "build_cognitive_blind_package.py",
    "prepare_cognitive_case001_source_bundle.py",
    "prepare_cognitive_case001_skill_bundle.py",
)
CASE001_SOURCE_MANIFEST = (
    DOGFOOD_DIR / "cognitive-dogfood-case-001-round1-source-manifest.json"
)
CASE001_SKILL_MANIFEST = (
    DOGFOOD_DIR / "cognitive-dogfood-case-001-skill-manifest.json"
)
CASE001_PRODUCT_COMMIT = "2232b3bb26647e5c4a083f55bdbf83c161698649"
CASE001_SKILL_COMMIT = "3988e12e5f7f316f377d3391e9486c8467a111d5"
CASE001_SOURCE_COUNT = 20
CASE001_SKILL_SOURCE_COUNT = 12
CASE001_SKILL_ROOT = PurePosixPath("src/ja-JP")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


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


def safe_manifest_path(raw: object) -> bool:
    if not isinstance(raw, str) or not raw:
        return False
    path = PurePosixPath(raw)
    return not path.is_absolute() and ".." not in path.parts


def validate_case001_source_manifest() -> list[str]:
    issues: list[str] = []
    if not CASE001_SOURCE_MANIFEST.is_file():
        return [f"{CASE001_SOURCE_MANIFEST.name}: missing frozen source manifest"]

    try:
        manifest = json.loads(CASE001_SOURCE_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{CASE001_SOURCE_MANIFEST.name}: invalid JSON ({exc})"]

    if manifest.get("schemaVersion") != 1:
        issues.append("Case 001 source manifest schemaVersion must be 1")
    if manifest.get("caseId") != "case-001" or manifest.get("round") != 1:
        issues.append("Case 001 source manifest must identify case-001 round 1")
    if manifest.get("productCommit") != CASE001_PRODUCT_COMMIT:
        issues.append("Case 001 product commit changed from the preregistered SHA")
    if manifest.get("skillCommitForArmsBD") != CASE001_SKILL_COMMIT:
        issues.append("Case 001 skill commit changed from the preregistered SHA")

    expected_manifest_id = f"case-001-r1-product@{CASE001_PRODUCT_COMMIT}"
    if manifest.get("manifestId") != expected_manifest_id:
        issues.append("Case 001 source manifestId does not match product commit")

    sources = manifest.get("commonSources")
    if not isinstance(sources, list):
        issues.append("Case 001 commonSources must be a list")
        return issues
    if len(sources) != CASE001_SOURCE_COUNT:
        issues.append(
            f"Case 001 commonSources count is {len(sources)}, expected {CASE001_SOURCE_COUNT}"
        )

    seen_paths: set[str] = set()
    for index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            issues.append(f"Case 001 source #{index} is not an object")
            continue
        path = source.get("path")
        blob_sha = source.get("blobSha")
        if not safe_manifest_path(path):
            issues.append(f"Case 001 source #{index} has unsafe/missing path")
        elif path in seen_paths:
            issues.append(f"Case 001 source path duplicated: {path}")
        else:
            seen_paths.add(path)
        if not isinstance(blob_sha, str) or not HEX40.fullmatch(blob_sha):
            issues.append(f"Case 001 source #{index} has invalid blobSha")

    excluded = manifest.get("round1ExcludedInputs")
    if not isinstance(excluded, list) or not excluded:
        issues.append("Case 001 round1ExcludedInputs must be a non-empty list")

    return issues


def validate_case001_skill_manifest() -> list[str]:
    issues: list[str] = []
    if not CASE001_SKILL_MANIFEST.is_file():
        return [f"{CASE001_SKILL_MANIFEST.name}: missing frozen skill manifest"]

    try:
        manifest = json.loads(CASE001_SKILL_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{CASE001_SKILL_MANIFEST.name}: invalid JSON ({exc})"]

    if manifest.get("schemaVersion") != 1:
        issues.append("Case 001 skill manifest schemaVersion must be 1")
    if manifest.get("caseId") != "case-001":
        issues.append("Case 001 skill manifest must identify case-001")
    if manifest.get("skillCommit") != CASE001_SKILL_COMMIT:
        issues.append("Case 001 skill commit changed from the preregistered SHA")
    if manifest.get("locale") != "ja-JP":
        issues.append("Case 001 skill locale must be ja-JP")
    if manifest.get("canonicalRoot") != CASE001_SKILL_ROOT.as_posix():
        issues.append("Case 001 skill canonicalRoot must be src/ja-JP")
    if manifest.get("appliesToArms") != ["B", "D"]:
        issues.append("Case 001 skill manifest must apply to B and D only")

    expected_manifest_id = f"case-001-skill-ja@{CASE001_SKILL_COMMIT}"
    if manifest.get("manifestId") != expected_manifest_id:
        issues.append("Case 001 skill manifestId does not match skill commit")

    sources = manifest.get("canonicalSources")
    if not isinstance(sources, list):
        issues.append("Case 001 canonicalSources must be a list")
        return issues
    if len(sources) != CASE001_SKILL_SOURCE_COUNT:
        issues.append(
            f"Case 001 canonicalSources count is {len(sources)}, expected {CASE001_SKILL_SOURCE_COUNT}"
        )

    seen_paths: set[str] = set()
    for index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            issues.append(f"Case 001 skill source #{index} is not an object")
            continue
        raw_path = source.get("path")
        blob_sha = source.get("blobSha")
        if not safe_manifest_path(raw_path):
            issues.append(f"Case 001 skill source #{index} has unsafe/missing path")
        else:
            path = PurePosixPath(raw_path)
            if path != CASE001_SKILL_ROOT and CASE001_SKILL_ROOT not in path.parents:
                issues.append(f"Case 001 skill source escapes canonical root: {raw_path}")
            if raw_path in seen_paths:
                issues.append(f"Case 001 skill source path duplicated: {raw_path}")
            else:
                seen_paths.add(raw_path)
        if not isinstance(blob_sha, str) or not HEX40.fullmatch(blob_sha):
            issues.append(f"Case 001 skill source #{index} has invalid blobSha")

    if "src/ja-JP/ROUTER.md" not in seen_paths:
        issues.append("Case 001 skill bundle must include src/ja-JP/ROUTER.md")

    excluded = manifest.get("excludedFromSkillBundle")
    if not isinstance(excluded, list) or not excluded:
        issues.append("Case 001 excludedFromSkillBundle must be a non-empty list")

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
    all_issues.extend(validate_case001_source_manifest())
    all_issues.extend(validate_case001_skill_manifest())

    for path in files:
        d = json.loads(path.read_text(encoding="utf-8"))
        print(
            f"  {path.name}: {len(d['cards'])}C/{len(d['edges'])}E/"
            f"{len(d['islands'])}I/{len(d['narratives'])}N"
        )

    for filename in COGNITIVE_TOOL_FILES:
        status = "present" if (DOGFOOD_DIR / filename).is_file() else "missing"
        print(f"  {filename}: {status} / syntax-check")

    source_status = "present" if CASE001_SOURCE_MANIFEST.is_file() else "missing"
    print(
        f"  {CASE001_SOURCE_MANIFEST.name}: {source_status} / "
        f"expected {CASE001_SOURCE_COUNT} frozen product sources"
    )
    skill_status = "present" if CASE001_SKILL_MANIFEST.is_file() else "missing"
    print(
        f"  {CASE001_SKILL_MANIFEST.name}: {skill_status} / "
        f"expected {CASE001_SKILL_SOURCE_COUNT} canonical ja-JP sources"
    )

    if all_issues:
        print(f"\nISSUES FOUND ({len(all_issues)}):")
        for issue in all_issues:
            print(f"  - {issue}")
        return 1

    print("\nALL DOGFOOD DOCUMENTS/TOOLS STRUCTURALLY VALID ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
