from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "04_Documentation/configuration.md"
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
PROVIDER = ROOT / "03_Implement/backend/src/kj_atlas_api/llm/provider.py"
KEY = "KJ_ATLAS_LLM_HIGH_REASONING_MODEL"


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
        raise AssertionError(f"expected one backend registry row for {key}, got {len(rows)}")
    return rows[0]


def _documented_tasks(row: str) -> set[str]:
    match = re.search(r"final_judgement系タスク（([^）]+)）", row)
    if match is None:
        raise AssertionError("final_judgement task clause not found")
    return {item.strip() for item in match.group(1).split("/") if item.strip()}


def _runtime_tasks(source: str) -> set[str]:
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "_FINAL_JUDGEMENT_TASKS" for target in node.targets):
            continue
        value = node.value
        if not isinstance(value, ast.Call) or not value.args:
            raise AssertionError("_FINAL_JUDGEMENT_TASKS must remain a literal frozenset call")
        literal = value.args[0]
        if not isinstance(literal, (ast.Set, ast.List, ast.Tuple)):
            raise AssertionError("_FINAL_JUDGEMENT_TASKS must contain a literal collection")
        tasks: set[str] = set()
        for element in literal.elts:
            if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                raise AssertionError("_FINAL_JUDGEMENT_TASKS contains a non-literal task")
            tasks.add(element.value)
        return tasks
    raise AssertionError("_FINAL_JUDGEMENT_TASKS assignment not found")


class HighReasoningTaskScopeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = CONFIG.read_text(encoding="utf-8")
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.provider = PROVIDER.read_text(encoding="utf-8")

    def test_public_configuration_matches_runtime_final_judgement_task_set(self) -> None:
        runtime = _runtime_tasks(self.provider)
        documented = _documented_tasks(_row(self.config, KEY))
        self.assertEqual(documented, runtime)
        self.assertEqual(runtime, {"check_narrative", "detect_contradiction"})

    def test_runtime_registry_names_the_same_task_set(self) -> None:
        runtime = _runtime_tasks(self.provider)
        documented = _documented_tasks(_backend_registry_row(self.registry, KEY))
        self.assertEqual(documented, runtime)

    def test_removed_non_runtime_task_is_not_advertised(self) -> None:
        self.assertNotIn("assess_card_importance", _row(self.config, KEY))


if __name__ == "__main__":
    unittest.main()
