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
- validates Case 001–003 Round 1 frozen product-source manifests
- verifies every frozen source path/blob against the preregistered product commit
- validates the shared frozen canonical cultural-substrate-weaving skill manifest
- validates Case 001–003 starter documents remain semantically empty
- validates every continuous-dogfood record is indexed with its matching canvas

It does not score or validate any future arm result.

Exit 0 = all documents/tools structurally valid. Exit 1 = any issue found.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

DOGFOOD_DIR = Path(__file__).parent
ROOT = DOGFOOD_DIR.parent.parent
GLOB = "doc_kj_atlas_dogfood_r*.json"
CONTINUOUS_GLOB = "cognitive-dogfood-continuous-*.md"
CONTINUOUS_INDEX = DOGFOOD_DIR / "cognitive-dogfood-index.md"
CONTINUOUS_ROUND_HEADING = re.compile(r"^# 継続dogfood R(\d+)\b", re.MULTILINE)
CONTINUOUS_CANVAS_REF = re.compile(r"`(doc_kj_atlas_dogfood_r\d+\.json)`")
COGNITIVE_TOOL_FILES = (
    "validate_cognitive_run_records.py",
    "build_cognitive_blind_package.py",
    "prepare_cognitive_case001_skill_bundle.py",
    "prepare_cognitive_frozen_source_bundle.py",
)
PRODUCT_REPOSITORY = "hat47x/kj-atlas"
SKILL_REPOSITORY = "hat47x/cultural-substrate-weaving"
PRODUCT_COMMIT = "2232b3bb26647e5c4a083f55bdbf83c161698649"
SKILL_COMMIT = "3988e12e5f7f316f377d3391e9486c8467a111d5"
PRODUCT_MANIFEST_SPECS = {
    "case-001": 20,
    "case-002": 18,
    "case-003": 18,
}
SHARED_SKILL_MANIFEST = (
    DOGFOOD_DIR / "cognitive-dogfood-case-001-skill-manifest.json"
)
SHARED_SKILL_SOURCE_COUNT = 12
SHARED_SKILL_ROOT = PurePosixPath("src/ja-JP")
STARTER_SPECS = {
    "case-001": "doc_cognitive_case_001_starter",
    "case-002": "doc_cognitive_case_002_starter",
    "case-003": "doc_cognitive_case_003_starter",
}
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


def validate_continuous_index() -> list[str]:
    """Keep continuous dogfood records reachable from the navigation index.

    The index is not an authority over the contents of a dogfood round. This
    check only prevents an existing round and its DocumentV1 canvas from
    becoming invisible to the normal navigation path.
    """

    issues: list[str] = []
    reports = sorted(DOGFOOD_DIR.glob(CONTINUOUS_GLOB))
    if not reports:
        return [f"no continuous dogfood records matched {CONTINUOUS_GLOB}"]
    if not CONTINUOUS_INDEX.is_file():
        return [f"{CONTINUOUS_INDEX.name}: missing cognitive dogfood navigation index"]

    index_text = CONTINUOUS_INDEX.read_text(encoding="utf-8")
    for report in reports:
        report_text = report.read_text(encoding="utf-8")
        if f"`{report.name}`" not in index_text:
            issues.append(
                f"{report.name}: continuous dogfood record is missing from "
                f"{CONTINUOUS_INDEX.name}"
            )

        heading = CONTINUOUS_ROUND_HEADING.search(report_text)
        if heading:
            expected_canvas = f"doc_kj_atlas_dogfood_r{heading.group(1)}.json"
        else:
            refs = sorted(set(CONTINUOUS_CANVAS_REF.findall(report_text)))
            if len(refs) != 1:
                issues.append(
                    f"{report.name}: cannot determine one matching dogfood canvas "
                    f"from heading/reference (found {refs})"
                )
                continue
            expected_canvas = refs[0]

        if f"`{expected_canvas}`" not in report_text:
            issues.append(
                f"{report.name}: does not reference its matching canvas {expected_canvas}"
            )
        if not (DOGFOOD_DIR / expected_canvas).is_file():
            issues.append(
                f"{report.name}: matching canvas does not exist: {expected_canvas}"
            )
        if f"`{expected_canvas}`" not in index_text:
            issues.append(
                f"{report.name}: matching canvas {expected_canvas} is missing from "
                f"{CONTINUOUS_INDEX.name}"
            )

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


def git_blob_at(commit: str, path: str) -> tuple[str | None, str | None]:
    command = ["git", "-C", str(ROOT), "rev-parse", f"{commit}:{path}"]
    try:
        completed = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return None, "git executable was not found"
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip()
        return None, stderr or f"git exited with {exc.returncode}"
    return completed.stdout.strip(), None


