from pathlib import Path

path = Path("01_Plans/triage_actionable_plans.py")
text = path.read_text(encoding="utf-8")

old = '''    related_refs: tuple[str, ...]\n    dependency_paths: tuple[str, ...]\n    dependency_adr_ids: tuple[str, ...]\n'''
new = '''    related_refs: tuple[str, ...]\n    dependency_paths: tuple[str, ...]\n    dependency_adr_ids: tuple[str, ...]\n    ambiguous_dependency_names: tuple[str, ...] = field(default_factory=tuple)\n'''
if old not in text:
    raise SystemExit("IssueMemo field anchor not found")
text = text.replace(old, new, 1)

old = '''        for dep_path in issue.dependency_paths:\n            dep_issue = issue_by_path.get(dep_path)\n            if dep_issue is None:\n                missing_id = Path(dep_path).name.removeprefix("issue-").removesuffix(".md")\n                blockers.append(f"{missing_id}:Missing")\n            elif dep_issue.path == issue.path:\n                blockers.append(f"{issue.backlog_id}:SelfDependency")\n            elif dep_issue.status != "Done":\n                blockers.append(f"{dep_issue.backlog_id}:{dep_issue.status}")\n'''
new = '''        for dep_path in issue.dependency_paths:\n            dep_name = Path(dep_path).name\n            if dep_name in issue.ambiguous_dependency_names:\n                ambiguous_id = dep_name.removeprefix("issue-").removesuffix(".md")\n                blockers.append(f"{ambiguous_id}:Ambiguous")\n                continue\n            dep_issue = issue_by_path.get(dep_path)\n            if dep_issue is None:\n                missing_id = dep_name.removeprefix("issue-").removesuffix(".md")\n                blockers.append(f"{missing_id}:Missing")\n            elif dep_issue.path == issue.path:\n                blockers.append(f"{issue.backlog_id}:SelfDependency")\n            elif dep_issue.status != "Done":\n                blockers.append(f"{dep_issue.backlog_id}:{dep_issue.status}")\n'''
if old not in text:
    raise SystemExit("blocker anchor not found")
text = text.replace(old, new, 1)

old = '''    # Done memos can live under issues/done/ or issues/archive/; dependency\n    # refs in still-active memos are written relative to issues/ and don't\n    # know which subfolder a graduated memo ended up in, so re-resolve by\n    # filename once here rather than requiring every reference to be rewritten.\n    name_to_path = {Path(issue.path).name: issue.path for issue in issues}\n    issues = [\n        replace(\n            issue,\n            dependency_paths=tuple(\n                name_to_path.get(Path(dep).name, dep) for dep in issue.dependency_paths\n            ),\n        )\n        for issue in issues\n    ]\n    errors: list[TriageError] = []\n    known_issue_paths = {issue.path for issue in issues}\n    known_adr_ids = {adr.adr_id for adr in adrs}\n'''
new = '''    # Done memos can live under issues/done/ or issues/archive/. Keep an exact\n    # normalized path when it still exists; only fall back to basename when the\n    # original path is gone. A basename fallback must be unique: choosing one of\n    # multiple candidates by dictionary overwrite order would silently attach\n    # the dependency to an arbitrary memo.\n    known_issue_paths = {issue.path for issue in issues}\n    paths_by_name: dict[str, list[str]] = {}\n    for issue in issues:\n        paths_by_name.setdefault(Path(issue.path).name, []).append(issue.path)\n\n    resolved_issues: list[IssueMemo] = []\n    for issue in issues:\n        resolved_paths: list[str] = []\n        ambiguous_names: list[str] = []\n        for dep in issue.dependency_paths:\n            if dep in known_issue_paths:\n                resolved_paths.append(dep)\n                continue\n            dep_name = Path(dep).name\n            candidates = paths_by_name.get(dep_name, [])\n            if len(candidates) == 1:\n                resolved_paths.append(candidates[0])\n            else:\n                resolved_paths.append(dep)\n                if len(candidates) > 1:\n                    ambiguous_names.append(dep_name)\n        resolved_issues.append(\n            replace(\n                issue,\n                dependency_paths=tuple(resolved_paths),\n                ambiguous_dependency_names=tuple(dict.fromkeys(ambiguous_names)),\n            )\n        )\n    issues = resolved_issues\n\n    errors: list[TriageError] = []\n    known_adr_ids = {adr.adr_id for adr in adrs}\n'''
if old not in text:
    raise SystemExit("dependency resolution anchor not found")
text = text.replace(old, new, 1)

old = '''        for dep in issue.dependency_paths:\n            if dep == issue.path:\n                errors.append(TriageError(path=issue.path, reason=f"self dependency: {dep}"))\n            elif dep not in known_issue_paths:\n                errors.append(TriageError(path=issue.path, reason=f"dependency path not found: {dep}"))\n'''
new = '''        for dep in issue.dependency_paths:\n            dep_name = Path(dep).name\n            if dep == issue.path:\n                errors.append(TriageError(path=issue.path, reason=f"self dependency: {dep}"))\n            elif dep_name in issue.ambiguous_dependency_names:\n                candidates = ", ".join(sorted(paths_by_name[dep_name]))\n                errors.append(\n                    TriageError(\n                        path=issue.path,\n                        reason=f"ambiguous dependency basename: {dep_name} -> {candidates}",\n                    )\n                )\n            elif dep not in known_issue_paths:\n                errors.append(TriageError(path=issue.path, reason=f"dependency path not found: {dep}"))\n'''
if old not in text:
    raise SystemExit("dependency error anchor not found")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
