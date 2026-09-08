from __future__ import annotations

from kj_atlas_api.llm.provider import LLMCallMetadata, LLMRequest, LLMResponse
from scripts import analyze_ai_route_provider_measurement as analysis
from scripts import measure_ai_route_provider_tokens as token_measure


class _ProvenanceProvider:
    provider_name = "named-provider"
    provider_kind = "test"

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
                requested_at=f"2026-09-05T00:00:{index:02d}+00:00",
                trace_id=f"trace-{index}",
                fallback_to_none=False,
                execution_path="primary",
            ),
            input_tokens=1000 + index,
            output_tokens=1,
        )


def _measured_report() -> dict:
    provider = _ProvenanceProvider()
    report = token_measure.measure(
        model="named-model",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
    )
    assert len(provider.calls) == 6
    return report


def test_measurement_records_call_provenance_for_every_provider_response() -> None:
    report = _measured_report()

    assert report["provider_call_provenance"] == {"version": 1}
    assert report["measurement_complete"] is True
    for index, row in enumerate(report["routes"].values(), start=1):
        assert row["provider_call"] == {
            "provider": "named-provider",
            "provider_kind": "test",
            "model_id": "named-model",
            "transport": "http",
            "requested_at": f"2026-09-05T00:00:{index:02d}+00:00",
            "fallback_to_none": False,
            "execution_path": "primary",
            "trace_id": f"trace-{index}",
        }


def test_measured_report_with_primary_trace_metadata_is_decision_ready() -> None:
    result = analysis.analyze(_measured_report())

    assert result["decision_ready"] is True
    assert result["errors"] == []


def test_missing_call_provenance_contract_fails_closed() -> None:
    report = _measured_report()
    del report["provider_call_provenance"]

    result = analysis.analyze(report)

    assert result["decision_ready"] is False
    assert "unsupported-or-missing-provider-call-provenance" in result["errors"]


def test_fallback_or_non_primary_measurement_fails_closed() -> None:
    report = _measured_report()
    row = report["routes"]["suggest-card-groups"]
    row["provider_call"]["fallback_to_none"] = True
    row["provider_call"]["execution_path"] = "fallback"

    result = analysis.analyze(report)

    assert result["decision_ready"] is False
    assert "provider-call-fallback-detected:suggest-card-groups" in result["errors"]


def test_missing_trace_id_fails_closed() -> None:
    report = _measured_report()
    report["routes"]["suggest-layout"]["provider_call"]["trace_id"] = ""

    result = analysis.analyze(report)

    assert result["decision_ready"] is False
    assert "provider-call-trace_id-missing:suggest-layout" in result["errors"]


def test_dry_run_keeps_provider_call_empty_and_never_becomes_evidence() -> None:
    report = token_measure.measure(
        model="named-model",
        expected_provider="named-provider",
        execute=False,
    )

    assert report["provider_call_provenance"] == {"version": 1}
    assert all(row["provider_call"] is None for row in report["routes"].values())
    result = analysis.analyze(report)
    assert result["decision_ready"] is False
    assert "report-not-executed" in result["errors"]
