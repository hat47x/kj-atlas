# Runtime Parameter Registry（環境変数・実行パラメータ正本）

この文書は、kj-atlas の**環境変数 / 実行パラメータの単一正本（SSOT）**です。

- 実装正本: `03_Implement/backend/src/kj_atlas_api/settings.py`
- 運用正本（Compose）: `03_Implement/deploy/docker-compose.yml`
- 本文書の目的: 命名規約の統一、既定値の一元管理、他文書の参照先集約

## 1. 命名規約（現行）

現行実装で採用している命名規約は次のとおりです。

1. すべて `UPPER_SNAKE_CASE`。
2. 機能ドメイン接頭辞を使う（例: `ACCESS_CONTROL_*`, `AUDIT_*`, `AUTH_*`, `LLM_*`）。
3. プロジェクト共通接頭辞（`KJ_*`）は**現行ランタイムでは採用しない**。
4. boolean は肯定形 + 既定値で意味を固定する（例: `ALLOW_JIT_PROVISIONING`, `LLM_ESCALATION_ENABLED`）。

## 2. バックエンド設定キー（`settings.py`）

| キー | 既定値 | 役割 |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./kj_atlas.db` | 永続化DB接続先 |
| `LLM_PROVIDER` | `none` | LLMプロバイダ種別 |
| `LOCAL_LLM_BASE_URL` | `None` | local LLM ベースURL |
| `LOCAL_LLM_MODEL` | `None` | local LLM モデル名 |
| `LARGE_SCALE_LLM_BASE_URL` | `None` | large-scale LLM ベースURL |
| `LARGE_SCALE_LLM_MODEL` | `None` | large-scale LLM モデル名 |
| `LLM_ESCALATION_ENABLED` | `false` | large-scale利用ガード |
| `LLM_LARGE_SCALE_OPT_IN` | `false` | large-scale明示opt-in |
| `LARGE_SCALE_LLM_ALLOWLIST` | `None` | large-scale接続許可先 |
| `LLM_FALLBACK_TO_NONE` | `true` | LLM失敗時の `none` 退避 |
| `API_KEY` | `None` | 簡易APIキー保護 |
| `AUDIT_EXPORT_ENABLED` | `false` | 監査外部送信有効化 |
| `AUDIT_TRANSPORT` | `noop` | 監査送信方式 |
| `AUDIT_HTTP_ENDPOINT` | `None` | 監査HTTP送信先 |
| `AUDIT_HTTP_API_KEY` | `None` | 監査HTTP認証キー |
| `AUDIT_HTTP_TIMEOUT_SECONDS` | `2.0` | 監査HTTP timeout |
| `AUDIT_QUEUE_SIZE` | `100` | 監査キュー上限 |
| `AUDIT_ALLOW_IN_SAFE_MODE` | `false` | SafeMode時の監査外送信許可 |
| `ACCESS_CONTROL_ADAPTER` | `noop` | 認可アダプタ種別 |
| `ACCESS_CONTROL_FAIL_SAFE_MODE` | `read_only` | 認可障害時フェイルセーフ |
| `ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` | `None` | external_http PDPエンドポイント |
| `ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS` | `1.5` | external_http timeout |
| `ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | external_http 認証モード |
| `ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` | `None` | external_http Bearer |
| `ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | `None` | external_http issuer ヘッダ値 |
| `ALLOW_JIT_PROVISIONING` | `true` | JITプロビジョニング許可 |
| `AUTH_PROVIDER_FIELD` | `x-auth-provider` | provider ヘッダ名 |
| `AUTH_USER_FIELD` | `x-forwarded-user` | user ヘッダ名 |
| `AUTH_EMAIL_FIELD` | `x-forwarded-email` | email ヘッダ名 |
| `AUTH_NAME_FIELD` | `x-forwarded-name` | display name ヘッダ名 |
| `AUTH_SUBJECT_FIELD` | `x-auth-subject` | subject ヘッダ名 |
| `REVIEWER_REF_RESOLVER_ADAPTER` | `user_id` | reviewerRef 解決方式 |

補足:
- `LLM_PROVIDER` は `none | local | local_http | large-scale | large_scale | external` を受理します。
- `LLM_PROVIDER=large-scale/external` は `LLM_LARGE_SCALE_OPT_IN=true` かつ `LLM_ESCALATION_ENABLED=true` が必須です。


## 3. Compose/デプロイ層パラメータ

| キー | 既定値 | 役割 |
|---|---|---|
| `POSTGRES_DB` | `kj_atlas` | DB名 |
| `POSTGRES_USER` | `kj_atlas` | DBユーザ |
| `POSTGRES_PASSWORD` | `kj_atlas` | DBパスワード |
| `WEB_PORT` | `8080` | web公開ポート |
| `VITE_API_BASE` | `/api` | frontend APIベースパス |

## 4. strict mode 例外運用（AUTH-OPS-03）

- `ALLOW_JIT_PROVISIONING=false` を本番 strict mode 標準とする。
- `ALLOW_JIT_PROVISIONING=true` は期限付き例外運用に限定する。
- いずれでも SafeMode/read-only 優先を弱めない。

## 5. 運用ルール（集約管理）

1. 環境変数・パラメータの追加/改名/削除時は、**先に本書を更新**する。
2. 他文書は値の列挙を最小化し、本書への参照を記載する。
3. 実装（`settings.py` / `docker-compose.yml`）との差分が出た場合、PRで同時に整合を取る。
