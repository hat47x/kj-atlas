# ADR-0064: SAML/OIDC/Broker/JWT 協調認証フローと外部 IdP 連携計画

- Status: Accepted (Phase 1 complete)
- Date: 2026-08-08
- Implemented (Phase 1): 2026-08-08
- Deciders: Project Maintainer
- Scope: `03_Implement/backend/`, `03_Implement/frontend/`, テストハーネス

## Context

ADR-0063 D9 により trusted auth edge（JWT 検証 → tenant 解決 → session persister）が実装完了し、`saas-multitenant` profile の起動が可能になった。しかし以下の認証フローは未検証・未実装である：

1. **SAML IdP → Broker (SAML→OIDC) → JWT → kj-atlas** のエンドツーエンド協調動作
2. **OAuth 2.0 / OIDC によるログインフロー**（認可コードグラント、PKCE）
3. **外部 IdP（Google, Azure AD, Okta）との連携手順**
4. **フロントエンドのログイン UI とセッション管理**

本 ADR は、mock レベルでのログイン実装から外部 IdP 連携までの包括的計画を定める。

### 実装済みの範囲（2026-08-08 Phase 1 完了後）

| コンポーネント | 状態 |
|---|---|
| `JwtSaasIdentityContextResolver` — JWT 検証 (RS256/ES256) | ✅ ADR-0063 D9-3 |
| `JwksStore` — JWKS キャッシュ・ローテーション | ✅ ADR-0063 D9-2 |
| `ClaimBasedTenantContextResolver` — claim → tenant 解決 | ✅ ADR-0063 D9-4 |
| `InMemoryActiveTenantSessionPersister` — セッション永続化 | ✅ ADR-0063 D9-6 |
| `main.py` SaaS bundle wiring | ✅ ADR-0063 D9-6 |
| Level 2 mock IdP — RS256 JWT + `/jwks.json` | ✅ ADR-0063 D9-7 |
| E2E HTTP tenant isolation test | ✅ ADR-0063 D9-8 (10 tests) |
| Mock IdP — `/login`, `/oauth/authorize`, `/oauth/token` | ✅ ADR-0064 D4-1/2 |
| Mock IdP — `/oauth/userinfo`, OIDC Discovery | ✅ ADR-0064 D4-3 |
| Mock SP — OAuth login flow proxy (`/sp/oauth-login/`) | ✅ ADR-0064 D4-4 |
| E2E OAuth login → JWT → API test | ✅ ADR-0064 (8 tests) |
| SAML assertion 検証 | ❌ 未実装 (broker に委譲) |
| フロントエンドログイン UI | ❌ 未実装 |
| 外部 IdP 連携 (Google etc.) | ❌ Phase 2 |
| 実 Broker (Keycloak) 連携 | ❌ Phase 2 |

### なぜ今この計画が必要か

ADR-0063 は「SAML をアプリに実装しない」と決定したが、その決定が正しく機能すること——broker が SAML→OIDC を変換し、kj-atlas が JWT を検証し、SAML 顧客が実際にログインできること——は未証明である。また OAuth 2.0 ログイン要件の有無も明示的に判断されていない。

## Decision

### D1: 認証フローは 3 層モデルとする

```
┌──────────────┐     SAML/OIDC      ┌──────────────┐     Signed JWT     ┌──────────────┐
│  External IdP │ ─────────────────→ │   Broker     │ ─────────────────→ │  kj-atlas    │
│  (Google etc) │                    │  (Keycloak/  │                    │  Backend     │
│  SAML IdP     │                    │   Authentik) │                    │  (JWT verify)│
└──────────────┘                    └──────────────┘                    └──────────────┘
  ユーザー認証                         SAML→OIDC変換                       tenant解決
  (外部委譲)                           JWT 発行                           認可・データ
```

- **Layer 1 (External IdP)**: Google, Azure AD, Okta, SAML IdP — ユーザーの実際の認証を行う。kj-atlas は関与しない。
- **Layer 2 (Broker)**: Keycloak / Authentik / WorkOS — 複数の外部 IdP を集約し、SAML→OIDC 変換、JWT 発行、tenant claim 注入を行う。kj-atlas は特定製品に依存しない。
- **Layer 3 (kj-atlas)**: JWT 検証、tenant 解決、認可。既存の `trusted_auth_edge.py` がこの層を実装する。

### D2: OAuth 2.0 ログインフローは kj-atlas に実装しない（Broker 委譲）

