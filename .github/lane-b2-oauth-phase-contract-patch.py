from pathlib import Path

REGISTRY = Path('02_Architecture/runtime_parameter_registry.md')
CONFIG = Path('04_Documentation/configuration.md')
TEST = Path('01_Plans/tests/test_production_profile_required_settings_contract.py')

registry = REGISTRY.read_text(encoding='utf-8')
replacements = {
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT` | 未設定 | BFF が authorization code を token へ交換する IdP の token endpoint（ADR-0074）。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可 | direct | 通常値（接続先URL。認証情報は別キー） | token 交換リクエストが正しい endpoint へ送信されることを確認する |':
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT` | 未設定 | BFF が authorization code を token へ交換する IdP の token endpoint（ADR-0074）。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可。process startup hard gateではないが、`/session/callback` の code 交換では redirect URI / client ID / client secret と4項目完全セットで必要で、欠損時は503でfail-closed | direct | 通常値（接続先URL。認証情報は別キー） | token 交換リクエストが正しい endpoint へ送信されること、欠損時にcallbackが503になることを確認する |',
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI` | 未設定 | OAuth フローの redirect URI（ADR-0074）。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可し、path は `/session/callback` 固定 | direct | 通常値（接続先URL。認証情報は別キー） | フロー完了後のリダイレクト先が設定値と一致することを確認する |':
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI` | 未設定 | OAuth フローの redirect URI（ADR-0074）。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可し、path は `/session/callback` 固定。process startup hard gateではないが、`/session/login` 開始時は client ID とともに必要で、callbackの code 交換では token endpoint / client ID / client secret と4項目完全セットで必要。欠損時は該当requestを503でfail-closed | direct | 通常値（接続先URL。認証情報は別キー） | login開始とcallback code交換で設定値が使われ、欠損時に該当requestが503になることを確認する |',
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID` | 未設定 | confidential-client OAuth の client ID（ADR-0074） | direct | 通常値 | 認可リクエストの client_id が設定値と一致することを確認する |':
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID` | 未設定 | confidential-client OAuth の client ID（ADR-0074）。process startup hard gateではないが、`/session/login` 開始時は redirect URI とともに必要で、callbackの code 交換では token endpoint / redirect URI / client secret と4項目完全セットで必要。欠損時は該当requestを503でfail-closed | direct | 通常値 | 認可リクエストの client_id が設定値と一致し、欠損時に該当requestが503になることを確認する |',
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET` | 未設定 | confidential-client OAuth の client secret（ADR-0074） | direct | 秘密値 | 設定後、token 交換が成功することを確認する（値自体は出力しない） |':
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET` | 未設定 | confidential-client OAuth の client secret（ADR-0074）。process startup hard gateではないが、`/session/callback` の code 交換では token endpoint / redirect URI / client ID と4項目完全セットで必要で、欠損時は503でfail-closed | direct | 秘密値 | 設定後にtoken交換が成功し、欠損時にcallbackが503になることを確認する（値自体は出力しない） |',
    'OAuth callback利用時必須: `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET`':
    'OAuth BFF request時の条件付き設定: `/session/login` 開始には `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID`。`/session/callback` の code 交換には `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET` の4項目完全セット':
    'callback用4項目の欠損は起動拒否ではなくcallbackを503でfail-closedする。':
    'これらはprocess startup hard gateではない。login開始用2項目の欠損は`/session/login`を503、callback用4項目の欠損は`/session/callback`を503でfail-closedする。',
}
for old, new in replacements.items():
    if registry.count(old) != 1:
        raise SystemExit(f'registry replacement expected once: {old[:80]!r} got {registry.count(old)}')
    registry = registry.replace(old, new, 1)
REGISTRY.write_text(registry, encoding='utf-8')

