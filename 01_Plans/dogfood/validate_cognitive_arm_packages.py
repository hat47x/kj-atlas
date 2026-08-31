#!/usr/bin/env python3
"""Validate assembled cognitive-dogfood arm packages before artifact upload.

This validator is intentionally fail-closed. It checks the *assembled* package,
not only the source manifests used to build it, so packaging regressions cannot
silently leak operator-only material or the wrong treatment into a fresh arm.

Expected treatment boundary:
- A: product + launch only
- B: product + skill + launch
- C: product + starter + launch
- D: product + skill + starter + launch

For product/skill bundles, the file set must match the generated bundle manifest
exactly and each source file must match its recorded SHA-256 digest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

CASES = ("001", "002", "003")
ARMS = ("A", "B", "C", "D")
EXPECTED_TOP_LEVEL = {
    "A": {"launch.md", "product"},
    "B": {"launch.md", "product", "skill"},
    "C": {"launch.md", "product", "starter.json"},
    "D": {"launch.md", "product", "skill", "starter.json"},
}
EMPTY_STARTER_LIST_FIELDS = (
    "cards",
    "islands",
    "evidenceLinks",
    "readingOrder",
    "narratives",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path, label: str, issues: list[str]) -> dict | None:
    if not path.is_file():
        issues.append(f"{label}: missing {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        issues.append(f"{label}: cannot read JSON {path}: {exc}")
        return None
    if not isinstance(value, dict):
        issues.append(f"{label}: JSON root must be an object: {path}")
        return None
    return value


def validate_exact_bundle_files(
    bundle_dir: Path,
    manifest_rel: str,
    label: str,
    issues: list[str],
) -> dict | None:
    manifest_path = bundle_dir / manifest_rel
    manifest = load_json(manifest_path, label, issues)
    if manifest is None:
        return None

    sources = manifest.get("sources")
    if not isinstance(sources, list):
        issues.append(f"{label}: manifest sources must be a list")
        return manifest

    expected_files = {manifest_rel}
    for index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            issues.append(f"{label}: source #{index} is not an object")
            continue
        raw_path = source.get("path")
        expected_sha = source.get("sha256")
        if not isinstance(raw_path, str) or not raw_path:
            issues.append(f"{label}: source #{index} has no path")
            continue
        if raw_path.startswith("/") or ".." in Path(raw_path).parts:
            issues.append(f"{label}: unsafe source path: {raw_path}")
            continue
        expected_files.add(raw_path)
        source_path = bundle_dir / raw_path
        if not source_path.is_file():
            issues.append(f"{label}: missing source file: {raw_path}")
            continue
        if not isinstance(expected_sha, str) or len(expected_sha) != 64:
            issues.append(f"{label}: source has invalid sha256 metadata: {raw_path}")
            continue
        actual_sha = sha256_file(source_path)
        if actual_sha != expected_sha:
            issues.append(
                f"{label}: sha256 mismatch for {raw_path}: "
                f"got {actual_sha}, expected {expected_sha}"
            )

    actual_files: set[str] = set()
    for path in bundle_dir.rglob("*"):
        if path.is_symlink():
            issues.append(f"{label}: symlink is not allowed: {path.relative_to(bundle_dir)}")
        if path.is_file():
            actual_files.add(path.relative_to(bundle_dir).as_posix())

    missing = sorted(expected_files - actual_files)
    extra = sorted(actual_files - expected_files)
    if missing:
        issues.append(f"{label}: bundle files missing from assembled package: {missing}")
    if extra:
        issues.append(f"{label}: unexpected bundle files leaked into package: {extra}")

    return manifest


def validate_product(package: Path, case_number: str, label: str, issues: list[str]) -> None:
    manifest = validate_exact_bundle_files(
        package / "product",
        "_experiment/bundle-manifest.json",
        f"{label} product",
        issues,
    )
    if manifest is None:
        return
    if manifest.get("caseId") != f"case-{case_number}":
        issues.append(f"{label}: product bundle caseId mismatch")
    if manifest.get("round") != 1:
        issues.append(f"{label}: product bundle round must remain 1")
    if manifest.get("operatorOnlyMetadataCopied") is not False:
        issues.append(f"{label}: product bundle must not copy operator-only metadata")


def validate_skill(package: Path, label: str, issues: list[str]) -> None:
    manifest = validate_exact_bundle_files(
        package / "skill",
        "_experiment/skill-bundle-manifest.json",
        f"{label} skill",
        issues,
    )
    if manifest is None:
        return

    required_false = (
        "caseScopedMetadataIncluded",
        "evaluationArtifactsCopied",
        "operatorManifestCopied",
        "repositoryDocsCopied",
    )
    for field in required_false:
        if manifest.get(field) is not False:
            issues.append(f"{label}: skill manifest {field} must be false")
    if manifest.get("locale") != "ja-JP":
        issues.append(f"{label}: skill locale must remain ja-JP")
    if manifest.get("canonicalRoot") != "src/ja-JP":
        issues.append(f"{label}: skill canonicalRoot must remain src/ja-JP")


def validate_starter(package: Path, case_number: str, label: str, issues: list[str]) -> None:
    starter = load_json(package / "starter.json", label, issues)
    if starter is None:
        return
    expected_id = f"doc_cognitive_case_{case_number}_starter"
    if starter.get("version") != 1:
        issues.append(f"{label}: starter version must remain 1")
    if starter.get("id") != expected_id:
        issues.append(f"{label}: starter id mismatch: expected {expected_id}")
    for field in EMPTY_STARTER_LIST_FIELDS:
        if starter.get(field) != []:
            issues.append(f"{label}: starter {field} must remain empty")
    if starter.get("transform") != {"panX": 0, "panY": 0, "zoom": 1}:
        issues.append(f"{label}: starter transform must remain neutral")


def validate_package(root: Path, case_number: str, arm: str) -> list[str]:
    issues: list[str] = []
    package = root / f"cognitive-dogfood-case-{case_number}-arms" / arm
    label = f"Case {case_number} Arm {arm}"
    if not package.is_dir():
        return [f"{label}: package directory missing: {package}"]

    actual_top = {path.name for path in package.iterdir()}
    expected_top = EXPECTED_TOP_LEVEL[arm]
    if actual_top != expected_top:
        issues.append(
            f"{label}: top-level boundary mismatch: "
            f"got {sorted(actual_top)}, expected {sorted(expected_top)}"
        )

    launch = package / "launch.md"
    if not launch.is_file() or not launch.read_text(encoding="utf-8").strip():
        issues.append(f"{label}: launch.md missing or empty")

    validate_product(package, case_number, label, issues)

    if arm in {"B", "D"}:
        validate_skill(package, label, issues)
    if arm in {"C", "D"}:
        validate_starter(package, case_number, label, issues)

    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("/tmp"),
        help="parent directory containing cognitive-dogfood-case-NNN-arms",
    )
    args = parser.parse_args()

    all_issues: list[str] = []
    for case_number in CASES:
        for arm in ARMS:
            issues = validate_package(args.root, case_number, arm)
            all_issues.extend(issues)
            status = "OK" if not issues else "FAIL"
            print(f"Case {case_number} Arm {arm}: {status}")

    if all_issues:
        print(f"\nISSUES FOUND ({len(all_issues)}):", file=sys.stderr)
        for issue in all_issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1

    print("\nAll assembled cognitive-dogfood arm packages satisfy treatment boundaries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
