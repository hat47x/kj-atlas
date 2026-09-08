from __future__ import annotations

import pytest

from kj_atlas_api.llm.provider import LLMCallMetadata, LLMRequest, LLMResponse
from scripts import analyze_ai_route_provider_measurement as analysis
from scripts import measure_ai_route_provider_tokens as token_measure


class _DeepSeekUsageProvider:
    provider_name = "named-deepseek"
    provider_kind = "deepseek"

    def __init__(self) -> None:
        self.calls: list[LLMRequest] = []

    def generate(self, req: LLMRequest) -> LLMResponse:
        self.calls.append(req)
        index = len(self.calls)
        return LLMResponse(
            raw_text="{}",
            metadata=LLMCallMetadata(
                provider_kind=self.provider_kind,
                provider_name=self.provider_name,
                model_id=req.model or "unknown",
                transport="http",
                requested_at=f"2026-09-06T00:00:{index:02d}+00:00",
                trace_id=f"roundtrip-trace-{index}",
                fallback_to_none=False,
                execution_path="primary",
                thinking_mode="disabled",
            ),
            # Deliberately arbitrary provider-reported values. They are not
            # derived from prompt bytes/chars and exist only to prove that the
            # producer report can be consumed unchanged by the analyzer.
            input_tokens=1_000 + index,
            output_tokens=1,
        )


def test_full_opt_in_deepseek_measurement_roundtrips_into_analyzer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(token_measure.settings, "deepseek_thinking_mode", "disabled")
    provider = _DeepSeekUsageProvider()

    report = token_measure.measure(
        model="deepseek-v4-flash",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
        include_groups_a2=True,
        include_layout_c=True,
        expected_deepseek_thinking_mode="disabled",
    )

    assert report["measurement_complete"] is True
    assert len(provider.calls) == 38
    assert report["expected_deepseek_thinking_mode"] == "disabled"
    assert report["provider_generation_provenance"] == (
        analysis.PROVIDER_GENERATION_PROVENANCE
    )

    result = analysis.analyze(
        report,
        context_window_tokens=1_000_000,
        context_window_source=(
            "https://api-docs.deepseek.com/quick_start/agent_integrations/pi_mono/"
        ),
    )

    assert result["decision_ready"] is True
    assert result["core_ready"] is True
    assert result["groups_a2_ready"] is True
    assert result["layout_c_ready"] is True
    assert result["errors"] == []

    groups = result["observations"]["groups"]
    assert groups["a2_input_tokens"] == 1_007

    layout = result["observations"]["layout"]
    assert layout["layout_c_requests"] == 31
    assert layout["layout_c_max_single_input_tokens"] == 1_038

    budget = result["context_budget"]
    assert budget["context_window_tokens"] == 1_000_000
    assert budget["core_hard_context_fit"] is True
    assert budget["groups_a2_hard_context_fit"] is True
    assert budget["layout_c_hard_context_fit"] is True
    assert budget["layout_c_max_single_minimum_context_tokens"] == 3_038
    assert budget["sufficient_headroom_policy"] is None
