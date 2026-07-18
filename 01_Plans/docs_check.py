#!/usr/bin/env python3
"""Run the local docs-contract checks through one deterministic entrypoint."""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from docs_contract_checks import (
    check_compose_service_commands,
    check_current_history_headings,
    check_document_contract_baseline,
    check_history_metadata,
    check_npm_script_commands,
    check_public_boundary,
    check_relative_links,
    check_repository_path_commands,
    check_runtime_parameter_key_commands,
    check_safety_routes,
    tracked_markdown_paths as contract_tracked_markdown_paths,
)
from issues.validate_active_issue_memos import discover_active_rows, validate
from triage_actionable_plans import collect


@dataclass(frozen=True)
class DocsCheckResult:
    active_count: int
    markdown_count: int
    errors: tuple[str, ...]


def _run_contract_tests(root: Path) -> list[str]:
    suites = (
        (root / "01_Plans" / "issues" / "tests"),
        (root / "01_Plans" / "tests"),
    )
    errors: list[str] = []
    for suite in suites:
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(suite), "-p", "test_*.py"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if completed.returncode == 0:
            continue
        detail = (completed.stderr or completed.stdout).strip()
        errors.append(
            f"DC-ACT-001 {suite.relative_to(root).as_posix()}: contract tests failed. "
            f"Fix: repair the failing fixture or rule implementation.\n{detail}"
        )
    return errors


def run_docs_check(
    root: Path,
    *,
    run_tests: bool = True,
) -> DocsCheckResult:
    repository_root = root.resolve()
    issue_root = repository_root / "01_Plans" / "issues"
    errors = [
        f"DC-ACT-001 01_Plans/issues: {error} Fix: update the named memo or its referenced file."
        for error in validate(issue_root)
    ]

    triage_report = collect(repository_root / "01_Plans")
    for error in triage_report["errors"]:
        errors.append(
            f"DC-ACT-001 01_Plans/{error['path']}: {error['reason']}. "
            "Fix: use canonical metadata or repair the dependency path."
        )

    active_rows = discover_active_rows(issue_root)
    triage_active_count = triage_report["summary"]["active_issue_count"]
    if len(active_rows) != triage_active_count:
        errors.append(
            "DC-ACT-001 01_Plans/issues: validator/triage active set count mismatch "
            f"({len(active_rows)} != {triage_active_count}). Fix: use the shared Status parser for both views."
        )

    markdown_paths = contract_tracked_markdown_paths(repository_root)
    errors.extend(finding.render() for finding in check_relative_links(repository_root, markdown_paths))
    errors.extend(finding.render() for finding in check_current_history_headings(repository_root))
    errors.extend(finding.render() for finding in check_document_contract_baseline(repository_root))
    errors.extend(finding.render() for finding in check_history_metadata(repository_root))
    errors.extend(finding.render() for finding in check_public_boundary(repository_root))
    errors.extend(finding.render() for finding in check_safety_routes(repository_root))
    errors.extend(finding.render() for finding in check_npm_script_commands(repository_root, markdown_paths))
    errors.extend(finding.render() for finding in check_compose_service_commands(repository_root, markdown_paths))
    errors.extend(finding.render() for finding in check_runtime_parameter_key_commands(repository_root, markdown_paths))
    errors.extend(finding.render() for finding in check_repository_path_commands(repository_root, markdown_paths))
    if run_tests:
        errors.extend(_run_contract_tests(repository_root))

    return DocsCheckResult(
        active_count=len(active_rows),
        markdown_count=len(markdown_paths),
        errors=tuple(errors),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root (defaults to the parent of 01_Plans)",
    )
    args = parser.parse_args()

    try:
        result = run_docs_check(args.root)
    except (OSError, RuntimeError) as exc:
        print(f"docs-check setup failed: {exc}")
        return 1

    if result.errors:
        print("docs-check failed:")
        for error in result.errors:
            print(f"- {error}")
        return 1

    print(
        "docs-check passed: "
        f"active_memos={result.active_count}, tracked_markdown={result.markdown_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
