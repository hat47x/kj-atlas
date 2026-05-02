# Runtime Parameter Registry（環境変数・実行パラメータ正本）

本書は、kj-atlas の環境変数/実行パラメータに関する **単一正本（SSOT）** です。

## 1. 基本ルール

1. 全ランタイムキーは `KJ_ATLAS_*` プレフィックスを必須とする。
2. プレフィックスなし旧キーは受理しない。
3. 新旧キーの混在指定は不正設定として扱う。
4. boolean は肯定形 + 既定値で意味を固定する（例: `KJ_ATLAS_ALLOW_JIT_PROVISIONING`, `KJ_ATLAS_LLM_ESCALATION_ENABLED`）。
5. CE4監査契約では `query/bundle/proposal/apply` の4イベント欠損を成功扱いしない（fail-closed）。
6. CE4の `dryRun=true` は常に `sideEffect=none` を必須とし、例外を許可しない。

## 2. バックエンド設定キー（`settings.py`）

| 正規キー | 既定値 | 役割 |
|---|---|---|
| `KJ_ATLAS_DATABASE_URL` | `sqlite:///./kj_atlas.db` | 永続化DB接続先 |
| `KJ_ATLAS_LLM_PROVIDER` | `none` | LLMプロバイダ種別 |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL` | `None` | local LLM ベースURL |
| `KJ_ATLAS_LOCAL_LLM_MODEL` | `None` | local LLM モデル名 |
| `KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL` | `None` | large-scale LLM ベースURL |
| `KJ_ATLAS_LARGE_SCALE_LLM_MODEL` | `None` | large-scale LLM モデル名 |
| `KJ_ATLAS_LLM_ESCALATION_ENABLED` | `false` | large-scale利用ガード |
| `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN` | `false` | large-scale明示opt-in |
| `KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST` | `None` | large-scale接続許可先 |
| `KJ_ATLAS_LLM_FALLBACK_TO_NONE` | `true` | LLM失敗時の `none` 退避 |
| `KJ_ATLAS_API_KEY` | `None` | 簡易APIキー保護 |
| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | 監査外部送信有効化 |
| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | 監査送信方式 |
| `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` | `None` | 監査HTTP送信先 |
| `KJ_ATLAS_AUDIT_HTTP_API_KEY` | `None` | 監査HTTP認証キー |
| `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS` | `2.0` | 監査HTTP timeout |
| `KJ_ATLAS_AUDIT_QUEUE_SIZE` | `100` | 監査キュー上限 |
| `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE` | `false` | SafeMode時の監査外送信許可 |
| `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` | `noop` | 認可アダプタ種別 |
| `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` | `read_only` | 認可障害時フェイルセーフ |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` | `None` | external_http PDPエンドポイント |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS` | `1.5` | external_http timeout |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | external_http 認証モード |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` | `None` | external_http Bearer |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | `None` | external_http issuer ヘッダ値 |
| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `true` | JITプロビジョニング許可 |
| `KJ_ATLAS_AUTH_PROVIDER_FIELD` | `x-auth-provider` | provider ヘッダ名 |
| `KJ_ATLAS_AUTH_USER_FIELD` | `x-forwarded-user` | user ヘッダ名 |
| `KJ_ATLAS_AUTH_EMAIL_FIELD` | `x-forwarded-email` | email ヘッダ名 |
| `KJ_ATLAS_AUTH_NAME_FIELD` | `x-forwarded-name` | display name ヘッダ名 |
| `KJ_ATLAS_AUTH_SUBJECT_FIELD` | `x-auth-subject` | subject ヘッダ名 |
| `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER` | `user_id` | reviewerRef 解決方式 |
| `KJ_ATLAS_CE4_EQUIVALENCE_MODE` | `equivalence_and_bundle_hash` | CE4 API/CLI/GUI 同値性判定モード |
| `KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT` | `true` | `apply --dry-run` 副作用0を強制 |
| `KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS` | `true` | query/bundle/proposal/apply 欠損時 fail-closed |
| `KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK` | `true` | `sourceBundleHash=mock:<hash>` を許容 |

補足:
- `KJ_ATLAS_LLM_PROVIDER` は `none | local | local_http | large-scale | large_scale | external` を受理する。
- `KJ_ATLAS_LLM_PROVIDER=large-scale/external` は `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true` かつ `KJ_ATLAS_LLM_ESCALATION_ENABLED=true` が必須。
- `KJ_ATLAS_CE4_EQUIVALENCE_MODE` は `equivalence_and_bundle_hash` 以外を許可しない（同値性定義多義化を防止）。
- CE4同値性契約は Phase 1〜6 で固定し、`equivalenceKey + bundleHash` のAND判定を共通基準とする（単独判定を許可しない）。

## 3. CE4 監査イベント必須キー（契約）

| Event | 必須キー |
|---|---|
| `query` | `queryId`, `timestamp`, `actor`, `safeMode`, `equivalenceKey` |
| `bundle` | `queryId`, `bundleHash`, `excludedReason[]`, `equivalenceKey` |
| `proposal` | `proposalId`, `sourceBundleHash`, `status`, `equivalenceKey` |
| `apply` | `proposalId`, `approver`, `dryRun`, `sideEffect`, `result`, `equivalenceKey` |

- `dryRun=true` の場合、`sideEffect=none` を必須とする（must）。
- 必須キー欠損時は成功扱いせず、監査失敗として扱う。

## 4. Compose/デプロイ層パラメータ

| キー | 既定値 | 役割 |
|---|---|---|
| `POSTGRES_DB` | `kj_atlas` | DB名 |
| `POSTGRES_USER` | `kj_atlas` | DBユーザ |
| `POSTGRES_PASSWORD` | `kj_atlas` | DBパスワード |
| `WEB_PORT` | `8080` | web公開ポート |
| `VITE_KJ_ATLAS_API_BASE` | `/api` | frontend APIベースパス（正規キー） |
| `VITE_API_BASE` | `/api` | frontend APIベースパス（後方互換shim。互換期間中のみ許容） |

## 5. ENV-ARCH-01 契約（一括移行）

- backend container defaults (`03_Implement/backend/Dockerfile`) も `KJ_ATLAS_DATABASE_URL` / `KJ_ATLAS_LLM_PROVIDER` を使用し、旧キーを導入しない。

- 切替方式: 一括移行（E1: Option B）
- 旧キー互換: なし（旧キーは受理しない）
- 移行痕跡: 追加しない（E2: Option C）
- 期限運用: 採用しない（E3: 考慮外）

## 6. strict mode 例外運用（AUTH-OPS-03）

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` を本番 strict mode 標準とする。
- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` は期限付き例外運用に限定する。
- いずれでも SafeMode/read-only 優先を弱めない。

## 7. フェイルセーフ停止条件（CE4）

以下を検知した場合は、設定反映を停止する。

1. 同値性定義の多義化（`KJ_ATLAS_CE4_EQUIVALENCE_MODE` の複数許容）
2. ログ欠損を成功扱いする設定
3. safeMode後退要求（未レビュー保護・share/export保護の緩和）

## 8. 運用ルール（集約管理）

1. 環境変数・パラメータの追加/改名/削除時は、先に本書を更新する。
2. 他文書は値の列挙を最小化し、本書への参照を記載する。
3. 実装（`settings.py` / `docker-compose.yml`）との差分が出た場合、PRで同時に整合を取る。
4. ENV移行方針を変更する場合は `ADR-0021` と本書を同一PRで更新する。
