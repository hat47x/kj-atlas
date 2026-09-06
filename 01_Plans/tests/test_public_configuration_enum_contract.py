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


def _rows_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path == REGISTRY_PATH:
        try:
            text = text.split("## Backend settings", 1)[1]
            text = text.split("## Compose and frontend build keys", 1)[0]
        except IndexError as exc:
            raise AssertionError("runtime registry Backend settings section is missing") from exc
    return text


def _row(path: Path, key: str) -> str:
    prefix = f"| `{key}` |"
    row = next(
        (line for line in _rows_text(path).splitlines() if line.startswith(prefix)),
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


def _code_tokens(text: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", text))


def _configuration_provider_values() -> set[str]:
    # The user-facing provider purpose cell is deliberately only the accepted list.
    return _code_tokens(_purpose_cell(CONFIG_PATH, "KJ_ATLAS_LLM_PROVIDER"))


def _configuration_log_level_values() -> set[str]:
    purpose = _purpose_cell(CONFIG_PATH, "KJ_ATLAS_LOG_LEVEL")
    match = re.search(r"OPS-OBSERV-01）。(?P<values>.*?)、未知値", purpose)
    if match is None:
        raise AssertionError("configuration LOG_LEVEL enum clause is missing")
    return _code_tokens(match.group("values"))


def _assert_registry_mentions_all(test: unittest.TestCase, key: str, values: set[str]) -> None:
    # The Backend settings purpose also carries runtime semantics, aliases,
    # probes, and fallback prose. Do not turn that prose into a second enum
    # grammar: require only that every implementation-accepted value remains
    # explicitly named in the authoritative Backend settings row.
    purpose = _purpose_cell(REGISTRY_PATH, key)
    for value in values:
        test.assertIn(f"`{value}`", purpose, f"registry omits {key} value: {value}")


class PublicConfigurationEnumContractTests(unittest.TestCase):
    def test_llm_provider_values_match_settings_and_registry(self) -> None:
        implementation = _literal_not_in_set(
            SETTINGS_PATH,
            function_name="validate_llm_provider_guards",
            variable_name="provider",
        )
        self.assertEqual(_configuration_provider_values(), implementation)
        _assert_registry_mentions_all(self, "KJ_ATLAS_LLM_PROVIDER", implementation)

    def test_log_level_values_match_logging_implementation_and_registry(self) -> None:
        implementation = _literal_not_in_set(
            OBSERVABILITY_PATH,
            function_name="configure_logging",
            variable_name="normalized_level",
        )
        self.assertEqual(_configuration_log_level_values(), implementation)
        _assert_registry_mentions_all(self, "KJ_ATLAS_LOG_LEVEL", implementation)


if __name__ == "__main__":
    unittest.main()
