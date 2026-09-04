#!/usr/bin/env python3
"""Validate assembled cognitive-dogfood arm packages before artifact upload.

This validator is intentionally fail-closed. It checks the *assembled* package,
not only the source manifests used to build it, so packaging regressions cannot
silently leak operator-only material, a wrong treatment, or a different frozen
snapshot into a fresh arm.

Expected treatment boundary:
- A: product + launch only
- B: product + skill + launch
- C: product + starter + launch
- D: product + skill + starter + launch

For product/skill bundles, the file set must match the generated bundle manifest
exactly, each source file must match both its SHA-256 digest and Git blob SHA,
and the bundle identity must match the preregistered operator-side manifest.
The assembled ``launch.md`` must be byte-for-byte identical to the frozen launch
packet for that case/arm.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

DOGFOOD_DIR = Path(__file__).resolve().parent
CASES = ("001", "002", "003")
ARMS = ("A", "B", "C", "D")
ARM_LAUNCH_MODE = {
    "A": "ordinary",
    "B": "skill",
    "C": "atlas",
    "D": "atlas-skill",
}
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


def git_blob_sha_file(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


def is_hex_sha(value: object, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(char in "0123456789abcdef" for char in value)
    )


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
    seen_source_paths: set[str] = set()
    for index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            issues.append(f"{label}: source #{index} is not an object")
            continue
        raw_path = source.get("path")
        expected_sha = source.get("sha256")
        expected_git_blob = source.get("gitBlobSha")
        if not isinstance(raw_path, str) or not raw_path:
            issues.append(f"{label}: source #{index} has no path")
            continue
        if raw_path in seen_source_paths:
            issues.append(f"{label}: duplicate source path in bundle manifest: {raw_path}")
            continue
        seen_source_paths.add(raw_path)
        if raw_path.startswith("/") or ".." in Path(raw_path).parts:
            issues.append(f"{label}: unsafe source path: {raw_path}")
            continue
        expected_files.add(raw_path)
        source_path = bundle_dir / raw_path
        if not source_path.is_file():
            issues.append(f"{label}: missing source file: {raw_path}")
            continue
        if not is_hex_sha(expected_sha, 64):
            issues.append(f"{label}: source has invalid sha256 metadata: {raw_path}")
        else:
            actual_sha = sha256_file(source_path)
            if actual_sha != expected_sha:
                issues.append(
                    f"{label}: sha256 mismatch for {raw_path}: "
                    f"got {actual_sha}, expected {expected_sha}"
                )
        if not is_hex_sha(expected_git_blob, 40):
            issues.append(f"{label}: source has invalid gitBlobSha metadata: {raw_path}")
        else:
            actual_git_blob = git_blob_sha_file(source_path)
            if actual_git_blob != expected_git_blob:
                issues.append(
                    f"{label}: git blob SHA mismatch for {raw_path}: "
                    f"got {actual_git_blob}, expected {expected_git_blob}"
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


def validate_frozen_source_identity(
    actual_manifest: dict,
    expected_sources: object,
    label: str,
    issues: list[str],
) -> None:
    actual_sources = actual_manifest.get("sources")
    if not isinstance(actual_sources, list) or not isinstance(expected_sources, list):
        issues.append(f"{label}: cannot compare frozen source identity")
        return

    def source_map(items: list, blob_field: str) -> dict[str, str] | None:
        result: dict[str, str] = {}
        for item in items:
            if not isinstance(item, dict):
                return None
            path = item.get("path")
            blob = item.get(blob_field)
            if not isinstance(path, str) or not isinstance(blob, str) or path in result:
                return None
            result[path] = blob
        return result

    actual = source_map(actual_sources, "gitBlobSha")
    expected = source_map(expected_sources, "blobSha")
    if actual is None or expected is None:
        issues.append(f"{label}: malformed or duplicate frozen source identity")
        return
    if actual != expected:
        issues.append(f"{label}: frozen source path/blob identity differs from preregistration")


def validate_launch(
    package: Path,
    case_number: str,
    arm: str,
    label: str,
    issues: list[str],
) -> None:
    launch = package / "launch.md"
    expected_launch = (
        DOGFOOD_DIR
        / f"cognitive-dogfood-case-{case_number}-launch-{ARM_LAUNCH_MODE[arm]}.md"
    )
    if not launch.is_file():
        issues.append(f"{label}: launch.md missing")
        return
    if not launch.read_bytes():
        issues.append(f"{label}: launch.md is empty")
        return
    if not expected_launch.is_file():
        issues.append(f"{label}: frozen launch packet missing: {expected_launch.name}")
        return
    if launch.read_bytes() != expected_launch.read_bytes():
        issues.append(
            f"{label}: launch.md differs from frozen {expected_launch.name}"
        )


def validate_product(package: Path, case_number: str, label: str, issues: list[str]) -> None:
    manifest = validate_exact_bundle_files(
        package / "product",
        "_experiment/bundle-manifest.json",
        f"{label} product",
        issues,
    )
    if manifest is None:
        return

    operator_manifest = load_json(
        DOGFOOD_DIR / f"cognitive-dogfood-case-{case_number}-round1-source-manifest.json",
        f"{label} preregistered product manifest",
        issues,
    )
    if operator_manifest is None:
        return

    expected_case = f"case-{case_number}"
    if manifest.get("caseId") != expected_case:
        issues.append(f"{label}: product bundle caseId mismatch")
    if manifest.get("round") != 1:
        issues.append(f"{label}: product bundle round must remain 1")
    if manifest.get("operatorOnlyMetadataCopied") is not False:
        issues.append(f"{label}: product bundle must not copy operator-only metadata")

    expected_identity = {
        "bundleId": operator_manifest.get("manifestId"),
        "productRepository": operator_manifest.get("productRepository"),
        "productCommit": operator_manifest.get("productCommit"),
    }
    for field, expected in expected_identity.items():
        if manifest.get(field) != expected:
            issues.append(
                f"{label}: product bundle {field} differs from preregistration"
            )

    expected_sources = operator_manifest.get("commonSources")
    if isinstance(expected_sources, list) and manifest.get("sourceCount") != len(expected_sources):
        issues.append(f"{label}: product bundle sourceCount differs from preregistration")
    validate_frozen_source_identity(manifest, expected_sources, f"{label} product", issues)


def validate_skill(package: Path, label: str, issues: list[str]) -> None:
    manifest = validate_exact_bundle_files(
        package / "skill",
        "_experiment/skill-bundle-manifest.json",
        f"{label} skill",
        issues,
    )
    if manifest is None:
        return

    operator_manifest = load_json(
        DOGFOOD_DIR / "cognitive-dogfood-case-001-skill-manifest.json",
        f"{label} preregistered skill manifest",
        issues,
    )
    if operator_manifest is None:
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

    skill_commit = operator_manifest.get("skillCommit")
    expected_identity = {
        "manifestId": (
            f"cognitive-dogfood-skill-ja@{skill_commit}"
            if isinstance(skill_commit, str)
            else None
        ),
        "skillRepository": operator_manifest.get("skillRepository"),
        "skillCommit": skill_commit,
        "locale": operator_manifest.get("locale"),
        "canonicalRoot": operator_manifest.get("canonicalRoot"),
    }
    for field, expected in expected_identity.items():
        if manifest.get(field) != expected:
            issues.append(f"{label}: skill bundle {field} differs from preregistration")

    expected_sources = operator_manifest.get("canonicalSources")
    if isinstance(expected_sources, list) and manifest.get("sourceCount") != len(expected_sources):
        issues.append(f"{label}: skill bundle sourceCount differs from preregistration")
    validate_frozen_source_identity(manifest, expected_sources, f"{label} skill", issues)


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

    validate_launch(package, case_number, arm, label, issues)
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

    print("\nAll assembled cognitive-dogfood arm packages satisfy frozen treatment boundaries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
