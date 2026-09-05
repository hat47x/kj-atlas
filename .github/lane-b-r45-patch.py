from pathlib import Path


def replace(path: str, old: str, new: str, *, count: int = 1) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    actual = text.count(old)
    assert actual >= count, (path, actual, old)
    text = text.replace(old, new, count)
    p.write_text(text, encoding="utf-8")


# Settings: move the supported default to V4 Flash and make thinking semantics explicit.
settings_path = "03_Implement/backend/src/kj_atlas_api/settings.py"
replace(
    settings_path,
    '    "DEEPSEEK_MODEL",\n',
    '    "DEEPSEEK_MODEL",\n    "DEEPSEEK_THINKING_MODE",\n',
)
replace(
    settings_path,
    '    deepseek_model: str = Field(\n        default="deepseek-chat",\n        validation_alias="KJ_ATLAS_DEEPSEEK_MODEL",\n    )\n',
    '    # DeepSeek retired the legacy deepseek-chat/deepseek-reasoner aliases on 2026-07-24.\n'
    '    # V4 enables thinking by default, but the historical KJ Atlas deepseek-chat default\n'
    '    # was non-thinking. Preserve that behavior explicitly unless the operator opts in.\n'
    '    deepseek_model: str = Field(\n        default="deepseek-v4-flash",\n        validation_alias="KJ_ATLAS_DEEPSEEK_MODEL",\n    )\n'
    '    deepseek_thinking_mode: str = Field(\n        default="disabled",\n        validation_alias="KJ_ATLAS_DEEPSEEK_THINKING_MODE",\n    )\n',
)
replace(
    settings_path,
    '    # Example: "re_layout=deepseek-chat,generate_narrative=deepseek-reasoner"\n',
    '    # Example: "re_layout=deepseek-v4-flash,generate_narrative=deepseek-v4-pro"\n',
)
replace(
    settings_path,
    '        _validate_optional_llm_model_id(\n            value=self.large_scale_llm_model,\n            value_key="KJ_ATLAS_LARGE_SCALE_LLM_MODEL",\n        )\n        self.large_scale_llm_allowlist = _normalize_llm_allowlist(\n',
    '        _validate_optional_llm_model_id(\n            value=self.large_scale_llm_model,\n            value_key="KJ_ATLAS_LARGE_SCALE_LLM_MODEL",\n        )\n'
    '        _validate_optional_llm_model_id(\n            value=self.deepseek_model,\n            value_key="KJ_ATLAS_DEEPSEEK_MODEL",\n        )\n'
    '        normalized_deepseek_thinking_mode = self.deepseek_thinking_mode.strip().lower()\n'
    '        if normalized_deepseek_thinking_mode not in {"disabled", "enabled"}:\n'
    '            raise ValueError(\n'
    '                "KJ_ATLAS_DEEPSEEK_THINKING_MODE must be one of disabled|enabled"\n'
    '            )\n'
    '        self.deepseek_thinking_mode = normalized_deepseek_thinking_mode\n'
    '        self.large_scale_llm_allowlist = _normalize_llm_allowlist(\n',
)

# DeepSeek OpenAI-chat transport: always send the configured thinking mode explicitly.
provider_path = "03_Implement/backend/src/kj_atlas_api/llm/provider.py"
replace(
    provider_path,
    '    provider_name: str,\n    provider_kind: str,\n) -> LLMResponse:\n',
    '    provider_name: str,\n    provider_kind: str,\n    thinking_mode: str,\n) -> LLMResponse:\n',
)
replace(
    provider_path,
    '        "max_tokens": req.max_tokens,\n        "stream": False,\n    }\n',
    '        "max_tokens": req.max_tokens,\n        "stream": False,\n        "thinking": {"type": thinking_mode},\n    }\n',
)
replace(
    provider_path,
    '            provider_name=self.provider_name,\n            provider_kind=self.provider_kind,\n        )\n\n\nclass RegisteredHTTPProvider',
    '            provider_name=self.provider_name,\n            provider_kind=self.provider_kind,\n            thinking_mode=settings.deepseek_thinking_mode,\n        )\n\n\nclass RegisteredHTTPProvider',
)
replace(
    provider_path,
    '            provider_name=self.provider_name,\n            provider_kind=self.provider_kind,\n        )\n\n\n_REGISTERED_PROVIDER_KIND_ALIASES',
    '            provider_name=self.provider_name,\n            provider_kind=self.provider_kind,\n            thinking_mode=settings.deepseek_thinking_mode,\n        )\n\n\n_REGISTERED_PROVIDER_KIND_ALIASES',
)
replace(
    provider_path,
    '    # that gate, so an otherwise valid deepseek-chat registration was rejected\n',
    '    # that gate, so an otherwise valid DeepSeek default-model registration was rejected\n',
)