ADR-0020 §1.1 の「認証・セッション・再認証の責務は前段 IAP/SP に委譲」に従い、**OAuth 2.0 認可コードグラント、PKCE、トークンエンドポイント、リダイレクト URI 管理は kj-atlas 本体に実装しない**。

- フロントエンドは Broker のログインページへリダイレクトする。
- Broker が認可コードグラント + PKCE を処理し、セッション cookie を発行する。
- kj-atlas Backend は Broker が発行した JWT を `X-Kj-Atlas-Authorization` ヘッダーで受け取る。

ただし、開発者体験のため、**mock レベルのログインフローを Level 2 テストハーネスに実装する**（D4 参照）。

### D3: フロントエンドの認証状態管理

フロントエンドは以下の最小限の認証状態を持つ：

| 状態 | 意味 | UI |
|---|---|---|
| `unauthenticated` | JWT 未取得 | ログインボタン / リダイレクト |
| `authenticated` | JWT 検証済み | 通常画面 |
| `session-expired` | JWT 期限切れ | 再ログイン案内 |

フロントエンドは Broker のログイン URL へリダイレクトし、認証完了後 Broker がフロントエンドへリダイレクトバックする。フロントエンドは Broker から JWT を受け取り、以降の API リクエストに `X-Kj-Atlas-Authorization: Bearer <jwt>` を付与する。

### D4: Mock ログインフロー実装計画（Phase 1）

Level 2 mock IdP に以下を追加する：

#### D4-1: Mock ログインページ
- `GET /login` — シンプルな HTML フォーム（username, password, tenant 選択）
- POST で `/oidc/authorize` へリダイレクト（OAuth 2.0 認可コードグラントの mock）

#### D4-2: Mock OAuth 2.0 認可コードグラント
- `GET /oauth/authorize` — 認可エンドポイント（mock）。クエリパラメータ `response_type=code`, `client_id`, `redirect_uri`, `scope`, `state` を受け取る。ログインフォームを表示。
- `POST /oauth/authorize` — ログイン情報を受け取り、認可コードを発行、`redirect_uri` へリダイレクト。
- `POST /oauth/token` — トークンエンドポイント（mock）。認可コードを JWT に交換。`grant_type=authorization_code`, `code`, `redirect_uri`, `client_id` を受け取る。RS256 署名付き JWT を返す。

#### D4-3: Mock セッション管理
- `GET /oauth/userinfo` — UserInfo エンドポイント（Bearer トークン検証後、claim を返す）
- トークンは 1 時間有効（mock）

#### D4-4: Mock SP の JWT ベアラーモード対応
- `tests/federation/mock_sp.py` の `/sp/jwt/{provider}/docs/{doc_id}` エンドポイント（実装済み）を拡張し、完全なログインフローに対応させる：
  1. `/login` → 認可コード取得
  2. `/oauth/token` → JWT 取得
  3. JWT を `X-Kj-Atlas-Authorization` ヘッダーで Backend へ転送

### D5: 外部 IdP 連携計画（Phase 2）

#### D5-1: Google OAuth 2.0 / OIDC
- Broker に Google IdP を設定する手順書を作成する（Keycloak の Identity Provider 設定）。
- kj-atlas 側の `identity_providers` テーブルに Google の issuer (`https://accounts.google.com`) と audience を登録する手順。
- tenant マッピング: Google の `hd` (hosted domain) claim またはカスタム claim を `external_tenant_ref` へマップ。

#### D5-2: その他の IdP
- Azure AD / Entra ID: OIDC 対応。tenant マッピングは `tid` claim。
- Okta: OIDC + SAML 両対応。
- 一般 SAML IdP: Broker で SAML→OIDC 変換。

### D6: 包括的テスト戦略

| テストレベル | 内容 | 対象 |
|---|---|---|
| Level 0 (unit) | JWT resolver, JWKS store, tenant resolver, session persister | ✅ 実装済み (42 tests) |
| Level 1 (integration) | HTTP-level E2E tenant isolation with signed JWT | ✅ 実装済み (10 tests) |
| Level 2 (mock login) | Mock OAuth 2.0 認可コードグラント + PKCE → JWT 発行 → リクエスト転送 | ✅ 実装済み (8 tests) |
| Level 3 (broker E2E) | 実 Broker (Keycloak) + mock IdP + kj-atlas Backend | ❌ Phase 2 |
| Level 4 (external IdP) | Google / Azure AD 連携実証 | ❌ Phase 2 |

