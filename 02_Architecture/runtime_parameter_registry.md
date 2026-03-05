# Runtime Parameter Registry（環境変数・実行パラメータ正本）

この文書は、kj-atlas の**環境変数 / 実行パラメータの単一正本（SSOT）**です。

- 実装正本: `03_Implement/backend/src/kj_atlas_api/settings.py`
- 運用正本（Compose）: `03_Implement/deploy/docker-compose.yml`
- 方針正本: `01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md`
- 本文書の目的: 命名規約の統一、既定値の一元管理、移行期限の単一管理

## 1. 命名規約（現行）

1. すべて `UPPER_SNAKE_CASE`。
2. **正規キーは `KJ_ATLAS_*` プレフィックスを必須**とする。
3. 互換期間中のみ旧キー（プレフィックスなし）を受理する。
4. 互換期間中は **新キー優先**（同時指定時は `KJ_ATLAS_*` を採用）とする。
5. boolean は肯定形 + 既定値で意味を固定する（例: `KJ_ATLAS_ALLOW_JIT_PROVISIONING`, `KJ_ATLAS_LLM_ESCALATION_ENABLED`）。

## 2. バックエンド設定キー（`settings.py`）

| 正規キー（新） | 旧キー（互換） | 既定値 | 役割 |
|---|---|---|---|
| `KJ_ATLAS_DATABASE_URL` | `DATABASE_URL` | `sqlite:///./kj_atlas.db` | 永続化DB接続先 |
| `KJ_ATLAS_LLM_PROVIDER` | `LLM_PROVIDER` | `none` | LLMプロバイダ種別 |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL` | `LOCAL_LLM_BASE_URL` | `None` | local LLM ベースURL |
| `KJ_ATLAS_LOCAL_LLM_MODEL` | `LOCAL_LLM_MODEL` | `None` | local LLM モデル名 |
| `KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL` | `LARGE_SCALE_LLM_BASE_URL` | `None` | large-scale LLM ベースURL |
| `KJ_ATLAS_LARGE_SCALE_LLM_MODEL` | `LARGE_SCALE_LLM_MODEL` | `None` | large-scale LLM モデル名 |
| `KJ_ATLAS_LLM_ESCALATION_ENABLED` | `LLM_ESCALATION_ENABLED` | `false` | large-scale利用ガード |
| `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN` | `LLM_LARGE_SCALE_OPT_IN` | `false` | large-scale明示opt-in |
| `KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST` | `LARGE_SCALE_LLM_ALLOWLIST` | `None` | large-scale接続許可先 |
| `KJ_ATLAS_LLM_FALLBACK_TO_NONE` | `LLM_FALLBACK_TO_NONE` | `true` | LLM失敗時の `none` 退避 |
| `KJ_ATLAS_API_KEY` | `API_KEY` | `None` | 簡易APIキー保護 |
| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `AUDIT_EXPORT_ENABLED` | `false` | 監査外部送信有効化 |
| `KJ_ATLAS_AUDIT_TRANSPORT` | `AUDIT_TRANSPORT` | `noop` | 監査送信方式 |
| `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` | `AUDIT_HTTP_ENDPOINT` | `None` | 監査HTTP送信先 |
| `KJ_ATLAS_AUDIT_HTTP_API_KEY` | `AUDIT_HTTP_API_KEY` | `None` | 監査HTTP認証キー |
| `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS` | `AUDIT_HTTP_TIMEOUT_SECONDS` | `2.0` | 監査HTTP timeout |
| `KJ_ATLAS_AUDIT_QUEUE_SIZE` | `AUDIT_QUEUE_SIZE` | `100` | 監査キュー上限 |
| `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE` | `AUDIT_ALLOW_IN_SAFE_MODE` | `false` | SafeMode時の監査外送信許可 |
| `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` | `ACCESS_CONTROL_ADAPTER` | `noop` | 認可アダプタ種別 |
| `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` | `ACCESS_CONTROL_FAIL_SAFE_MODE` | `read_only` | 認可障害時フェイルセーフ |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` | `ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` | `None` | external_http PDPエンドポイント |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS` | `ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS` | `1.5` | external_http timeout |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | external_http 認証モード |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` | `ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` | `None` | external_http Bearer |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | `ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | `None` | external_http issuer ヘッダ値 |
| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `ALLOW_JIT_PROVISIONING` | `true` | JITプロビジョニング許可 |
| `KJ_ATLAS_AUTH_PROVIDER_FIELD` | `AUTH_PROVIDER_FIELD` | `x-auth-provider` | provider ヘッダ名 |
| `KJ_ATLAS_AUTH_USER_FIELD` | `AUTH_USER_FIELD` | `x-forwarded-user` | user ヘッダ名 |
| `KJ_ATLAS_AUTH_EMAIL_FIELD` | `AUTH_EMAIL_FIELD` | `x-forwarded-email` | email ヘッダ名 |
| `KJ_ATLAS_AUTH_NAME_FIELD` | `AUTH_NAME_FIELD` | `x-forwarded-name` | display name ヘッダ名 |
| `KJ_ATLAS_AUTH_SUBJECT_FIELD` | `AUTH_SUBJECT_FIELD` | `x-auth-subject` | subject ヘッダ名 |
| `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER` | `REVIEWER_REF_RESOLVER_ADAPTER` | `user_id` | reviewerRef 解決方式 |

補足:
- `KJ_ATLAS_LLM_PROVIDER` は `none | local | local_http | large-scale | large_scale | external` を受理します。
- `KJ_ATLAS_LLM_PROVIDER=large-scale/external` は `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true` かつ `KJ_ATLAS_LLM_ESCALATION_ENABLED=true` が必須です。

## 3. Compose/デプロイ層パラメータ

| キー | 既定値 | 役割 |
|---|---|---|
| `POSTGRES_DB` | `kj_atlas` | DB名 |
| `POSTGRES_USER` | `kj_atlas` | DBユーザ |
| `POSTGRES_PASSWORD` | `kj_atlas` | DBパスワード |
| `WEB_PORT` | `8080` | web公開ポート |
| `VITE_API_BASE` | `/api` | frontend APIベースパス |

## 4. ENV-ARCH-01 移行契約（旧→新）

- 正規化開始日: `2026-03-05`
- 旧キー互換受理の終了期限（deprecation）: `2026-09-30 23:59:59 UTC`
- 期限内の契約:
  - 旧キー単独指定: 受理
  - 新旧同時指定: **新キー優先**
  - 旧キーの警告出力: 実装側ログポリシーに従う（本レジストリでは値契約のみ管理）
- 期限到来後の契約:
  - 旧キー受理を廃止（起動時に失敗させる実装へ移行予定）

## 5. strict mode 例外運用（AUTH-OPS-03）

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` を本番 strict mode 標準とする。
- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` は期限付き例外運用に限定する。
- いずれでも SafeMode/read-only 優先を弱めない。

## 6. 運用ルール（集約管理）

1. 環境変数・パラメータの追加/改名/削除時は、**先に本書を更新**する。
2. 他文書は値の列挙を最小化し、本書への参照を記載する。
3. 実装（`settings.py` / `docker-compose.yml`）との差分が出た場合、PRで同時に整合を取る。
4. 旧キー廃止日時を変更する場合は、`ADR-0021` と本書を同一PRで更新する。