def validate_product_source_manifest(case_id: str, expected_count: int) -> list[str]:
    issues: list[str] = []
    path = DOGFOOD_DIR / f"cognitive-dogfood-{case_id}-round1-source-manifest.json"
    label = case_id.replace("case-", "Case ")
    if not path.is_file():
        return [f"{path.name}: missing frozen source manifest"]

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON ({exc})"]

    if manifest.get("schemaVersion") != 1:
        issues.append(f"{label} source manifest schemaVersion must be 1")
    if manifest.get("caseId") != case_id or manifest.get("round") != 1:
        issues.append(f"{label} source manifest must identify {case_id} round 1")
    if manifest.get("productRepository") != PRODUCT_REPOSITORY:
        issues.append(f"{label} product repository changed from the preregistration")
    if manifest.get("productCommit") != PRODUCT_COMMIT:
        issues.append(f"{label} product commit changed from the preregistered SHA")
    if manifest.get("skillRepository") != SKILL_REPOSITORY:
        issues.append(f"{label} skill repository changed from the preregistration")
    if manifest.get("skillCommitForArmsBD") != SKILL_COMMIT:
        issues.append(f"{label} skill commit changed from the preregistered SHA")

    expected_manifest_id = f"{case_id}-r1-product@{PRODUCT_COMMIT}"
    if manifest.get("manifestId") != expected_manifest_id:
        issues.append(f"{label} source manifestId does not match product commit")

    sources = manifest.get("commonSources")
    if not isinstance(sources, list):
        issues.append(f"{label} commonSources must be a list")
        return issues
    if len(sources) != expected_count:
        issues.append(
            f"{label} commonSources count is {len(sources)}, expected {expected_count}"
        )

    seen_paths: set[str] = set()
    for index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            issues.append(f"{label} source #{index} is not an object")
            continue
        raw_path = source.get("path")
        blob_sha = source.get("blobSha")
        path_valid = safe_manifest_path(raw_path)
        blob_valid = isinstance(blob_sha, str) and HEX40.fullmatch(blob_sha)
        if not path_valid:
            issues.append(f"{label} source #{index} has unsafe/missing path")
        elif raw_path in seen_paths:
            issues.append(f"{label} source path duplicated: {raw_path}")
        else:
            seen_paths.add(raw_path)
        if not blob_valid:
            issues.append(f"{label} source #{index} has invalid blobSha")

        if path_valid and blob_valid:
            actual_blob, error = git_blob_at(PRODUCT_COMMIT, raw_path)
            if error:
                issues.append(
                    f"{label} source cannot resolve at frozen commit: {raw_path} ({error})"
                )
            elif actual_blob != blob_sha:
                issues.append(
                    f"{label} source blob mismatch: {raw_path} got {actual_blob}, expected {blob_sha}"
                )

    excluded = manifest.get("round1ExcludedInputs")
    if not isinstance(excluded, list) or not excluded:
        issues.append(f"{label} round1ExcludedInputs must be a non-empty list")

    return issues


