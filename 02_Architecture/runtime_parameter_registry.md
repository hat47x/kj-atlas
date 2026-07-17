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

この表は、代表的な実行環境ごとの推奨値を示します。`KJ_ATLAS_RUNTIME_PROFILE`でprofile名を明示し、未指定時は`local-dev`を使います。各profileのRequired settingsは別キーで明示し、profile名だけで秘密値や接続先を補完しません。実装既定値を変更する場合や、公開設定キーを追加・改名する場合はADRで扱います。

| Profile | Purpose | Required settings | Notes |
|---|---|---|---|
| `local-dev` | 開発者の手元で最小起動する | `KJ_ATLAS_DATABASE_URL=sqlite:///./kj_atlas.db`, `KJ_ATLAS_LLM_PROVIDER=none`, `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` | 外部サービスを使わずに動作確認する。共有・export の安全境界は緩めない。 |
| `evaluation` | Docker Compose で利用者評価や検証を行う | `KJ_ATLAS_DATABASE_URL=postgresql+asyncpg://...`, `KJ_ATLAS_LLM_PROVIDER=none`, `KJ_ATLAS_AUDIT_TRANSPORT=noop`, `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=noop` | 組織内評価では PostgreSQL を推奨する。LLM、監査HTTP連携、外部PDP連携は明示的に必要な場合だけ有効化する。 |
| `enterprise-production` | 企業・行政の本番相当で運用する | `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`, `KJ_ATLAS_LLM_PROVIDER=none`, `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=read_only` または `deny` | 認証、認可、監査の接続先は組織基盤で管理する。HTTP連携を使う場合は接続先、timeout、fail-safe、秘密情報管理を同時に確認する。 |
| `saas-multitenant`（予約・起動拒否） | 相互に信頼しない複数tenantを同じサービスへ収容する | PostgreSQL等のDB側tenant guard、検証済みTenantContext、`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`, `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http`, `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=deny` | `ADR-0059`のImplementation gateと`SAAS-TENANT-01`が未完了のため、現行releaseではsettings validationが起動を拒否する。SQLite、noop、mock、read_only、endpoint欠損時fallbackを許可しない。 |

Profile に関係なく、利用者が設定する公開環境変数は例外なく `KJ_ATLAS_*` で始めます。サードパーティが別名を要求する場合は、実装または deployment adapter が内部で写像します。

### Profile default vs recommendation（既定値と推奨値）

運用ドリフトを防ぐため、実装既定値（未設定時）と profile 推奨値（運用上の標準）を区別して扱います。

| Key | Implementation default | Enterprise recommendation | Rationale |
| --- | --- | --- | --- |
| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `true` | `false` | 初期導入時の接続確認容易性と、本番運用時の厳格運用を分離するため。 |
| `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` | `read_only` | `read_only` または `deny` | 障害時の安全側挙動を明示的に選べるようにするため。 |
| `KJ_ATLAS_LLM_PROVIDER` | `none` | `none`（必要時のみ opt-in） | 外部共有の既定無効を維持するため。 |


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
4. `saas-multitenant` は現行releaseで選択不可
   - `enterprise-production`を共有SaaSとして読み替えない。
   - TenantContext、tenant従属DB制約、DB側tenant guard、deny-only adapter、越境negative testが実装・検証されるまで予約名に留める。

### SaaS profile implementation gate（ADR-0059）

