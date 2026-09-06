from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"
SETTINGS_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
OBSERVABILITY_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/observability.py"


def _row(path: Path, key: str) -> str:
    prefix = f"| `{key}` |"
    row = next(
        (line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(prefix)),
        None,
    )
    if row is None:
        raise AssertionError(f"public configuration row is missing: {key} in {path}")
    return row


def _purpose_cell(path: Path, key: str) -> str:
    cells = _row(path, key).split("|")
    if len(cells) < 5:
        raise AssertionError(f"malformed public configuration row: {key} in {path}")
    return cells[3].strip()


def _literal_not_in_set(path: Path, *, function_name: str, variable_name: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != function_name:
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Compare) or len(child.ops) != 1:
                continue
            if not isinstance(child.ops[0], ast.NotIn) or len(child.comparators) != 1:
                continue
            if not isinstance(child.left, ast.Name) or child.left.id != variable_name:
                continue
            value = ast.literal_eval(child.comparators[0])
            if isinstance(value, set) and all(isinstance(item, str) for item in value):
                return value
    raise AssertionError(
        f"literal not-in enum is missing: {function_name}:{variable_name} in {path}"
    )


def _provider_values_from_purpose(purpose: str) -> set[str]:
    # The public configuration row is only the accepted-value list. The SSOT row
    # prefixes that list with "LLM provider 種別。" and then continues with runtime
    # semantics, so only the first sentence after that prefix is the enum clause.
    if "LLM provider 種別。" in purpose:
        purpose = purpose.split("LLM provider 種別。", 1)[1].split("。", 1)[0]
    return set(re.findall(r"`([a-z][a-z0-9_-]*)`", purpose))


def _log_level_values_from_purpose(purpose: str) -> set[str]:
    # INFO is repeated as the fallback value; set semantics intentionally collapse
    # that repetition while still detecting an extra accepted token such as NOTSET.
    return set(re.findall(r"`([A-Z][A-Z0-9_-]*)`", purpose))


class PublicConfigurationEnumContractTests(unittest.TestCase):
    def test_llm_provider_values_match_settings_and_registry(self) -> None:
        implementation = _literal_not_in_set(
            SETTINGS_PATH,
            function_name="validate_llm_provider_guards",
            variable_name="provider",
        )
        registry = _provider_values_from_purpose(
            _purpose_cell(REGISTRY_PATH, "KJ_ATLAS_LLM_PROVIDER")
        )
        documentation = _provider_values_from_purpose(
            _purpose_cell(CONFIG_PATH, "KJ_ATLAS_LLM_PROVIDER")
        )
        self.assertEqual(registry, implementation)
        self.assertEqual(documentation, implementation)

    def test_log_level_values_match_logging_implementation_and_registry(self) -> None:
        implementation = _literal_not_in_set(
            OBSERVABILITY_PATH,
            function_name="configure_logging",
            variable_name="normalized_level",
        )
        registry = _log_level_values_from_purpose(
            _purpose_cell(REGISTRY_PATH, "KJ_ATLAS_LOG_LEVEL")
        )
        documentation = _log_level_values_from_purpose(
            _purpose_cell(CONFIG_PATH, "KJ_ATLAS_LOG_LEVEL")
        )
        self.assertEqual(registry, implementation)
        self.assertEqual(documentation, implementation)


if __name__ == "__main__":
    unittest.main()
