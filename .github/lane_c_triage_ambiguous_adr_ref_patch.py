from pathlib import Path

path = Path("01_Plans/triage_actionable_plans.py")
text = path.read_text(encoding="utf-8")

old = '''def build_actionable_adrs(adrs: list[AdrRecord], issues: list[IssueMemo]) -> list[ActionableAdr]:
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
'''

new = '''def build_active_issue_paths_by_name(issues: list[IssueMemo]) -> dict[str, tuple[str, ...]]:
    paths_by_name: dict[str, list[str]] = {}
    for issue in issues:
        if issue.status in ACTIVE_ISSUE_STATUSES:
            paths_by_name.setdefault(Path(issue.path).name, []).append(issue.path)
    return {
        name: tuple(sorted(paths))
        for name, paths in paths_by_name.items()
    }


def resolve_adr_active_issue_refs(
    adr: AdrRecord,
    active_issue_paths: set[str],
    active_paths_by_name: dict[str, tuple[str, ...]],
) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
    refs: list[str] = []
    ambiguous: dict[str, tuple[str, ...]] = {}
    for ref in adr.related_refs:
        if "issue-" not in ref:
            continue
        ref_norm = normalize_issue_ref(ref)
        ref_name = Path(ref_norm).name
        if ref_norm in active_issue_paths:
            refs.append(ref_norm)
            continue
        candidates = active_paths_by_name.get(ref_name, ())
        if len(candidates) == 1:
            refs.append(candidates[0])
        elif len(candidates) > 1:
            ambiguous[ref_name] = candidates
    return tuple(sorted(dict.fromkeys(refs))), ambiguous


def build_actionable_adrs(adrs: list[AdrRecord], issues: list[IssueMemo]) -> list[ActionableAdr]:
    active_issue_paths = {issue.path for issue in issues if issue.status in ACTIVE_ISSUE_STATUSES}
    active_paths_by_name = build_active_issue_paths_by_name(issues)
    actionable: list[ActionableAdr] = []
    for adr in adrs:
        if adr.status not in ADR_ACTIONABLE_STATUSES:
            continue
        refs, _ = resolve_adr_active_issue_refs(adr, active_issue_paths, active_paths_by_name)
        if refs:
            actionable.append(
                ActionableAdr(
                    adr_id=adr.adr_id,
                    path=adr.path,
                    status=adr.status,
                    source_issue=adr.source_issue,
                    active_issue_refs=refs,
                )
            )
    return sorted(actionable, key=lambda x: x.path)
'''

if old not in text:
    raise SystemExit("build_actionable_adrs block not found")
text = text.replace(old, new, 1)

old_collect = '''    for cycle in find_active_dependency_cycles(issues):
        errors.append(
            TriageError(
                path=cycle[0],
                reason="dependency cycle among active issues: " + ", ".join(cycle),
            )
        )
    actionable_issues = build_actionable_issues(issues, adrs, root)
    actionable_adrs = build_actionable_adrs(adrs, issues)
'''

new_collect = '''    for cycle in find_active_dependency_cycles(issues):
        errors.append(
            TriageError(
                path=cycle[0],
                reason="dependency cycle among active issues: " + ", ".join(cycle),
            )
        )

    active_issue_paths = {
        issue.path for issue in issues if issue.status in ACTIVE_ISSUE_STATUSES
    }
    active_paths_by_name = build_active_issue_paths_by_name(issues)
    for adr in adrs:
        if adr.status not in ADR_ACTIONABLE_STATUSES:
            continue
        _, ambiguous_refs = resolve_adr_active_issue_refs(
            adr, active_issue_paths, active_paths_by_name
        )
        for ref_name, candidates in sorted(ambiguous_refs.items()):
            errors.append(
                TriageError(
                    path=adr.path,
                    reason=(
                        f"ambiguous active issue basename: {ref_name} -> "
                        + ", ".join(candidates)
                    ),
                )
            )

    actionable_issues = build_actionable_issues(issues, adrs, root)
    actionable_adrs = build_actionable_adrs(adrs, issues)
'''

if old_collect not in text:
    raise SystemExit("collect insertion point not found")
text = text.replace(old_collect, new_collect, 1)

path.write_text(text, encoding="utf-8")
