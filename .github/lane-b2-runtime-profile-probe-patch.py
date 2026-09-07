from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
TEST = ROOT / "01_Plans/tests/test_runtime_profile_probe_contract.py"

old = "| `KJ_ATLAS_RUNTIME_PROFILE` | `local-dev` | Backend/MCPの実行profile。`local-dev`, `evaluation`, `enterprise-production`, `saas-multitenant`を受理する。SaaS backendはPostgreSQL共有認証表と必須policyを検査し、不足時は起動拒否。 | direct / base Compose | 通常値 | 起動ログまたは `/healthz` で profile 名（値のみ）を確認する |"
new = "| `KJ_ATLAS_RUNTIME_PROFILE` | `local-dev` | Backend/MCPの実行profile。`local-dev`, `evaluation`, `enterprise-production`, `saas-multitenant`を受理する。SaaS backendはPostgreSQL共有認証表と必須policyを検査し、不足時は起動拒否。 | direct / base Compose | 通常値 | `GET /version` の `runtimeProfile` が設定後のvalidated profileと一致することを確認する。`/healthz` はliveness-onlyでprofileを返さない |"
raw = REGISTRY.read_bytes()
if raw.count(old.encode()) != 1:
    raise SystemExit("expected exactly one runtime-profile backend row")
REGISTRY.write_bytes(raw.replace(old.encode(), new.encode(), 1))

TEST.write_text('''from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
MAIN = ROOT / "03_Implement/backend/src/kj_atlas_api/main.py"
KEY = "KJ_ATLAS_RUNTIME_PROFILE"


def _backend_row(text: str, key: str) -> str:
    backend_tail = text.split("## Backend settings", 1)[1]
    backend = backend_tail.split("\n## ", 1)[0]
    prefix = f"| `{key}` |"
    rows = [line for line in backend.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one backend row for {key}, got {len(rows)}")
    return rows[0]


class RuntimeProfileProbeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.main = MAIN.read_text(encoding="utf-8")

    def test_registry_uses_version_runtime_profile_as_the_probe(self) -> None:
        row = _backend_row(self.registry, KEY)
        self.assertIn("GET /version", row)
        self.assertIn("runtimeProfile", row)
        self.assertIn("validated profile", row)
        self.assertNotIn("起動ログまたは `/healthz`", row)

    def test_version_exposes_exact_runtime_profile(self) -> None:
        self.assertIn('@app.get("/version")', self.main)
        self.assertIn('"runtimeProfile": app.state.runtime_profile', self.main)
        self.assertIn("else settings.runtime_profile", self.main)

    def test_healthz_remains_liveness_only_without_profile_data(self) -> None:
        health_start = self.main.index('@app.get("/healthz")')
        ready_start = self.main.index('@app.get("/readyz")', health_start)
        health = self.main[health_start:ready_start]
        self.assertIn('return {"status": "ok"}', health)
        self.assertNotIn("runtimeProfile", health)
        self.assertNotIn("runtime_profile", health)


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")
