from pathlib import Path

path = Path("01_Plans/triage_actionable_plans.py")
text = path.read_text(encoding="utf-8")

old_stage = '''        if not issue.dependency_paths:
            stage_cache[path] = 0
            return 0
        value = max(dependency_stage(dep, set(stack)) + 1 for dep in issue.dependency_paths if dep in issue_by_path)
        stage_cache[path] = value
        return value
'''
new_stage = '''        if not issue.dependency_paths:
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
'''
if old_stage not in text:
    raise SystemExit("dependency_stage block did not match expected main content")
text = text.replace(old_stage, new_stage, 1)

old_issue_blocker = '''        for dep_path in issue.dependency_paths:
            dep_issue = issue_by_path.get(dep_path)
            if dep_issue and dep_issue.path != issue.path and dep_issue.status != "Done":
                blockers.append(f"{dep_issue.backlog_id}:{dep_issue.status}")
'''
new_issue_blocker = '''        for dep_path in issue.dependency_paths:
            dep_issue = issue_by_path.get(dep_path)
            if dep_issue is None:
                missing_id = Path(dep_path).name.removeprefix("issue-").removesuffix(".md")
                blockers.append(f"{missing_id}:Missing")
            elif dep_issue.path != issue.path and dep_issue.status != "Done":
                blockers.append(f"{dep_issue.backlog_id}:{dep_issue.status}")
'''
if old_issue_blocker not in text:
    raise SystemExit("issue blocker block did not match expected main content")
text = text.replace(old_issue_blocker, new_issue_blocker, 1)

old_adr_blocker = '''        for adr_id in issue.dependency_adr_ids:
            dep_adr = adr_by_id.get(adr_id)
            if dep_adr is not None and dep_adr.status != "Accepted":
                blockers.append(f"{adr_id}:{dep_adr.status}")
'''
new_adr_blocker = '''        for adr_id in issue.dependency_adr_ids:
            dep_adr = adr_by_id.get(adr_id)
            if dep_adr is None:
                blockers.append(f"{adr_id}:Missing")
            elif dep_adr.status != "Accepted":
                blockers.append(f"{adr_id}:{dep_adr.status}")
'''
if old_adr_blocker not in text:
    raise SystemExit("ADR blocker block did not match expected main content")
text = text.replace(old_adr_blocker, new_adr_blocker, 1)

path.write_text(text, encoding="utf-8")
