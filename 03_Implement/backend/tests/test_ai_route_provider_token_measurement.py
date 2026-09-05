from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from kj_atlas_api.llm.provider import LLMCallMetadata, LLMRequest, LLMResponse
from scripts import measure_ai_route_provider_tokens as token_measure


EXPECTED_ROUTES = {
    "suggest-card-groups",
    "suggest-card-groups-route-b",
    "suggest-layout",
    "suggest-layout-route-b",
    "generate-narrative",
    "check-narrative",
}
LAYOUT_C_ROUTES = {
    *(f"suggest-layout-c-local-{index:02d}" for index in range(1, 31)),
    "suggest-layout-c-global",
}


class _UsageProvider:
    provider_name = "named-test-provider"
    provider_kind = "deepseek"

    def __init__(self, *, report_usage: bool = True) -> None:
        self.report_usage = report_usage
        self.calls: list[LLMRequest] = []

    def generate(self, req: LLMRequest) -> LLMResponse:
        self.calls.append(req)
        input_tokens = None
        output_tokens = None
        if self.report_usage:
            # Fake provider-reported usage. The values are intentionally arbitrary
            # and are not derived from bytes/chars; the test only proves that the
            # measurement harness records each provider response under the right row.
            base = (4000, 5000, 7000, 8000, 6000, 11000)
            index = len(self.calls) - 1
            input_tokens = base[index] if index < len(base) else 100 + index
            output_tokens = 1
        return LLMResponse(
            raw_text="{}",
            metadata=LLMCallMetadata(
                provider_kind=self.provider_kind,
                provider_name=self.provider_name,
                model_id=req.model or "unknown",
                transport="http",
                requested_at="2026-09-05T00:00:00+00:00",
                trace_id=f"trace-{len(self.calls)}",
            ),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )


def test_representative_requests_compare_current_b_and_full_routes() -> None:
    requests = token_measure.build_representative_requests("named-model")

    assert set(requests) == EXPECTED_ROUTES
    groups = requests["suggest-card-groups"]
    groups_b = requests["suggest-card-groups-route-b"]
    layout = requests["suggest-layout"]
    layout_b = requests["suggest-layout-route-b"]
    narrative = requests["generate-narrative"]
    check = requests["check-narrative"]

    assert groups.task == groups_b.task == "suggest_card_groups"
    assert layout.task == layout_b.task == "re_layout"
    assert narrative.task == "generate_narrative"
    assert check.task == "check_narrative"
    assert {req.model for req in requests.values()} == {"named-model"}
    assert {req.max_tokens for req in requests.values()} == {1}

    # R23 current/B pairs use the same 300-card scenarios. The B candidate
    # restores route-required coverage without changing production caps.
    assert len((groups.inputs or {}).get("cards", [])) == 200
    assert len((groups_b.inputs or {}).get("cards", [])) == 300
    assert (groups.inputs or {})["truncation"]["reason_codes"] == ["MAX_CARDS"]
    assert (groups_b.inputs or {})["truncation"] == {
        "truncated": False,
        "reason_codes": [],
    }
    assert len((layout.inputs or {}).get("coordinates", [])) == 200
    assert len((layout_b.inputs or {}).get("coordinates", [])) == 300
    assert len((layout.inputs or {}).get("relations", [])) == 199
    assert len((layout_b.inputs or {}).get("relations", [])) == 300

    # Pin R23 dry-run diagnostics so the later provider run compares exactly the
    # candidate prompts that were structurally characterized. These are NOT tokens.
    assert len(groups.prompt.encode("utf-8")) == 38044
    assert len(groups_b.prompt.encode("utf-8")) == 48791
    assert len(layout.prompt.encode("utf-8")) == 117389
    assert len(layout_b.prompt.encode("utf-8")) == 128562

    # Existing whole-document comparison routes remain present.
    assert "coordinates" not in (narrative.inputs or {})
    assert check.inputs is None
    assert 'id="c299"' in check.prompt
    assert 'id="i29"' in check.prompt


def test_layout_c_requests_are_explicit_opt_in_and_match_r25_diagnostics() -> None:
    default_requests = token_measure.build_representative_requests("named-model")
    requests = token_measure.build_representative_requests(
        "named-model", include_layout_c=True
    )

    assert set(default_requests) == EXPECTED_ROUTES
    assert set(requests) == EXPECTED_ROUTES | LAYOUT_C_ROUTES
    assert len(requests) == 37

    c_requests = [requests[name] for name in sorted(LAYOUT_C_ROUTES)]
    assert {req.task for req in c_requests} == {"re_layout"}
    assert {req.model for req in c_requests} == {"named-model"}
    assert {req.max_tokens for req in c_requests} == {1}
    assert all(req.inputs is None for req in c_requests)

    c_prompt_bytes = [len(req.prompt.encode("utf-8")) for req in c_requests]
    assert max(c_prompt_bytes) == 7_486
    assert sum(c_prompt_bytes) == 87_705


