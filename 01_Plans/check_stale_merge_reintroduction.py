#!/usr/bin/env python3
"""Diagnose strong stale-state reintroduction candidates before branch integration.

This tool is intentionally narrower than a merge policy:
- commit distance is reported but never treated as a defect by itself;
- paths changed on both sides are review signals, not automatic failures;
- only strong path-level state reversals are eligible for --fail-on-strong.

It complements, rather than replaces, typecheck/tests and exact-path regression guards.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Finding:
    path: str
    base_status: str
    head_status: str
    base_exists: bool
    head_exists: bool
    classification: str
    severity: str


@dataclass(frozen=True)
class Report:
    schemaVersion: int
    baseRef: str
    headRef: str
    baseCommit: str
    headCommit: str
    mergeBase: str
    baseCommitsSinceMergeBase: int
    headCommitsSinceMergeBase: int
    baseChangedPathCount: int
    headChangedPathCount: int
    overlapCount: int
    strongCount: int
    findings: list[Finding]


def _git(repo_root: Path, args: Iterable[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _resolve(repo_root: Path, ref: str) -> str:
    return _git(repo_root, ["rev-parse", "--verify", f"{ref}^{{commit}}"]).stdout.strip()


def _parse_name_status(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            raise ValueError(f"unexpected git --name-status line: {raw_line!r}")
        status, path = parts
        # --no-renames keeps the path shape single-valued. Keep only the primary
        # status letter so future score suffixes cannot change classification.
        result[path] = status[:1]
    return result


def _changed_paths(repo_root: Path, merge_base: str, ref: str) -> dict[str, str]:
    completed = _git(
        repo_root,
        ["diff", "--name-status", "--no-renames", f"{merge_base}..{ref}", "--"],
    )
    return _parse_name_status(completed.stdout)


def _tree_has(repo_root: Path, ref: str, path: str) -> bool:
    completed = _git(repo_root, ["cat-file", "-e", f"{ref}:{path}"], check=False)
    return completed.returncode == 0


def _commit_count(repo_root: Path, merge_base: str, ref: str) -> int:
    return int(_git(repo_root, ["rev-list", "--count", f"{merge_base}..{ref}"]).stdout.strip())


def analyze_repository(repo_root: Path, base_ref: str, head_ref: str) -> Report:
    repo_root = repo_root.resolve()
    base_commit = _resolve(repo_root, base_ref)
    head_commit = _resolve(repo_root, head_ref)
    merge_base = _git(repo_root, ["merge-base", base_commit, head_commit]).stdout.strip()
    if not merge_base:
        raise RuntimeError("git merge-base returned no commit")

    base_changes = _changed_paths(repo_root, merge_base, base_commit)
    head_changes = _changed_paths(repo_root, merge_base, head_commit)

    findings: list[Finding] = []
    for path in sorted(set(base_changes) & set(head_changes)):
        base_status = base_changes[path]
        head_status = head_changes[path]
        base_exists = _tree_has(repo_root, base_commit, path)
        head_exists = _tree_has(repo_root, head_commit, path)

        if base_status == "D" and not base_exists and head_exists:
            classification = "main_deleted_branch_present"
            severity = "strong"
        elif head_status == "D" and base_exists and not head_exists:
            classification = "branch_deletes_main_present"
            severity = "strong"
        elif not base_exists and not head_exists:
            classification = "aligned_absence"
            severity = "info"
        else:
            classification = "overlap_review"
            severity = "review"

        findings.append(
            Finding(
                path=path,
                base_status=base_status,
                head_status=head_status,
                base_exists=base_exists,
                head_exists=head_exists,
                classification=classification,
                severity=severity,
            )
        )

    strong_count = sum(1 for finding in findings if finding.severity == "strong")
    return Report(
        schemaVersion=1,
        baseRef=base_ref,
        headRef=head_ref,
        baseCommit=base_commit,
        headCommit=head_commit,
        mergeBase=merge_base,
        baseCommitsSinceMergeBase=_commit_count(repo_root, merge_base, base_commit),
        headCommitsSinceMergeBase=_commit_count(repo_root, merge_base, head_commit),
        baseChangedPathCount=len(base_changes),
        headChangedPathCount=len(head_changes),
        overlapCount=len(findings),
        strongCount=strong_count,
        findings=findings,
    )


def report_as_dict(report: Report) -> dict[str, object]:
    data = asdict(report)
    # Keep the public JSON shape explicit and stable even though dataclasses use
    # Python naming internally.
    return data


def _print_text(report: Report) -> None:
    print(f"base: {report.baseRef} ({report.baseCommit})")
    print(f"head: {report.headRef} ({report.headCommit})")
    print(f"merge-base: {report.mergeBase}")
    print(
        "commits since merge-base: "
        f"base={report.baseCommitsSinceMergeBase}, head={report.headCommitsSinceMergeBase}"
    )
    print(
        "changed paths: "
        f"base={report.baseChangedPathCount}, head={report.headChangedPathCount}, "
        f"overlap={report.overlapCount}, strong={report.strongCount}"
    )
    for finding in report.findings:
        print(
            f"[{finding.severity}] {finding.classification}: {finding.path} "
            f"(base={finding.base_status}, head={finding.head_status}, "
            f"base_exists={finding.base_exists}, head_exists={finding.head_exists})"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagnose stale-state reintroduction candidates before merge."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--fail-on-strong",
        action="store_true",
        help="exit 2 when strong path-level state reversal candidates exist",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = analyze_repository(args.repo_root, args.base_ref, args.head_ref)
    except (subprocess.CalledProcessError, ValueError, RuntimeError) as exc:
        if isinstance(exc, subprocess.CalledProcessError):
            detail = exc.stderr.strip() or str(exc)
        else:
            detail = str(exc)
        print(f"ERROR: {detail}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(report_as_dict(report), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_text(report)

    if args.fail_on_strong and report.strongCount:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
