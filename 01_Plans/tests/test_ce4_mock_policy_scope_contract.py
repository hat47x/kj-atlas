from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG = ROOT / "04_Documentation/configuration.md"
DOCS_ROUTE = ROOT / "03_Implement/backend/src/kj_atlas_api/routes/docs.py"
CONTEXT_ROUTE = ROOT / "03_Implement/backend/src/kj_atlas_api/routes/context.py"
KEY = "KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK"
ATTR = "ce4_source_bundle_hash_allow_mock"


def _row(path: Path) -> str:
    prefix = f"| `{KEY}` |"
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {KEY} in {path}, got {len(rows)}")
    return rows[0]


class Ce4MockPolicyScopeContractTests(unittest.TestCase):
    def test_public_contract_names_docs_context_audit_scope(self) -> None:
        for row in (_row(REGISTRY), _row(CONFIG)):
            self.assertIn("/docs/{doc_id}/context-audit", row)
            self.assertIn("proposal", row)
            self.assertIn("CE4 resolve", row)
            self.assertIn("対象外", row)

    def test_runtime_policy_is_owned_by_docs_ce4_context_audit(self) -> None:
        docs_route = DOCS_ROUTE.read_text(encoding="utf-8")
        context_route = CONTEXT_ROUTE.read_text(encoding="utf-8")

        self.assertIn(f"settings.{ATTR}", docs_route)
        self.assertIn("mock_source_bundle_hash_disabled", docs_route)
        self.assertNotIn(ATTR, context_route)


if __name__ == "__main__":
    unittest.main()