def validate_shared_skill_manifest() -> list[str]:
    issues: list[str] = []
    if not SHARED_SKILL_MANIFEST.is_file():
        return [f"{SHARED_SKILL_MANIFEST.name}: missing frozen skill manifest"]

    try:
        manifest = json.loads(SHARED_SKILL_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{SHARED_SKILL_MANIFEST.name}: invalid JSON ({exc})"]

    if manifest.get("schemaVersion") != 1:
        issues.append("Shared skill manifest schemaVersion must be 1")
    if manifest.get("caseId") != "case-001":
        issues.append("Shared skill manifest remains anchored to case-001")
    if manifest.get("skillCommit") != SKILL_COMMIT:
        issues.append("Shared skill commit changed from the preregistered SHA")
    if manifest.get("locale") != "ja-JP":
        issues.append("Shared skill locale must be ja-JP")
    if manifest.get("canonicalRoot") != SHARED_SKILL_ROOT.as_posix():
        issues.append("Shared skill canonicalRoot must be src/ja-JP")
    if manifest.get("appliesToArms") != ["B", "D"]:
        issues.append("Shared skill manifest must apply to B and D only")

    expected_manifest_id = f"case-001-skill-ja@{SKILL_COMMIT}"
    if manifest.get("manifestId") != expected_manifest_id:
        issues.append("Shared skill manifestId does not match skill commit")

    sources = manifest.get("canonicalSources")
    if not isinstance(sources, list):
        issues.append("Shared canonicalSources must be a list")
        return issues
    if len(sources) != SHARED_SKILL_SOURCE_COUNT:
        issues.append(
            f"Shared canonicalSources count is {len(sources)}, expected {SHARED_SKILL_SOURCE_COUNT}"
        )

    seen_paths: set[str] = set()
    for index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            issues.append(f"Shared skill source #{index} is not an object")
            continue
        raw_path = source.get("path")
        blob_sha = source.get("blobSha")
        if not safe_manifest_path(raw_path):
            issues.append(f"Shared skill source #{index} has unsafe/missing path")
        else:
            source_path = PurePosixPath(raw_path)
            if source_path != SHARED_SKILL_ROOT and SHARED_SKILL_ROOT not in source_path.parents:
                issues.append(f"Shared skill source escapes canonical root: {raw_path}")
            if raw_path in seen_paths:
                issues.append(f"Shared skill source path duplicated: {raw_path}")
            else:
                seen_paths.add(raw_path)
        if not isinstance(blob_sha, str) or not HEX40.fullmatch(blob_sha):
            issues.append(f"Shared skill source #{index} has invalid blobSha")

    if "src/ja-JP/ROUTER.md" not in seen_paths:
        issues.append("Shared skill bundle must include src/ja-JP/ROUTER.md")

    excluded = manifest.get("excludedFromSkillBundle")
    if not isinstance(excluded, list) or not excluded:
        issues.append("Shared excludedFromSkillBundle must be a non-empty list")

    return issues


def validate_starter(case_id: str, expected_id: str) -> list[str]:
    issues: list[str] = []
    number = case_id.removeprefix("case-")
    path = DOGFOOD_DIR / f"doc_cognitive_case_{number}_starter.json"
    label = case_id.replace("case-", "Case ")
    if not path.is_file():
        return [f"{path.name}: missing empty starter document"]

    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON ({exc})"]

    if document.get("version") != 1:
        issues.append(f"{label} starter version must be 1")
    if document.get("id") != expected_id:
        issues.append(f"{label} starter id must be {expected_id}")

    for field in ("cards", "islands", "evidenceLinks", "readingOrder", "narratives"):
        if document.get(field) != []:
            issues.append(f"{label} starter {field} must remain an empty list")

    transform = document.get("transform")
    if not isinstance(transform, dict):
        issues.append(f"{label} starter transform must be an object")
    else:
        expected_transform = {"panX": 0, "panY": 0, "zoom": 1}
        if transform != expected_transform:
            issues.append(
                f"{label} starter transform changed from neutral {expected_transform}"
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

    all_issues.extend(validate_continuous_index())
    all_issues.extend(validate_cognitive_tools())
    for case_id, expected_count in PRODUCT_MANIFEST_SPECS.items():
        all_issues.extend(validate_product_source_manifest(case_id, expected_count))
    all_issues.extend(validate_shared_skill_manifest())
    for case_id, expected_id in STARTER_SPECS.items():
        all_issues.extend(validate_starter(case_id, expected_id))

    for path in files:
        d = json.loads(path.read_text(encoding="utf-8"))
        print(
            f"  {path.name}: {len(d['cards'])}C/{len(d['edges'])}E/"
            f"{len(d['islands'])}I/{len(d['narratives'])}N"
        )

    continuous_reports = sorted(DOGFOOD_DIR.glob(CONTINUOUS_GLOB))
    print(
        f"  {CONTINUOUS_INDEX.name}: continuous-index coverage for "
        f"{len(continuous_reports)} records"
    )

    for filename in COGNITIVE_TOOL_FILES:
        status = "present" if (DOGFOOD_DIR / filename).is_file() else "missing"
        print(f"  {filename}: {status} / syntax-check")

    for case_id, expected_count in PRODUCT_MANIFEST_SPECS.items():
        manifest = DOGFOOD_DIR / f"cognitive-dogfood-{case_id}-round1-source-manifest.json"
        status = "present" if manifest.is_file() else "missing"
        print(
            f"  {manifest.name}: {status} / expected {expected_count} frozen product sources"
        )

    skill_status = "present" if SHARED_SKILL_MANIFEST.is_file() else "missing"
    print(
        f"  {SHARED_SKILL_MANIFEST.name}: {skill_status} / "
        f"expected {SHARED_SKILL_SOURCE_COUNT} canonical ja-JP sources"
    )

    for case_id, expected_id in STARTER_SPECS.items():
        number = case_id.removeprefix("case-")
        starter = DOGFOOD_DIR / f"doc_cognitive_case_{number}_starter.json"
        status = "present" if starter.is_file() else "missing"
        print(f"  {starter.name}: {status} / expected empty id={expected_id}")

    if all_issues:
        print(f"\nISSUES FOUND ({len(all_issues)}):")
        for issue in all_issues:
            print(f"  - {issue}")
        return 1

    print("\nAll dogfood documents and cognitive experiment helpers look structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
