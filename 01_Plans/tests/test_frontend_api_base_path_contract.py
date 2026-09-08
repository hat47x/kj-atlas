from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLIENT_PATH = ROOT / "03_Implement/frontend/src/api/client.ts"
ADMIN_CLIENT_PATH = ROOT / "03_Implement/frontend/src/admin/model_allowlist_api.ts"
HELPER_IMPORT = "resolveFrontendApiBase"
ENV_KEY = "import.meta.env.KJ_ATLAS_FRONTEND_API_BASE"


class FrontendApiBasePathContractTests(unittest.TestCase):
    def test_main_and_admin_clients_share_the_same_path_resolver(self) -> None:
        for path in (CLIENT_PATH, ADMIN_CLIENT_PATH):
            source = path.read_text(encoding="utf-8")
            self.assertIn(HELPER_IMPORT, source, f"shared API base resolver missing from {path}")
            self.assertIn(ENV_KEY, source, f"frontend API base env key missing from {path}")
            self.assertNotIn(
                "function resolveApiBase",
                source,
                f"duplicated local API base resolver reintroduced in {path}",
            )


if __name__ == "__main__":
    unittest.main()
