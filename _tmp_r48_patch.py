from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{path}: expected one match, got {count}: {old[:80]!r}")
    p.write_text(text.replace(old, new, 1))


provider = "03_Implement/backend/src/kj_atlas_api/llm/provider.py"
replace_once(
    provider,
    '    execution_path: str = "primary"\n\n    def as_audit_fields(self) -> dict[str, object]:',
    '    execution_path: str = "primary"\n    # DeepSeek V4 request mode. Kept separate from generic audit fields because\n    # it is a provider-specific generation setting, not prompt/token content.\n    thinking_mode: str | None = None\n\n    def as_audit_fields(self) -> dict[str, object]:',
)
replace_once(
    provider,
    'def _new_metadata(*, provider_kind: str, provider_name: str, model_id: str, transport: str, fallback_to_none: bool = False) -> LLMCallMetadata:\n',
    'def _new_metadata(*, provider_kind: str, provider_name: str, model_id: str, transport: str, fallback_to_none: bool = False, thinking_mode: str | None = None) -> LLMCallMetadata:\n',
)
replace_once(
    provider,
    '        fallback_to_none=fallback_to_none,\n    )\n\n\nclass NoneProvider:',
    '        fallback_to_none=fallback_to_none,\n        thinking_mode=thinking_mode,\n    )\n\n\nclass NoneProvider:',
)
text = Path(provider).read_text()
marker = 'def _generate_via_openai_chat(\n'
start = text.index(marker)
end = text.index('\n    if (\n', start)
segment = text[start:end]
old = '        model_id=model_id,\n        transport="http",\n    )'
if segment.count(old) != 1:
    raise AssertionError("provider: could not locate DeepSeek/OpenAI metadata construction")
segment = segment.replace(
    old,
    '        model_id=model_id,\n        transport="http",\n        thinking_mode=thinking_mode,\n    )',
    1,
)
Path(provider).write_text(text[:start] + segment + text[end:])

