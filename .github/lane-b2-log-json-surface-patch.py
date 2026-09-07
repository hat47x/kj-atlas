from pathlib import Path

REGISTRY = Path("02_Architecture/runtime_parameter_registry.md")
CONFIG = Path("04_Documentation/configuration.md")
OBSERVABILITY_DOC = Path("04_Documentation/observability.md")
TEST = Path("01_Plans/tests/test_log_json_observability_surface_contract.py")


def replace_bytes_once(path: Path, old: str, new: str, label: str) -> None:
    raw = path.read_bytes()
    old_b = old.encode("utf-8")
    new_b = new.encode("utf-8")
    count = raw.count(old_b)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, got {count}")
    path.write_bytes(raw.replace(old_b, new_b, 1))


replace_bytes_once(
    REGISTRY,
    "| `KJ_ATLAS_LOG_JSON` | `true` | OPS-OBSERV-01: ログを1行1JSONで出力する。`extra={...}` で渡される `tenantId` / `docId` / `requestId` / LLM `trace_id` はこの経路でのみ出力される（`false` の場合も `requestId` は人間可読書式に含む） | direct | 通常値 | 出力行が JSON として解析でき、`requestId` フィールドを持つことを確認する |",
    "| `KJ_ATLAS_LOG_JSON` | `true` | OPS-OBSERV-01: ログを1行1JSONで出力する。`true` では caller-supplied `extra={...}` の `tenantId` / `docId` / `queueLength` / LLM `trace_id` などを構造化fieldとして出力する。`false` ではこれらextra fieldは出力せず、人間可読書式に correlation metadata の `requestId` / `actorRefHash` / `appRevision` を残す | direct | 通常値 | `true` でextra fieldがJSON fieldとして出ること、`false` で `requestId` / `actorRefHash` / `appRevision` が人間可読書式に残ることを確認する |",
    "registry LOG_JSON row",
)

replace_bytes_once(
    CONFIG,
    "| `KJ_ATLAS_LOG_JSON` | `true` | ログを1行1JSONで出力。`tenantId` / `docId` / `requestId` はこの経路で出力される（OPS-OBSERV-01） |",
    "| `KJ_ATLAS_LOG_JSON` | `true` | 既定は1行1JSON。`true` では `extra={...}` の `tenantId` / `docId` / `queueLength` / LLM `trace_id` などを構造化fieldとして出力する。`false` ではこれらextra fieldは出力せず、人間可読書式に `requestId` / `actorRefHash` / `appRevision` を残す（OPS-OBSERV-01） |",
    "configuration LOG_JSON row",
)

replace_bytes_once(
    OBSERVABILITY_DOC,
    "出力レベルは `KJ_ATLAS_LOG_LEVEL` で変更します。`KJ_ATLAS_LOG_JSON=false` にすると人間可読の1行書式になり、`requestId` は角括弧内に出ます。",
    "出力レベルは `KJ_ATLAS_LOG_LEVEL` で変更します。`KJ_ATLAS_LOG_JSON=false` にすると人間可読の1行書式になり、correlation metadata の `requestId` / `actorRefHash` / `appRevision` は残ります。一方、`tenantId` / `docId` / `queueLength` / LLM `trace_id` など caller-supplied `extra={...}` のfieldは人間可読formatterでは出力しません。これらの構造化fieldが必要な運用ではJSON出力を維持してください。",
    "observability human-readable paragraph",
)

TEST.write_text(
    '''from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"
OBSERVABILITY_DOC = ROOT / "04_Documentation/observability.md"
OBSERVABILITY_SOURCE = ROOT / "03_Implement/backend/src/kj_atlas_api/observability.py"
KEY = "KJ_ATLAS_LOG_JSON"


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


class LogJsonObservabilitySurfaceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.configuration = CONFIGURATION.read_text(encoding="utf-8")
        self.observability_doc = OBSERVABILITY_DOC.read_text(encoding="utf-8")
        self.source = OBSERVABILITY_SOURCE.read_text(encoding="utf-8")

    def test_public_rows_distinguish_structured_extra_from_correlation_metadata(self) -> None:
        for surface in (self.registry, self.configuration):
            row = _row(surface, KEY)
            for extra_field in ("tenantId", "docId", "queueLength", "trace_id"):
                with self.subTest(surface="public-row", extra_field=extra_field):
                    self.assertIn(extra_field, row)
            for correlation_field in ("requestId", "actorRefHash", "appRevision"):
                with self.subTest(surface="public-row", correlation_field=correlation_field):
                    self.assertIn(correlation_field, row)
            self.assertIn("`false`", row)
            self.assertIn("人間可読", row)

    def test_human_readable_contract_matches_formatter_scope(self) -> None:
        human_section = self.source.split("if json_format:", 1)[1].split(
            "logging.config.dictConfig", 1
        )[0]
        for field in ("requestId", "actorRefHash", "appRevision"):
            with self.subTest(field=field):
                self.assertIn(f"%({field})s", human_section)
        for extra_field in ("tenantId", "docId", "queueLength", "trace_id"):
            with self.subTest(extra_field=extra_field):
                self.assertNotIn(f"%({extra_field})s", human_section)

        self.assertIn("for key, value in record.__dict__.items():", self.source)
        for phrase in (
            "`requestId` / `actorRefHash` / `appRevision` は残ります",
            "caller-supplied `extra={...}` のfieldは人間可読formatterでは出力しません",
        ):
            self.assertIn(phrase, self.observability_doc)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)
