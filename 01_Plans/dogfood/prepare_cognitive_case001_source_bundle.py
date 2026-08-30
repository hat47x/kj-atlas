#!/usr/bin/env python3
"""Prepare the frozen Case 001 Round 1 product-source bundle.

This is experiment tooling, not a KJ Atlas product feature. It reads the
machine-readable source manifest, extracts every common source from the frozen
product commit with git, verifies the Git blob SHA, and writes a self-contained
read-only input directory for an isolated arm context.

The tool deliberately does not copy launch packets, Case 0 audits, PR notes,
Round 2 material, or other excluded inputs into the product evidence bundle.
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
DEFAULT_MANIFEST = DOGFOOD_DIR / "cognitive-dogfood-case-001-round1-source-manifest.json"
BUNDLE_METADATA_DIR = "_experiment"
BUNDLE_METADATA_FILE = "bundle-manifest.json"
FROZEN_SOURCE_MANIFEST_FILE = "source-manifest.json"


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
        raise BundleError("unsupported source manifest schemaVersion")
    if data.get("caseId") != "case-001" or data.get("round") != 1:
        raise BundleError("manifest is not Case 001 Round 1")
    commit = data.get("productCommit")
    sources = data.get("commonSources")
    if not isinstance(commit, str) or len(commit) < 7:
        raise BundleError("manifest productCommit is missing")
    if not isinstance(sources, list) or not sources:
        raise BundleError("manifest commonSources is empty")
    return data


def validate_relative_repo_path(raw: str) -> PurePosixPath:
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise BundleError(f"unsafe repository path in manifest: {raw!r}")
    return path


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def prepare_bundle(
    repo_root: Path,
    manifest_path: Path,
    output_dir: Path,
    force: bool,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    product_commit = manifest["productCommit"]
    common_sources = manifest["commonSources"]

    repo_root = repo_root.resolve()
    git_marker = repo_root / ".git"
    if not git_marker.exists():
        raise BundleError(f"not a git checkout/worktree: {repo_root}")

    resolved_commit = run_git(
        repo_root, "rev-parse", f"{product_commit}^{{commit}}", text=True
    )
    if resolved_commit != product_commit:
        raise BundleError(
            f"frozen product commit resolved to {resolved_commit}, expected {product_commit}"
        )

    output_dir = output_dir.resolve()
    if output_dir == repo_root or output_dir in repo_root.parents:
        raise BundleError(
            "refusing to use the repository root or one of its ancestors as output"
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
        for source in common_sources:
            if not isinstance(source, dict):
                raise BundleError("commonSources contains a non-object entry")
            raw_path = source.get("path")
            expected_blob = source.get("blobSha")
            if not isinstance(raw_path, str) or not isinstance(expected_blob, str):
                raise BundleError("source entry requires path and blobSha strings")
            if raw_path in seen_paths:
                raise BundleError(f"duplicate source path: {raw_path}")
            seen_paths.add(raw_path)
            repo_path = validate_relative_repo_path(raw_path)

            actual_blob = run_git(
                repo_root,
                "rev-parse",
                f"{product_commit}:{repo_path.as_posix()}",
                text=True,
            )
            if actual_blob != expected_blob:
                raise BundleError(
                    f"blob mismatch for {raw_path}: got {actual_blob}, expected {expected_blob}"
                )

            content = run_git(
                repo_root,
                "show",
                f"{product_commit}:{repo_path.as_posix()}",
            )
            assert isinstance(content, bytes)
            # All registered Case 001 sources are intended to be UTF-8 textual
            # evidence. Fail closed rather than silently handing binary/garbled
            # material to only some arms.
            try:
                content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise BundleError(f"source is not UTF-8 text: {raw_path}") from exc

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

        frozen_manifest_bytes = manifest_path.read_bytes()
        (metadata_dir / FROZEN_SOURCE_MANIFEST_FILE).write_bytes(frozen_manifest_bytes)

        bundle_metadata = {
            "schemaVersion": 1,
            "manifestId": manifest["manifestId"],
            "caseId": manifest["caseId"],
            "round": manifest["round"],
            "productRepository": manifest["productRepository"],
            "productCommit": product_commit,
            "sourceCount": len(bundle_sources),
            "sources": bundle_sources,
            "sourceManifestSha256": sha256_bytes(frozen_manifest_bytes),
            "excludedInputsCopied": False,
            "notes": [
                "This directory contains only the common frozen product evidence sources plus experiment metadata.",
                "Launch/method packets are intentionally supplied separately so the evidence bundle is identical across arms.",
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
        description="Prepare and verify the frozen Case 001 Round 1 source bundle."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="kj-atlas git checkout/worktree (default: current directory)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="machine-readable frozen source manifest",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new bundle directory to create",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing output directory",
    )
    args = parser.parse_args()

    try:
        metadata = prepare_bundle(
            args.repo_root, args.manifest, args.output, args.force
        )
    except BundleError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        "PASS: prepared "
        f"{metadata['sourceCount']} frozen sources for {metadata['manifestId']}"
    )
    print(f"PRODUCT_COMMIT: {metadata['productCommit']}")
    print(f"OUTPUT: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