measure = "03_Implement/backend/scripts/measure_ai_route_provider_tokens.py"
replace_once(
    measure,
    'from kj_atlas_api.models import SuggestLayoutRequest\n',
    'from kj_atlas_api.models import SuggestLayoutRequest\nfrom kj_atlas_api.settings import settings\n',
)
replace_once(
    measure,
    'OPT_IN_ENV = "KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN"\n_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})\n',
    'OPT_IN_ENV = "KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN"\n_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})\n_DEEPSEEK_THINKING_MODES = frozenset({"disabled", "enabled"})\nPROVIDER_GENERATION_PROVENANCE = {\n    "version": 1,\n    "deepseek_field": "thinking.type",\n}\n',
)
replace_once(
    measure,
    '        "provider_call": None,\n        "provider_input": None,\n',
    '        "provider_call": None,\n        "provider_input": None,\n        "provider_generation": None,\n',
)
replace_once(
    measure,
    '    include_layout_c: bool = False,\n    include_groups_a2: bool = False,\n) -> dict[str, Any]:',
    '    include_layout_c: bool = False,\n    include_groups_a2: bool = False,\n    expected_deepseek_thinking_mode: str | None = None,\n) -> dict[str, Any]:',
)
replace_once(
    measure,
    '    if not expected_provider.strip():\n        raise ValueError("`expected_provider` にはプロバイダー名を指定してください")\n\n    requests = build_representative_requests(',
    '    if not expected_provider.strip():\n        raise ValueError("`expected_provider` にはプロバイダー名を指定してください")\n    if (\n        expected_deepseek_thinking_mode is not None\n        and expected_deepseek_thinking_mode not in _DEEPSEEK_THINKING_MODES\n    ):\n        raise ValueError("DeepSeek thinking mode must be disabled or enabled")\n\n    requests = build_representative_requests(',
)
replace_once(
    measure,
    '        "provider_input_provenance": {\n            "version": 1,\n            "deepseek_kind": "openai-chat-messages-v1",\n            "algorithm": "sha256",\n            "encoding": "utf-8",\n        },\n        "executed": execute,',
    '        "provider_input_provenance": {\n            "version": 1,\n            "deepseek_kind": "openai-chat-messages-v1",\n            "algorithm": "sha256",\n            "encoding": "utf-8",\n        },\n        "provider_generation_provenance": PROVIDER_GENERATION_PROVENANCE,\n        "expected_deepseek_thinking_mode": expected_deepseek_thinking_mode,\n        "executed": execute,',
)
replace_once(
    measure,
    '    if provider.provider_name != expected_provider:\n        raise ValueError(\n            "現在設定されているプロバイダーが、計測対象として指定したプロバイダー名と一致しません"\n        )\n\n    all_measured = True',
    '    if provider.provider_name != expected_provider:\n        raise ValueError(\n            "現在設定されているプロバイダーが、計測対象として指定したプロバイダー名と一致しません"\n        )\n    if provider.provider_kind == "deepseek":\n        if expected_deepseek_thinking_mode not in _DEEPSEEK_THINKING_MODES:\n            raise ValueError(\n                "DeepSeek measurement requires an explicit expected thinking mode"\n            )\n        if settings.deepseek_thinking_mode != expected_deepseek_thinking_mode:\n            raise ValueError(\n                "configured DeepSeek thinking mode does not match the measurement expectation"\n            )\n    elif expected_deepseek_thinking_mode is not None:\n        raise ValueError(\n            "DeepSeek thinking mode expectation is only valid for a DeepSeek provider"\n        )\n\n    all_measured = True',
)
replace_once(
    measure,
    '        if response.metadata.provider_kind == "deepseek":\n            row["provider_input"] = {\n                "kind": "openai-chat-messages-v1",\n                "sha256": _openai_chat_messages_sha256(req),\n            }\n        row["provider_reported"] = {',
    '        if response.metadata.provider_kind == "deepseek":\n            row["provider_input"] = {\n                "kind": "openai-chat-messages-v1",\n                "sha256": _openai_chat_messages_sha256(req),\n            }\n            row["provider_generation"] = {\n                "thinking_mode": response.metadata.thinking_mode,\n            }\n        row["provider_reported"] = {',
)
replace_once(
    measure,
    '        elif response.metadata.model_id != model:\n            row["status"] = "model-mismatch"\n            all_measured = False\n        elif response.input_tokens is None:',
    '        elif response.metadata.model_id != model:\n            row["status"] = "model-mismatch"\n            all_measured = False\n        elif (\n            response.metadata.provider_kind == "deepseek"\n            and response.metadata.thinking_mode != expected_deepseek_thinking_mode\n        ):\n            row["status"] = "generation-mode-mismatch"\n            all_measured = False\n        elif response.input_tokens is None:',
)
replace_once(
    measure,
    '    parser.add_argument(\n        "--execute",\n',
    '    parser.add_argument(\n        "--deepseek-thinking-mode",\n        choices=("disabled", "enabled"),\n        default=None,\n        help=(\n            "Expected DeepSeek V4 thinking.type for this measurement. "\n            "Required before executing a DeepSeek provider so an environment override "\n            "cannot silently change the measured request mode."\n        ),\n    )\n    parser.add_argument(\n        "--execute",\n',
)
replace_once(
    measure,
    '                    include_groups_a2=args.include_groups_a2,\n                ),',
    '                    include_groups_a2=args.include_groups_a2,\n                    expected_deepseek_thinking_mode=args.deepseek_thinking_mode,\n                ),',
)
replace_once(
    measure,
    '            include_groups_a2=args.include_groups_a2,\n        )\n    except ValueError as exc:',
    '            include_groups_a2=args.include_groups_a2,\n            expected_deepseek_thinking_mode=args.deepseek_thinking_mode,\n        )\n    except ValueError as exc:',
)

