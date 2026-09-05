from pathlib import Path

measure_path = Path("03_Implement/backend/scripts/measure_ai_route_provider_tokens.py")
s = measure_path.read_text(encoding="utf-8")
s = s.replace(
    "import argparse\nimport json\nimport os\n",
    "import argparse\nimport hashlib\nimport json\nimport os\n",
    1,
)
needle = '''\ndef _route_row(req: LLMRequest) -> dict[str, Any]:\n    return {\n'''
replacement = '''\ndef _prompt_sha256(prompt: str) -> str:\n    """Return an identity fingerprint for the exact UTF-8 provider prompt."""\n    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()\n\n\ndef _route_row(req: LLMRequest) -> dict[str, Any]:\n    return {\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
needle = '''        "prompt": {\n            "unicode_chars": len(req.prompt),\n            "utf8_bytes": len(req.prompt.encode("utf-8")),\n        },\n'''
replacement = '''        "prompt": {\n            "unicode_chars": len(req.prompt),\n            "utf8_bytes": len(req.prompt.encode("utf-8")),\n            "sha256": _prompt_sha256(req.prompt),\n        },\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
needle = '''        "expected_model": model,\n        "executed": execute,\n'''
replacement = '''        "expected_model": model,\n        "prompt_fingerprint": {"algorithm": "sha256", "encoding": "utf-8"},\n        "executed": execute,\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
measure_path.write_text(s, encoding="utf-8")

analyzer_path = Path("03_Implement/backend/scripts/analyze_ai_route_provider_measurement.py")
a = analyzer_path.read_text(encoding="utf-8")
needle = '''from pathlib import Path\nfrom typing import Any\n\nMEASUREMENT_NAME = "ai-route-provider-reported-input-tokens"\n'''
replacement = '''from pathlib import Path\nfrom typing import Any\n\ntry:\n    from scripts.measure_ai_route_provider_tokens import (\n        _prompt_sha256,\n        build_representative_requests,\n    )\nexcept ModuleNotFoundError as exc:\n    if exc.name != "scripts":\n        raise\n    from measure_ai_route_provider_tokens import (\n        _prompt_sha256,\n        build_representative_requests,\n    )\n\nMEASUREMENT_NAME = "ai-route-provider-reported-input-tokens"\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''SCENARIO_NAME = "300-cards-30-islands-ring"\nCORE_ROUTE_TASKS = {\n'''
replacement = '''SCENARIO_NAME = "300-cards-30-islands-ring"\nPROMPT_FINGERPRINT = {"algorithm": "sha256", "encoding": "utf-8"}\nCORE_ROUTE_TASKS = {\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''    expected_task: str,\n    expected_provider: str,\n    expected_model: str,\n    errors: list[str],\n) -> int | None:\n'''
replacement = '''    expected_task: str,\n    expected_provider: str,\n    expected_model: str,\n    expected_prompt_sha256: str | None,\n    errors: list[str],\n) -> int | None:\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''    if row.get("task") != expected_task:\n        errors.append(f"task-mismatch:{name}")\n        return None\n    if row.get("status") != "measured":\n'''
replacement = '''    if row.get("task") != expected_task:\n        errors.append(f"task-mismatch:{name}")\n        return None\n    prompt = row.get("prompt")\n    if not isinstance(prompt, dict):\n        errors.append(f"prompt-diagnostics-missing:{name}")\n        return None\n    if expected_prompt_sha256 is None:\n        errors.append(f"canonical-prompt-missing:{name}")\n        return None\n    if prompt.get("sha256") != expected_prompt_sha256:\n        errors.append(f"prompt-fingerprint-mismatch:{name}")\n        return None\n    if row.get("status") != "measured":\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''    if report.get("scenario") != SCENARIO_NAME:\n        errors.append("unexpected-scenario")\n\n    expected_provider = report.get("expected_provider")\n'''
replacement = '''    if report.get("scenario") != SCENARIO_NAME:\n        errors.append("unexpected-scenario")\n    if report.get("prompt_fingerprint") != PROMPT_FINGERPRINT:\n        errors.append("unsupported-or-missing-prompt-fingerprint")\n\n    expected_provider = report.get("expected_provider")\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''    routes = report.get("routes")\n    if not isinstance(routes, dict):\n        errors.append("routes-not-object")\n        routes = {}\n\n    tokens: dict[str, int] = {}\n'''
replacement = '''    routes = report.get("routes")\n    if not isinstance(routes, dict):\n        errors.append("routes-not-object")\n        routes = {}\n\n    include_groups_a2 = GROUPS_A2_ROUTE in routes\n    include_layout_c = any(name.startswith(LAYOUT_C_PREFIX) for name in routes)\n    canonical_requests = (\n        build_representative_requests(\n            expected_model,\n            include_groups_a2=include_groups_a2,\n            include_layout_c=include_layout_c,\n        )\n        if expected_model\n        else {}\n    )\n    canonical_prompt_hashes = {\n        name: _prompt_sha256(req.prompt) for name, req in canonical_requests.items()\n    }\n    for unexpected in sorted(set(routes) - set(canonical_requests)):\n        errors.append(f"unexpected-route:{unexpected}")\n\n    tokens: dict[str, int] = {}\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
# Add expected_prompt_sha256 to all three validation call shapes.
needle = '''            expected_task=expected_task,\n            expected_provider=expected_provider,\n            expected_model=expected_model,\n            errors=errors,\n'''
replacement = '''            expected_task=expected_task,\n            expected_provider=expected_provider,\n            expected_model=expected_model,\n            expected_prompt_sha256=canonical_prompt_hashes.get(name),\n            errors=errors,\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''            expected_task="suggest_card_groups",\n            expected_provider=expected_provider,\n            expected_model=expected_model,\n            errors=errors,\n'''
replacement = '''            expected_task="suggest_card_groups",\n            expected_provider=expected_provider,\n            expected_model=expected_model,\n            expected_prompt_sha256=canonical_prompt_hashes.get(GROUPS_A2_ROUTE),\n            errors=errors,\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''                expected_task="re_layout",\n                expected_provider=expected_provider,\n                expected_model=expected_model,\n                errors=errors,\n'''
replacement = '''                expected_task="re_layout",\n                expected_provider=expected_provider,\n                expected_model=expected_model,\n                expected_prompt_sha256=canonical_prompt_hashes.get(name),\n                errors=errors,\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''            "All token observations and deltas come only from provider_reported.input_tokens. "\n            "Prompt bytes/chars are never converted into tokens. This report does not know the "\n'''
replacement = '''            "All token observations and deltas come only from provider_reported.input_tokens. "\n            "Prompt SHA-256 is used only for exact UTF-8 prompt identity/provenance; bytes, chars, "\n            "and hashes are never converted into tokens. This report does not know the "\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
analyzer_path.write_text(a, encoding="utf-8")

# Update existing analyzer test fixtures so every synthetic measured row carries the
# same canonical prompt fingerprint that the production harness now records.
test_path = Path("03_Implement/backend/tests/test_ai_route_provider_measurement_analysis.py")
t = test_path.read_text(encoding="utf-8")
needle = '''from scripts import analyze_ai_route_provider_measurement as analysis\n\n\ndef _row(tokens: int, *, task: str, prompt_bytes: int = 999_999) -> dict:\n'''
replacement = '''from scripts import analyze_ai_route_provider_measurement as analysis\nfrom scripts import measure_ai_route_provider_tokens as token_measure\n\n\ndef _row(\n    tokens: int,\n    *,\n    task: str,\n    prompt_sha256: str,\n    prompt_bytes: int = 999_999,\n) -> dict:\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
needle = '''        "prompt": {"unicode_chars": 123_456, "utf8_bytes": prompt_bytes},\n'''
replacement = '''        "prompt": {\n            "unicode_chars": 123_456,\n            "utf8_bytes": prompt_bytes,\n            "sha256": prompt_sha256,\n        },\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
needle = '''def _core_report() -> dict:\n    values = {\n'''
replacement = '''def _core_report() -> dict:\n    requests = token_measure.build_representative_requests("named-model")\n    values = {\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
needle = '''        "measurement_complete": True,\n        "routes": {\n            name: _row(tokens, task=analysis.CORE_ROUTE_TASKS[name])\n            for name, tokens in values.items()\n        },\n'''
replacement = '''        "measurement_complete": True,\n        "prompt_fingerprint": analysis.PROMPT_FINGERPRINT.copy(),\n        "routes": {\n            name: _row(\n                tokens,\n                task=analysis.CORE_ROUTE_TASKS[name],\n                prompt_sha256=token_measure._prompt_sha256(requests[name].prompt),\n            )\n            for name, tokens in values.items()\n        },\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
needle = '''def _add_complete_layout_c(report: dict) -> None:\n    for index in range(1, 31):\n        report["routes"][f"suggest-layout-c-local-{index:02d}"] = _row(\n            100 + index,\n            task="re_layout",\n        )\n    report["routes"]["suggest-layout-c-global"] = _row(900, task="re_layout")\n'''
replacement = '''def _add_complete_layout_c(report: dict) -> None:\n    requests = token_measure.build_representative_requests(\n        "named-model", include_layout_c=True\n    )\n    for index in range(1, 31):\n        name = f"suggest-layout-c-local-{index:02d}"\n        report["routes"][name] = _row(\n            100 + index,\n            task="re_layout",\n            prompt_sha256=token_measure._prompt_sha256(requests[name].prompt),\n        )\n    name = "suggest-layout-c-global"\n    report["routes"][name] = _row(\n        900,\n        task="re_layout",\n        prompt_sha256=token_measure._prompt_sha256(requests[name].prompt),\n    )\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
needle = '''    report["routes"][analysis.GROUPS_A2_ROUTE] = _row(\n        5_750,\n        task="suggest_card_groups",\n        prompt_bytes=56_047,\n    )\n'''
replacement = '''    requests = token_measure.build_representative_requests(\n        "named-model", include_groups_a2=True\n    )\n    report["routes"][analysis.GROUPS_A2_ROUTE] = _row(\n        5_750,\n        task="suggest_card_groups",\n        prompt_sha256=token_measure._prompt_sha256(\n            requests[analysis.GROUPS_A2_ROUTE].prompt\n        ),\n        prompt_bytes=56_047,\n    )\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
needle = '''    report["routes"]["suggest-layout-c-local-01"] = _row(101, task="re_layout")\n'''
replacement = '''    requests = token_measure.build_representative_requests(\n        "named-model", include_layout_c=True\n    )\n    name = "suggest-layout-c-local-01"\n    report["routes"][name] = _row(\n        101,\n        task="re_layout",\n        prompt_sha256=token_measure._prompt_sha256(requests[name].prompt),\n    )\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
needle = '''    report["routes"]["suggest-layout-c-local-99"] = _row(199, task="re_layout")\n'''
replacement = '''    report["routes"]["suggest-layout-c-local-99"] = _row(\n        199,\n        task="re_layout",\n        prompt_sha256="0" * 64,\n    )\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
# Add explicit stale/missing fingerprint tests before the usage/provider mismatch case.
needle = '''\ndef test_missing_usage_and_provider_mismatch_fail_closed() -> None:\n'''
replacement = '''\ndef test_changed_prompt_fingerprint_fails_closed() -> None:\n    report = _core_report()\n    report["routes"]["suggest-layout-route-b"]["prompt"]["sha256"] = "0" * 64\n\n    result = analysis.analyze(report)\n\n    assert result["decision_ready"] is False\n    assert result["core_ready"] is False\n    assert "prompt-fingerprint-mismatch:suggest-layout-route-b" in result["errors"]\n\n\ndef test_legacy_report_without_fingerprint_contract_fails_closed() -> None:\n    report = _core_report()\n    del report["prompt_fingerprint"]\n\n    result = analysis.analyze(report)\n\n    assert result["decision_ready"] is False\n    assert "unsupported-or-missing-prompt-fingerprint" in result["errors"]\n\n\ndef test_missing_usage_and_provider_mismatch_fail_closed() -> None:\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
test_path.write_text(t, encoding="utf-8")
