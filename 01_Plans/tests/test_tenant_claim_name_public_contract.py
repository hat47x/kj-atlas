from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / '03_Implement/backend/src/kj_atlas_api/settings.py'
AUTH_EDGE = ROOT / '03_Implement/backend/src/kj_atlas_api/trusted_auth_edge.py'
RUNTIME = ROOT / '03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py'
CONFIG = ROOT / '04_Documentation/configuration.md'
REGISTRY = ROOT / '02_Architecture/runtime_parameter_registry.md'


class TenantClaimNamePublicContractTest(unittest.TestCase):
    def test_settings_default_is_not_runtime_fixed_requirement(self) -> None:
        settings = SETTINGS.read_text(encoding='utf-8')
        self.assertIn('default="tenant_ref"', settings)
        self.assertIn('KJ_ATLAS_TENANT_CLAIM_NAME must not be empty', settings)
        self.assertIn('KJ_ATLAS_TENANT_CLAIM_NAME must be ≤ 256 characters', settings)
        self.assertIn('KJ_ATLAS_TENANT_CLAIM_NAME must not have leading/trailing whitespace', settings)
        self.assertIn('KJ_ATLAS_TENANT_CLAIM_NAME must not contain spaces', settings)

        runtime_source = RUNTIME.read_text(encoding='utf-8')
        self.assertIn('(bool(self.tenant_claim_name.strip()), "tenant claim name set")', runtime_source)
        self.assertNotIn('self.tenant_claim_name == "tenant_ref"', runtime_source)

    def test_auth_edge_reads_configured_claim_name(self) -> None:
        edge = AUTH_EDGE.read_text(encoding='utf-8')
        self.assertIn('tenant_claim_name = settings.tenant_claim_name', edge)
        self.assertIn('verified_claims.get(tenant_claim_name)', edge)

    def test_public_surfaces_distinguish_default_from_requirement(self) -> None:
        registry = REGISTRY.read_text(encoding='utf-8')
        config = CONFIG.read_text(encoding='utf-8')
        self.assertNotIn('`KJ_ATLAS_TENANT_CLAIM_NAME=tenant_ref`', registry)
        self.assertIn('未指定は既定 `tenant_ref`', registry)
        self.assertIn('固定名ではなく', registry)
        self.assertIn('`tenant_ref` は既定値で固定名ではない', config)
        self.assertIn('カスタム名を指定でき', config)


if __name__ == '__main__':
    unittest.main()
