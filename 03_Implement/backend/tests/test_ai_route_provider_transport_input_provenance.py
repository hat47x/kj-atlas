from __future__ import annotations

from kj_atlas_api.llm.provider import (
    LLMCallMetadata,
    LLMRequest,
    LLMResponse,
    _openai_chat_messages,
)
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
                requested_at=f"2026-09-05T00:00:{index:02d}+00:00",
                trace_id=f"deepseek-trace-{index}",
                fallback_to_none=False,
                execution_path="primary",
                thinking_mode="disabled",
            ),
            input_tokens=2000 + index,
            output_tokens=1,
        )


def _measured_report() -> dict:
    provider = _DeepSeekUsageProvider()
    report = token_measure.measure(
        model="named-model",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
        expected_deepseek_thinking_mode="disabled",
    )
    assert len(provider.calls) == 6
    return report


def test_openai_chat_message_builder_matches_current_transport_content() -> None:
    req = LLMRequest(task="re_layout", prompt="exact user prompt")
    assert _openai_chat_messages(req) == [
        {
            "role": "system",
            "content": (
                "You are performing the task: re_layout. "
                "Respond with only the requested output, no preamble."
            ),
        },
        {"role": "user", "content": "exact user prompt"},
    ]


def test_deepseek_measurement_records_exact_message_fingerprint() -> None:
    report = _measured_report()
    requests = token_measure.build_representative_requests("named-model")

    assert report["provider_input_provenance"] == analysis.PROVIDER_INPUT_PROVENANCE
    assert (
        report["provider_generation_provenance"]
        == analysis.PROVIDER_GENERATION_PROVENANCE
    )
    assert report["expected_deepseek_thinking_mode"] == "disabled"
    for name, req in requests.items():
        assert report["routes"][name]["provider_input"] == {
            "kind": "openai-chat-messages-v1",
            "sha256": token_measure._openai_chat_messages_sha256(req),
        }
        assert report["routes"][name]["provider_generation"] == {
            "thinking_mode": "disabled",
        }

    result = analysis.analyze(report)
    assert result["decision_ready"] is True
    assert result["errors"] == []


def test_changed_deepseek_message_fingerprint_fails_closed() -> None:
    report = _measured_report()
    report["routes"]["check-narrative"]["provider_input"]["sha256"] = "0" * 64

    result = analysis.analyze(report)

    assert result["decision_ready"] is False
    assert "provider-input-fingerprint-mismatch:check-narrative" in result["errors"]


def test_missing_deepseek_provider_input_contract_fails_closed() -> None:
    report = _measured_report()
    del report["provider_input_provenance"]

    result = analysis.analyze(report)

    assert result["decision_ready"] is False
    assert "unsupported-or-missing-provider-input-provenance" in result["errors"]


def test_deepseek_measurement_requires_expected_thinking_mode_before_calls() -> None:
    provider = _DeepSeekUsageProvider()

    try:
        token_measure.measure(
            model="named-model",
            expected_provider=provider.provider_name,
            execute=True,
            provider=provider,
        )
    except ValueError as exc:
        assert "explicit expected thinking mode" in str(exc)
    else:
        raise AssertionError("DeepSeek measurement must require an explicit thinking mode")

    assert provider.calls == []


def test_changed_deepseek_thinking_mode_fails_closed() -> None:
    report = _measured_report()
    report["routes"]["suggest-layout"]["provider_generation"]["thinking_mode"] = "enabled"

    result = analysis.analyze(report)

    assert result["decision_ready"] is False
    assert "provider-generation-mode-mismatch:suggest-layout" in result["errors"]


def test_missing_deepseek_generation_provenance_fails_closed() -> None:
    report = _measured_report()
    del report["provider_generation_provenance"]

    result = analysis.analyze(report)

    assert result["decision_ready"] is False
    assert "unsupported-or-missing-provider-generation-provenance" in result["errors"]


def test_system_task_content_changes_message_fingerprint_even_with_same_user_prompt() -> None:
    layout = LLMRequest(task="re_layout", prompt="same user prompt")
    groups = LLMRequest(task="suggest_card_groups", prompt="same user prompt")

    assert token_measure._prompt_sha256(layout.prompt) == token_measure._prompt_sha256(
        groups.prompt
    )
    assert token_measure._openai_chat_messages_sha256(
        layout
    ) != token_measure._openai_chat_messages_sha256(groups)
