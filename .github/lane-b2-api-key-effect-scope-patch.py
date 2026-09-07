from pathlib import Path

REGISTRY = Path('02_Architecture/runtime_parameter_registry.md')
CONFIG = Path('04_Documentation/configuration.md')
TEST = Path('01_Plans/tests/test_api_key_effect_scope_contract.py')


def replace_text_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, got {count}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


def replace_bytes_once(path: Path, old: str, new: str, label: str) -> None:
    raw = path.read_bytes()
    old_b = old.encode('utf-8')
    new_b = new.encode('utf-8')
    count = raw.count(old_b)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, got {count}')
    path.write_bytes(raw.replace(old_b, new_b, 1))


replace_text_once(
    REGISTRY,
    '| `KJ_ATLAS_API_KEY` | 未設定 | `/healthz` 以外の API を `X-API-Key` で保護する | direct / base Compose | 秘密値 | 未設定時は `/healthz` 以外も無防備。設定時: キーなしは 401、正しい `X-API-Key` は成功、誤ったキーも 401（値自体は出力しない） |',
    '| `KJ_ATLAS_API_KEY` | 未設定 | business-plane APIを `X-API-Key` で保護する。`/healthz` / `/readyz` / `/version` は運用probeとして常に対象外。`/admin/*` もbusiness keyの対象外で、`X-Admin-Api-Key` またはprovision capabilityによるcontrol-plane認可へ分離する | direct / base Compose | 秘密値 | business-plane routeでキーなし/誤りが401、正しいキーが成功すること。3つの運用probeはキーなしで到達でき、`/admin/*` はbusiness keyではなくcontrol-plane資格情報で認可されることを確認する |',
    'registry API_KEY row',
)

replace_bytes_once(
    CONFIG,
    '| `KJ_ATLAS_API_KEY` | 未設定 | `/healthz` 以外の API を `X-API-Key` で保護 |',
    '| `KJ_ATLAS_API_KEY` | 未設定 | business-plane APIを `X-API-Key` で保護。`/healthz` / `/readyz` / `/version` は運用probeとして対象外。`/admin/*` もbusiness key対象外で、別のcontrol-plane認可（`X-Admin-Api-Key` / provision capability）を使う |',
    'configuration API_KEY row',
)
replace_bytes_once(
    CONFIG,
    '`/healthz` は API キーなしで確認できます。それ以外の API には次のヘッダーを付けます。',
    '`/healthz` / `/readyz` / `/version` は運用probeとして API キーなしで確認できます。`/admin/*` はbusiness API keyでは保護せず、`X-Admin-Api-Key` またはprovision capabilityによるcontrol-plane認可を使います。それ以外のbusiness-plane APIへアクセスする場合は次のヘッダーを付けます。',
    'configuration API key usage paragraph',
)

TEST.write_text(
    '''from __future__ import annotations

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
''',
    encoding='utf-8',
)
