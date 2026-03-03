# ADR-0020: OIDC/SAML 対応における認証アーキテクチャ（IAPヘッダー認証 + Mock SP/IdP 検証プロファイル）

- Status: Proposed
- Date: 2026-03-03
- Deciders: Project Maintainers
- Scope: `01_Plans/adr/`

## Context

`kj-atlas` は enterprise/government 運用を想定しつつ、OSS として軽量性・安全性・再現性を維持する必要がある。
既存方針では、アプリ本体は認証機構を内包せず、外部基盤（リバースプロキシ / IdP）へ委譲する。`02_Architecture/enterprise_architecture.md`

一方で、OIDC/SAML 連携の実装～検証を AI エージェント主体で継続するには、次の論点を同時に解く必要がある。

- 本番運用での最適解（自前SP/RP実装 vs リバースプロキシ + OSS製品）
- ローカル開発での簡易認証導線（開発者体験）
- E2Eでの再現可能な検証導線（Docker-in-Docker 非依存）
- ユーザー情報（JIT Provisioning で作る最小属性）のデータ設計整合

## Decision

### 1) 本番運用アーキテクチャの採用方針

本番/準本番は **「完全ヘッダー認証方式（Identity-Aware Proxy モデル）」** を第一選択とする。

- 認証（OIDC/SAML）とセッション管理は前段SP/IAPにオフロードする。
- `kj-atlas` Backend は、信頼されたプロキシから渡される認証済みヘッダーを受け取って `AuthContext` を構築する。
- アプリ本体はパスワード・秘密情報・認証セッションを保持しない。

この判断は、`enterprise_architecture.md` の「認証は外部責務」「アプリは署名済みユーザコンテキストを受け取る」方針を具体化するものである。

### 2) 方式比較（意思決定根拠）

#### A. 自前で SAML SP / OIDC RP をアプリ内実装する方式

利点:

- アプリ単体で完結し、PoC 立ち上げが速い。
- UI/業務ロジックとの密結合が容易。

課題:

- 認証プロトコル実装責務（署名検証、証明書更新、脆弱性追随）がアプリ側に集中する。
- 企業・行政監査で「なぜ標準IAPを使わないか」の説明コストが高い。
- セキュリティレビュー対象が広がり、OSS保守負荷が増える。

#### B. リバースプロキシ + OSS IAP（推奨方式）

利点:

- 認証責務を分離し、アプリ本体の攻撃面を縮小できる。
- 企業・行政で一般的な統制（IdP連携、証明書運用、監査）と親和性が高い。
- `kj-atlas` はヘッダー契約に集中でき、後方互換維持が容易。

課題:

- 配備時にプロキシ設定（trusted proxy, header contract）が必須。
- ローカル開発では簡易導線（Basic認証等）を別途準備する必要がある。

**結論**: `kj-atlas` の価値軸（軽量・安全・外部統合）を優先し、B を採用する。

### 3) Backend（kj-atlas 本体）必須契約

FastAPI 側に「ヘッダー認証 Dependency / Middleware」を実装し、以下を満たす。

1. Trust Proxy 強制
   - `TRUSTED_PROXIES`（CIDR/IP）で許可元を制限する。
   - 非許可信頼元 + 認証ヘッダー付き要求は拒否（401/403）。
2. 汎用 `AuthContextAdapter`（設定駆動）
   - 認証情報の受け取り方式は **設定で切替可能** とする（実装追加なしで吸収）。
   - 最低限サポートする入力モード:
     - `header`（`X-Forwarded-*` 等のHTTPヘッダー群）
     - `jwt_header`（例: `Authorization: Bearer <JWT>` または `X-Auth-Token`）
   - いずれのモードでも、最終的に同一の `AuthContext` へ正規化する。
