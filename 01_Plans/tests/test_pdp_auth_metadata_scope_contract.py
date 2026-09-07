from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"
ACCESS_CONTROL = ROOT / "03_Implement/backend/src/kj_atlas_api/access_control.py"
SETTINGS = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


def _backend_registry_row(text: str, key: str) -> str:
    return _row(text.split("## Backend settings", 1)[1], key)


class PdpAuthMetadataScopeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.configuration = CONFIGURATION.read_text(encoding="utf-8")
        self.access_control = ACCESS_CONTROL.read_text(encoding="utf-8")
        self.settings = SETTINGS.read_text(encoding="utf-8")

    def _rows(self, key: str) -> tuple[str, str]:
        return (
            _backend_registry_row(self.registry, key),
            _row(self.configuration, key),
        )

    def test_auth_mode_is_documented_as_pdp_metadata_not_authorization_generation(self) -> None:
        key = "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE"
        for row in self._rows(key):
            self.assertIn("x-acl-auth-mode", row)
            self.assertIn("Authorization", row)
            self.assertIn("STATIC_BEARER_TOKEN", row)
        self.assertIn('"x-acl-auth-mode": self._config.auth_mode', self.access_control)
        self.assertIn('headers["authorization"] = f"Bearer {self._config.static_bearer_token}"', self.access_control)

    def test_idp_issuer_is_forwarded_metadata_not_local_issuer_verification(self) -> None:
        key = "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER"
        for row in self._rows(key):
            self.assertIn("x-idp-issuer", row)
            self.assertIn("ローカル検証", row)
        registry_row = _backend_registry_row(self.registry, key)
        self.assertNotIn("issuer 検証が設定値と一致", registry_row)
        self.assertIn('headers["x-idp-issuer"] = self._config.idp_issuer', self.access_control)
        self.assertIn("_validate_optional_header_value(", self.settings)
        self.assertIn('value_key="KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER"', self.settings)


if __name__ == "__main__":
    unittest.main()
