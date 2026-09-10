from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROVIDER_PATH = ROOT / "03_Implement/backend/src/sui_sensemaking_api/llm/provider.py"
SETTINGS_PATH = ROOT / "03_Implement/backend/src/sui_sensemaking_api/settings.py"
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"


def _function_source(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    node = next(
        item
        for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name
    )
    return ast.get_source_segment(text, node) or ""


def _public_row(path: Path, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith(prefix)
    ]
    if len(rows) != 1:
        raise AssertionError(f"expected one public row for {key} in {path}, got {len(rows)}")
    return rows[0]


class DeepSeekThinkingEffectScopeContractTests(unittest.TestCase):
    def test_thinking_mode_only_reaches_deepseek_chat_payload(self) -> None:
        provider = PROVIDER_PATH.read_text(encoding="utf-8")
        tree = ast.parse(provider)

        chat_source = _function_source(PROVIDER_PATH, "_generate_via_openai_chat")
        self.assertIn('"thinking": {"type": thinking_mode}', chat_source)

        chat_calls = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not (isinstance(node.func, ast.Name) and node.func.id == "_generate_via_openai_chat"):
                continue
            chat_calls.append(ast.get_source_segment(provider, node) or "")

        self.assertEqual(len(chat_calls), 2)
        for source in chat_calls:
            self.assertIn("thinking_mode=settings.deepseek_thinking_mode", source)

        generic_source = _function_source(PROVIDER_PATH, "_serialize_http_provider_request")
        self.assertNotIn('"thinking"', generic_source)
        self.assertNotIn("thinking_mode", generic_source)

    def test_setting_enum_and_public_effect_scope_match(self) -> None:
        validator_source = _function_source(SETTINGS_PATH, "validate_llm_provider_guards")
        self.assertIn('{"disabled", "enabled"}', validator_source)
        self.assertIn(
            "self.deepseek_thinking_mode = normalized_deepseek_thinking_mode",
            validator_source,
        )

        key = "SUI_DEEPSEEK_THINKING_MODE"
        registry_row = _public_row(REGISTRY_PATH, key)
        configuration_row = _public_row(CONFIG_PATH, key)

        for row in (registry_row, configuration_row):
            self.assertIn("disabled", row)
            self.assertIn("enabled", row)
            self.assertIn("thinking.type", row)

        self.assertIn("registered DeepSeek", configuration_row)


if __name__ == "__main__":
    unittest.main()