- `KJ_ATLAS_RUNTIME_PROFILE`でprofileを明示選択する。`local-dev`、`evaluation`、`enterprise-production`は正規化して受理する。
- `saas-multitenant`は予約値として認識するが、現行releaseでは常に起動をfail-fastにする。無視して`local-dev`へfallbackしない。
- 実装issueの後続段階で、tenant解決、PDP、DB guardのcross-key validationがすべて成立した場合だけ起動拒否を解除する。
- `external_http` endpoint欠損時のnoop fallbackは既存profileの互換挙動としてのみ残し、SaaS profileでは禁止する。

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
| `KJ_ATLAS_RUNTIME_PROFILE` | `local-dev` | Backend/MCPの実行profile。`local-dev`, `evaluation`, `enterprise-production`を受理する。`saas-multitenant`は予約値で、現行releaseでは両processが起動拒否。 |
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
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER` | `none` | server-owned binding IDを一時的なpolicyRefへ解決するresolver。`none`, `external_http`。adapter実装済みだがSaaS runtime未配線 |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT` | 未設定 | binding resolverの接続先。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY` | 未設定 | binding resolver専用の固定bearer token。DB・監査・diagnosticsへ出力しない |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_TIMEOUT_SECONDS` | `1.5` | binding resolverのtimeout秒数。`0 < value <= 30` |
| `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER` | `none` | tenant-scoped effective capability resolver。`none`, `external_http`。adapterとlifecycle境界は実装済み |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT` | 未設定 | capability resolverの接続先。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY` | 未設定 | capability resolver専用の固定bearer token。DB・監査・diagnosticsへ出力しない |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_TIMEOUT_SECONDS` | `1.5` | capability resolverのtimeout秒数。`0 < value <= 30` |
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

## Verification harness keys (non-public)

以下は製品ランタイムの公開設定ではなく、ローカル検証・CI・リハーサル用の環境変数です。利用者向けの 04 文書では公開ランタイム設定として扱いませんが、名前の例外を作らないため `KJ_ATLAS_*` を使います。

| Key | Owner | Default | Purpose |
| --- | --- | --- | --- |
| `KJ_ATLAS_RUN_PG_TESTS` | backend pytest | 未設定 | PostgreSQL roundtrip tests を明示的に実行する opt-in flag |
| `KJ_ATLAS_RUN_PG_RLS_TESTS` | backend pytest | 未設定 | 非superuser・非BYPASSRLS runtime roleによるtenant RLS実地matrixを明示実行するopt-in flag |
| `KJ_ATLAS_TEST_POSTGRES_RUNTIME_DATABASE_URL` | backend pytest | 未設定 | RLS実地matrix専用のruntime role接続URL。migration用`KJ_ATLAS_DATABASE_URL`と別資格情報を必須とする |
| `KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR` | Auth Level2 test harness | `03_Implement/backend/tests/federation/profiles` | provider profile fixture の読み込み先 |
| `KJ_ATLAS_AUTH_LEVEL2_BACKEND_PORT` | `tests/scripts/run_auth_level2.sh` | `18000` | Auth Level2 mock 検証で起動する backend port |
| `KJ_ATLAS_AUTH_LEVEL2_SP_PORT` | `tests/scripts/run_auth_level2.sh` | `18080` | Auth Level2 mock SP port |
| `KJ_ATLAS_AUTH_LEVEL2_IDP_PORT` | `tests/scripts/run_auth_level2.sh` | `18081` | Auth Level2 mock IdP port |
| `KJ_ATLAS_AUTH_LEVEL2_BACKEND_BASE_URL` | Auth Level2 mock SP | `http://127.0.0.1:18000` | mock SP から backend へ転送する base URL |
| `KJ_ATLAS_AUTH_LEVEL2_MOCK_IDP_BASE_URL` | Auth Level2 mock SP | `http://127.0.0.1:18081` | mock SP から mock IdP を参照する base URL |
| `KJ_ATLAS_AUTH_LEVEL2_SP_BASE_URL` | Auth Level2 tests | `http://127.0.0.1:18080` | pytest から mock SP を参照する base URL |
| `KJ_ATLAS_LEVEL2_DIAG_DIR` | Auth Level2 test harness | 未設定（Level2 scripts は `.artifacts/auth-level2/legacy-federation` を設定） | legacy federation fixture の診断JSON出力先。未設定の通常pytestでは診断ファイルを書き出さない |
| `KJ_ATLAS_RECOVERY_DOC_ID` | data maintenance rehearsal | `doc-data-maint-pg-recovery-20260525` | PostgreSQL recovery rehearsal の対象 document id |

## Validation rules

- `KJ_ATLAS_LLM_PROVIDER=large-scale`, `large_scale`, `external` は `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true` と `KJ_ATLAS_LLM_ESCALATION_ENABLED=true` を必須にします。
- `KJ_ATLAS_RUNTIME_PROFILE` は `local-dev`, `evaluation`, `enterprise-production`, `saas-multitenant` だけを名前として認識し、`saas-multitenant`は`SAAS-TENANT-01`完了まで起動を拒否します。
- `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` は `noop`, `mock`, `external_http` だけを許可します。
- `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` は `read_only`, `deny` だけを許可します。
- `KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER` は `none`, `external_http` だけを許可します。`external_http`ではendpointを必須とし、非loopback HTTP、URL内credential/query/fragment、空白・制御文字を含むAPI keyを拒否します。`none`でHTTP設定だけを残すことも拒否します。
- `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER`も同じtrusted HTTP接続制約を適用します。外部応答は既知capabilityの重複なし配列とopaque capability versionだけを受理し、不明値・不完全設定はfail-closedにします。
- 外部PDP、監査HTTP、Document policy binding、tenant capability、LLMのoutbound HTTPは3xx redirectを追跡しません。検証済みendpointやhost allowlistをredirect先で迂回させず、固定bearer、tenant context、policyRef、promptを別の接続先へ転送しません。
- `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` は `none`, `oidc`, `saml` だけを許可します。
- `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER` は `user_id`, `sso_subject` だけを許可します。
- CE4 の固定契約値は、実装で安全側に検証します。

