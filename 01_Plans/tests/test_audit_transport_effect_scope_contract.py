from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"
AUDIT = ROOT / "03_Implement/backend/src/kj_atlas_api/audit.py"


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


def _backend_registry_row(text: str, key: str) -> str:
    return _row(text.split("## Backend settings", 1)[1], key)


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


if __name__ == "__main__":
    unittest.main()
