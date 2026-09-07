from __future__ import annotations

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
