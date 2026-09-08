from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
MAIN = ROOT / "03_Implement/backend/src/kj_atlas_api/main.py"
KEY = "KJ_ATLAS_DATABASE_URL"


def _backend_row(text: str, key: str) -> str:
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
        raise AssertionError(f"expected one backend row for {key}, got {len(rows)}")
    return rows[0]


class DatabaseReadyProbeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.main = MAIN.read_text(encoding="utf-8")

    def test_registry_uses_readyz_for_database_and_schema_readiness(self) -> None:
        row = _backend_row(self.registry, KEY)
        self.assertIn("GET /readyz", row)
        self.assertIn("checks.database=ok", row)
        self.assertIn("checks.schema=ok", row)
        self.assertIn("liveness-only", row)
        self.assertNotIn("`/healthz` が 200", row)

    def test_readyz_checks_database_reachability_and_schema_head(self) -> None:
        ready_start = self.main.index('@app.get("/readyz")')
        version_start = self.main.index('@app.get("/version")', ready_start)
        ready = self.main[ready_start:version_start]
        self.assertIn('session.execute(text("SELECT 1"))', ready)
        self.assertIn('checks["database"] = "ok"', ready)
        self.assertIn('SELECT version_num FROM alembic_version', ready)
        self.assertIn('checks["schema"] = "ok"', ready)
        self.assertIn('status_code=200 if ready else 503', ready)

    def test_healthz_remains_liveness_only_without_database_access(self) -> None:
        health_start = self.main.index('@app.get("/healthz")')
        ready_start = self.main.index('@app.get("/readyz")', health_start)
        health = self.main[health_start:ready_start]
        self.assertIn('return {"status": "ok"}', health)
        self.assertNotIn("SessionLocal()", health)
        self.assertNotIn('session.execute(text("SELECT 1"))', health)


if __name__ == "__main__":
    unittest.main()
