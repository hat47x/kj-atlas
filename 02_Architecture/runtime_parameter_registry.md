# Runtime Parameter Registry

この文書は kj-atlas の環境変数と実行時パラメータの単一正本です。実装、Docker Compose、利用者向け文書で設定キーを追加・変更・削除する場合は、先にこの表を更新します。

## 基本ルール

1. 利用者または運用者が設定する環境変数は、すべて例外なく `KJ_ATLAS_` で始めます。
2. 接頭辞のない旧キーや、別接頭辞の互換キーは公開設定として扱いません。
3. サードパーティコンテナや build tool が内部的に別名を必要とする場合でも、kj-atlas の公開設定キーは `KJ_ATLAS_*` だけです。実装側で内部名へ写像します。
4. boolean は肯定形で命名し、既定値と安全側の意味を固定します。
5. 04 文書には「主要なもの」だけではなく、この文書に載る公開環境変数をすべて記載します。
6. サードパーティイメージや build tool が要求する内部名は、kj-atlas の公開設定キーではありません。必要な内部変換は `01_Plans/adr/ADR-0029-third-party-runtime-env-boundary.md` で扱い、利用者は `KJ_ATLAS_*` だけを設定します。

## Runtime profiles

この表は、代表的な実行環境ごとの推奨値を示します。`Default` 列は実装が未指定時に使う値、`Runtime profiles` は利用者や運用者が目的に応じて選ぶ値です。実装既定値を変更する場合や、公開設定キーを追加・改名する場合は ADR で扱います。

| Profile | Purpose | Required settings | Notes |
|---|---|---|---|
| `local-dev` | 開発者の手元で最小起動する | `KJ_ATLAS_DATABASE_URL=sqlite:///./kj_atlas.db`, `KJ_ATLAS_LLM_PROVIDER=none`, `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` | 外部サービスを使わずに動作確認する。共有・export の安全境界は緩めない。 |
| `evaluation` | Docker Compose で利用者評価や検証を行う | `KJ_ATLAS_DATABASE_URL=postgresql+asyncpg://...`, `KJ_ATLAS_LLM_PROVIDER=none`, `KJ_ATLAS_AUDIT_TRANSPORT=noop`, `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=noop` | 組織内評価では PostgreSQL を推奨する。LLM、監査HTTP連携、外部PDP連携は明示的に必要な場合だけ有効化する。 |
| `enterprise-production` | 企業・行政の本番相当で運用する | `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`, `KJ_ATLAS_LLM_PROVIDER=none`, `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=read_only` または `deny` | 認証、認可、監査の接続先は組織基盤で管理する。HTTP連携を使う場合は接続先、timeout、fail-safe、秘密情報管理を同時に確認する。 |

Profile に関係なく、利用者が設定する公開環境変数は例外なく `KJ_ATLAS_*` で始めます。サードパーティが別名を要求する場合は、実装または deployment adapter が内部で写像します。


## Profile selection criteria（運用判断基準）

実行プロファイルは「どこで動かすか」ではなく「どこまで外部依存を許可するか」で選びます。

1. `local-dev` を選ぶ条件
   - 目的が機能開発または再現テストであり、外部連携が不要。
   - DB を SQLite でよい（`KJ_ATLAS_DATABASE_URL=sqlite:///./kj_atlas.db`）。
2. `evaluation` を選ぶ条件
   - Docker Compose 上で利用者評価を行い、PostgreSQL や Nginx 経由の導線を含めて検証したい。
   - 外部監査/外部PDPは原則無効（`noop`）で、必要時のみ限定有効化する。
3. `enterprise-production` を選ぶ条件
   - 認証・認可・監査の責務分離が必要で、障害時の fail-safe を `read_only` か `deny` で固定する。
   - JIT provisioning を無効化し、運用承認済みの接続先・秘密管理がある。

### Drift check gates（設定ドリフト防止ゲート）

- 命名ゲート: 公開キーは `KJ_ATLAS_*` のみ。
- 既定値ゲート: `Default` 列と実装既定値が一致しない変更は差し戻す。
- 境界ゲート: `POSTGRES_*` など vendor 名は private adapter 扱いとし、公開文書で利用者入力として記載しない。
- プロファイルゲート: profile 変更は `runtime profiles` 表と同時に理由（Purpose/Notes）を更新する。

## Prefix migration governance（互換期間と切替条件）

- Backend runtime key は `ADR-0021` に基づき **互換期間なし** で `KJ_ATLAS_*` へ一括切替済みです。
- 旧キー（接頭辞なし/別接頭辞）は公開契約外であり、受理しません。
- 切替条件（Go/No-Go）:
  1. `runtime_parameter_registry.md`、`deployment.md`、Compose 定義で公開キーが一致していること。
  2. backend settings validation が旧キー単独・新旧混在を拒否すること。
  3. runbook/公開文書で利用者向けキーが `KJ_ATLAS_*` のみであること。
