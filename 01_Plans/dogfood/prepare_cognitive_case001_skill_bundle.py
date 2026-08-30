#!/usr/bin/env python3
"""Prepare the frozen Case 001 Japanese canonical skill bundle.

This is experiment tooling. It extracts only the preregistered canonical
`src/ja-JP` files from the frozen cultural-substrate-weaving commit and verifies
each Git blob SHA. Repository docs, evals, generated plugin copies, adapters,
PR material, and coevolution notes are not copied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

DOGFOOD_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST = DOGFOOD_DIR / "cognitive-dogfood-case-001-skill-manifest.json"
BUNDLE_METADATA_DIR = "_experiment"
BUNDLE_METADATA_FILE = "skill-bundle-manifest.json"


class BundleError(RuntimeError):
    pass


def run_git(repo_root: Path, *args: str, text: bool = False) -> bytes | str:
    command = ["git", "-C", str(repo_root), *args]
    try:
        completed = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise BundleError("git executable was not found") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="replace").strip()
        raise BundleError(
            f"git command failed ({' '.join(command)}): {stderr or exc.returncode}"
        ) from exc
    if text:
        return completed.stdout.decode("utf-8").strip()
    return completed.stdout


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BundleError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BundleError(f"manifest is not valid JSON: {path}: {exc}") from exc

    if data.get("schemaVersion") != 1:
        raise BundleError("unsupported skill manifest schemaVersion")
    if data.get("caseId") != "case-001":
        raise BundleError("manifest is not for Case 001")
    if data.get("locale") != "ja-JP" or data.get("canonicalRoot") != "src/ja-JP":
        raise BundleError("skill manifest must identify canonical ja-JP source")
    commit = data.get("skillCommit")
    sources = data.get("canonicalSources")
    if not isinstance(commit, str) or len(commit) < 7:
        raise BundleError("manifest skillCommit is missing")
    if not isinstance(sources, list) or not sources:
        raise BundleError("manifest canonicalSources is empty")
    return data


def validate_relative_repo_path(raw: str, canonical_root: str) -> PurePosixPath:
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise BundleError(f"unsafe repository path in manifest: {raw!r}")
    root = PurePosixPath(canonical_root)
    if path != root and root not in path.parents:
        raise BundleError(f"skill path escapes canonical root {canonical_root}: {raw}")
    return path


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def prepare_bundle(
    skill_repo_root: Path,
    manifest_path: Path,
    output_dir: Path,
    force: bool,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    skill_commit = manifest["skillCommit"]
    canonical_root = manifest["canonicalRoot"]
    canonical_sources = manifest["canonicalSources"]

    skill_repo_root = skill_repo_root.resolve()
    if not (skill_repo_root / ".git").exists():
        raise BundleError(f"not a git checkout/worktree: {skill_repo_root}")

    resolved_commit = run_git(
        skill_repo_root, "rev-parse", f"{skill_commit}^{{commit}}", text=True
    )
    if resolved_commit != skill_commit:
        raise BundleError(
            f"frozen skill commit resolved to {resolved_commit}, expected {skill_commit}"
        )

    output_dir = output_dir.resolve()
    if output_dir == skill_repo_root or output_dir in skill_repo_root.parents:
        raise BundleError(
            "refusing to use the skill repository root or one of its ancestors as output"
        )
    if output_dir.exists():
        if not force:
            raise BundleError(
                f"output already exists: {output_dir}; use --force to replace it"
            )
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)

    seen_paths: set[str] = set()
    bundle_sources: list[dict[str, str]] = []

    try:
        for source in canonical_sources:
            if not isinstance(source, dict):
                raise BundleError("canonicalSources contains a non-object entry")
            raw_path = source.get("path")
            expected_blob = source.get("blobSha")
            if not isinstance(raw_path, str) or not isinstance(expected_blob, str):
                raise BundleError("skill source entry requires path and blobSha strings")
            if raw_path in seen_paths:
                raise BundleError(f"duplicate skill source path: {raw_path}")
            seen_paths.add(raw_path)
            repo_path = validate_relative_repo_path(raw_path, canonical_root)

            actual_blob = run_git(
                skill_repo_root,
                "rev-parse",
                f"{skill_commit}:{repo_path.as_posix()}",
                text=True,
            )
            if actual_blob != expected_blob:
                raise BundleError(
                    f"blob mismatch for {raw_path}: got {actual_blob}, expected {expected_blob}"
                )

            content = run_git(
                skill_repo_root,
                "show",
                f"{skill_commit}:{repo_path.as_posix()}",
            )
            assert isinstance(content, bytes)
            try:
                content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise BundleError(f"skill source is not UTF-8 text: {raw_path}") from exc

            target = output_dir.joinpath(*repo_path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            bundle_sources.append(
                {
                    "path": raw_path,
                    "gitBlobSha": actual_blob,
                    "sha256": sha256_bytes(content),
                }
            )

        metadata_dir = output_dir / BUNDLE_METADATA_DIR
        metadata_dir.mkdir(parents=True, exist_ok=True)
        bundle_metadata = {
            "schemaVersion": 1,
            "manifestId": manifest["manifestId"],
            "skillRepository": manifest["skillRepository"],
            "skillCommit": skill_commit,
            "locale": manifest["locale"],
            "canonicalRoot": canonical_root,
            "sourceCount": len(bundle_sources),
            "sources": bundle_sources,
            "operatorManifestCopied": False,
            "repositoryDocsCopied": False,
            "evaluationArtifactsCopied": False,
            "notes": [
                "This bundle contains only the frozen canonical ja-JP skill source preregistered for B/D.",
                "ROUTER.md decides relevance; bundle presence does not force every canonical file to be activated.",
            ],
        }
        metadata_text = json.dumps(
            bundle_metadata, ensure_ascii=False, indent=2, sort_keys=True
        ) + "\n"
        (metadata_dir / BUNDLE_METADATA_FILE).write_text(metadata_text, encoding="utf-8")
    except Exception:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise

    return bundle_metadata


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare and verify the frozen Case 001 ja-JP skill bundle."
    )
    parser.add_argument(
        "--skill-repo-root",
        type=Path,
        required=True,
        help="cultural-substrate-weaving git checkout/worktree",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="operator-only frozen skill manifest",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new sanitized skill bundle directory to create",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing output directory",
    )
    args = parser.parse_args()

    try:
        metadata = prepare_bundle(
            args.skill_repo_root, args.manifest, args.output, args.force
        )
    except BundleError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        "PASS: prepared "
        f"{metadata['sourceCount']} canonical skill sources for {metadata['manifestId']}"
    )
    print(f"SKILL_COMMIT: {metadata['skillCommit']}")
    print(f"OUTPUT: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
