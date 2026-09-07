from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"
MAIN = ROOT / "03_Implement/backend/src/kj_atlas_api/main.py"
KEY = "KJ_ATLAS_API_KEY"


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


class ApiKeyEffectScopeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.configuration = CONFIGURATION.read_text(encoding="utf-8")
        self.main = MAIN.read_text(encoding="utf-8")

    def test_public_contract_matches_business_key_middleware_scope(self) -> None:
        expected_probes = ("/healthz", "/readyz", "/version")
        for surface in (self.registry, self.configuration):
            row = _row(surface, KEY)
            self.assertIn("business", row)
            for path in expected_probes:
                with self.subTest(surface="row", path=path):
                    self.assertIn(path, row)
            self.assertIn("/admin/*", row)
            self.assertIn("control-plane", row)

        self.assertIn(
            '_UNAUTHENTICATED_PATHS = frozenset({"/healthz", "/readyz", "/version"})',
            self.main,
        )
        self.assertIn(
            'if request.url.path in _UNAUTHENTICATED_PATHS or request.url.path.startswith("/admin/"):',
            self.main,
        )

    def test_user_facing_usage_section_does_not_claim_healthz_is_the_only_exception(self) -> None:
        section = self.configuration.split("## API キーを有効にする", 1)[1].split(
            "## local LLM を使う", 1
        )[0]
        for path in ("`/healthz`", "`/readyz`", "`/version`", "`/admin/*`"):
            with self.subTest(path=path):
                self.assertIn(path, section)
        self.assertIn("control-plane", section)
        self.assertNotIn("`/healthz` は API キーなしで確認できます。それ以外の API", section)


if __name__ == "__main__":
    unittest.main()
