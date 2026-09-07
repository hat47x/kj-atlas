from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "04_Documentation/configuration.md"
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
SETTINGS = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
PROVIDER = ROOT / "03_Implement/backend/src/kj_atlas_api/llm/provider.py"
KEY = "KJ_ATLAS_LLM_ESCALATION_ENABLED"


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
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            segment = ast.get_source_segment(source, node)
            if segment is None:
                raise AssertionError(f"could not recover {name}")
            return segment
    raise AssertionError(f"{name} not found")


def _class_source(source: str, name: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            segment = ast.get_source_segment(source, node)
            if segment is None:
                raise AssertionError(f"could not recover {name}")
            return segment
    raise AssertionError(f"{name} not found")


class LargeScaleExecutionGateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = CONFIG.read_text(encoding="utf-8")
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.settings = SETTINGS.read_text(encoding="utf-8")
        self.provider = PROVIDER.read_text(encoding="utf-8")

    def test_readiness_requires_escalation_gate_for_large_scale_kind(self) -> None:
        readiness = _function_source(self.settings, "provider_kind_readiness_errors")
        self.assertIn('elif normalized == "large-scale":', readiness)
        self.assertIn('if not cfg.llm_escalation_enabled:', readiness)
        self.assertIn('KJ_ATLAS_LLM_ESCALATION_ENABLED is not set', readiness)

    def test_direct_and_registered_large_scale_execution_share_the_gate(self) -> None:
        direct = _class_source(self.provider, "LargeScaleProvider")
        registered = _function_source(self.provider, "build_registered_provider")
        self.assertIn('if not settings.llm_escalation_enabled:', direct)
        self.assertIn('Large-scale provider disabled by local-first policy', direct)
        self.assertIn('if not settings.llm_large_scale_opt_in or not settings.llm_escalation_enabled:', registered)
        self.assertIn('Registered large-scale provider is disabled by policy', registered)

    def test_public_docs_call_it_an_execution_gate_not_only_escalation(self) -> None:
        for row in (_row(self.config, KEY), _backend_row(self.registry, KEY)):
            self.assertIn("large-scale provider kind", row)
            self.assertIn("実行gate", row)
            self.assertIn("KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true", row)
        self.assertIn("primary", _row(self.config, KEY))
        self.assertIn("registered", _backend_row(self.registry, KEY))


if __name__ == "__main__":
    unittest.main()