3. クレーム/ヘッダーのマッピング規則
   - `AUTH_USER_FIELD`, `AUTH_EMAIL_FIELD`, `AUTH_NAME_FIELD`, `AUTH_GROUPS_FIELD` などの設定キーで、
     受信元フィールド名を差し替え可能にする。
   - 既定値は標準的な `X-Forwarded-User` などを採用するが、AWS ALB / Cloud IAP 等の差異は
     **provider preset（設定テンプレート）** で吸収し、サービス別の個別実装を避ける。
   - `X-Forwarded-For` は認証IDではなく、`TRUSTED_PROXIES` 判定と監査補助にのみ利用する。
4. リクエストコンテキスト
   - 正規化した `AuthContext` をAPIで参照可能にする。
5. JIT Provisioning（最小）
   - 未知ユーザーアクセス時に最小属性を登録（userId / displayName / email 等）。
   - パスワード・ハッシュは保持しない。

### 4) Frontend 必須契約

- フロントエンドは「自前ログイン画面」を正本導線にしない。
- 認証状態は backend の `AuthContext` 反映結果で表示する。
- ログアウトは前段SP/IAPへリダイレクトする終端（RP-Initiated logout）を使う。

### 5) ローカル開発プロファイル（簡易裏口）

開発者向けに `docker-compose.local.yml` を用意し、前段プロキシ（推奨: Caddy）で次を提供する。

- Basic認証は **local/dev 限定** とし、本番/準本番では無効を既定とする。
- Basic認証は明示的な環境変数（例: `DEV_BASIC_AUTH_ENABLED=true`）が指定された場合のみ有効化する。
- 環境ごとの有効/無効は compose ファイルで制御する（例: `docker-compose.local.yml` でのみ指定）。

- Basic認証（固定管理者資格情報）
- 認証成功時ヘッダー付与（例: `X-Forwarded-User: admin`）
- backend への reverse proxy

これにより、本体コードの認証仕様を変えずに開発導線を確保する。

### 6) E2E検証プロファイル（Mock SP/IdP の必要性を含む再整理）

結論として、`kj-atlas` の主契約は「IAP/プロキシ -> AuthContext 正規化」であり、
**常に Mock SP/IdP を必須化しない**。検証は次の2層で運用する。

#### Level 1: 既定（必須）— AuthContext 契約E2E

- 対象: `TRUSTED_PROXIES`、header/JWTマッピング、JIT Provisioning、拒否/許可制御。
- 方式: 軽量プロキシ（またはテストハーネス）から認証済みコンテキストを注入し、
  `kj-atlas` 側の契約を直接検証する。
- 目的: 本プロジェクトの本質価値（アプリ境界の安全性・互換性）を最短経路で回帰保証する。

#### Level 2: 拡張（条件付き）— Federation フローE2E

- 対象: OIDC/SAML フロー全体（redirect/callback/logout、署名検証、`xmlsec1` 依存など）。
- 方式: FastAPI製モック群（`mock_sp` + `mock_idp`）を起動して検証する。
  - `mock_idp`: SAML（`pysaml2`）, OIDC（`Authlib`）
  - `mock_sp`: 認証成功後に `X-Forwarded-User` 等を付与して backend へフォワード
- 実行例（Docker非依存）:
  - `uvicorn mock_idp:app --port 8081`
  - `uvicorn mock_sp:app --port 8080`
  - `uvicorn kj_atlas_backend.main:app --port 8000`

#### Mock SP/IdP を実施すべき条件

- `AuthContextAdapter` の入力モードや provider preset の仕様変更。
- logout / step-up / `amr` 等、IdP連携境界に関わる仕様変更。
- 依存ライブラリ更新（`pysaml2`, `Authlib`, `xmlsec1`）で連携回帰リスクが高い場合。

上記条件に該当しないPRでは、Level 1 を満たせば受入可能とする。

### 7) 暗号素材と依存

- SAML署名/OIDC JWKS はテスト起動時に動的生成する。
- 鍵素材は平文コミット禁止。
- `pysaml2` 実行要件として `xmlsec1` を導入する（ローカル手順 + Dockerfile）。

### 8) 受入基準（最小）

