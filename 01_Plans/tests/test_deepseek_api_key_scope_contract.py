from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "04_Documentation/configuration.md"
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
SETTINGS = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
PROVIDER = ROOT / "03_Implement/backend/src/kj_atlas_api/llm/provider.py"
KEY = "KJ_ATLAS_DEEPSEEK_API_KEY"


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


def _backend_row(text: str, key: str) -> str:
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


def _function_source(source: str, name: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            segment = ast.get_source_segment(source, node)
            if segment is None:
                raise AssertionError(f"could not recover {name}")
            return segment
    raise AssertionError(f"{name} not found")


class DeepseekApiKeyScopeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = CONFIG.read_text(encoding="utf-8")
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.settings = SETTINGS.read_text(encoding="utf-8")
        self.provider = PROVIDER.read_text(encoding="utf-8")

    def test_primary_deepseek_readiness_requires_the_key(self) -> None:
        readiness = _function_source(self.settings, "provider_kind_readiness_errors")
        self.assertIn('if normalized == "deepseek":', readiness)
        self.assertIn('if not cfg.deepseek_api_key:', readiness)
        self.assertIn('KJ_ATLAS_DEEPSEEK_API_KEY is not set', readiness)
        self.assertIn('provider_kind_readiness_errors("deepseek", self)', self.settings)

    def test_registered_deepseek_resolves_the_same_env_key_and_fails_closed(self) -> None:
        resolver = _function_source(self.provider, "_resolve_registered_api_key")
        builder = _function_source(self.provider, "build_registered_provider")
        self.assertIn('KJ_ATLAS_DEEPSEEK_API_KEY', self.provider)
        self.assertIn('settings.deepseek_api_key', resolver)
        self.assertIn('if kind == "deepseek":', builder)
        self.assertIn('_resolve_registered_api_key(config.api_key_ref)', builder)
        self.assertIn('Registered provider credential is unavailable', builder)

    def test_public_docs_distinguish_startup_and_registered_request_time_scope(self) -> None:
        config_row = _row(self.config, KEY)
        registry_row = _backend_row(self.registry, KEY)
        for row in (config_row, registry_row):
            self.assertIn("primary", row)
            self.assertIn("registered DeepSeek", row)
            self.assertIn("api_key_ref=KJ_ATLAS_DEEPSEEK_API_KEY", row)
            self.assertIn("fail-closed", row)
        self.assertIn("起動readiness", config_row)
        self.assertIn("request-time", registry_row)


if __name__ == "__main__":
    unittest.main()
