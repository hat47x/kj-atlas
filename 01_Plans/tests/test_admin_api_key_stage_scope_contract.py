from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"
CONTROL_PLANE_AUTH = ROOT / "03_Implement/backend/src/kj_atlas_api/control_plane_auth.py"
KEY = "KJ_ATLAS_ADMIN_API_KEY"


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


def _backend_registry_row(text: str, key: str) -> str:
    backend = text.split("## Backend settings", 1)[1]
    return _row(backend, key)


class AdminApiKeyStageScopeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.configuration = CONFIGURATION.read_text(encoding="utf-8")
        self.auth = CONTROL_PLANE_AUTH.read_text(encoding="utf-8")

    def _public_rows(self) -> tuple[str, str]:
        return (
            _backend_registry_row(self.registry, KEY),
            _row(self.configuration, KEY),
        )

    def test_public_rows_describe_both_control_plane_authorization_stages(self) -> None:
        for row in self._public_rows():
            self.assertIn("Stage A", row)
            self.assertIn("X-Admin-Api-Key", row)
            self.assertIn("Stage B", row)
            self.assertIn("tenant.provision", row)
            self.assertIn("KJ_ATLAS_API_KEY", row)
            self.assertIn("enterprise-production", row)
            self.assertIn("saas-multitenant", row)
            self.assertIn("local-dev", row)
            self.assertIn("evaluation", row)

    def test_rows_match_implemented_stage_a_and_stage_b_inputs(self) -> None:
        self.assertIn('ADMIN_API_KEY_HEADER = "x-admin-api-key"', self.auth)
        self.assertIn('TENANT_PROVISION_CAPABILITY = "tenant.provision"', self.auth)
        self.assertIn("if _matches_admin_bearer(request):", self.auth)
        self.assertIn(
            "if TENANT_PROVISION_CAPABILITY in trusted_session.session.effective_capabilities:",
            self.auth,
        )

    def test_development_open_exception_is_explicit_and_narrow(self) -> None:
        self.assertIn(
            '_OPEN_WHEN_UNCONFIGURED_PROFILES = frozenset({"local-dev", "evaluation"})',
            self.auth,
        )
        self.assertIn(
            "if settings.admin_api_key is None and profile in _OPEN_WHEN_UNCONFIGURED_PROFILES:",
            self.auth,
        )
        for row in self._public_rows():
            self.assertIn("未設定時", row)
            self.assertIn("development", row)


if __name__ == "__main__":
    unittest.main()
