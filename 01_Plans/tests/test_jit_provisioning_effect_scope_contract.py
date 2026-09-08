from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"
AUTH_CONTEXT = ROOT / "03_Implement/backend/src/kj_atlas_api/auth_context.py"
TRUSTED_AUTH_EDGE = ROOT / "03_Implement/backend/src/kj_atlas_api/trusted_auth_edge.py"
TRUSTED_SAAS_RUNTIME = ROOT / "03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py"
KEY = "KJ_ATLAS_ALLOW_JIT_PROVISIONING"


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


def _backend_registry_row(text: str, key: str) -> str:
    backend = text.split("## Backend settings", 1)[1]
    return _row(backend, key)


class JitProvisioningEffectScopeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.configuration = CONFIGURATION.read_text(encoding="utf-8")
        self.auth_context = AUTH_CONTEXT.read_text(encoding="utf-8")
        self.trusted_auth_edge = TRUSTED_AUTH_EDGE.read_text(encoding="utf-8")
        self.trusted_saas_runtime = TRUSTED_SAAS_RUNTIME.read_text(encoding="utf-8")

    def _public_rows(self) -> tuple[str, str]:
        return (
            _backend_registry_row(self.registry, KEY),
            _row(self.configuration, KEY),
        )

    def test_public_rows_limit_jit_to_single_tenant_header_identity(self) -> None:
        for row in self._public_rows():
            self.assertIn("single-tenant", row)
            self.assertIn("forwarded-header", row)
            self.assertIn("identity_not_provisioned", row)
            self.assertIn("saas-multitenant", row)
            self.assertIn("trusted JWT/cookie", row)

    def test_single_tenant_resolver_is_the_only_jit_consumer(self) -> None:
        self.assertIn("if identity is None:", self.auth_context)
        self.assertIn("if not settings.allow_jit_provisioning:", self.auth_context)
        self.assertIn('"code": "identity_not_provisioned"', self.auth_context)
        self.assertIn("user_id = str(uuid4())", self.auth_context)
        self.assertIn("ensure_local_default_membership(", self.auth_context)
        self.assertNotIn("allow_jit_provisioning", self.trusted_auth_edge)

    def test_saas_rejects_unprovisioned_identity_and_requires_jit_disabled(self) -> None:
        self.assertIn(
            'raise JwtIdentityError(status_code=403, code="identity_not_provisioned")',
            self.trusted_auth_edge,
        )
        self.assertIn(
            '(not self.allow_jit_provisioning, "disabled JIT provisioning")',
            self.trusted_saas_runtime,
        )


if __name__ == "__main__":
    unittest.main()
