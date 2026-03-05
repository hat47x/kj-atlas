# Runtime Parameter Registry（環境変数・実行パラメータ正本）

この文書は、kj-atlas の**環境変数 / 実行パラメータの単一正本（SSOT）**です。

- 実装正本: `03_Implement/backend/src/kj_atlas_api/settings.py`
- 運用正本（Compose）: `03_Implement/deploy/docker-compose.yml`
- 本文書の目的: 命名規約の統一、既定値の一元管理、他文書の参照先集約

## 1. 命名規約（現行）

現行実装で採用している命名規約は次のとおりです。

1. すべて `UPPER_SNAKE_CASE`。
2. すべてのランタイム環境変数は `KJ_ATLAS_*` を正規キーとして採用する。
3. 旧キー（プレフィックス無し）は互換期間のみ受理し、**新キー優先**で評価する。
4. boolean は肯定形 + 既定値で意味を固定する（例: `KJ_ATLAS_ALLOW_JIT_PROVISIONING`, `KJ_ATLAS_LLM_ESCALATION_ENABLED`）。

## 2. 互換期限（Deprecation Window）

- 旧キー互換受理の期限: **2026-12-31 (UTC)**
- 期限後の挙動:
  - 旧キーのみ設定され、新キーが未設定の場合は設定エラー（fail-fast）。
  - 新旧が同時設定されている場合は新キーを採用。

## 3. バックエンド設定キー（`settings.py`）

| 正規キー (`KJ_ATLAS_*`) | 旧キー（互換） | 既定値 | 役割 |
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


## 4. Compose/デプロイ層パラメータ

| キー | 既定値 | 役割 |
|---|---|---|
| `KJ_ATLAS_POSTGRES_DB` | `kj_atlas` | DB名 |
| `KJ_ATLAS_POSTGRES_USER` | `kj_atlas` | DBユーザ |
| `KJ_ATLAS_POSTGRES_PASSWORD` | `kj_atlas` | DBパスワード |
| `KJ_ATLAS_WEB_PORT` | `8080` | web公開ポート |
| `KJ_ATLAS_VITE_API_BASE` | `/api` | frontend APIベースパス |

## 5. strict mode 例外運用（AUTH-OPS-03）

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` を本番 strict mode 標準とする。
- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` は期限付き例外運用に限定する。
- いずれでも SafeMode/read-only 優先を弱めない。

## 6. 運用ルール（集約管理）

1. 環境変数・パラメータの追加/改名/削除時は、**先に本書を更新**する。
2. 他文書は値の列挙を最小化し、本書への参照を記載する。
3. 実装（`settings.py` / `docker-compose.yml`）との差分が出た場合、PRで同時に整合を取る。