raw = CONFIG.read_bytes()
config_replacements = {
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT` | 未設定 | ADR-0074 BFF: code 交換用 token endpoint。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可 |':
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT` | 未設定 | ADR-0074 BFF: code 交換用 token endpoint。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可。起動必須ではないが、callbackでは redirect URI / client ID / client secret と4項目完全セットで必要。欠損時503 |',
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI` | 未設定 | ADR-0074 BFF: OAuth callback の redirect URI。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可し、path は `/session/callback` 固定 |':
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI` | 未設定 | ADR-0074 BFF: OAuth callback の redirect URI。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可し、path は `/session/callback` 固定。起動必須ではないが、login開始では client ID とともに必要、callbackでは4項目完全セットの一部。欠損時は該当requestを503 |',
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID` | 未設定 | ADR-0074 BFF: OAuth client ID |':
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID` | 未設定 | ADR-0074 BFF: OAuth client ID。起動必須ではないが、login開始では redirect URI とともに必要、callbackでは4項目完全セットの一部。欠損時は該当requestを503 |',
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET` | 未設定 | ADR-0074 BFF: OAuth client secret（秘密。ログ・監査・DBへ保存しない） |':
    '| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET` | 未設定 | ADR-0074 BFF: OAuth client secret（秘密。ログ・監査・DBへ保存しない）。起動必須ではないがcallbackの4項目完全セットで必要。欠損時503 |',
    '- `saas-multitenant`: **起動hard gate**は `KJ_ATLAS_ADMIN_API_KEY`、PostgreSQL、外部PDP/document binding/tenant capabilityと各endpoint、JIT無効、deny fail-safe、OAuth authorize endpoint、auth-session hash key。OAuth callbackを使う場合はtoken endpoint / redirect URI / client ID / client secretも必要で、欠損時はcallbackを503で拒否。':
    '- `saas-multitenant`: **起動hard gate**は `KJ_ATLAS_ADMIN_API_KEY`、PostgreSQL、外部PDP/document binding/tenant capabilityと各endpoint、JIT無効、deny fail-safe、OAuth authorize endpoint、auth-session hash key。OAuth BFFのlogin開始にはredirect URI + client ID、callback code交換にはtoken endpoint + redirect URI + client ID + client secretの完全セットが必要。これらは起動hard gateではなく、欠損時は該当requestを503で拒否。',
}
for old, new in config_replacements.items():
    old_b = old.encode('utf-8')
    new_b = new.encode('utf-8')
    if raw.count(old_b) != 1:
        raise SystemExit(f'config replacement expected once: {old[:80]!r} got {raw.count(old_b)}')
    raw = raw.replace(old_b, new_b, 1)
CONFIG.write_bytes(raw)

test = TEST.read_text(encoding='utf-8')
test = test.replace(
    'MAIN = ROOT / "03_Implement/backend/src/kj_atlas_api/main.py"\n',
    'MAIN = ROOT / "03_Implement/backend/src/kj_atlas_api/main.py"\nOAUTH_BFF = ROOT / "03_Implement/backend/src/kj_atlas_api/oauth_bff.py"\n',
    1,
)
test = test.replace(
    '        self.main = MAIN.read_text(encoding="utf-8")\n',
    '        self.main = MAIN.read_text(encoding="utf-8")\n        self.oauth_bff = OAUTH_BFF.read_text(encoding="utf-8")\n',
    1,
)
marker = '    def test_saas_profile_exposes_startup_hard_gate_without_promoting_callback_only_fields(self) -> None:\n'
addition = '''    def test_oauth_bff_conditional_rows_expose_request_phase_requiredness(self) -> None:
        backend = self.registry.split("## Backend settings", 1)[1].split(
            "## Compose and frontend build keys", 1
        )[0]
        token_key = "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT"
        redirect_key = "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI"
        client_id_key = "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID"
        secret_key = "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET"

        registry_rows = {
            key: next(line for line in backend.splitlines() if line.startswith(f"| `{key}` |"))
            for key in (token_key, redirect_key, client_id_key, secret_key)
        }
        config_rows = {
            key: next(
                line for line in self.configuration.splitlines() if line.startswith(f"| `{key}` |")
            )
            for key in (token_key, redirect_key, client_id_key, secret_key)
        }
        for key in (redirect_key, client_id_key):
            self.assertIn("login", registry_rows[key])
            self.assertIn("login", config_rows[key])
        for key in (token_key, redirect_key, client_id_key, secret_key):
            self.assertIn("callback", registry_rows[key])
            self.assertIn("503", registry_rows[key])
            self.assertIn("callback", config_rows[key])
            self.assertIn("503", config_rows[key])

        self.assertIn(
            "if not authorize_endpoint or not client_id or not redirect_uri:",
            self.oauth_bff,
        )
        self.assertIn('503, "oauth_login_unavailable"', self.oauth_bff)
        self.assertIn('503, "oauth_broker_unavailable"', self.oauth_bff)

'''
if marker not in test or 'test_oauth_bff_conditional_rows_expose_request_phase_requiredness' in test:
    raise SystemExit('test insertion point unavailable')
test = test.replace(marker, addition + marker, 1)
# Rename the older test so its name no longer overstates all four fields as callback-only.
test = test.replace(
    'def test_saas_profile_exposes_startup_hard_gate_without_promoting_callback_only_fields(self)',
    'def test_saas_profile_separates_startup_hard_gate_from_bff_request_conditions(self)',
    1,
)
TEST.write_text(test, encoding='utf-8')
