from pathlib import Path

path = Path("01_Plans/triage_actionable_plans.py")
text = path.read_text(encoding="utf-8")

old = '''    dependents: dict[str, list[str]] = {issue.path: [] for issue in issues}\n    for issue in issues:\n        for dep_path in issue.dependency_paths:\n            if dep_path in dependents and dep_path != issue.path:\n                dependents[dep_path].append(issue.path)\n'''
new = '''    dependents: dict[str, list[str]] = {issue.path: [] for issue in issues}\n    for issue in issues:\n        if issue.status not in ACTIVE_ISSUE_STATUSES:\n            continue\n        for dep_path in issue.dependency_paths:\n            if dep_path in dependents and dep_path != issue.path:\n                dependents[dep_path].append(issue.path)\n'''
if old not in text:
    raise SystemExit("dependents block not found")
text = text.replace(old, new, 1)

old = '''        issue = issue_by_path.get(path)\n        if issue is None:\n            return 999\n        if not issue.dependency_paths:\n'''
new = '''        issue = issue_by_path.get(path)\n        if issue is None:\n            return 999\n        # Done memos are satisfied dependency leaves. Their historical\n        # dependency notes must not re-enter the active graph and inflate a\n        # current issue's stage or create a false cycle through old edges.\n        if issue.status == "Done":\n            stage_cache[path] = 0\n            return 0\n        if not issue.dependency_paths:\n'''
if old not in text:
    raise SystemExit("dependency stage block not found")
text = text.replace(old, new, 1)

marker = '''def build_actionable_issues(\n    issues: list[IssueMemo], adrs: list[AdrRecord], root: Path\n) -> list[ActionableIssue]:\n'''
helper = '''def find_active_dependency_cycles(issues: list[IssueMemo]) -> list[tuple[str, ...]]:\n    """Return strongly connected components in the active issue graph.\n\n    Done memos are deliberately excluded: once an issue is Done its historical\n    dependencies no longer participate in current actionability. Self\n    dependencies are diagnosed separately with the more specific error.\n    """\n    active = {\n        issue.path: issue\n        for issue in issues\n        if issue.status in ACTIVE_ISSUE_STATUSES\n    }\n    graph = {\n        path: tuple(\n            dep\n            for dep in issue.dependency_paths\n            if dep in active and dep != path\n        )\n        for path, issue in active.items()\n    }\n\n    index = 0\n    indices: dict[str, int] = {}\n    lowlinks: dict[str, int] = {}\n    stack: list[str] = []\n    on_stack: set[str] = set()\n    cycles: list[tuple[str, ...]] = []\n\n    def visit(path: str) -> None:\n        nonlocal index\n        indices[path] = index\n        lowlinks[path] = index\n        index += 1\n        stack.append(path)\n        on_stack.add(path)\n\n        for dep in graph[path]:\n            if dep not in indices:\n                visit(dep)\n                lowlinks[path] = min(lowlinks[path], lowlinks[dep])\n            elif dep in on_stack:\n                lowlinks[path] = min(lowlinks[path], indices[dep])\n\n        if lowlinks[path] != indices[path]:\n            return\n\n        component: list[str] = []\n        while True:\n            member = stack.pop()\n            on_stack.remove(member)\n            component.append(member)\n            if member == path:\n                break\n        if len(component) > 1:\n            cycles.append(tuple(sorted(component)))\n\n    for path in sorted(graph):\n        if path not in indices:\n            visit(path)\n\n    return sorted(cycles)\n\n\n'''
if marker not in text:
    raise SystemExit("build_actionable marker not found")
text = text.replace(marker, helper + marker, 1)

old = '''        for adr_id in issue.dependency_adr_ids:\n            if adr_id not in known_adr_ids:\n                errors.append(\n                    TriageError(path=issue.path, reason=f"dependency ADR not found: {adr_id}")\n                )\n    actionable_issues = build_actionable_issues(issues, adrs, root)\n'''
new = '''        for adr_id in issue.dependency_adr_ids:\n            if adr_id not in known_adr_ids:\n                errors.append(\n                    TriageError(path=issue.path, reason=f"dependency ADR not found: {adr_id}")\n                )\n    for cycle in find_active_dependency_cycles(issues):\n        errors.append(\n            TriageError(\n                path=cycle[0],\n                reason="dependency cycle among active issues: " + ", ".join(cycle),\n            )\n        )\n    actionable_issues = build_actionable_issues(issues, adrs, root)\n'''
if old not in text:
    raise SystemExit("collect insertion point not found")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
