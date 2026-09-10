from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "03_Implement/backend/src/sui_sensemaking_api/audit.py"
AI_ROUTES = ROOT / "03_Implement/backend/src/sui_sensemaking_api/routes/ai.py"
DOC_ROUTES = ROOT / "03_Implement/backend/src/sui_sensemaking_api/routes/docs.py"
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"


def _function_source(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    node = next(
        item
        for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name
    )
    return "\n".join(lines[node.lineno - 1 : node.end_lineno])


def _build_event_safe_modes(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    result: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "build_event":
            continue
        event_node = next((kw.value for kw in node.keywords if kw.arg == "event_type"), None)
        safe_node = next((kw.value for kw in node.keywords if kw.arg == "safe_mode"), None)
        if event_node is None or safe_node is None:
            continue
        event = ast.get_source_segment(text, event_node)
        safe = ast.get_source_segment(text, safe_node)
        if event is not None and safe is not None:
            result.append((event, safe))
    return result


def _row(path: Path, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key} in {path}, got {len(rows)}")
    return rows[0]


class AuditSafeModeEventScopeContractTests(unittest.TestCase):
    def test_dispatcher_gates_event_flag_not_global_runtime_mode(self) -> None:
        source = _function_source(AUDIT, "emit")
        self.assertIn("event.safeMode and not self._allow_in_safe_mode", source)
        self.assertIn('reason="safe_mode_blocked"', source)

    def test_current_event_producers_keep_positive_and_negative_controls(self) -> None:
        ai_modes = _build_event_safe_modes(AI_ROUTES)
        docs_modes = _build_event_safe_modes(DOC_ROUTES)

        self.assertIn(('"llm"', "False"), ai_modes)
        self.assertGreaterEqual(ai_modes.count(('"proposal"', "False")), 2)
        self.assertIn(('"view"', "True"), docs_modes)
        self.assertIn(("payload.operation", "payload.safeMode"), docs_modes)
        self.assertIn(('"export"', "payload.safeMode"), docs_modes)

    def test_public_rows_describe_event_flag_scope_and_negative_controls(self) -> None:
        key = "SUI_AUDIT_ALLOW_IN_SAFE_MODE"
        for row in (_row(REGISTRY, key), _row(CONFIGURATION, key)):
            self.assertIn("AuditEvent.safeMode=true", row)
            self.assertIn("view", row)
            self.assertIn("context", row)
            self.assertIn("export", row)
            self.assertIn("LLM", row)
            self.assertIn("proposal", row)
            self.assertIn("対象外", row)


if __name__ == "__main__":
    unittest.main()