### D7: OAuth 2.0 ログイン要件の確認

以下のユースケースについて、kj-atlas の要件を確認する：

| ユースケース | kj-atlas での必要性 | 実装場所 |
|---|---|---|
| 認可コードグラント (Authorization Code Grant) | ✅ 必要（Broker→フロントエンド間） | Broker |
| PKCE (Proof Key for Code Exchange) | ✅ 必要（public client 対応） | Broker |
| クライアントクレデンシャルグラント | ❌ v1 では不要（M2M は将来） | — |
| リフレッシュトークン | ✅ 必要（セッション継続） | Broker |
| ログアウト / シングルログアウト | ✅ 必要 | Broker + Backend |
| OIDC Session Management | ✅ 必要 | Broker |
| RP-Initiated Logout | ✅ 必要 | Broker |

**結論**: OAuth 2.0 / OIDC ログインフローは **すべて Broker が担当**する。kj-atlas Backend は JWT 検証のみ。フロントエンドは Broker のログインページへリダイレクトする。

### D8: 実装フェーズ

#### Phase 1: Mock ログイン ✅ 完了 (2026-08-08)

1. ✅ **D4-1**: Mock ログインページ (`GET /login`, `POST /login`) — `tests/level2/mock_idp.py`
2. ✅ **D4-2**: Mock OAuth 2.0 認可コードグラント (`/oauth/authorize`, `/oauth/token`) — `tests/level2/mock_idp.py`
3. ✅ **D4-3**: Mock セッション管理 (`/oauth/userinfo`, OIDC Discovery) — `tests/level2/mock_idp.py`
4. ✅ **D4-4**: Mock SP の OAuth ログインプロキシ (`/sp/oauth-login/*`) — `tests/federation/mock_sp.py`
5. ✅ **テスト**: `test_saas_oauth_login_e2e.py` (8 tests) — OAuth login → JWT → API → tenant 分離
6. ✅ **既存テスト**: 全 530 tests パス、リグレッション無し

#### Phase 2: Broker + 外部 IdP 連携 (後続 ADR)

1. Broker 製品の選定・セットアップ手順書（Keycloak 推奨）
2. Google OAuth 2.0 / OIDC 設定手順
3. SAML IdP → Broker 設定手順
4. `identity_providers` テーブルへの Broker 登録手順
5. Level 3 E2E test (実 Broker + kj-atlas)
6. フロントエンドのログインリダイレクト対応

#### Phase 3: 本番運用準備 (将来)

1. `TRUSTED_PROXIES` 実装
2. `InMemoryActiveTenantSessionPersister` → Redis/DB ベース
3. SCIM provisioning
4. Audit logging for auth events

## Alternatives considered

1. **kj-atlas に OAuth 2.0 RP を実装する**: ADR-0020 で否決済み。認証プロトコル実装責務をアプリに持ち込まない原則を維持する。
2. **フロントエンドが JWT を直接保持しない**: セッション cookie のみで運用する方式。SPA の API 呼び出しに JWT が必要なため、フロントエンドが JWT をメモリに保持することは許容する。HttpOnly cookie との二重管理は複雑性を増すため不採用。
3. **Broker なしで Google OAuth を直接検証**: ADR-0063 D1 で否決。multi-IdP 対応の拡張性を失う。

## Consequences

- 開発者は mock ログインで E2E 認証フローをテストできる。
- SAML 顧客は Broker の SAML→OIDC 変換を通じて kj-atlas を利用できる。
- OAuth 2.0 ログインフローは kj-atlas 本体に実装されず、Broker が担当する。
- フロントエンドは最小限の認証状態管理（リダイレクト + JWT 保持）で済む。

## Non-goals

- kj-atlas 本体への OAuth 2.0 RP 実装
- Broker 製品の同梱・配布
- SCIM / 自動 deprovisioning
- M2M (machine-to-machine) client credentials grant

## Traceability

- Parent: `01_Plans/adr/ADR-0063-saas-multitenant-trusted-auth-edge.md`（trusted auth edge 実装）
- Derived-from: `01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`（認証責務境界）
- Related: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`（tenant 認可境界）
- Implementation: 新規 issue を起票予定
- Mock harness: `03_Implement/backend/tests/level2/mock_idp.py`, `tests/federation/mock_sp.py`
