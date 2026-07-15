#!/usr/bin/env python3
"""Run the local docs-contract checks through one deterministic entrypoint."""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from docs_contract_checks import (
    RequiredRoute,
    check_conflict_markers,
    check_current_only_headings,
    check_history_documents,
    check_public_ui_catalog,
    check_relative_links,
    check_required_routes,
    check_safety_invariant_route,
)
from issues.validate_active_issue_memos import discover_active_rows, validate
from triage_actionable_plans import collect

ENABLED_RULES = (
    "DC-ACT-001",
    "DC-LNK-001",
    "DC-CUR-001",
    "DC-HIS-001",
    "DC-RTE-001",
    "DC-PUB-001",
    "DC-FMT-001",
    "DC-SAF-001",
)
NOT_ENABLED_RULES = (
    "DC-ARC-001",
)
HISTORY_INDEX_PATH = Path("02_Architecture/history/README.md")
PUBLIC_CATALOG_PATH = Path("04_Documentation/ui_catalog.md")
SCREENSHOT_LEDGER_PATH = Path("04_Documentation/assets/screenshots/README.md")
SAFETY_ENTRY_PATH = Path("AGENTS.md")
REQUIRED_ROUTES = (
    RequiredRoute(Path("README.md"), Path("CONTRIBUTING.md"), "CONTRIBUTING.md", True),
    RequiredRoute(
        Path("README.md"),
        Path("04_Documentation/public_index.md"),
        "04_Documentation/public_index.md",
        True,
    ),
    RequiredRoute(
        Path("CONTRIBUTING.md"),
        Path("01_Plans/triage_actionable_plans.py"),
        "python 01_Plans/triage_actionable_plans.py",
        False,
    ),
    RequiredRoute(
        Path("CONTRIBUTING.md"),
        Path("01_Plans/issues/README.md"),
        "01_Plans/issues/README.md",
        False,
    ),
    RequiredRoute(
        Path("CONTRIBUTING.md"),
        Path("01_Plans/issues/TEMPLATE.md"),
        "01_Plans/issues/TEMPLATE.md",
        False,
    ),
    RequiredRoute(
        Path("CONTRIBUTING.md"),
        Path("01_Plans/docs_check.py"),
        "python 01_Plans/docs_check.py",
        False,
    ),
    RequiredRoute(
        Path("01_Plans/issues/README.md"),
        Path("01_Plans/issues/TEMPLATE.md"),
        "TEMPLATE.md",
        False,
    ),
    RequiredRoute(
        Path("01_Plans/issues/README.md"),
        Path("01_Plans/issues/validate_active_issue_memos.py"),
        "python 01_Plans/issues/validate_active_issue_memos.py",
        False,
    ),
    RequiredRoute(
        Path("01_Plans/issues/README.md"),
        Path("01_Plans/triage_actionable_plans.py"),
        "python 01_Plans/triage_actionable_plans.py",
        False,
    ),
    RequiredRoute(
        Path("01_Plans/issues/README.md"),
        Path("01_Plans/docs_check.py"),
        "python 01_Plans/docs_check.py",
        False,
    ),
    *(
        RequiredRoute(
            Path("04_Documentation/public_index.md"),
            Path(f"04_Documentation/{name}"),
            name,
            True,
        )
        for name in (
            "installation.md",
            "configuration.md",
            "data_handling.md",
            "operations.md",
            "acceptance_check.md",
            "diagnostics.md",
        )
    ),
)

CURRENT_ONLY_PATHS = (
    Path("01_Plans/project-progress-dashboard.md"),
    Path("01_Plans/issues/README.md"),
    Path("01_Plans/documentation_quality.md"),
    Path("02_Architecture/architecture.md"),
    Path("02_Architecture/api.md"),
    Path("02_Architecture/schemas.md"),
    Path("02_Architecture/data_model_operations_overview.md"),
)


@dataclass(frozen=True)
class DocsCheckResult:
    active_count: int
    markdown_count: int
    errors: tuple[str, ...]


def tracked_markdown_paths(root: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "*.md"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "git ls-files failed"
        raise RuntimeError(detail)
    return [Path(line) for line in completed.stdout.splitlines() if line]


def _run_contract_tests(root: Path) -> list[str]:
    suites = (
        ("DC-ACT-001", root / "01_Plans" / "issues" / "tests"),
        ("DC-ACT-001/DC-LNK-001", root / "01_Plans" / "tests"),
    )
    errors: list[str] = []
    for rule_ids, suite in suites:
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
            f"{rule_ids} {suite.relative_to(root).as_posix()}: contract tests failed. "
            f"Fix: repair the failing fixture or rule implementation.\n{detail}"
        )
    return errors


def _run_local_diff_checks(root: Path) -> list[str]:
    errors: list[str] = []
    for label, command in (
        ("working tree", ["git", "diff", "--check"]),
        ("staged changes", ["git", "diff", "--cached", "--check"]),
    ):
        completed = subprocess.run(
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if completed.returncode == 0:
            continue
        detail = (completed.stdout or completed.stderr).strip()
        errors.append(
            f"DC-FMT-001 repository: git diff --check failed for {label}. "
            f"Fix: remove the reported whitespace/error markers.\n{detail}"
        )
    return errors


def run_docs_check(
    root: Path,
    *,
    run_tests: bool = True,
    required_routes: tuple[RequiredRoute, ...] = REQUIRED_ROUTES,
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

    markdown_paths = tracked_markdown_paths(repository_root)
    errors.extend(finding.render() for finding in check_relative_links(repository_root, markdown_paths))
    errors.extend(finding.render() for finding in check_conflict_markers(repository_root, markdown_paths))
    errors.extend(
        finding.render()
        for finding in check_current_only_headings(repository_root, list(CURRENT_ONLY_PATHS))
    )
    history_root = repository_root / HISTORY_INDEX_PATH.parent
    history_paths = [
        path
        for path in history_root.glob("*.md")
        if path.name.casefold() != "readme.md"
    ]
    errors.extend(
        finding.render()
        for finding in check_history_documents(repository_root, history_paths, HISTORY_INDEX_PATH)
    )
    errors.extend(
        finding.render()
        for finding in check_required_routes(repository_root, list(required_routes))
    )
    errors.extend(
        finding.render()
        for finding in check_public_ui_catalog(
            repository_root, PUBLIC_CATALOG_PATH, SCREENSHOT_LEDGER_PATH
        )
    )
    errors.extend(_run_local_diff_checks(repository_root))
    errors.extend(
        finding.render()
        for finding in check_safety_invariant_route(repository_root, SAFETY_ENTRY_PATH)
    )
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

    print(f"enabled rules: {', '.join(ENABLED_RULES)}")
    print(f"not enabled: {', '.join(NOT_ENABLED_RULES)}")
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
