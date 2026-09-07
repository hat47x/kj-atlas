from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG = ROOT / "04_Documentation/configuration.md"
TEST = ROOT / "01_Plans/tests/test_pdp_auth_metadata_scope_contract.py"


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
    "| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | `external_http` adapter の認証モード。`none`, `oidc`, `saml` | direct | 通常値 | 選択した認証 mode で PDP リクエストの認証ヘッダ形式が変わることを確認する（値は出力しない） |",
    "| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | `external_http` adapter がPDPへ渡す認証方式metadata。`none`, `oidc`, `saml` を `x-acl-auth-mode` headerへ写す。この値自体は `Authorization` headerを生成・変更せず、固定bearerは別設定 `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` が担う | direct | 通常値 | PDP test doubleで `x-acl-auth-mode` が設定値と一致することを確認する。`Authorization` はこの値だけでは付与されないことも確認する |",
)
replace_once(
    REGISTRY,
    "| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | 未設定 | `external_http` adapter に渡す IdP issuer | direct | 通常値 | OIDC/SAML 認証時に issuer 検証が設定値と一致することを確認する |",
    "| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | 未設定 | `external_http` adapter がPDPへ渡すIdP issuer metadata。canonical header valueとして検査し、設定時は `x-idp-issuer` headerへ写す。この設定自体はJWT/SAML issuerのローカル検証を行わない | direct | 通常値 | PDP test doubleで `x-idp-issuer` が設定値と一致することを確認する。issuer検証の結果を示すProbeとしては扱わない |",
)
replace_once(
    CONFIG,
    "| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | `none`, `oidc`, `saml` |",
    "| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | PDPへ渡す `x-acl-auth-mode` metadata。`none`, `oidc`, `saml`。この値自体は `Authorization` headerを生成・変更せず、固定bearerは `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` で別設定する |",
)
replace_once(
    CONFIG,
    "| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | 未設定 | `external_http` adapter で使う IdP issuer |",
    "| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | 未設定 | PDPへ `x-idp-issuer` として渡すIdP issuer metadata。canonical header valueとして検査するが、この設定自体はJWT/SAML issuerをローカル検証しない |",
)

TEST.write_text(
    '''from __future__ import annotations

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
''',
    encoding="utf-8",
)
