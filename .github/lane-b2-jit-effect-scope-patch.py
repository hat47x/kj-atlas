from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG = ROOT / "04_Documentation/configuration.md"
TEST = ROOT / "01_Plans/tests/test_jit_provisioning_effect_scope_contract.py"


def replace_once(path: Path, old: str, new: str) -> None:
    raw = path.read_bytes()
    old_b = old.encode("utf-8")
    new_b = new.encode("utf-8")
    count = raw.count(old_b)
    if count != 1:
        raise SystemExit(f"expected one match in {path}, got {count}")
    path.write_bytes(raw.replace(old_b, new_b, 1))


replace_once(
    REGISTRY,
    "| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `false` | 未登録 identity の JIT provisioning を許可する（SEC-RATE-LIMIT-01: 既定 fail-closed） | direct / base Compose | 通常値 | `false` 時、未登録 identity でのアクセスが拒否され新規作成されないことを確認する |",
    "| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `false` | single-tenant の forwarded-header identity path にだけ作用するJIT provisioning gate。未登録 provider/subject で `true` の場合は user・identity binding・local-default membership を作成し、`false` では 403 `identity_not_provisioned`。`saas-multitenant` は起動policyで `false` を必須とし、trusted JWT/cookie identity resolver はこの設定を参照せず未登録subjectを常に403で拒否する（SEC-RATE-LIMIT-01） | direct / base Compose | 通常値 | single-tenant header pathで `false` 時は未登録identityが403かつ新規作成されず、`true` 時だけ作成されること。SaaSでは `true` が起動拒否され、未登録subjectが設定値に関係なく403になることを確認する |",
)

replace_once(
    CONFIG,
    "| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `false` | 未登録 identity の JIT provisioning を許可（既定は fail-closed。SEC-RATE-LIMIT-01・2026-08-13 変更） |",
    "| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `false` | single-tenant の forwarded-header identity path でだけ未登録identityのJIT provisioningを許可する。`true` なら user・identity binding・local-default membershipを作成し、`false` なら403 `identity_not_provisioned`。`saas-multitenant` は起動時に `false` が必須で、trusted JWT/cookie pathはこの設定に関係なく未登録subjectを403で拒否する（SEC-RATE-LIMIT-01・2026-08-13変更） |",
)

TEST.write_text(
    '''from __future__ import annotations

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
''',
    encoding="utf-8",
)
