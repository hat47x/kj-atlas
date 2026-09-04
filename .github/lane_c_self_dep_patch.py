from pathlib import Path

path = Path('01_Plans/triage_actionable_plans.py')
text = path.read_text(encoding='utf-8')
old = '''        for dep_path in issue.dependency_paths:\n            dep_issue = issue_by_path.get(dep_path)\n            if dep_issue is None:\n                missing_id = Path(dep_path).name.removeprefix("issue-").removesuffix(".md")\n                blockers.append(f"{missing_id}:Missing")\n            elif dep_issue.path != issue.path and dep_issue.status != "Done":\n                blockers.append(f"{dep_issue.backlog_id}:{dep_issue.status}")\n'''
new = '''        for dep_path in issue.dependency_paths:\n            dep_issue = issue_by_path.get(dep_path)\n            if dep_issue is None:\n                missing_id = Path(dep_path).name.removeprefix("issue-").removesuffix(".md")\n                blockers.append(f"{missing_id}:Missing")\n            elif dep_issue.path == issue.path:\n                blockers.append(f"{issue.backlog_id}:SelfDependency")\n            elif dep_issue.status != "Done":\n                blockers.append(f"{dep_issue.backlog_id}:{dep_issue.status}")\n'''
if old not in text:
    raise SystemExit('blocker target not found')
text = text.replace(old, new, 1)
old2 = '''        for dep in issue.dependency_paths:\n            if dep not in known_issue_paths:\n                errors.append(TriageError(path=issue.path, reason=f"dependency path not found: {dep}"))\n'''
new2 = '''        for dep in issue.dependency_paths:\n            if dep == issue.path:\n                errors.append(TriageError(path=issue.path, reason=f"self dependency: {dep}"))\n            elif dep not in known_issue_paths:\n                errors.append(TriageError(path=issue.path, reason=f"dependency path not found: {dep}"))\n'''
if old2 not in text:
    raise SystemExit('error target not found')
text = text.replace(old2, new2, 1)
path.write_text(text, encoding='utf-8')
