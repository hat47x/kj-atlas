#!/usr/bin/env python3
"""Summarize actionable ADR and issue memo targets with minimal file reads."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

from issues.issue_memo_status import (
    ACTIVE_ISSUE_STATUSES,
    CANONICAL_ISSUE_STATUSES,
    parse_issue_status,
)

ADR_ACTIONABLE_STATUSES = {"Accepted", "Proposed"}
CANONICAL_ADR_STATUSES = ("Accepted", "Proposed", "Superseded", "Deprecated", "Rejected")
META_RE = re.compile(r"^- (?P<key>[^:]+):\s*(?P<value>.+)$")
BACKTICK_RE = re.compile(r"`([^`]+)`")
REL_PATH_RE = re.compile(r"`([^`]*issue-[^`]+\.md)`")
ADR_REF_RE = re.compile(r"`(ADR-\d{4}[^`]*)`")
SECTION_RE = re.compile(r"^##+\s+")
DEPENDENCY_HEADING_RE = re.compile(r"^##+\s+(?:\d+\)\s*)?(?:依存関係|Dependencies)")
MOCK_POLICY_RE = re.compile(r"^- (?P<label>Mock(?:適用可否| Policy|方針)?|Mock readiness):\s*(?P<value>.+)$")


@dataclass(frozen=True)
class IssueMemo:
    path: str
    title: str
    backlog_id: str
    status: str
    priority: str
    owner: str
    related_backlog: str
    source_issue: str
    related_refs: tuple[str, ...]
    dependency_paths: tuple[str, ...]
    dependency_adr_ids: tuple[str, ...]


@dataclass(frozen=True)
class AdrRecord:
    path: str
    title: str
    adr_id: str
    status: str
    source_issue: str
    related_refs: tuple[str, ...]


@dataclass(frozen=True)
class ActionableIssue:
    backlog_id: str
    path: str
    status: str
    priority: str
    owner: str
    ready: bool
    blockers: tuple[str, ...] = field(default_factory=tuple)
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    unlocks: tuple[str, ...] = field(default_factory=tuple)
    classification: str = "Blocked"
    dependency_stage: int = 0
    mock_applicable: str = "Unknown"


@dataclass(frozen=True)
class TriageError:
    path: str
    reason: str


@dataclass(frozen=True)
class ActionableAdr:
    adr_id: str
    path: str
    status: str
    source_issue: str
    active_issue_refs: tuple[str, ...] = field(default_factory=tuple)


def normalize_adr_status(raw: str) -> str:
    """Return the canonical ADR status while preserving free-form annotations in docs.

    ADR metadata historically allows a canonical status followed by a note,
    using whitespace, ASCII parentheses, or Japanese full-width parentheses.
    Only those explicit delimiters are accepted so values such as
    ``AcceptedButPending`` cannot be mistaken for ``Accepted``.
    """
    for status in CANONICAL_ADR_STATUSES:
        if raw == status or any(raw.startswith(status + delimiter) for delimiter in (" ", "(", "（")):
            return status
    return raw


def read_header_lines(path: Path, limit: int = 120) -> list[str]:
    lines: list[str] = []
    with path.open(encoding="utf-8") as fh:
        for _, line in zip(range(limit), fh):
            lines.append(line.rstrip("\n"))
    return lines


def normalize_issue_ref(ref: str) -> str:
    return ref.removeprefix("01_Plans/") if ref.startswith("01_Plans/") else f"issues/{ref}"


def extract_dependency_paths(lines: list[str]) -> tuple[str, ...]:
    in_dependencies = False
    refs: list[str] = []
    for line in lines:
        if DEPENDENCY_HEADING_RE.match(line.strip()):
            in_dependencies = True
            continue
        if in_dependencies and SECTION_RE.match(line.strip()):
            break
        if in_dependencies:
            refs.extend(normalize_issue_ref(ref) for ref in REL_PATH_RE.findall(line))
    return tuple(dict.fromkeys(refs))


def extract_dependency_adr_ids(lines: list[str]) -> tuple[str, ...]:
    in_dependencies = False
    refs: list[str] = []
    for line in lines:
        if DEPENDENCY_HEADING_RE.match(line.strip()):
            in_dependencies = True
            continue
        if in_dependencies and SECTION_RE.match(line.strip()):
            break
        if in_dependencies:
            for value in BACKTICK_RE.findall(line):
                refs.extend(re.findall(r"ADR-\d{4}", value))
    return tuple(dict.fromkeys(refs))


def parse_issue(path: Path, root: Path) -> IssueMemo:
    # Dependencies are intentionally kept in a dedicated section, which can be
    # well below the metadata header in long-running issue memos. Read the full
    # memo so a long implementation log cannot silently turn a blocked issue
    # into a Ready issue.
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip() if lines else path.stem
    meta: dict[str, str] = {}
    for line in lines[1:20]:
        m = META_RE.match(line)
        if m:
            meta[m.group("key")] = m.group("value")
    backlog_id = path.name.removeprefix("issue-").removesuffix(".md")
    related_refs = tuple(dict.fromkeys(BACKTICK_RE.findall(meta.get("Related ADR/Spec", ""))))
    dependency_paths = extract_dependency_paths(lines)
    raw_status = meta.get("Status", "Unknown").strip()
    return IssueMemo(
        path=str(path.relative_to(root).as_posix()),
        title=title,
        backlog_id=backlog_id,
        status=parse_issue_status(raw_status) or raw_status,
        priority=meta.get("Priority", "N/A"),
        owner=meta.get("Owner", "N/A"),
        related_backlog=meta.get("Related Backlog", "").strip("`"),
        source_issue=meta.get("Source Issue", "N/A"),
        related_refs=related_refs,
        dependency_paths=dependency_paths,
        dependency_adr_ids=extract_dependency_adr_ids(lines),
    )


def detect_mock_applicability(path: Path) -> str:
    lines = read_header_lines(path, limit=180)
    for line in lines:
        m = MOCK_POLICY_RE.match(line.strip())
        if not m:
            continue
        value = m.group("value").lower()
        if any(token in value for token in ("yes", "可", "可能", "applicable", "enabled")):
            return "Yes"
        if any(token in value for token in ("no", "不可", "not applicable", "disabled")):
            return "No"
        return "Conditional"
    return "Unknown"


def parse_adr(path: Path) -> AdrRecord:
    lines = read_header_lines(path, limit=40)
    title = lines[0].lstrip("# ").strip() if lines else path.stem
    meta: dict[str, str] = {}
    for line in lines[1:10]:
        m = META_RE.match(line)
        if m:
            meta[m.group("key")] = m.group("value")
    adr_id_match = re.search(r"(ADR-\d{4})", title)
    adr_id = adr_id_match.group(1) if adr_id_match else path.stem
    refs = []
    refs.extend(ADR_REF_RE.findall(meta.get("Related", "")))
    source_issue = meta.get("Source Issue", "").strip("`")
    if source_issue:
        refs.extend(REL_PATH_RE.findall(f"`{source_issue}`"))
    return AdrRecord(
        path=str(path.relative_to(path.parents[1]).as_posix()),
        title=title,
        adr_id=adr_id,
        status=normalize_adr_status(meta.get("Status", "Unknown")),
        source_issue=source_issue,
        related_refs=tuple(dict.fromkeys(refs)),
    )


def build_actionable_issues(
    issues: list[IssueMemo], adrs: list[AdrRecord], root: Path
) -> list[ActionableIssue]:
    issue_by_path = {issue.path: issue for issue in issues}
    adr_by_id = {adr.adr_id: adr for adr in adrs}
    dependents: dict[str, list[str]] = {issue.path: [] for issue in issues}
    for issue in issues:
        for dep_path in issue.dependency_paths:
            if dep_path in dependents and dep_path != issue.path:
                dependents[dep_path].append(issue.path)

    stage_cache: dict[str, int] = {}

    def dependency_stage(path: str, stack: set[str] | None = None) -> int:
        if path in stage_cache:
            return stage_cache[path]
        stack = stack or set()
        if path in stack:
            return 999
        stack.add(path)
        issue = issue_by_path.get(path)
        if issue is None:
            return 999
        if not issue.dependency_paths:
            stage_cache[path] = 0
            return 0
        dependency_stages = [
            dependency_stage(dep, set(stack)) for dep in issue.dependency_paths
        ]
        # Missing paths and cycles use 999 as an unresolved-stage sentinel.
        # Preserve that sentinel instead of filtering missing dependencies out:
        # filtering can leave max() empty and crash before triage can report the
        # broken reference.
        value = (
            999
            if any(stage >= 999 for stage in dependency_stages)
            else max(stage + 1 for stage in dependency_stages)
        )
        stage_cache[path] = value
        return value

    actionable: list[ActionableIssue] = []
    for issue in issues:
        if issue.status not in ACTIVE_ISSUE_STATUSES:
            continue
        blockers: list[str] = []
        for dep_path in issue.dependency_paths:
            dep_issue = issue_by_path.get(dep_path)
            if dep_issue is None:
                missing_id = Path(dep_path).name.removeprefix("issue-").removesuffix(".md")
                blockers.append(f"{missing_id}:Missing")
            elif dep_issue.path != issue.path and dep_issue.status != "Done":
                blockers.append(f"{dep_issue.backlog_id}:{dep_issue.status}")
        for adr_id in issue.dependency_adr_ids:
            dep_adr = adr_by_id.get(adr_id)
            if dep_adr is None:
                blockers.append(f"{adr_id}:Missing")
            elif dep_adr.status != "Accepted":
                blockers.append(f"{adr_id}:{dep_adr.status}")
        ready = issue.status != "Draft" and not blockers
        classification = "Ready" if ready else "Blocked"
        actionable.append(
            ActionableIssue(
                backlog_id=issue.backlog_id,
                path=issue.path,
                status=issue.status,
                priority=issue.priority,
                owner=issue.owner,
                ready=ready,
                blockers=tuple(blockers),
                depends_on=issue.dependency_paths + issue.dependency_adr_ids,
                unlocks=tuple(sorted(dependents.get(issue.path, []))),
                classification=classification,
                dependency_stage=dependency_stage(issue.path),
                mock_applicable=detect_mock_applicability(root / issue.path),
            )
        )
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return sorted(
        actionable,
        key=lambda x: (not x.ready, x.dependency_stage, order.get(x.priority, 9), x.path),
    )


def build_actionable_adrs(adrs: list[AdrRecord], issues: list[IssueMemo]) -> list[ActionableAdr]:
    active_issue_paths = {issue.path for issue in issues if issue.status in ACTIVE_ISSUE_STATUSES}
    active_issue_names = {Path(path).name: path for path in active_issue_paths}
    actionable: list[ActionableAdr] = []
    for adr in adrs:
        if adr.status not in ADR_ACTIONABLE_STATUSES:
            continue
        refs: list[str] = []
        for ref in adr.related_refs:
            ref_norm = normalize_issue_ref(ref) if "issue-" in ref else ref
            ref_name = Path(ref_norm).name
            if ref_norm in active_issue_paths:
                refs.append(ref_norm)
            elif ref_name in active_issue_names:
                refs.append(active_issue_names[ref_name])
        if refs:
            actionable.append(
                ActionableAdr(
                    adr_id=adr.adr_id,
                    path=adr.path,
                    status=adr.status,
                    source_issue=adr.source_issue,
                    active_issue_refs=tuple(sorted(dict.fromkeys(refs))),
                )
            )
    return sorted(actionable, key=lambda x: x.path)


def collect(root: Path) -> dict[str, object]:
    issue_files = sorted((root / "issues").rglob("issue-*.md"))
    adr_files = sorted((root / "adr").glob("ADR-*.md"))
    issues = [parse_issue(path, root) for path in issue_files]
    adrs = [parse_adr(path) for path in adr_files]
    # Done memos can live under issues/done/ or issues/archive/; dependency
    # refs in still-active memos are written relative to issues/ and don't
    # know which subfolder a graduated memo ended up in, so re-resolve by
    # filename once here rather than requiring every reference to be rewritten.
    name_to_path = {Path(issue.path).name: issue.path for issue in issues}
    issues = [
        replace(
            issue,
            dependency_paths=tuple(
                name_to_path.get(Path(dep).name, dep) for dep in issue.dependency_paths
            ),
        )
        for issue in issues
    ]
    errors: list[TriageError] = []
    known_issue_paths = {issue.path for issue in issues}
    known_adr_ids = {adr.adr_id for adr in adrs}
    for issue in issues:
        if issue.status == "Unknown":
            errors.append(TriageError(path=issue.path, reason="missing Status metadata"))
        elif issue.status not in CANONICAL_ISSUE_STATUSES:
            errors.append(TriageError(path=issue.path, reason=f"invalid Status metadata: {issue.status}"))
        if issue.priority == "N/A" or not issue.priority.strip():
            errors.append(TriageError(path=issue.path, reason="missing Priority metadata"))
        for dep in issue.dependency_paths:
            if dep not in known_issue_paths:
                errors.append(TriageError(path=issue.path, reason=f"dependency path not found: {dep}"))
        for adr_id in issue.dependency_adr_ids:
            if adr_id not in known_adr_ids:
                errors.append(
                    TriageError(path=issue.path, reason=f"dependency ADR not found: {adr_id}")
                )
    actionable_issues = build_actionable_issues(issues, adrs, root)
    actionable_adrs = build_actionable_adrs(adrs, issues)
    return {
        "actionable_issues": [asdict(item) for item in actionable_issues],
        "actionable_adrs": [asdict(item) for item in actionable_adrs],
        "summary": {
            "active_issue_count": len(actionable_issues),
            "ready_issue_count": sum(1 for item in actionable_issues if item.ready),
            "blocked_issue_count": sum(1 for item in actionable_issues if item.blockers or item.status == "Draft"),
            "actionable_adr_count": len(actionable_adrs),
        },
        "errors": [asdict(item) for item in errors],
    }


def render_text(report: dict[str, object]) -> str:
    lines: list[str] = []
    summary = report["summary"]
    lines.append("# Minimal Context Triage")
    lines.append(
        "summary: "
        f"active_issues={summary['active_issue_count']}, "
        f"ready={summary['ready_issue_count']}, "
        f"blocked={summary['blocked_issue_count']}, "
        f"actionable_adrs={summary['actionable_adr_count']}"
    )
    lines.append("")
    lines.append("## Ready issues")
    ready = [item for item in report["actionable_issues"] if item["ready"]]
    if ready:
        for item in ready:
            lines.append(
                f"- {item['backlog_id']} [{item['status']}/{item['priority']}] "
                f"stage={item['dependency_stage']} mock={item['mock_applicable']} owner={item['owner']} path={item['path']}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Parked or blocked issues")
    blocked = [item for item in report["actionable_issues"] if not item["ready"]]
    if blocked:
        for item in blocked:
            blocker_text = ", ".join(item["blockers"]) if item["blockers"] else "draft gate"
            lines.append(
                f"- {item['backlog_id']} [{item['status']}/{item['priority']}] "
                f"stage={item['dependency_stage']} mock={item['mock_applicable']} blockers={blocker_text} path={item['path']}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## ADRs linked to active work")
    adrs = report["actionable_adrs"]
    if adrs:
        for item in adrs:
            refs = ", ".join(item["active_issue_refs"])
            lines.append(f"- {item['adr_id']} [{item['status']}] refs={refs} path={item['path']}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Triage errors (stopper)")
    if report.get("errors"):
        for err in report["errors"]:
            lines.append(f"- {err['path']}: {err['reason']}")
    else:
        lines.append("- none")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    report = collect(args.root)
    if report.get("errors"):
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(render_text(report))
        return 2
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