# Architecture / operator docs.
replace(
    "02_Architecture/llm_provider_spec.md",
    'KJ_ATLAS_DEEPSEEK_MODEL=deepseek-chat\n',
    'KJ_ATLAS_DEEPSEEK_MODEL=deepseek-v4-flash\nKJ_ATLAS_DEEPSEEK_THINKING_MODE=disabled\n',
)
replace(
    "02_Architecture/llm_provider_spec.md",
    '- `KJ_ATLAS_LLM_PROVIDER=deepseek` は `KJ_ATLAS_DEEPSEEK_API_KEY` を必須とし、未設定時は起動を拒否する。\n',
    '- `KJ_ATLAS_LLM_PROVIDER=deepseek` は `KJ_ATLAS_DEEPSEEK_API_KEY` を必須とし、未設定時は起動を拒否する。\n'
    '- `KJ_ATLAS_DEEPSEEK_THINKING_MODE` は `disabled|enabled`。既定 `disabled` は旧 `deepseek-chat` のnon-thinking semanticsを維持する。\n',
)
replace(
    "02_Architecture/runtime_parameter_registry.md",
    '| `KJ_ATLAS_DEEPSEEK_MODEL` | `deepseek-chat` | DeepSeek API に渡すmodel ID。256文字以下のcanonical | direct | 通常値 | 呼び出しペイロードの model フィールドが設定値と一致することを確認する |\n',
    '| `KJ_ATLAS_DEEPSEEK_MODEL` | `deepseek-v4-flash` | DeepSeek API に渡すmodel ID。256文字以下のcanonical | direct | 通常値 | 呼び出しペイロードの model フィールドが設定値と一致することを確認する |\n'
    '| `KJ_ATLAS_DEEPSEEK_THINKING_MODE` | `disabled` | DeepSeek V4 Chat Completionsのthinking mode。`disabled|enabled`。旧 `deepseek-chat` のnon-thinking semanticsを保つため既定はdisabled | direct | 通常値 | DeepSeek送信payloadの `thinking.type` が設定値と一致することを確認する |\n',
)
replace(
    "04_Documentation/configuration.md",
    '| `KJ_ATLAS_LLM_PROVIDER` | `none` | `none`, `local`, `local_http`, `large-scale`, `large_scale`, `external` |\n',
    '| `KJ_ATLAS_LLM_PROVIDER` | `none` | `none`, `local`, `local_http`, `large-scale`, `large_scale`, `external`, `deepseek` |\n',
)
replace(
    "04_Documentation/configuration.md",
    '| `KJ_ATLAS_DEEPSEEK_MODEL` | `deepseek-chat` | DeepSeek API に渡すmodel ID |\n',
    '| `KJ_ATLAS_DEEPSEEK_MODEL` | `deepseek-v4-flash` | DeepSeek API に渡すmodel ID |\n'
    '| `KJ_ATLAS_DEEPSEEK_THINKING_MODE` | `disabled` | DeepSeek V4 thinking mode（`disabled` / `enabled`）。旧既定のnon-thinking挙動を維持するため既定はdisabled |\n',
)
replace(
    "03_Implement/backend/README.md",
    "  --id deepseek-chat --provider-id deepseek --display-name 'DeepSeek Chat' \\\n  --capabilities intermediate,generate\n",
    "  --id deepseek-v4-flash --provider-id deepseek --display-name 'DeepSeek V4 Flash' \\\n  --capabilities intermediate,generate\n",
)
replace(
    "03_Implement/backend/README.md",
    '  --tenant-id local-default --model-id deepseek-chat\n',
    '  --tenant-id local-default --model-id deepseek-v4-flash\n',
)
replace(
    "03_Implement/backend/README.md",
    '  --id deepseek-chat --state disabled\n',
    '  --id deepseek-v4-flash --state disabled\n',
)
replace(
    "03_Implement/backend/tests/test_llm_integration.py",
    '                    --model deepseek-chat\n',
    '                    --model deepseek-v4-flash\n',
)

# Active evaluation / generated-test stubs should reflect the supported default.
replace(
    "03_Implement/backend/scripts/run_ai_eval.py",
    '        model_id="deepseek-chat",\n',
    '        model_id="deepseek-v4-flash",\n',
)
replace(
    "03_Implement/backend/scripts/generate_from_design_decision.py",
    '        provider_kind="deepseek", provider_name="deepseek", model_id="deepseek-chat",\n',
    '        provider_kind="deepseek", provider_name="deepseek", model_id="deepseek-v4-flash",\n',
)

