from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from kj_atlas_api.llm.provider import LLMCallMetadata, LLMRequest, LLMResponse
from scripts import measure_ai_route_provider_tokens as token_measure


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
            input_tokens = {
                "re_layout": 7000,
                "generate_narrative": 5000,
                "check_narrative": 11000,
            }[req.task]
            output_tokens = 1
        return LLMResponse(
            raw_text="{}",
            metadata=LLMCallMetadata(
                provider_kind=self.provider_kind,
                provider_name=self.provider_name,
                model_id=req.model or "unknown",
                transport="http",
                requested_at="2026-09-03T00:00:00+00:00",
                trace_id=f"trace-{req.task}",
            ),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )


def test_representative_requests_compare_ir_routes_and_full_check_narrative() -> None:
    requests = token_measure.build_representative_requests("named-model")

    assert set(requests) == {"suggest-layout", "generate-narrative", "check-narrative"}
    layout = requests["suggest-layout"]
    narrative = requests["generate-narrative"]
    check = requests["check-narrative"]

    assert layout.task == "re_layout"
    assert narrative.task == "generate_narrative"
    assert check.task == "check_narrative"
    assert layout.model == narrative.model == check.model == "named-model"
    assert layout.max_tokens == narrative.max_tokens == check.max_tokens == 1

    # 同じ300カード入力について、座標を使うIR route、座標を使わないIR route、
    # そしてStage 5で最後に残る全量prompt routeを同じ計測面へ置く。
    assert len((layout.inputs or {}).get("coordinates", [])) == 200
    assert "coordinates" not in (narrative.inputs or {})
    assert (layout.inputs or {})["truncation"]["reason_codes"] == ["MAX_CARDS"]
    assert (narrative.inputs or {})["truncation"]["reason_codes"] == ["MAX_CARDS"]

    # check-narrativeは現行production routeを忠実に再現し、まだIRを通さない。
    # coverageを落とさず全量を載せていることを、末尾のカード・島まで確認する。
    assert check.inputs is None
    assert 'id="c299"' in check.prompt
    assert 'id="i29"' in check.prompt
    assert "観察290" in check.prompt


def test_dry_run_never_needs_a_provider_or_claims_exact_tokens() -> None:
    report = token_measure.measure(
        model="named-model",
        expected_provider="named-test-provider",
        execute=False,
    )

    assert report["executed"] is False
    assert report["measurement_complete"] is False
    assert set(report["routes"]) == {"suggest-layout", "generate-narrative", "check-narrative"}
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
    assert set(report["routes"]) == {"suggest-layout", "generate-narrative", "check-narrative"}
    assert report["routes"]["check-narrative"]["status"] == "dry-run"


def test_provider_reported_usage_is_recorded_without_token_estimation() -> None:
    provider = _UsageProvider()
    report = token_measure.measure(
        model="named-model",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
    )

    assert report["measurement_complete"] is True
    assert len(provider.calls) == 3
    assert report["routes"]["suggest-layout"]["status"] == "measured"
    assert report["routes"]["suggest-layout"]["provider_reported"] == {
        "input_tokens": 7000,
        "output_tokens": 1,
    }
    assert report["routes"]["generate-narrative"]["provider_reported"] == {
        "input_tokens": 5000,
        "output_tokens": 1,
    }
    assert report["routes"]["check-narrative"]["provider_reported"] == {
        "input_tokens": 11000,
        "output_tokens": 1,
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
    assert len(provider.calls) == 3
    assert {
        row["status"] for row in report["routes"].values()
    } == {"provider-did-not-report-usage"}


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