analyzer = "03_Implement/backend/scripts/analyze_ai_route_provider_measurement.py"
replace_once(
    analyzer,
    'PROVIDER_INPUT_PROVENANCE = {\n    "version": 1,\n    "deepseek_kind": "openai-chat-messages-v1",\n    "algorithm": "sha256",\n    "encoding": "utf-8",\n}\n',
    'PROVIDER_INPUT_PROVENANCE = {\n    "version": 1,\n    "deepseek_kind": "openai-chat-messages-v1",\n    "algorithm": "sha256",\n    "encoding": "utf-8",\n}\nPROVIDER_GENERATION_PROVENANCE = {\n    "version": 1,\n    "deepseek_field": "thinking.type",\n}\n_DEEPSEEK_THINKING_MODES = frozenset({"disabled", "enabled"})\n',
)
replace_once(
    analyzer,
    '    expected_deepseek_input_sha256: str | None,\n    errors: list[str],\n) -> int | None:',
    '    expected_deepseek_input_sha256: str | None,\n    expected_deepseek_thinking_mode: str | None,\n    errors: list[str],\n) -> int | None:',
)
replace_once(
    analyzer,
    '        if (\n            expected_deepseek_input_sha256 is None\n            or provider_input.get("sha256") != expected_deepseek_input_sha256\n        ):\n            errors.append(f"provider-input-fingerprint-mismatch:{name}")\n            return None\n\n    token = _int_token(row)',
    '        if (\n            expected_deepseek_input_sha256 is None\n            or provider_input.get("sha256") != expected_deepseek_input_sha256\n        ):\n            errors.append(f"provider-input-fingerprint-mismatch:{name}")\n            return None\n        provider_generation = row.get("provider_generation")\n        if not isinstance(provider_generation, dict):\n            errors.append(f"provider-generation-metadata-missing:{name}")\n            return None\n        if provider_generation.get("thinking_mode") != expected_deepseek_thinking_mode:\n            errors.append(f"provider-generation-mode-mismatch:{name}")\n            return None\n\n    token = _int_token(row)',
)
replace_once(
    analyzer,
    '    has_deepseek_measurement = any(\n        isinstance(row, dict) and row.get("actual_provider_kind") == "deepseek"\n        for row in routes.values()\n    )\n    if (\n        has_deepseek_measurement\n        and report.get("provider_input_provenance") != PROVIDER_INPUT_PROVENANCE\n    ):\n        errors.append("unsupported-or-missing-provider-input-provenance")\n',
    '    has_deepseek_measurement = any(\n        isinstance(row, dict) and row.get("actual_provider_kind") == "deepseek"\n        for row in routes.values()\n    )\n    expected_deepseek_thinking_mode = report.get("expected_deepseek_thinking_mode")\n    if has_deepseek_measurement:\n        if report.get("provider_input_provenance") != PROVIDER_INPUT_PROVENANCE:\n            errors.append("unsupported-or-missing-provider-input-provenance")\n        if (\n            report.get("provider_generation_provenance")\n            != PROVIDER_GENERATION_PROVENANCE\n        ):\n            errors.append("unsupported-or-missing-provider-generation-provenance")\n        if expected_deepseek_thinking_mode not in _DEEPSEEK_THINKING_MODES:\n            errors.append("missing-or-invalid-expected-deepseek-thinking-mode")\n            expected_deepseek_thinking_mode = None\n',
)
# Pass the expected mode through every route validator invocation.
needle = '            expected_deepseek_input_sha256=canonical_deepseek_input_hashes.get(name),\n            errors=errors,\n'
replacement = '            expected_deepseek_input_sha256=canonical_deepseek_input_hashes.get(name),\n            expected_deepseek_thinking_mode=expected_deepseek_thinking_mode,\n            errors=errors,\n'
text = Path(analyzer).read_text()
if text.count(needle) != 2:
    raise AssertionError(f"analyzer: expected 2 direct route validator calls, got {text.count(needle)}")
text = text.replace(needle, replacement)
needle_multiline = '            expected_deepseek_input_sha256=canonical_deepseek_input_hashes.get(\n                GROUPS_A2_ROUTE\n            ),\n            errors=errors,\n'
replacement_multiline = '            expected_deepseek_input_sha256=canonical_deepseek_input_hashes.get(\n                GROUPS_A2_ROUTE\n            ),\n            expected_deepseek_thinking_mode=expected_deepseek_thinking_mode,\n            errors=errors,\n'
if text.count(needle_multiline) != 1:
    raise AssertionError("analyzer: groups A2 validator call not found")
