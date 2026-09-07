from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"
AUDIT = ROOT / "03_Implement/backend/src/kj_atlas_api/audit.py"
DOCS_ROUTE = ROOT / "03_Implement/backend/src/kj_atlas_api/routes/docs.py"
AI_ROUTE = ROOT / "03_Implement/backend/src/kj_atlas_api/routes/ai.py"


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


def _backend_registry_row(text: str, key: str) -> str:
    return _row(text.split("## Backend settings", 1)[1], key)


def _dispatcher_emit_dedup_calls(path: Path) -> list[ast.Call]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "emit":
            continue
        if any(keyword.arg == "dedup_key" for keyword in node.keywords):
            calls.append(node)
    return calls


class AuditTransportEffectScopeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.configuration = CONFIGURATION.read_text(encoding="utf-8")
        self.audit = AUDIT.read_text(encoding="utf-8")

    def _rows(self, key: str) -> tuple[str, str]:
        return (
            _backend_registry_row(self.registry, key),
            _row(self.configuration, key),
        )

    def test_public_rows_describe_export_enabled_as_master_gate(self) -> None:
        for row in self._rows("KJ_ATLAS_AUDIT_EXPORT_ENABLED"):
            self.assertIn("master gate", row)
            self.assertIn("NoopAuditTransport", row)
            self.assertIn("KJ_ATLAS_AUDIT_TRANSPORT", row)

    def test_transport_rows_make_http_activation_conditional_on_export_enabled(self) -> None:
        for row in self._rows("KJ_ATLAS_AUDIT_TRANSPORT"):
            self.assertIn("KJ_ATLAS_AUDIT_EXPORT_ENABLED=true", row)
            self.assertIn("NoopAuditTransport", row)
        registry_row = _backend_registry_row(self.registry, "KJ_ATLAS_AUDIT_TRANSPORT")
        self.assertNotIn("HTTP transport が選択されることをログで確認", registry_row)
        self.assertIn("test double", registry_row)

    def test_dispatcher_short_circuits_to_noop_before_http_selection_when_disabled(self) -> None:
        disabled = self.audit.index("if not enabled:")
        disabled_noop = self.audit.index("transport=NoopAuditTransport()", disabled)
        http_selection = self.audit.index('if settings.audit_transport == "http":', disabled_noop)
        http_transport = self.audit.index("transport: AuditTransport = HttpAuditTransport(", http_selection)
        self.assertLess(disabled, disabled_noop)
        self.assertLess(disabled_noop, http_selection)
        self.assertLess(http_selection, http_transport)

    def test_dedup_window_is_limited_to_context_and_export_audit_callsites(self) -> None:
        docs_dedup_calls = _dispatcher_emit_dedup_calls(DOCS_ROUTE)
        ai_dedup_calls = _dispatcher_emit_dedup_calls(AI_ROUTE)
        self.assertEqual(len(docs_dedup_calls), 2)
        self.assertEqual(len(ai_dedup_calls), 0)

        docs_source = DOCS_ROUTE.read_text(encoding="utf-8")
        dedup_sources = [ast.get_source_segment(docs_source, call) or "" for call in docs_dedup_calls]
        self.assertTrue(any('"context-audit"' in source for source in dedup_sources))
        self.assertTrue(any('"export-audit"' in source for source in dedup_sources))

        for row in self._rows("KJ_ATLAS_AUDIT_DEDUP_WINDOW_SECONDS"):
            self.assertIn("context-audit", row)
            self.assertIn("export-audit", row)
            self.assertIn("view", row)
            self.assertIn("LLM", row)
            self.assertIn("proposal", row)
            self.assertIn("適用しない", row)

    def test_queue_size_only_bounds_fail_open_retry_buffer(self) -> None:
        emit_body = self.audit.split("def emit(", 1)[1].split("def _flush_queue", 1)[0]
        send_call = emit_body.index("self._transport.send(event)")
        except_block = emit_body.index("except Exception as exc", send_call)
        enqueue = emit_body.index("self._enqueue(event, dedup_key)", except_block)
        success_return = emit_body.index("return AuditDispatchResult(sent=True)", enqueue)
        self.assertLess(send_call, except_block)
        self.assertLess(except_block, enqueue)
        self.assertLess(enqueue, success_return)

        for row in self._rows("KJ_ATLAS_AUDIT_QUEUE_SIZE"):
            self.assertIn("送信失敗", row)
            self.assertIn("fail-open", row)
            self.assertIn("retry", row)
            self.assertIn("正常送信", row)
            self.assertIn("export無効", row)


if __name__ == "__main__":
    unittest.main()
