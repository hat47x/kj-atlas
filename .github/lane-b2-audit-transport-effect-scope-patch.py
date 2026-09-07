from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG = ROOT / "04_Documentation/configuration.md"
TEST = ROOT / "01_Plans/tests/test_audit_transport_effect_scope_contract.py"


def replace_once(path: Path, old: str, new: str) -> None:
    raw = path.read_bytes()
    old_b = old.encode("utf-8")
    new_b = new.encode("utf-8")
    count = raw.count(old_b)
    if count != 1:
        raise SystemExit(f"expected one match in {path}, got {count}")
    path.write_bytes(raw.replace(old_b, new_b, 1))


replace_once(
    REGISTRY,
    "| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | audit event のHTTP連携を有効化する | direct | 通常値 | `true` 時に監査イベントが transport 経由で送出されること（内容は出力せず送信有無のみ確認） |",
    "| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | audit export のmaster gate。`false` では configured transport に関係なく dispatcher は無効化され `NoopAuditTransport` を使い、外部送信しない。`true` のときだけ `KJ_ATLAS_AUDIT_TRANSPORT` が実送信transportを選ぶ | direct | 通常値 | `false` ではtest doubleへ1件も到達しないこと、`true` + `http` では監査イベントがtest doubleへ到達することを確認する |",
)
replace_once(
    REGISTRY,
    "| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | audit transport。`noop` または `http` | direct | 通常値 | `http` 指定時に HTTP transport が選択されることをログで確認する |",
    "| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | audit transport。`noop` または `http`。実送信transportとして作用するのは `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true` の場合だけで、export無効時は `http` 指定でも dispatcher は `NoopAuditTransport` を使う | direct | 通常値 | transport名の正常時startup self-reportはない。`AUDIT_EXPORT_ENABLED=true` + `http` + test doubleでPOST到達を確認し、export無効時は到達しないことを確認する |",
)
replace_once(
    CONFIG,
    "| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | 監査イベントを HTTP の接続先に連携する |",
    "| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | audit export のmaster gate。`false` では transport 設定に関係なく外部送信せず `NoopAuditTransport` を使う。`true` のときだけ `KJ_ATLAS_AUDIT_TRANSPORT` が実送信transportを選ぶ |",
)
replace_once(
    CONFIG,
    "| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | `noop` または `http` |",
    "| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | `noop` または `http`。`http` が実送信に使われるのは `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true` の場合だけ。export無効時は `http` 指定でも dispatcher は `NoopAuditTransport` を使う |",
)

TEST.write_text(
    '''from __future__ import annotations

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
''',
    encoding="utf-8",
)