def test_layout_c_dry_run_never_calls_provider_or_claims_tokens() -> None:
    report = token_measure.measure(
        model="named-model",
        expected_provider="named-test-provider",
        execute=False,
        include_layout_c=True,
    )

    assert report["executed"] is False
    assert report["measurement_complete"] is False
    assert set(report["routes"]) == EXPECTED_ROUTES | LAYOUT_C_ROUTES
    summary = report["layout_c_summary"]
    assert summary["included"] is True
    assert summary["requests"] == 31
    assert summary["prompt"] == {
        "max_single_utf8_bytes": 7_486,
        "aggregate_utf8_bytes": 87_705,
    }
    assert summary["provider_reported"] == {
        "input_tokens_complete": False,
        "aggregate_input_tokens": None,
        "max_single_input_tokens": None,
    }


def test_dry_run_never_needs_a_provider_or_claims_exact_tokens() -> None:
    report = token_measure.measure(
        model="named-model",
        expected_provider="named-test-provider",
        execute=False,
    )

    assert report["executed"] is False
    assert report["measurement_complete"] is False
    assert set(report["routes"]) == EXPECTED_ROUTES
    for row in report["routes"].values():
        assert row["status"] == "dry-run"
        assert row["provider_reported"]["input_tokens"] is None
        assert row["prompt"]["utf8_bytes"] > 0
    assert report["routes"]["check-narrative"]["ir"] == {
        "cards": 0,
        "relations": 0,
        "islands": 0,
        "coordinates": 0,
        "truncation": None,
    }


def test_documented_direct_cli_runs_as_a_dry_run_without_network_access() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/measure_ai_route_provider_tokens.py",
            "--provider",
            "named-test-provider",
            "--model",
            "named-model",
        ],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)

    assert report["executed"] is False
    assert report["measurement_complete"] is False
    assert set(report["routes"]) == EXPECTED_ROUTES
    assert report["routes"]["suggest-card-groups-route-b"]["status"] == "dry-run"
    assert report["routes"]["suggest-layout-route-b"]["status"] == "dry-run"


def test_direct_cli_layout_c_dry_run_is_network_free() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/measure_ai_route_provider_tokens.py",
            "--provider",
            "named-test-provider",
            "--model",
            "named-model",
            "--include-layout-c",
        ],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)

    assert report["executed"] is False
    assert len(report["routes"]) == 37
    assert report["layout_c_summary"]["requests"] == 31
    assert report["layout_c_summary"]["prompt"]["aggregate_utf8_bytes"] == 87_705


def test_provider_reported_usage_is_recorded_per_comparison_without_estimation() -> None:
    provider = _UsageProvider()
    report = token_measure.measure(
        model="named-model",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
    )

    assert report["measurement_complete"] is True
    assert len(provider.calls) == 6
    expected_tokens = {
        "suggest-card-groups": 4000,
        "suggest-card-groups-route-b": 5000,
        "suggest-layout": 7000,
        "suggest-layout-route-b": 8000,
        "generate-narrative": 6000,
        "check-narrative": 11000,
    }
    for route, expected in expected_tokens.items():
        assert report["routes"][route]["status"] == "measured"
        assert report["routes"][route]["provider_reported"] == {
            "input_tokens": expected,
            "output_tokens": 1,
        }


def test_layout_c_provider_usage_aggregates_only_reported_usage() -> None:
    provider = _UsageProvider()
    report = token_measure.measure(
        model="named-model",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
        include_layout_c=True,
    )

    assert report["measurement_complete"] is True
    assert len(provider.calls) == 37
    summary = report["layout_c_summary"]
    assert summary["included"] is True
    assert summary["requests"] == 31
    # Calls 7..37 receive arbitrary provider-reported values 106..136.
    assert summary["provider_reported"] == {
        "input_tokens_complete": True,
        "aggregate_input_tokens": 3_751,
        "max_single_input_tokens": 136,
    }
    assert summary["provider_reported"]["aggregate_input_tokens"] != summary["prompt"][
        "aggregate_utf8_bytes"
    ]


def test_layout_c_missing_usage_stays_incomplete_without_estimation() -> None:
    provider = _UsageProvider(report_usage=False)
    report = token_measure.measure(
        model="named-model",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
        include_layout_c=True,
    )

    assert report["measurement_complete"] is False
    assert len(provider.calls) == 37
    assert report["layout_c_summary"]["provider_reported"] == {
        "input_tokens_complete": False,
        "aggregate_input_tokens": None,
        "max_single_input_tokens": None,
    }


def test_missing_provider_usage_is_recorded_as_measurement_incomplete() -> None:
    provider = _UsageProvider(report_usage=False)
    report = token_measure.measure(
        model="named-model",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
    )

    assert report["measurement_complete"] is False
    assert len(provider.calls) == 6
    assert {row["status"] for row in report["routes"].values()} == {
        "provider-did-not-report-usage"
    }


def test_provider_name_mismatch_fails_before_any_request_is_sent() -> None:
    provider = _UsageProvider()
    with pytest.raises(ValueError, match="プロバイダー名と一致しません"):
        token_measure.measure(
            model="named-model",
            expected_provider="different-provider",
            execute=True,
            provider=provider,
        )
    assert provider.calls == []


def test_external_execution_requires_explicit_environment_opt_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(token_measure.OPT_IN_ENV, raising=False)
    assert token_measure._opted_in() is False

    monkeypatch.setenv(token_measure.OPT_IN_ENV, "true")
    assert token_measure._opted_in() is True

    monkeypatch.setenv(token_measure.OPT_IN_ENV, "0")
    assert token_measure._opted_in() is False