text = text.replace(needle_multiline, replacement_multiline, 1)
Path(analyzer).write_text(text)
replace_once(
    analyzer,
    '            "and hashes are never converted into tokens. DeepSeek measurements additionally bind "\n            "the exact current OpenAI-chat system+user message content. Context minimums add the "',
    '            "and hashes are never converted into tokens. DeepSeek measurements additionally bind "\n            "the exact current OpenAI-chat system+user message content and record the explicit "\n            "thinking.type used by the transport. That generation mode is provenance, not a token "\n            "estimate. Context minimums add the "',
)

test_transport = "03_Implement/backend/tests/test_ai_route_provider_transport_input_provenance.py"
replace_once(
    test_transport,
    '                execution_path="primary",\n            ),',
    '                execution_path="primary",\n                thinking_mode="disabled",\n            ),',
)
replace_once(
    test_transport,
    '        execute=True,\n        provider=provider,\n    )',
    '        execute=True,\n        provider=provider,\n        expected_deepseek_thinking_mode="disabled",\n    )',
)
replace_once(
    test_transport,
    '    assert report["provider_input_provenance"] == analysis.PROVIDER_INPUT_PROVENANCE\n    for name, req in requests.items():\n',
    '    assert report["provider_input_provenance"] == analysis.PROVIDER_INPUT_PROVENANCE\n    assert (\n        report["provider_generation_provenance"]\n        == analysis.PROVIDER_GENERATION_PROVENANCE\n    )\n    assert report["expected_deepseek_thinking_mode"] == "disabled"\n    for name, req in requests.items():\n',
)
replace_once(
    test_transport,
    '        assert report["routes"][name]["provider_input"] == {\n            "kind": "openai-chat-messages-v1",\n            "sha256": token_measure._openai_chat_messages_sha256(req),\n        }\n\n    result = analysis.analyze(report)',
    '        assert report["routes"][name]["provider_input"] == {\n            "kind": "openai-chat-messages-v1",\n            "sha256": token_measure._openai_chat_messages_sha256(req),\n        }\n        assert report["routes"][name]["provider_generation"] == {\n            "thinking_mode": "disabled",\n        }\n\n    result = analysis.analyze(report)',
)
# Add focused fail-closed/preflight cases before the final fingerprint-difference test.
insert_marker = '\ndef test_system_task_content_changes_message_fingerprint_even_with_same_user_prompt() -> None:\n'
addition = '''\ndef test_deepseek_measurement_requires_expected_thinking_mode_before_calls() -> None:\n    provider = _DeepSeekUsageProvider()\n\n    try:\n        token_measure.measure(\n            model="named-model",\n            expected_provider=provider.provider_name,\n            execute=True,\n            provider=provider,\n        )\n    except ValueError as exc:\n        assert "explicit expected thinking mode" in str(exc)\n    else:\n        raise AssertionError("DeepSeek measurement must require an explicit thinking mode")\n\n    assert provider.calls == []\n\n\ndef test_changed_deepseek_thinking_mode_fails_closed() -> None:\n    report = _measured_report()\n    report["routes"]["suggest-layout"]["provider_generation"]["thinking_mode"] = "enabled"\n\n    result = analysis.analyze(report)\n\n    assert result["decision_ready"] is False\n    assert "provider-generation-mode-mismatch:suggest-layout" in result["errors"]\n\n\ndef test_missing_deepseek_generation_provenance_fails_closed() -> None:\n    report = _measured_report()\n    del report["provider_generation_provenance"]\n\n    result = analysis.analyze(report)\n\n    assert result["decision_ready"] is False\n    assert "unsupported-or-missing-provider-generation-provenance" in result["errors"]\n\n'''
replace_once(test_transport, insert_marker, addition + insert_marker)

test_provider = "03_Implement/backend/tests/test_llm_provider.py"
replace_once(
    test_provider,
    '        assert response.metadata.model_id == "deepseek-v4-flash"\n        assert response.transport == "http"\n',
    '        assert response.metadata.model_id == "deepseek-v4-flash"\n        assert response.metadata.thinking_mode == "disabled"\n        assert response.transport == "http"\n',
)