- 破壊的な再移行（例: 旧キー互換の再導入、公開キー改名）は新規 ADR を必須とします。

## Backend settings

| Key | Default | Purpose |
| --- | --- | --- |
| `KJ_ATLAS_DATABASE_URL` | `sqlite:///./kj_atlas.db` | 永続化 DB 接続先 |
| `KJ_ATLAS_LLM_PROVIDER` | `none` | LLM provider 種別。`none`, `local`, `local_http`, `large-scale`, `large_scale`, `external` |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL` | 未設定 | local LLM の base URL |
| `KJ_ATLAS_LOCAL_LLM_MODEL` | 未設定 | local LLM に渡す model 名 |
| `KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL` | 未設定 | large-scale LLM の base URL |
| `KJ_ATLAS_LARGE_SCALE_LLM_MODEL` | 未設定 | large-scale LLM に渡す model 名 |
| `KJ_ATLAS_LLM_ESCALATION_ENABLED` | `false` | large-scale LLM への昇格許可 |
| `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN` | `false` | large-scale LLM 利用の明示 opt-in |
| `KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST` | 未設定 | large-scale LLM 接続を許可する host のカンマ区切り |
| `KJ_ATLAS_LLM_FALLBACK_TO_NONE` | `true` | LLM 失敗時に `none` へ退避する |
| `KJ_ATLAS_API_KEY` | 未設定 | `/healthz` 以外の API を `X-API-Key` で保護する |
| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | audit event のHTTP連携を有効化する |
| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | audit transport。`noop` または `http` |
| `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` | 未設定 | 監査ログHTTP連携の接続先 |
| `KJ_ATLAS_AUDIT_HTTP_API_KEY` | 未設定 | 監査ログHTTP連携用 API key |
| `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS` | `2.0` | audit HTTP timeout 秒数 |
| `KJ_ATLAS_AUDIT_QUEUE_SIZE` | `100` | audit queue 上限 |
| `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE` | `false` | SafeMode 中の監査ログHTTP連携を許可する |
| `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` | `noop` | access control adapter。`noop`, `mock`, `external_http` |
| `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` | `read_only` | access control 障害時の動作。`read_only` または `deny` |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` | 未設定 | `external_http` adapter が利用する PDP の接続先 |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS` | `1.5` | `external_http` adapter の timeout 秒数 |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | `external_http` adapter の認証モード。`none`, `oidc`, `saml` |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` | 未設定 | `external_http` adapter の固定 bearer token |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | 未設定 | `external_http` adapter に渡す IdP issuer |
| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `true` | 未登録 identity の JIT provisioning を許可する |
| `KJ_ATLAS_AUTH_PROVIDER_FIELD` | `x-auth-provider` | auth provider を受け取る header 名 |
| `KJ_ATLAS_AUTH_USER_FIELD` | `x-forwarded-user` | user id を受け取る header 名 |
| `KJ_ATLAS_AUTH_EMAIL_FIELD` | `x-forwarded-email` | email を受け取る header 名 |
| `KJ_ATLAS_AUTH_NAME_FIELD` | `x-forwarded-name` | display name を受け取る header 名 |
| `KJ_ATLAS_AUTH_SUBJECT_FIELD` | `x-auth-subject` | subject を受け取る header 名 |
| `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER` | `user_id` | reviewerRef 解決 adapter。`user_id` または `sso_subject` |
| `KJ_ATLAS_CE4_EQUIVALENCE_MODE` | `equivalence_and_bundle_hash` | CE4 同値性判定 mode |
| `KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT` | `true` | CE4 dry-run が副作用なしであることを強制する |
| `KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS` | `true` | CE4 の query/bundle/proposal/apply audit 欠損を fail-closed にする |
| `KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK` | `true` | `sourceBundleHash=mock:<hash>` を許容する |
| `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS` | `true` | 未確定 CE4 契約を stub 応答で隔離し、成功扱いにしない |

## Compose and frontend build keys

| Key | Default | Purpose |
| --- | --- | --- |
| `KJ_ATLAS_WEB_PORT` | `8080` | Compose の web 公開 port |
| `KJ_ATLAS_POSTGRES_DB` | `kj_atlas` | Compose PostgreSQL の database 名 |
| `KJ_ATLAS_POSTGRES_USER` | `kj_atlas` | Compose PostgreSQL の user 名 |
| `KJ_ATLAS_POSTGRES_PASSWORD` | `kj_atlas` | Compose PostgreSQL の password |
| `KJ_ATLAS_FRONTEND_API_BASE` | `/api` | frontend build 時に埋め込む API base path。`/` で始まる path のみ受理し、それ以外は frontend 側で `/api` にフォールバック |


