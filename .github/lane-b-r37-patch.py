from pathlib import Path

# 1) Make OpenAI-compatible chat message construction a shared source of truth.
provider_path = Path("03_Implement/backend/src/kj_atlas_api/llm/provider.py")
s = provider_path.read_text(encoding="utf-8")
needle = "def _generate_via_openai_chat(\n    req: LLMRequest,\n"
replacement = '''def _openai_chat_messages(req: LLMRequest) -> list[dict[str, str]]:\n    \"\"\"Build the exact system+user message content sent by chat transports.\"\"\"\n    system_prompt = (\n        f\"You are performing the task: {req.task}. \"\n        \"Respond with only the requested output, no preamble.\"\n    )\n    return [\n        {\"role\": \"system\", \"content\": system_prompt},\n        {\"role\": \"user\", \"content\": req.prompt},\n    ]\n\n\ndef _generate_via_openai_chat(\n    req: LLMRequest,\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
needle = '''    system_prompt = f\"You are performing the task: {req.task}. Respond with only the requested output, no preamble.\"\n    payload = {\n        \"model\": model_id,\n        \"messages\": [\n            {\"role\": \"system\", \"content\": system_prompt},\n            {\"role\": \"user\", \"content\": req.prompt},\n        ],\n'''
replacement = '''    payload = {\n        \"model\": model_id,\n        \"messages\": _openai_chat_messages(req),\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
provider_path.write_text(s, encoding="utf-8")

# 2) Bind measured DeepSeek usage to the exact message content sent by the transport.
measure_path = Path("03_Implement/backend/scripts/measure_ai_route_provider_tokens.py")
s = measure_path.read_text(encoding="utf-8")
needle = '''    ProviderError,\n    get_provider,\n)\n'''
replacement = '''    ProviderError,\n    _openai_chat_messages,\n    get_provider,\n)\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
needle = '''def _prompt_sha256(prompt: str) -> str:\n    \"\"\"Return an identity fingerprint for the exact UTF-8 provider prompt.\"\"\"\n    return hashlib.sha256(prompt.encode(\"utf-8\")).hexdigest()\n\n\ndef _route_row(req: LLMRequest) -> dict[str, Any]:\n'''
replacement = '''def _prompt_sha256(prompt: str) -> str:\n    \"\"\"Return an identity fingerprint for the exact UTF-8 provider prompt.\"\"\"\n    return hashlib.sha256(prompt.encode(\"utf-8\")).hexdigest()\n\n\ndef _openai_chat_messages_sha256(req: LLMRequest) -> str:\n    \"\"\"Fingerprint the exact system+user message content for DeepSeek chat input.\"\"\"\n    serialized = json.dumps(\n        _openai_chat_messages(req),\n        ensure_ascii=False,\n        allow_nan=False,\n        sort_keys=True,\n        separators=(\",\", \":\"),\n    ).encode(\"utf-8\")\n    return hashlib.sha256(serialized).hexdigest()\n\n\ndef _route_row(req: LLMRequest) -> dict[str, Any]:\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
needle = '''        \"provider_call\": None,\n        \"provider_reported\": {\n'''
replacement = '''        \"provider_call\": None,\n        \"provider_input\": None,\n        \"provider_reported\": {\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
needle = '''        \"provider_call_provenance\": {\"version\": 1},\n        \"executed\": execute,\n'''
replacement = '''        \"provider_call_provenance\": {\"version\": 1},\n        \"provider_input_provenance\": {\n            \"version\": 1,\n            \"deepseek_kind\": \"openai-chat-messages-v1\",\n            \"algorithm\": \"sha256\",\n            \"encoding\": \"utf-8\",\n        },\n        \"executed\": execute,\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
needle = '''        row[\"provider_call\"] = response.metadata.as_audit_fields()\n        row[\"provider_reported\"] = {\n'''
replacement = '''        row[\"provider_call\"] = response.metadata.as_audit_fields()\n        if response.metadata.provider_kind == \"deepseek\":\n            row[\"provider_input\"] = {\n                \"kind\": \"openai-chat-messages-v1\",\n                \"sha256\": _openai_chat_messages_sha256(req),\n            }\n        row[\"provider_reported\"] = {\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
measure_path.write_text(s, encoding="utf-8")

# 3) The analyzer requires the transport-input fingerprint only for DeepSeek rows.
analyzer_path = Path("03_Implement/backend/scripts/analyze_ai_route_provider_measurement.py")
a = analyzer_path.read_text(encoding="utf-8")
needle = '''        _prompt_sha256,\n        build_representative_requests,\n'''
replacement = '''        _openai_chat_messages_sha256,\n        _prompt_sha256,\n        build_representative_requests,\n'''
assert a.count(needle) == 2
a = a.replace(needle, replacement)
needle = '''PROVIDER_CALL_PROVENANCE = {\"version\": 1}\nCORE_ROUTE_TASKS = {\n'''
replacement = '''PROVIDER_CALL_PROVENANCE = {\"version\": 1}\nPROVIDER_INPUT_PROVENANCE = {\n    \"version\": 1,\n    \"deepseek_kind\": \"openai-chat-messages-v1\",\n    \"algorithm\": \"sha256\",\n    \"encoding\": \"utf-8\",\n}\nCORE_ROUTE_TASKS = {\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''    expected_model: str,\n    expected_prompt_sha256: str | None,\n    errors: list[str],\n) -> int | None:\n'''
replacement = '''    expected_model: str,\n    expected_prompt_sha256: str | None,\n    expected_deepseek_input_sha256: str | None,\n    errors: list[str],\n) -> int | None:\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''    if provider_call.get(\"execution_path\") != \"primary\":\n        errors.append(f\"provider-call-non-primary-path:{name}\")\n        return None\n\n    token = _int_token(row)\n'''
replacement = '''    if provider_call.get(\"execution_path\") != \"primary\":\n        errors.append(f\"provider-call-non-primary-path:{name}\")\n        return None\n\n    if row.get(\"actual_provider_kind\") == \"deepseek\":\n        provider_input = row.get(\"provider_input\")\n        if not isinstance(provider_input, dict):\n            errors.append(f\"provider-input-fingerprint-missing:{name}\")\n            return None\n        if provider_input.get(\"kind\") != \"openai-chat-messages-v1\":\n            errors.append(f\"provider-input-kind-mismatch:{name}\")\n            return None\n        if (\n            expected_deepseek_input_sha256 is None\n            or provider_input.get(\"sha256\") != expected_deepseek_input_sha256\n        ):\n            errors.append(f\"provider-input-fingerprint-mismatch:{name}\")\n            return None\n\n    token = _int_token(row)\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''    if report.get(\"provider_call_provenance\") != PROVIDER_CALL_PROVENANCE:\n        errors.append(\"unsupported-or-missing-provider-call-provenance\")\n\n    expected_provider = report.get(\"expected_provider\")\n'''
replacement = '''    if report.get(\"provider_call_provenance\") != PROVIDER_CALL_PROVENANCE:\n        errors.append(\"unsupported-or-missing-provider-call-provenance\")\n\n    expected_provider = report.get(\"expected_provider\")\n'''
assert a.count(needle) == 1
# No unconditional provider-input contract check here; generic providers remain valid.
a = a.replace(needle, replacement, 1)
needle = '''    canonical_prompt_hashes = {\n        name: _prompt_sha256(req.prompt) for name, req in canonical_requests.items()\n    }\n    for unexpected in sorted(set(routes) - set(canonical_requests)):\n'''
replacement = '''    canonical_prompt_hashes = {\n        name: _prompt_sha256(req.prompt) for name, req in canonical_requests.items()\n    }\n    canonical_deepseek_input_hashes = {\n        name: _openai_chat_messages_sha256(req)\n        for name, req in canonical_requests.items()\n    }\n    has_deepseek_measurement = any(\n        isinstance(row, dict) and row.get(\"actual_provider_kind\") == \"deepseek\"\n        for row in routes.values()\n    )\n    if (\n        has_deepseek_measurement\n        and report.get(\"provider_input_provenance\") != PROVIDER_INPUT_PROVENANCE\n    ):\n        errors.append(\"unsupported-or-missing-provider-input-provenance\")\n    for unexpected in sorted(set(routes) - set(canonical_requests)):\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''            expected_prompt_sha256=canonical_prompt_hashes.get(name),\n            errors=errors,\n'''
replacement = '''            expected_prompt_sha256=canonical_prompt_hashes.get(name),\n            expected_deepseek_input_sha256=canonical_deepseek_input_hashes.get(name),\n            errors=errors,\n'''
assert a.count(needle) == 2
a = a.replace(needle, replacement)
needle = '''            expected_prompt_sha256=canonical_prompt_hashes.get(GROUPS_A2_ROUTE),\n            errors=errors,\n'''
replacement = '''            expected_prompt_sha256=canonical_prompt_hashes.get(GROUPS_A2_ROUTE),\n            expected_deepseek_input_sha256=canonical_deepseek_input_hashes.get(\n                GROUPS_A2_ROUTE\n            ),\n            errors=errors,\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
needle = '''            \"Prompt SHA-256 is used only for exact UTF-8 prompt identity/provenance; bytes, chars, \"\n            \"and hashes are never converted into tokens. This report does not know the \"\n'''
replacement = '''            \"Prompt/provider-input SHA-256 values are identity/provenance only; bytes, chars, \"\n            \"and hashes are never converted into tokens. DeepSeek measurements additionally bind \"\n            \"the exact current OpenAI-chat system+user message content. This report does not know the \"\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
analyzer_path.write_text(a, encoding="utf-8")

# 4) Focused regression: DeepSeek transport input identity without disturbing generic fixtures.
new_test = Path("03_Implement/backend/tests/test_ai_route_provider_transport_input_provenance.py")
assert not new_test.exists()
new_test.write_text('''from __future__ import annotations\n\nfrom kj_atlas_api.llm.provider import (\n    LLMCallMetadata,\n    LLMRequest,\n    LLMResponse,\n    _openai_chat_messages,\n)\nfrom scripts import analyze_ai_route_provider_measurement as analysis\nfrom scripts import measure_ai_route_provider_tokens as token_measure\n\n\nclass _DeepSeekUsageProvider:\n    provider_name = \"named-deepseek\"\n    provider_kind = \"deepseek\"\n\n    def __init__(self) -> None:\n        self.calls: list[LLMRequest] = []\n\n    def generate(self, req: LLMRequest) -> LLMResponse:\n        self.calls.append(req)\n        index = len(self.calls)\n        return LLMResponse(\n            raw_text=\"{}\",\n            metadata=LLMCallMetadata(\n                provider_kind=self.provider_kind,\n                provider_name=self.provider_name,\n                model_id=req.model or \"unknown\",\n                transport=\"http\",\n                requested_at=f\"2026-09-05T00:00:{index:02d}+00:00\",\n                trace_id=f\"deepseek-trace-{index}\",\n                fallback_to_none=False,\n                execution_path=\"primary\",\n            ),\n            input_tokens=2000 + index,\n            output_tokens=1,\n        )\n\n\ndef _measured_report() -> dict:\n    provider = _DeepSeekUsageProvider()\n    report = token_measure.measure(\n        model=\"named-model\",\n        expected_provider=provider.provider_name,\n        execute=True,\n        provider=provider,\n    )\n    assert len(provider.calls) == 6\n    return report\n\n\ndef test_openai_chat_message_builder_matches_current_transport_content() -> None:\n    req = LLMRequest(task=\"re_layout\", prompt=\"exact user prompt\")\n    assert _openai_chat_messages(req) == [\n        {\n            \"role\": \"system\",\n            \"content\": (\n                \"You are performing the task: re_layout. \"\n                \"Respond with only the requested output, no preamble.\"\n            ),\n        },\n        {\"role\": \"user\", \"content\": \"exact user prompt\"},\n    ]\n\n\ndef test_deepseek_measurement_records_exact_message_fingerprint() -> None:\n    report = _measured_report()\n    requests = token_measure.build_representative_requests(\"named-model\")\n\n    assert report[\"provider_input_provenance\"] == analysis.PROVIDER_INPUT_PROVENANCE\n    for name, req in requests.items():\n        assert report[\"routes\"][name][\"provider_input\"] == {\n            \"kind\": \"openai-chat-messages-v1\",\n            \"sha256\": token_measure._openai_chat_messages_sha256(req),\n        }\n\n    result = analysis.analyze(report)\n    assert result[\"decision_ready\"] is True\n    assert result[\"errors\"] == []\n\n\ndef test_changed_deepseek_message_fingerprint_fails_closed() -> None:\n    report = _measured_report()\n    report[\"routes\"][\"check-narrative\"][\"provider_input\"][\"sha256\"] = \"0\" * 64\n\n    result = analysis.analyze(report)\n\n    assert result[\"decision_ready\"] is False\n    assert \"provider-input-fingerprint-mismatch:check-narrative\" in result[\"errors\"]\n\n\ndef test_missing_deepseek_provider_input_contract_fails_closed() -> None:\n    report = _measured_report()\n    del report[\"provider_input_provenance\"]\n\n    result = analysis.analyze(report)\n\n    assert result[\"decision_ready\"] is False\n    assert \"unsupported-or-missing-provider-input-provenance\" in result[\"errors\"]\n\n\ndef test_system_task_content_changes_message_fingerprint_even_with_same_user_prompt() -> None:\n    layout = LLMRequest(task=\"re_layout\", prompt=\"same user prompt\")\n    groups = LLMRequest(task=\"suggest_card_groups\", prompt=\"same user prompt\")\n\n    assert token_measure._prompt_sha256(layout.prompt) == token_measure._prompt_sha256(\n        groups.prompt\n    )\n    assert token_measure._openai_chat_messages_sha256(\n        layout\n    ) != token_measure._openai_chat_messages_sha256(groups)\n''', encoding="utf-8")
