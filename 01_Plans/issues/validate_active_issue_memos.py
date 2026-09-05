#!/usr/bin/env python3
"""Validate active issue memo metadata consistency.

Checks active memo files discovered from their own `Status` metadata. README is
an entry point, not a second status registry.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from .issue_memo_status import (
        ACTIVE_ISSUE_STATUSES,
        CANONICAL_ISSUE_STATUSES,
        parse_issue_status,
    )
except ImportError:  # Direct script execution from 01_Plans/issues/.
    from issue_memo_status import (
        ACTIVE_ISSUE_STATUSES,
        CANONICAL_ISSUE_STATUSES,
        parse_issue_status,
    )

ALLOWED_VERIFICATION_LEVELS = {"docs-check", "unit", "integration", "e2e"}
REQUIRED_FIELDS = [
    "- Type:",
    "- Status:",
    "- Source Issue:",
    "- Priority:",
    "- Scope:",
    "- Related ADR/Spec:",
    "- Expected verification level:",
]

# DOC-ISSUE-LIFECYCLE-01: R18 observed 58 historical memos whose Status is
# already Done while the file still lives directly under 01_Plans/issues/.
# Keep that existing debt non-blocking, but require this baseline to move down
# in the same change whenever legacy memos are migrated. Exact equality makes
# the ratchet monotonic: debt cannot silently grow back after it has shrunk.
LEGACY_DONE_AT_ROOT_BASELINE = 25

# DOC-ISSUE-LEGACY-PATH-01: count equality cannot detect a same-count swap in
# which one historical Done-at-root memo is migrated while a newly completed
# memo is left at the active root. Preserve the R18 identity boundary as an
# immutable, machine-generated manifest. Unlike the count baseline, this file
# never shrinks; current Done-at-root paths must remain a subset of it.
LEGACY_DONE_AT_ROOT_IDENTITY_COMMIT = "88aebae242d5d1a24278b3247d3544aeaa1ad386"
LEGACY_DONE_AT_ROOT_IDENTITY_MANIFEST = Path(__file__).resolve().with_name(
    "legacy_done_at_root_r18.json"
)


@dataclass(frozen=True)
class ActiveMemoRow:
    backlog: str
    memo: str
    status: str
    source: str


def parse_active_rows(readme_text: str) -> list[ActiveMemoRow]:
    rows: list[ActiveMemoRow] = []
    in_active_section = False
    for line in readme_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_active_section = stripped == "## Active issue memos"
            continue

        if not in_active_section:
            continue

        if "issue-" not in stripped or not stripped.startswith("|"):
            continue

        cols = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cols) != 4:
            continue
        if cols[0] == "Backlog ID":
            continue

        rows.append(
            ActiveMemoRow(
                backlog=cols[0],
                memo=cols[1].strip("`"),
                status=cols[2],
                source=cols[3],
            )
        )
    return rows


def discover_active_rows(root: Path) -> list[ActiveMemoRow]:
    """DOC-NORM-03: `memo` carries the path relative to `root`, not the bare
    filename. `root.rglob` already finds memos anywhere under `root`
    (including `done/`), but `validate_rows()` re-resolves `root / row.memo`
    to check existence -- a bare filename makes that re-resolution assume the
    memo sits directly under `root` and misreport a real, discovered file in
    `done/` as missing.
    """
    rows: list[ActiveMemoRow] = []
    for memo_path in sorted(root.rglob("issue-*.md")):
        text = memo_path.read_text(encoding="utf-8")
        status = parse_issue_status(extract_field_value(text, "Status"))
        if status not in ACTIVE_ISSUE_STATUSES:
            continue
        rows.append(
            ActiveMemoRow(
                backlog=memo_path.stem.removeprefix("issue-"),
                memo=memo_path.relative_to(root).as_posix(),
                status=status,
                source=extract_field_value(text, "Source Issue") or "",
            )
        )
    return rows


def extract_dependency_paths(memo_text: str) -> list[str]:
    lines = memo_text.splitlines()
    in_dependencies = False
    refs: list[str] = []
    heading_re = re.compile(r"^##+\s+(?:\d+\)\s*)?(?:依存関係|Dependencies)")
    section_re = re.compile(r"^##+\s+")
    for line in lines:
        stripped = line.strip()
        if heading_re.match(stripped):
            in_dependencies = True
            continue
        if in_dependencies and section_re.match(stripped):
            break
        if not in_dependencies:
            continue
        refs.extend(re.findall(r"`([^`]*issue-[^`]+\.md)`", line))
    return refs


def extract_field_value(memo_text: str, field_name: str) -> str | None:
    # Keep metadata parsing line-local. ``\s`` also matches newlines, so an
    # empty field could otherwise consume the next metadata line as its value.
    pattern = rf"^- {re.escape(field_name)}:[ \t]*(.*)$"
    match = re.search(pattern, memo_text, re.M)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def extract_verification_level(memo_text: str) -> str | None:
    # Preserve the existing contract: only the canonical backticked value is
    # interpreted here. The whitespace matcher is line-local for the same
    # reason as extract_field_value().
    match = re.search(
        r"^- Expected verification level:[ \t]*`([^`]+)`", memo_text, re.M
    )
    if not match:
        return None
    return match.group(1).strip()


def discover_done_memos_at_root(root: Path) -> list[Path]:
    """Return Done issue memos that still live directly at the active root."""
    done_paths: list[Path] = []
    for memo_path in sorted(root.glob("issue-*.md")):
        text = memo_path.read_text(encoding="utf-8")
        status = parse_issue_status(extract_field_value(text, "Status"))
        if status == "Done":
            done_paths.append(memo_path)
    return done_paths


def load_done_at_root_identity_manifest(
    manifest_path: Path = LEGACY_DONE_AT_ROOT_IDENTITY_MANIFEST,
) -> tuple[set[str] | None, list[str]]:
    """Load and validate the immutable R18 Done-at-root identity boundary."""
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [f"cannot read Done-at-root identity manifest: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid Done-at-root identity manifest JSON: {exc}"]

    errors: list[str] = []
    if not isinstance(raw, dict):
        return None, ["Done-at-root identity manifest must be a JSON object"]

    if raw.get("schemaVersion") != 1:
        errors.append("Done-at-root identity manifest schemaVersion must be 1")

    if raw.get("capturedFromCommit") != LEGACY_DONE_AT_ROOT_IDENTITY_COMMIT:
        errors.append(
            "Done-at-root identity manifest capturedFromCommit does not match "
            f"the fixed R18 boundary `{LEGACY_DONE_AT_ROOT_IDENTITY_COMMIT}`"
        )

    raw_paths = raw.get("paths")
    if not isinstance(raw_paths, list) or not all(
        isinstance(name, str) for name in raw_paths
    ):
        errors.append("Done-at-root identity manifest paths must be a string array")
        return None, errors

    paths = set(raw_paths)
    if len(paths) != len(raw_paths):
        errors.append("Done-at-root identity manifest contains duplicate paths")

    if raw.get("count") != len(paths):
        errors.append(
            "Done-at-root identity manifest count does not match unique path count "
            f"({raw.get('count')} != {len(paths)})"
        )

    invalid_names = sorted(
        name
        for name in paths
        if Path(name).name != name
        or not name.startswith("issue-")
        or not name.endswith(".md")
    )
    if invalid_names:
        errors.append(
            "Done-at-root identity manifest must contain memo basenames only: "
            + ", ".join(invalid_names)
        )

    return (paths if not errors else None), errors

def _legacy_done_paths_from_git_removed_by_merge(
    root: Path,
    baseline_commit: str = "",
) -> tuple[set[str] | None, str | None]:
    """Reconstruct the R18 root Done paths when running inside a Git checkout.

    Isolated unit-test fixtures are intentionally not repositories; callers can
    skip the identity guard there and test it by injecting `legacy_paths`.
    """
    try:
        repository = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError:
        return None, None
    except FileNotFoundError:
        return None, "git executable was not found; cannot verify Done-at-root identity"

    repository_root = Path(repository.stdout.strip()).resolve()
    try:
        relative_root = root.resolve().relative_to(repository_root).as_posix()
    except ValueError:
        return None, None

    pathspec = f"{relative_root}/issue-*.md"
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(repository_root),
            "grep",
            "-l",
            "-e",
            r"^- Status: Done$",
            baseline_commit,
            "--",
            pathspec,
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in (0, 1):
        detail = completed.stderr.strip() or f"git grep exited with {completed.returncode}"
        return None, f"cannot read R18 Done-at-root identity baseline: {detail}"

    prefix = f"{baseline_commit}:{relative_root}/"
    paths: set[str] = set()
    for line in completed.stdout.splitlines():
        if not line.startswith(prefix):
            return None, f"unexpected R18 baseline result `{line}`"
        paths.add(line[len(prefix) :])
    return paths, None


def validate_done_memo_identity(
    root: Path,
    *,
    legacy_paths: set[str] | None = None,
    manifest_path: Path = LEGACY_DONE_AT_ROOT_IDENTITY_MANIFEST,
) -> list[str]:
    """Reject new Done-at-root paths even when count-neutral swaps occur.

    The immutable R18 set is a historical admission boundary, not the current
    state. Existing legacy paths may disappear as they move to done/, but no
    path outside the R18 set may enter the root as Status Done.
    """
    if legacy_paths is None:
        legacy_paths, errors = load_done_at_root_identity_manifest(manifest_path)
        if errors:
            return errors
        assert legacy_paths is not None

    current_paths = {path.name for path in discover_done_memos_at_root(root)}
    unexpected = sorted(current_paths - legacy_paths)
    return [
        f"{name}: Status `Done` at active root was not part of the R18 legacy set; "
        "move the newly completed memo to 01_Plans/issues/done/. "
        "A same-count replacement does not preserve the lifecycle contract."
        for name in unexpected
    ]


def validate_memo_identity_and_placement(root: Path) -> list[str]:
    """Keep one physical memo per basename and reject active memos under done/.

    DOC-ISSUE-IDENTITY-01 was triggered by a completed memo whose old Draft copy
    reappeared at the active root while the authoritative Done copy still lived
    under done/. Status-only discovery then treated the stale copy as a new
    active P1. A move must therefore remain a move: the same memo basename may
    not coexist at root, done/, archive/, or another issue subdirectory.

    DOC-NORM-03 still applies: if an active memo is misplaced under done/, keep
    the discovered relative path so validation never misreports the file as
    missing. This check adds the more useful placement diagnosis on top.
    """
    errors: list[str] = []
    paths_by_name: dict[str, list[str]] = {}

    for memo_path in sorted(root.rglob("issue-*.md")):
        relative_path = memo_path.relative_to(root).as_posix()
        paths_by_name.setdefault(memo_path.name, []).append(relative_path)

        if memo_path.parent == root / "done":
            text = memo_path.read_text(encoding="utf-8")
            status = parse_issue_status(extract_field_value(text, "Status"))
            if status in ACTIVE_ISSUE_STATUSES:
                errors.append(
                    f"{relative_path}: active Status `{status}` is not allowed under done/; "
                    "move the memo to the active root or complete it as Status `Done`"
                )

    for memo_name, relative_paths in sorted(paths_by_name.items()):
        if len(relative_paths) > 1:
            errors.append(
                f"duplicate issue memo basename `{memo_name}`: "
                f"{', '.join(relative_paths)}; move the memo instead of keeping multiple copies"
            )

    return errors
def default_legacy_done_at_root_baseline(root: Path) -> int:
    """Return historical debt only for this repository's canonical issue root.

    `LEGACY_DONE_AT_ROOT_BASELINE` is not a generic invariant for every
    directory passed to the validator. It records historical debt in the
    checked-in `01_Plans/issues/` tree. Temporary repositories used by contract
    tests start with no historical debt, so their default baseline is zero.
    Dedicated lifecycle tests can still pass an explicit baseline when they
    exercise ratchet behaviour on synthetic roots.
    """
    canonical_root = Path(__file__).resolve().parent
    return LEGACY_DONE_AT_ROOT_BASELINE if root.resolve() == canonical_root else 0

def validate_done_memo_location(
    root: Path,
    *,
    legacy_baseline: int | None = None,
) -> list[str]:
    """Keep Done-at-root legacy debt on a monotonic downward ratchet.

    A count above the checked-in baseline means new debt was introduced. A
    count below it means debt was removed but the baseline was not lowered in
    the same change; allowing that would let later changes grow back up to the
    stale value. Requiring equality makes each intentional migration advance
    the baseline and prevents regression without freezing a permanent allowlist.

    The checked-in baseline applies only to the canonical issue directory.
    Synthetic or caller-supplied roots default to zero historical debt unless
    the caller provides `legacy_baseline` explicitly.
    """
    if legacy_baseline is None:
        legacy_baseline = default_legacy_done_at_root_baseline(root)

    count = len(discover_done_memos_at_root(root))
    if count == legacy_baseline:
        return []

    if count > legacy_baseline:
        return [
            "Done-at-root count exceeds the checked-in R18 legacy baseline "
            f"({count} > {legacy_baseline}). "
            "Move newly completed memo(s) to 01_Plans/issues/done/; "
            "do not increase legacy debt."
        ]

    return [
        "Done-at-root legacy debt decreased but the checked-in baseline was not lowered "
        f"({count} < {legacy_baseline}). "
        f"Set LEGACY_DONE_AT_ROOT_BASELINE to {count} in the same migration change "
        "so the debt cannot grow back later."
    ]


def validate_rows(root: Path, rows: Iterable[ActiveMemoRow]) -> list[str]:
    errors: list[str] = []
    for row in rows:
        memo_path = root / row.memo
        if not memo_path.exists():
            errors.append(f"missing memo file: {row.memo}")
            continue

        text = memo_path.read_text(encoding="utf-8")
        for field in REQUIRED_FIELDS:
            field_name = field.removeprefix("- ").removesuffix(":")
            if extract_field_value(text, field_name) is None:
                errors.append(f"{row.memo}: missing or empty field {field}")

        level = extract_verification_level(text)
        if level and level not in ALLOWED_VERIFICATION_LEVELS:
            errors.append(
                f"{row.memo}: invalid Expected verification level `{level}` "
                f"(allowed: {sorted(ALLOWED_VERIFICATION_LEVELS)})"
            )

        memo_status = extract_field_value(text, "Status")
        memo_source = extract_field_value(text, "Source Issue")

        if row.status not in ACTIVE_ISSUE_STATUSES:
            errors.append(
                f"{row.memo}: invalid active status `{row.status}` (allowed: {sorted(ACTIVE_ISSUE_STATUSES)})"
            )

        for dep in extract_dependency_paths(text):
            name = Path(dep).name
            candidates = (root / name, root / "done" / name, root / "archive" / name)
            if not any(candidate.exists() for candidate in candidates):
                errors.append(f"{row.memo}: dependency path not found `{dep}`")

        if row.status != "Draft" and row.source == "TBD":
            errors.append(
                f"{row.memo}: status is {row.status} but Source Issue is TBD in index"
            )

        if memo_status and memo_source:
            if memo_status != row.status or memo_source != row.source:
                errors.append(
                    f"{row.memo}: index status/source mismatch "
                    f"(index=({row.status}, {row.source}), memo=({memo_status}, {memo_source}))"
                )

    return errors


def validate_status_contract(root: Path) -> list[str]:
    errors: list[str] = []
    requirement_paths: dict[str, list[str]] = {}

    for memo_path in sorted(root.rglob("issue-*.md")):
        text = memo_path.read_text(encoding="utf-8")
        raw_status = extract_field_value(text, "Status")
        status = parse_issue_status(raw_status)
        if raw_status is None:
            errors.append(f"{memo_path.name}: missing Status metadata")
            continue
        if status is None:
            errors.append(
                f"{memo_path.name}: invalid Status `{raw_status}` "
                f"(allowed: {sorted(CANONICAL_ISSUE_STATUSES)})"
            )
            continue
        if status not in ACTIVE_ISSUE_STATUSES:
            continue

        requirement_id = extract_field_value(text, "RequirementID")
        if requirement_id:
            canonical_id = requirement_id.strip().strip("`")
            requirement_paths.setdefault(canonical_id, []).append(memo_path.name)

    for requirement_id, memo_names in sorted(requirement_paths.items()):
        if len(memo_names) > 1:
            errors.append(
                f"duplicate active RequirementID `{requirement_id}`: {', '.join(memo_names)}"
            )

    return errors


def validate(
    root: Path,
    *,
    enforce_done_baseline: bool | None = None,
    legacy_done_baseline: int = LEGACY_DONE_AT_ROOT_BASELINE,
    enforce_done_identity: bool | None = None,
    legacy_done_paths: set[str] | None = None,
) -> list[str]:
    """Validate issue memos without leaking repo-local debt into test fixtures.

    The Done-at-root count and identity baselines are repository-local history.
    Synthetic roots used by contract tests have no relationship to that debt,
    so the unified validator only applies them automatically to the real issues
    root. Tests can opt into either contract explicitly with fixture-sized
    baselines.
    """
    real_issues_root = Path(__file__).resolve().parent
    is_real_issues_root = root.resolve() == real_issues_root
    should_enforce_done_baseline = (
        is_real_issues_root
        if enforce_done_baseline is None
        else enforce_done_baseline
    )
    should_enforce_done_identity = (
        is_real_issues_root
        if enforce_done_identity is None
        else enforce_done_identity
    )

    errors = validate_status_contract(root)
    errors += validate_memo_identity_and_placement(root)
    if should_enforce_done_baseline:
        errors += validate_done_memo_location(
            root,
            legacy_baseline=legacy_done_baseline,
        )
    if should_enforce_done_identity:
        errors += validate_done_memo_identity(
            root,
            legacy_paths=legacy_done_paths,
        )
    errors += validate_rows(root, discover_active_rows(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory that contains issues README and memo files",
    )
    args = parser.parse_args()

    errors = validate(args.root)
    if errors:
        print("validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    rows = discover_active_rows(args.root)
    print(f"ok: validated {len(rows)} active issue memos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
