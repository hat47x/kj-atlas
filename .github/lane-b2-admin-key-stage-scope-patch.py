from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG = ROOT / "04_Documentation/configuration.md"
TEST = ROOT / "01_Plans/tests/test_admin_api_key_stage_scope_contract.py"


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
    "| `KJ_ATLAS_ADMIN_API_KEY` | 未設定 | ADR-0072 D1=A: 管理面（`/admin/provision/**`）専用の制御プレーン資格情報。`X-Admin-Api-Key` で提示する。**業務面の `KJ_ATLAS_API_KEY` は管理面へ到達できず、同じ秘密値の設定も起動時に拒否する**。IdP未登録状態（bootstrap）で使える唯一の経路 | direct | 秘密値 | 業務面キーで `/admin/provision/*` が 401 になること、正しい `X-Admin-Api-Key` が成功すること、両キー同値でSettings構築が失敗することを確認する（値自体は出力しない） |",
    "| `KJ_ATLAS_ADMIN_API_KEY` | 未設定 | ADR-0072 D1=A+B: control-plane の Stage A bootstrap 資格情報。`X-Admin-Api-Key` で提示する。Stage B では trusted SaaS session の `tenant.provision` capability でも認可でき、request に admin bearer は不要。**業務面の `KJ_ATLAS_API_KEY` はどちらの Stage でも受理せず、同じ秘密値の設定も起動時に拒否する**。`enterprise-production` / `saas-multitenant` では設定自体が起動必須。`local-dev` / `evaluation` では未設定時だけ development 用に control plane を開く。IdP未登録 bootstrap では Stage B を使えないため Stage A が production の経路 | direct | 秘密値 | 業務面キーで `/admin/provision/*` が 401、正しい `X-Admin-Api-Key` が成功、trusted SaaS session + `tenant.provision` も admin bearer なしで成功することを確認する。併せて両キー同値がSettings構築で拒否されることを確認する（秘密値自体は出力しない） |",
)

replace_once(
    CONFIG,
    "| `KJ_ATLAS_ADMIN_API_KEY` | 未設定 | 管理面（`/admin/provision/**`）を `X-Admin-Api-Key` で保護。業務面キーでは到達不可。`KJ_ATLAS_API_KEY`と同じ値は起動時に拒否。`enterprise-production` / `saas-multitenant` では**必須**（未設定なら起動しない） |",
    "| `KJ_ATLAS_ADMIN_API_KEY` | 未設定 | control-plane の Stage A bootstrap 資格情報。`X-Admin-Api-Key` で提示する。Stage B では trusted SaaS session の `tenant.provision` capability でも `/admin/provision/**` を認可でき、request に admin bearer は不要。業務面 `KJ_ATLAS_API_KEY` は管理面で受理しない。`enterprise-production` / `saas-multitenant` では設定自体が**必須**（未設定なら起動しない）。`local-dev` / `evaluation` は admin key 未設定時だけ development 用に管理面を開く |",
)

TEST.write_text(
    '''from __future__ import annotations

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


class AdminApiKeyStageScopeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.configuration = CONFIGURATION.read_text(encoding="utf-8")
        self.auth = CONTROL_PLANE_AUTH.read_text(encoding="utf-8")

    def test_public_rows_describe_both_control_plane_authorization_stages(self) -> None:
        for surface in (self.registry, self.configuration):
            row = _row(surface, KEY)
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
        for surface in (self.registry, self.configuration):
            row = _row(surface, KEY)
            self.assertIn("未設定時", row)
            self.assertIn("development", row)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)