## Operating rule

公開文書、runbook、Docker Compose の利用者入力、CI 設定例では、上記以外の環境変数名を kj-atlas の設定キーとして記載しません。内部実装上の写像が必要な場合も、利用者には `KJ_ATLAS_*` のみを提示します。


### Public contract boundary (ENV-CONFIG-DRIFT-01)

- This registry is the SSOT for public runtime keys and exposes only `KJ_ATLAS_*` names.
- Vendor-defined names are implementation-internal adapter details and MUST NOT be treated as public keys.
- A policy that bans non-`KJ_ATLAS_*` names from every process environment is a separate deployment redesign decision.

### Productization readiness boundary（ENV-CONFIG-DRIFT-01 / 2026-06-02）

製品化判定では、「公開設定として利用者に求めるもの」と「実装内部で第三者コンポーネントに渡すもの」を分けて評価します。

| 判定対象 | 現在の扱い | Done への影響 |
| --- | --- | --- |
| 公開環境変数 | この registry と公開文書に載せるキーは `KJ_ATLAS_*` のみ。 | 現在の方針で充足。キーを追加する場合はこの表を先に更新する。 |
| 第三者コンテナ内部名 | `POSTGRES_*` は `ADR-0029` の private adapter boundary。利用者には設定させない。 | 現在の方針では Done 阻害要因ではない。全 process env からの排除を求める場合は別 ADR と deployment 再設計が必要。 |
| `external_http` endpoint 未設定時の挙動 | 現挙動の変更はこの registry では決めない。 | fail-fast 既定化を求める場合は、設定表更新ではなく ADR で可用性/安全性トレードオフを先に決める。 |
| 最終検証 | settings validation、docs key-drift search、Compose config、frontend build key の確認を実行する。 | issue Done 前の確認事項として残す。 |

## Drift recurrence prevention checklist（ENV-CONFIG-DRIFT-01 / ENV-ARCH-01 / ENV-PROFILE-01）

次のチェックは、runtime parameter contract 変更時に毎回実施します。

1. **Naming**: 追加・変更する公開キーが `KJ_ATLAS_*` で始まること。
2. **Defaults**: `Default` 列と実装既定値（settings/frontend build）が一致していること。
3. **Boundary**: vendor 名（例: `POSTGRES_*`）を public key として公開文書に露出していないこと。
4. **Profiles**: `local-dev` / `evaluation` / `enterprise-production` の推奨差分が変更理由と整合し、予約中の`saas-multitenant`を利用可能と誤記していないこと。
5. **Cross-doc sync**: `deployment.md` と `04_Documentation/configuration.md` に同じ公開キー集合が反映されていること。
6. **Compatibility gate**: 非互換が必要な場合は即実装せず、ADR/Issue に Go/No-Go とロールバックを先に記録すること。

Stopper条件:
- 上記 1〜6 のうち未充足がある場合は変更を停止し、承認待ちに切り替える。


## Global prefix migration adapter boundary（Stream D contract）

`ADR-0021` に基づき backend runtime key は互換期間なしで `KJ_ATLAS_*` へ移行済みです。
一方で deploy/frontend build には、利用者向け公開キーと実装内部adapterの境界があるため、次の2層で固定します。

1. **Public contract layer（利用者入力）**
   - 受理する公開キーは `KJ_ATLAS_*` のみ。
   - 旧prefix/無接頭辞キーは fail-fast で拒否する。
2. **Private adapter layer（実装内部写像）**
   - third-party container が要求する `POSTGRES_*` 等は内部写像に限定する。
   - frontend build は `envPrefix: "KJ_ATLAS_"` とし、`KJ_ATLAS_FRONTEND_API_BASE` だけを読み取る。旧frontendキーの互換shimは設けない。

### Plan → Execute → Verify → Proceed gate

- Plan: 変更前に `Naming / Defaults / Boundary / Profiles` の4観点を固定する。
- Execute: 公開契約の更新を先に行い、実装・deploy・docs を追随させる。
- Verify: docs-check + settings validation + compose config で同一キー集合を確認する。
- Proceed: 4観点がすべて pass の場合のみ進行し、1つでも fail なら停止して Issue/ADR へ戻す。

### Failure budget（3回失敗で停止）

- 同一論点で Verify が3回連続失敗した場合、4回目の試行に進まず **Stop** とする。
- Stop 時は「失敗原因」「再開条件」「要追加判断（ADR/Issue）」を `01_Plans/issues/` に記録する。
