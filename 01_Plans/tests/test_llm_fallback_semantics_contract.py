from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "04_Documentation/configuration.md"
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
PROVIDER = ROOT / "03_Implement/backend/src/kj_atlas_api/llm/provider.py"
KEY = "KJ_ATLAS_LLM_FALLBACK_TO_NONE"


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


def _backend_registry_row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows: list[str] = []
    in_backend = False
    for line in text.splitlines():
        if line == "## Backend settings":
            in_backend = True
            continue
        if in_backend and line.startswith("## "):
            break
        if in_backend and line.startswith(prefix):
            rows.append(line)
    if len(rows) != 1:
        raise AssertionError(f"expected one backend row for {key}, got {len(rows)}")
    return rows[0]


def _generate_with_fallback_source(source: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "generate_with_fallback":
            segment = ast.get_source_segment(source, node)
            if segment is None:
                raise AssertionError("could not recover generate_with_fallback source")
            return segment
    raise AssertionError("generate_with_fallback not found")


class LlmFallbackSemanticsContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = CONFIG.read_text(encoding="utf-8")
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.provider = PROVIDER.read_text(encoding="utf-8")
        self.function = _generate_with_fallback_source(self.provider)

    def test_runtime_fallback_is_fail_closed_not_a_successful_generation(self) -> None:
        self.assertIn('except ProviderRequestError as exc:', self.function)
        self.assertIn('if exc.code == "provider_validation" or not settings.llm_fallback_to_none:', self.function)
        self.assertIn('fallback_to_none=True', self.function)
        self.assertIn('execution_path=f"{exc.metadata.provider_name}->none"', self.function)
        self.assertIn('raise ProviderDisabledError(', self.function)

    def test_configuration_states_the_fail_closed_scope(self) -> None:
        row = _row(self.config, KEY)
        for token in ("provider_unavailable", "provider_timeout", "ProviderDisabledError", "provider_validation", "ProviderRequestError"):
            self.assertIn(token, row)
        self.assertIn("成功応答へ切り替えず", row)

    def test_runtime_registry_probe_matches_the_same_error_semantics(self) -> None:
        row = _backend_registry_row(self.registry, KEY)
        for token in ("provider_kind=none", "fallback_to_none=true", "<provider>->none", "ProviderDisabledError"):
            self.assertIn(token, row)
        self.assertIn("validationでは元エラー", row)


if __name__ == "__main__":
    unittest.main()