## Private adapter boundary (non-public keys)

以下は公開設定キーではなく、third-party adapter が内部で使用する名前です。利用者は設定しません。

| Internal name | Adapter owner | Source public key | Scope |
| --- | --- | --- | --- |
| `POSTGRES_DB` | `docker-compose.yml` `db` service | `KJ_ATLAS_POSTGRES_DB` | PostgreSQL container internal env |
| `POSTGRES_USER` | `docker-compose.yml` `db` service | `KJ_ATLAS_POSTGRES_USER` | PostgreSQL container internal env |
| `POSTGRES_PASSWORD` | `docker-compose.yml` `db` service | `KJ_ATLAS_POSTGRES_PASSWORD` | PostgreSQL container internal env |

## Validation rules

- `KJ_ATLAS_LLM_PROVIDER=large-scale`, `large_scale`, `external` は `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true` と `KJ_ATLAS_LLM_ESCALATION_ENABLED=true` を必須にします。
- `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` は `noop`, `mock`, `external_http` だけを許可します。
- `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` は `read_only`, `deny` だけを許可します。
- `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` は `none`, `oidc`, `saml` だけを許可します。
- `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER` は `user_id`, `sso_subject` だけを許可します。
- CE4 の固定契約値は、実装で安全側に検証します。

## Operating rule

公開文書、runbook、Docker Compose の利用者入力、CI 設定例では、上記以外の環境変数名を kj-atlas の設定キーとして記載しません。内部実装上の写像が必要な場合も、利用者には `KJ_ATLAS_*` のみを提示します。


### Public contract boundary (ENV-CONFIG-DRIFT-01)

- This registry is the SSOT for public runtime keys and exposes only `KJ_ATLAS_*` names.
- Vendor-defined names are implementation-internal adapter details and MUST NOT be treated as public keys.
- A policy that bans non-`KJ_ATLAS_*` names from every process environment is a separate deployment redesign decision.

## Drift recurrence prevention checklist（ENV-CONFIG-DRIFT-01 / ENV-ARCH-01 / ENV-PROFILE-01）

次のチェックは、runtime parameter contract 変更時に毎回実施します。

1. **Naming**: 追加・変更する公開キーが `KJ_ATLAS_*` で始まること。
2. **Defaults**: `Default` 列と実装既定値（settings/frontend build）が一致していること。
3. **Boundary**: vendor 名（例: `POSTGRES_*`）を public key として公開文書に露出していないこと。
4. **Profiles**: `local-dev` / `evaluation` / `enterprise-production` の推奨差分が変更理由と整合していること。
5. **Cross-doc sync**: `deployment.md` と `04_Documentation/configuration.md` に同じ公開キー集合が反映されていること。
6. **Compatibility gate**: 非互換が必要な場合は即実装せず、ADR/Issue に Go/No-Go とロールバックを先に記録すること。

Stopper条件:
- 上記 1〜6 のうち未充足がある場合は変更を停止し、承認待ちに切り替える。


## Global prefix migration compatibility layer design（Stream D contract）

`ADR-0021` に基づき backend runtime key は互換期間なしで `KJ_ATLAS_*` へ移行済みです。
一方で deploy/frontend build には、利用者向け公開キーと実装内部adapterの境界があるため、互換レイヤを次の2層で固定します。

1. **Public contract layer（利用者入力）**
   - 受理する公開キーは `KJ_ATLAS_*` のみ。
   - 旧prefix/無接頭辞キーは fail-fast で拒否する。
2. **Private adapter layer（実装内部写像）**
   - third-party container が要求する `POSTGRES_*` 等は内部写像に限定する。
   - frontend の `VITE_API_BASE` は公開契約ではなく互換shimとして扱い、正規キーは `KJ_ATLAS_FRONTEND_API_BASE` を維持する。

### Plan → Execute → Verify → Proceed gate

- Plan: 変更前に `Naming / Defaults / Boundary / Profiles` の4観点を固定する。
- Execute: 公開契約の更新を先に行い、実装・deploy・docs を追随させる。
- Verify: docs-check + settings validation + compose config で同一キー集合を確認する。
- Proceed: 4観点がすべて pass の場合のみ進行し、1つでも fail なら停止して Issue/ADR へ戻す。

### Failure budget（3回失敗で停止）

- 同一論点で Verify が3回連続失敗した場合、4回目の試行に進まず **Stop** とする。
- Stop 時は「失敗原因」「再開条件」「要追加判断（ADR/Issue）」を `01_Plans/issues/` に記録する。