1. trusted proxy 外からのヘッダー偽装要求を拒否できる。
2. trusted proxy 経由時に `AuthContext` が構築される。
3. JIT Provisioning で最小ユーザーレコードが作成される（パスワード列なし）。
4. E2E受入基準:
   - **必須**: Level 1（AuthContext 契約E2E）を通過する。
   - **条件付き必須**: IdP連携境界を変更するPRでは Level 2（Mock SP/IdP）も通過する。

### 9) 未決事項（TODO / Issue化）

以下は本ADRで結論固定しない。

- ユーザー最小属性スキーマ（永続保存する項目、PII最小化、表示名の扱い）
- reviewerRef / ownerRef と AuthContext.userId の正規マッピング規則
- 組織向け roles/groups/policyRef の永続境界（アプリ内保存 vs 外部照会）
- `amr/acr/aal/auth_time` を AuthContext にどこまで保持・表示・監査出力するか

上記は issue memo `issue-AUTH-ARCH-01-authcontext-jit-provisioning-data-boundary.md` で管理する。

### 10) IdP がパスキー（FIDO2/WebAuthn）を提供する場合の考慮事項

前段 IdP/SP 側がパスキー認証を採用しても、`kj-atlas` 本体の基本原則（認証情報を保持しない）は維持する。

- 位置づけ:
  - パスキーは IdP 側の認証手段（Authenticator）であり、`kj-atlas` は直接 WebAuthn 検証を実装しない。
  - `kj-atlas` が信頼するのは最終的な認証済みコンテキスト（ヘッダー/トークン検証結果）のみ。
- 最低限の受信属性（将来拡張を含む）:
  - 必須: `userId`（`X-Forwarded-User` 相当）
  - 任意: `amr`（認証手段, 例: `pwd`, `webauthn`）, `acr`/`aal`（保証レベル）, `auth_time`（認証時刻）
- 運用上の必須ルール:
  - 高リスク操作（将来の export/share/admin 相当）は `amr/acr/aal` に基づく追加制御が可能なI/Fで設計する（値が無い場合は保守的に拒否/read-only）。
  - `amr` 等の属性は監査目的で扱うが、端末固有情報や公開鍵クレデンシャルIDなど識別子の過剰保存は避ける。
  - セッション長・再認証要求（step-up）は IAP 側ポリシーで実施し、アプリ本体は結果のみ受け取る。
- テスト観点:
  - Mock SP/IdP で `amr=webauthn` を模擬できるようにし、属性有無の両ケースをE2Eで確認する。
  - 「パスキー利用時でもヘッダー契約が不変であること」を回帰条件に含める。

### 非目標

- 本ADRは「本番IdP製品選定（Keycloak/Authentik/Cloud IAP等）」を固定しない。
- 本ADRはアプリ内パスワード認証機能を追加しない。
- 本ADRは全RBAC実装を完了条件にしない（I/F整備を優先）。

## Consequences

- `kj-atlas` は認証実装責務を最小化し、OSSとしての安全運用性を高める。
- 企業・行政で要求される監査/統制との整合が取りやすくなる。
- 一方で、プロキシ設定ミス（trusted proxy, header mapping）が主要リスクとなるため、Level 1 E2Eを常時維持する必要がある。
- Mock SP/IdP は「常時必須」ではなく、IdP連携境界変更時の拡張ゲートとして運用する。
- 入力方式の差異（header/JWT、各IAPのヘッダー名差異）は設定テンプレートで吸収し、実装分岐の増殖を抑制する。
- ユーザーデータ境界は未確定のため、スキーマ更新を伴う後続タスク管理が必要。

## Traceability

- Related: `02_Architecture/enterprise_architecture.md`
- Related: `02_Architecture/schemas.md`
- Related: `02_Architecture/api.md`
- Related: `02_Architecture/review_attribution.md`
- Related: `04_Documentation/security.md`
- Related: `04_Documentation/e2e_testing.md`
- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Related: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Follow-up: `01_Plans/issues/issue-AUTH-ARCH-01-authcontext-jit-provisioning-data-boundary.md`
- Replaces: `04_Documentation/auth_oidc_saml_mock_idp.md`