# Provider/settings regressions.
test_provider = "03_Implement/backend/tests/test_llm_provider.py"
replace(test_provider, '    assert loaded.deepseek_model == "deepseek-chat"\n', '    assert loaded.deepseek_model == "deepseek-v4-flash"\n    assert loaded.deepseek_thinking_mode == "disabled"\n')
replace(test_provider, '    monkeypatch.setenv("KJ_ATLAS_DEEPSEEK_MODEL", "deepseek-reasoner")\n\n    loaded = Settings()\n    assert loaded.deepseek_model == "deepseek-reasoner"\n', '    monkeypatch.setenv("KJ_ATLAS_DEEPSEEK_MODEL", "deepseek-v4-pro")\n    monkeypatch.setenv("KJ_ATLAS_DEEPSEEK_THINKING_MODE", "enabled")\n\n    loaded = Settings()\n    assert loaded.deepseek_model == "deepseek-v4-pro"\n    assert loaded.deepseek_thinking_mode == "enabled"\n')
# Two provider-path tests: default model first, then task-map override.
replace(test_provider, '    settings.deepseek_model = "deepseek-chat"\n', '    settings.deepseek_model = "deepseek-v4-flash"\n', count=2)
replace(test_provider, '        assert payload["model"] == "deepseek-chat"\n', '        assert payload["model"] == "deepseek-v4-flash"\n        assert payload["thinking"] == {"type": "disabled"}\n')
replace(test_provider, '        assert response.metadata.model_id == "deepseek-chat"\n', '        assert response.metadata.model_id == "deepseek-v4-flash"\n')
replace(test_provider, '    settings.llm_task_model_map = "suggest_document_title=deepseek-reasoner"\n', '    settings.llm_task_model_map = "suggest_document_title=deepseek-v4-pro"\n')
replace(test_provider, '        assert payload["model"] == "deepseek-reasoner"\n', '        assert payload["model"] == "deepseek-v4-pro"\n        assert payload["thinking"] == {"type": "disabled"}\n')
replace(test_provider, '        assert response.metadata.model_id == "deepseek-reasoner"\n', '        assert response.metadata.model_id == "deepseek-v4-pro"\n')
# Add invalid-mode coverage before auth-error test.
replace(
    test_provider,
    '\n\ndef test_deepseek_auth_error_401(monkeypatch: pytest.MonkeyPatch) -> None:\n',
    '\n\ndef test_deepseek_settings_reject_invalid_thinking_mode(monkeypatch: pytest.MonkeyPatch) -> None:\n'
    '    monkeypatch.setenv("KJ_ATLAS_LLM_PROVIDER", "deepseek")\n'
    '    monkeypatch.setenv("KJ_ATLAS_DEEPSEEK_API_KEY", "sk-test-key")\n'
    '    monkeypatch.setenv("KJ_ATLAS_DEEPSEEK_THINKING_MODE", "auto")\n\n'
    '    with pytest.raises(ValueError, match="KJ_ATLAS_DEEPSEEK_THINKING_MODE"):\n'
    '        Settings()\n'
    '\n\ndef test_deepseek_auth_error_401(monkeypatch: pytest.MonkeyPatch) -> None:\n',
)

# Evaluation pipeline defaults / metadata.
eval_test = "03_Implement/backend/tests/test_ai_eval_pipeline.py"
replace(eval_test, '        model_id="deepseek-chat",\n', '        model_id="deepseek-v4-flash",\n')
replace(eval_test, '        settings.deepseek_model = "deepseek-chat"\n', '        settings.deepseek_model = "deepseek-v4-flash"\n')
replace(eval_test, '        assert resolve_model_for_task("refine_card_text") == "deepseek-chat"\n        assert resolve_model_for_task("suggest_island_summary") == "deepseek-chat"\n', '        assert resolve_model_for_task("refine_card_text") == "deepseek-v4-flash"\n        assert resolve_model_for_task("suggest_island_summary") == "deepseek-v4-flash"\n')
replace(eval_test, '    assert meta.get("model_id") == "deepseek-chat"\n', '    assert meta.get("model_id") == "deepseek-v4-flash"\n')

# Env registry seeding test is specifically about the configured default model.
gov_test = "03_Implement/backend/tests/test_model_governance.py"
replace(gov_test, '    monkeypatch.setattr(settings, "deepseek_model", "deepseek-chat")\n', '    monkeypatch.setattr(settings, "deepseek_model", "deepseek-v4-flash")\n')
replace(gov_test, '        assert db.get(LLMModelRegistryRow, "deepseek-chat") is not None\n', '        assert db.get(LLMModelRegistryRow, "deepseek-v4-flash") is not None\n')
