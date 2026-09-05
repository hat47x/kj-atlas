from pathlib import Path

path = Path("03_Implement/backend/tests/test_ai_route_provider_token_measurement.py")
t = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global t
    assert t.count(old) == 1, (old[:80], t.count(old))
    t = t.replace(old, new)


replace_once(
    '''EXPECTED_ROUTES = {\n    "suggest-card-groups",\n    "suggest-card-groups-route-b",\n    "suggest-layout",\n    "suggest-layout-route-b",\n    "generate-narrative",\n    "check-narrative",\n}\n''',
    '''EXPECTED_ROUTES = {\n    "suggest-card-groups",\n    "suggest-card-groups-route-b",\n    "suggest-layout",\n    "suggest-layout-route-b",\n    "generate-narrative",\n    "check-narrative",\n}\nLAYOUT_C_ROUTES = {\n    *(f"suggest-layout-c-local-{index:02d}" for index in range(1, 31)),\n    "suggest-layout-c-global",\n}\n''',
)
replace_once(
    '''            input_tokens = (4000, 5000, 7000, 8000, 6000, 11000)[len(self.calls) - 1]\n            output_tokens = 1\n''',
    '''            base = (4000, 5000, 7000, 8000, 6000, 11000)\n            index = len(self.calls) - 1\n            input_tokens = base[index] if index < len(base) else 100 + index\n            output_tokens = 1\n''',
)
replace_once(
    '''def test_dry_run_never_needs_a_provider_or_claims_exact_tokens() -> None:\n''',
    '''def test_layout_c_requests_are_explicit_opt_in_and_match_r25_diagnostics() -> None:\n    default_requests = token_measure.build_representative_requests("named-model")\n    requests = token_measure.build_representative_requests(\n        "named-model", include_layout_c=True\n    )\n\n    assert set(default_requests) == EXPECTED_ROUTES\n    assert set(requests) == EXPECTED_ROUTES | LAYOUT_C_ROUTES\n    assert len(requests) == 37\n\n    c_requests = [requests[name] for name in sorted(LAYOUT_C_ROUTES)]\n    assert {req.task for req in c_requests} == {"re_layout"}\n    assert {req.model for req in c_requests} == {"named-model"}\n    assert {req.max_tokens for req in c_requests} == {1}\n    assert all(req.inputs is None for req in c_requests)\n\n    c_prompt_bytes = [len(req.prompt.encode("utf-8")) for req in c_requests]\n    assert max(c_prompt_bytes) == 7_486\n    assert sum(c_prompt_bytes) == 87_705\n\n\ndef test_layout_c_dry_run_never_calls_provider_or_claims_tokens() -> None:\n    report = token_measure.measure(\n        model="named-model",\n        expected_provider="named-test-provider",\n        execute=False,\n        include_layout_c=True,\n    )\n\n    assert report["executed"] is False\n    assert report["measurement_complete"] is False\n    assert set(report["routes"]) == EXPECTED_ROUTES | LAYOUT_C_ROUTES\n    summary = report["layout_c_summary"]\n    assert summary["included"] is True\n    assert summary["requests"] == 31\n    assert summary["prompt"] == {\n        "max_single_utf8_bytes": 7_486,\n        "aggregate_utf8_bytes": 87_705,\n    }\n    assert summary["provider_reported"] == {\n        "input_tokens_complete": False,\n        "aggregate_input_tokens": None,\n        "max_single_input_tokens": None,\n    }\n\n\ndef test_dry_run_never_needs_a_provider_or_claims_exact_tokens() -> None:\n''',
)
replace_once(
    '''def test_provider_reported_usage_is_recorded_per_comparison_without_estimation() -> None:\n''',
    '''def test_direct_cli_layout_c_dry_run_is_network_free() -> None:\n    backend_dir = Path(__file__).resolve().parents[1]\n    completed = subprocess.run(\n        [\n            sys.executable,\n            "scripts/measure_ai_route_provider_tokens.py",\n            "--provider",\n            "named-test-provider",\n            "--model",\n            "named-model",\n            "--include-layout-c",\n        ],\n        cwd=backend_dir,\n        check=True,\n        capture_output=True,\n        text=True,\n    )\n    report = json.loads(completed.stdout)\n\n    assert report["executed"] is False\n    assert len(report["routes"]) == 37\n    assert report["layout_c_summary"]["requests"] == 31\n    assert report["layout_c_summary"]["prompt"]["aggregate_utf8_bytes"] == 87_705\n\n\ndef test_provider_reported_usage_is_recorded_per_comparison_without_estimation() -> None:\n''',
)
replace_once(
    '''def test_missing_provider_usage_is_recorded_as_measurement_incomplete() -> None:\n''',
    '''def test_layout_c_provider_usage_aggregates_only_reported_usage() -> None:\n    provider = _UsageProvider()\n    report = token_measure.measure(\n        model="named-model",\n        expected_provider=provider.provider_name,\n        execute=True,\n        provider=provider,\n        include_layout_c=True,\n    )\n\n    assert report["measurement_complete"] is True\n    assert len(provider.calls) == 37\n    summary = report["layout_c_summary"]\n    assert summary["included"] is True\n    assert summary["requests"] == 31\n    # Calls 7..37 receive arbitrary provider-reported values 106..136.\n    assert summary["provider_reported"] == {\n        "input_tokens_complete": True,\n        "aggregate_input_tokens": 3_751,\n        "max_single_input_tokens": 136,\n    }\n    assert summary["provider_reported"]["aggregate_input_tokens"] != summary["prompt"][\n        "aggregate_utf8_bytes"\n    ]\n\n\ndef test_layout_c_missing_usage_stays_incomplete_without_estimation() -> None:\n    provider = _UsageProvider(report_usage=False)\n    report = token_measure.measure(\n        model="named-model",\n        expected_provider=provider.provider_name,\n        execute=True,\n        provider=provider,\n        include_layout_c=True,\n    )\n\n    assert report["measurement_complete"] is False\n    assert len(provider.calls) == 37\n    assert report["layout_c_summary"]["provider_reported"] == {\n        "input_tokens_complete": False,\n        "aggregate_input_tokens": None,\n        "max_single_input_tokens": None,\n    }\n\n\ndef test_missing_provider_usage_is_recorded_as_measurement_incomplete() -> None:\n''',
)

path.write_text(t, encoding="utf-8")
