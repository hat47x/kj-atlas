from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
AUDIT_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/audit.py"
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"


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


class AuditExportValidationContractTests(unittest.TestCase):
    def test_http_transport_validation_is_independent_of_export_dispatch_gate(self) -> None:
        settings_validator = _function_source(SETTINGS_PATH, "validate_llm_provider_guards")
        self.assertIn('enabled=normalized_audit_transport == "http"', settings_validator)

        factory = _function_source(AUDIT_PATH, "build_audit_dispatcher")
        endpoint_guard = 'if settings.audit_transport == "http" and endpoint is None:'
        disabled_guard = "if not enabled:"
        self.assertIn(endpoint_guard, factory)
        self.assertIn(disabled_guard, factory)
        self.assertLess(factory.index(endpoint_guard), factory.index(disabled_guard))

    def test_public_docs_distinguish_validation_from_external_dispatch(self) -> None:
        for path in (REGISTRY_PATH, CONFIG_PATH):
            export_row = _public_row(path, "KJ_ATLAS_AUDIT_EXPORT_ENABLED")
            transport_row = _public_row(path, "KJ_ATLAS_AUDIT_TRANSPORT")

            self.assertIn("外部送信", export_row)
            self.assertIn("NoopAuditTransport", export_row)
            self.assertIn("false", export_row)
            self.assertIn("http", export_row)
            self.assertIn("endpoint", export_row)
            self.assertTrue("validation" in export_row or "検証" in export_row)

            self.assertIn("http", transport_row)
            self.assertIn("endpoint", transport_row)
            self.assertIn("false", transport_row)
            self.assertIn("NoopAuditTransport", transport_row)
            self.assertTrue("validation" in transport_row or "検証" in transport_row)


if __name__ == "__main__":
    unittest.main()
