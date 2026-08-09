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
| `saas-multitenant` | 相互に信頼しない複数tenantを同じサービスへ収容する | PostgreSQL等のDB側tenant guard、検証済みTenantContext、`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`, `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http`, `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=deny`, `KJ_ATLAS_JWT_ALGORITHMS=RS256,ES256`, `KJ_ATLAS_TENANT_CLAIM_NAME=tenant_ref` | `ADR-0063` D9により trusted auth edge が実装された。起動時の `TrustedSaasRuntimePolicy.validate()` と lifespan preflight が必須設定の完備を検証する。SQLite、noop、mock、read_only、endpoint欠損時fallbackを許可しない。 |

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
- backendのtrusted SaaS adapter bundleは`saas-multitenant`と相互必須である。profile、非秘密runtime safety policy、bundleの型・欠損・相互必須、started-stateに加え、構築済みPDP／capability／binding componentの実型を状態変更なしでpreflightし、DB初期化前とadapter有効化前に同じ判定を再実行する。single-tenant profileへのbundle注入、SaaS profileでのbundle欠損、未知profile、設定はexternalでも実componentがnoop／unavailableとなる構成はDB接続前に起動拒否する。runtime safety policyはPostgreSQL、JIT無効、external access-control、`deny` fail-safe、external document binding、external tenant capabilityを必須とし、実componentも`ExternalPolicyAccessControlAdapter`、`ExternalHttpTenantCapabilityResolver`、`ExternalHttpDocumentPolicyBindingResolver`の完全セットを必須とする。現行の予約profile拒否を将来解除しても、この完全セットが欠ける構成は起動しない。
- backendはvalidation済みprofileを起動時にsnapshotし、`GET /session/bootstrap-policy`でprofile名を公開せず`single-tenant`または`tenant-session-required`へclosed-worldに写像する。frontend buildも同じprofileを受け取り、既存3 profileはpolicy通信なしでlocal-first起動、`saas-multitenant`だけはserver policy一致とsession bootstrap成功までAppをmountしない。未知・空・非canonical build値、policy不一致・取得失敗はsingle-tenantへfallbackせずblocked stateへ閉じる。
- 実装issueの後続段階で、tenant解決、PDP、DB guardのcross-key validationがすべて成立した場合だけ起動拒否を解除する。
- `ADR-0062`により、profileを問わず `external_http` / `http` を明示選択した場合は対応endpointを必須とする。endpoint欠損をnoopへfallbackせず、DB初期化やrequest受付より前に起動を拒否する。

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

`Delivery surface` は、現時点でそのキーがどの起動面へ実際に届くかを示します（ENV-COMPOSE-01）。

- `direct` — backend を直接起動する場合にのみ有効。標準 Compose・overlay のいずれからも配送されない。
- `base Compose` — 標準 `docker-compose.yml` の `api.environment` が配送する。
- `llm-stub overlay` — `docker-compose.llm-stub.yml`（検証専用 overlay。本番相当の利用者向けデプロイでは使わない）からのみ配送される。
- `fixed` — `Settings.validate_llm_provider_guards` が既定値以外を拒否する固定契約値。運用者が変更する対象ではない。

`direct` と記載されたキーは、`04_Documentation/configuration.md` 等で Compose 起動時の設定例として案内しても実際には `api` コンテナへ届かない。標準 `docker-compose.yml` は `KJ_ATLAS_API_KEY` と `KJ_ATLAS_ALLOW_JIT_PROVISIONING` をホスト環境からの pass-through（値なし `environment` entry）として配送する（ENV-COMPOSE-01 Phase 2）。ホスト側で未設定の場合はコンテナ内でも未設定のまま（空文字は注入しない）で、実装既定値を維持する。監査HTTP・外部PDP・large-scale LLM・local LLM の接続系キーは標準 Compose では unsupported であり、必要な場合は組織側 overlay で関連キーを一組として配送する。

`Probe` 列は、設定後に秘密値を出力せず効果を確認する方法の説明である。`KJ_ATLAS_API_KEY` と `KJ_ATLAS_ALLOW_JIT_PROVISIONING` の代表probeは `03_Implement/deploy/tools/verify_env_delivery.sh`（Docker利用可能なローカル環境向け、CIでは実行しない）として実装済み。他キーの手順は記載のみで、自動テストとしては未実装（後続作業）。

| Key | Default | Purpose | Delivery surface | Secret | Probe (non-secret) |
| --- | --- | --- | --- | --- | --- |
| `KJ_ATLAS_RUNTIME_PROFILE` | `local-dev` | Backend/MCPの実行profile。`local-dev`, `evaluation`, `enterprise-production`を受理する。`saas-multitenant`は予約値で、現行releaseでは両processが起動拒否。 | direct / base Compose | 通常値 | 起動ログまたは `/healthz` で profile 名（値のみ）を確認する |
| `KJ_ATLAS_DATABASE_URL` | `sqlite:///./kj_atlas.db` | 永続化 DB 接続先。VerifiedはSQLite、PostgreSQL、MySQL 8.4、MariaDB 11.4、SQL Server 2022、CockroachDB 26.2。candidate/未知DBはengine生成・migration前に拒否する。対応表は`database_portability.md` | direct / base Compose | 資格情報を含み得る（URL に password を埋め込む場合がある） | `/healthz` が 200 を返し、起動ログに接続エラーがないことを確認する（URL 値は出力しない） |
| `KJ_ATLAS_LLM_PROVIDER` | `none` | LLM provider 種別。`none`, `local`, `local_http`, `large-scale`, `large_scale`, `external` | direct / base Compose | 通常値 | 起動ログまたは `/healthz` で provider 名（値のみ）を確認する |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL` | 未設定 | local LLM のbase URL。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 | direct / llm-stub overlay のみ | 通常値（接続先ホスト名。認証情報は含まない） | overlay 使用時、`local` provider 経由のリクエストが stub へ到達すること（成否のみ確認、payload は出力しない） |
| `KJ_ATLAS_LOCAL_LLM_MODEL` | 未設定 | local LLM に渡す256文字以下のcanonical model ID | direct / llm-stub overlay のみ | 通常値 | stub 側ログの model 欄が設定値と一致することを確認する |
| `KJ_ATLAS_LLM_TASK_MODEL_MAP` | 未設定（空文字） | ADR-0065: タスク別モデル割当（`task=model,...`）。未設定タスクは既定モデル。 | direct | 通常値 | 指定 task のリクエスト model が設定値と一致することをログで確認する |
| `KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL` | 未設定 | large-scale LLM のbase URL。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 | direct | 通常値（接続先ホスト名。認証情報は別キー） | allowlist 外ホストを設定した場合に呼び出しが拒否されることを確認する |
| `KJ_ATLAS_LARGE_SCALE_LLM_MODEL` | 未設定 | large-scale LLM に渡す256文字以下のcanonical model ID | direct | 通常値 | 呼び出しペイロードの model フィールドが設定値と一致することを確認する |
| `KJ_ATLAS_LLM_ESCALATION_ENABLED` | `false` | large-scale LLM への昇格許可 | direct | 通常値 | `false` のとき large-scale provider への昇格が拒否されることを確認する |
| `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN` | `false` | large-scale LLM 利用の明示 opt-in | direct | 通常値 | `false` のとき `large-scale`/`external` provider 指定が起動時に拒否されることを確認する（validator で既に強制） |
| `KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST` | 未設定 | large-scale接続を許可するcanonical hostのカンマ区切り。URL、wildcard、port、path、重複は不可 | direct | 通常値（ホスト名リスト。認証情報を含まない） | allowlist 外ホストへの接続が拒否されることを確認する |
| `KJ_ATLAS_LLM_FALLBACK_TO_NONE` | `true` | LLM 失敗時に `none` へ退避する | direct | 通常値 | LLM 呼び出し失敗時に `none` provider へフォールバックすることを確認する |
| `KJ_ATLAS_API_KEY` | 未設定 | `/healthz` 以外の API を `X-API-Key` で保護する | direct / base Compose | 秘密値 | 未設定時は `/healthz` 以外も無防備。設定時: キーなしは 401、正しい `X-API-Key` は成功、誤ったキーも 401（値自体は出力しない） |
| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | audit event のHTTP連携を有効化する | direct | 通常値 | `true` 時に監査イベントが transport 経由で送出されること（内容は出力せず送信有無のみ確認） |
| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | audit transport。`noop` または `http` | direct | 通常値 | `http` 指定時に HTTP transport が選択されることをログで確認する |
| `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` | 未設定 | 監査ログHTTP連携の接続先。`KJ_ATLAS_AUDIT_TRANSPORT=http` 時は必須 | direct | 通常値（接続先URL。認証情報は別キー） | test double への到達確認（実サービスへは送らない） |
| `KJ_ATLAS_AUDIT_HTTP_API_KEY` | 未設定 | 監査ログHTTP連携用 API key | direct | 秘密値 | 送信ヘッダにキーが付与されることを確認する（値はマスクして確認） |
| `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS` | `2.0` | audit HTTP timeout 秒数 | direct | 通常値 | timeout 超過時に監査送出が失敗として扱われることを確認する |
| `KJ_ATLAS_AUDIT_QUEUE_SIZE` | `100` | audit queue 上限 | direct | 通常値 | 上限到達時の drop 挙動をログで確認する |
| `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE` | `false` | SafeMode 中の監査ログHTTP連携を許可する | direct | 通常値 | SafeMode 中に `false` のとき監査HTTP送出が抑止されることを確認する |
| `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` | `noop` | access control adapter。`noop`, `mock`, `external_http` | direct | 通常値 | 選択した adapter 名が起動ログに反映されることを確認する |
| `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` | `read_only` | access control 障害時の動作。`read_only` または `deny` | direct | 通常値 | 外部PDP障害を模擬し、`read_only`/`deny` いずれの挙動になるか確認する |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` | 未設定 | `external_http` adapter が利用する必須のPDP接続先 | direct | 通常値 | test double への到達確認（実 PDP へは送らない） |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS` | `1.5` | `external_http` adapter の timeout 秒数 | direct | 通常値 | timeout 超過時に fail-safe mode の挙動が発火することを確認する |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | `external_http` adapter の認証モード。`none`, `oidc`, `saml` | direct | 通常値 | 選択した認証 mode で PDP リクエストの認証ヘッダ形式が変わることを確認する（値は出力しない） |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` | 未設定 | `external_http` adapter の固定 bearer token | direct | 秘密値 | PDP リクエストに Bearer ヘッダが付与されることを確認する（値はマスク） |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | 未設定 | `external_http` adapter に渡す IdP issuer | direct | 通常値 | OIDC/SAML 認証時に issuer 検証が設定値と一致することを確認する |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER` | `none` | server-owned binding IDを一時的なpolicyRefへ解決するresolver。`none`, `external_http`。adapter実装済みだがSaaS runtime未配線 | direct | 通常値 | 選択した resolver 名が起動ログに反映されることを確認する |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT` | 未設定 | binding resolverの接続先。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 | direct | 通常値（接続先URL。認証情報は別キー） | test double への到達確認（実サービスへは送らない） |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY` | 未設定 | binding resolver専用の固定bearer token。DB・監査・diagnosticsへ出力しない | direct | 秘密値 | 送信ヘッダにキーが付与されることを確認する（値はマスクして確認） |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_TIMEOUT_SECONDS` | `1.5` | binding resolverのtimeout秒数。`0 < value <= 30` | direct | 通常値 | timeout 超過時に resolver が fail-closed へ倒れることを確認する |
| `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER` | `none` | tenant-scoped effective capability resolver。`none`, `external_http`。adapterとlifecycle境界は実装済み | direct | 通常値 | 選択した resolver 名が起動ログに反映されることを確認する |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT` | 未設定 | capability resolverの接続先。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 | direct | 通常値（接続先URL。認証情報は別キー） | test double への到達確認（実サービスへは送らない） |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY` | 未設定 | capability resolver専用の固定bearer token。DB・監査・diagnosticsへ出力しない | direct | 秘密値 | 送信ヘッダにキーが付与されることを確認する（値はマスクして確認） |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_TIMEOUT_SECONDS` | `1.5` | capability resolverのtimeout秒数。`0 < value <= 30` | direct | 通常値 | timeout 超過時に resolver が fail-closed へ倒れることを確認する |
| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `true` | 未登録 identity の JIT provisioning を許可する | direct / base Compose | 通常値 | `false` 時、未登録 identity でのアクセスが拒否され新規作成されないことを確認する |
| `KJ_ATLAS_AUTH_PROVIDER_FIELD` | `x-auth-provider` | auth provider を受け取る header 名 | direct | 通常値 | 指定 header から provider 値が読み取られることを確認する |
| `KJ_ATLAS_AUTH_USER_FIELD` | `x-forwarded-user` | user id を受け取る header 名 | direct | 通常値 | 指定 header から user id が読み取られ、identity へ反映されることを確認する |
| `KJ_ATLAS_AUTH_EMAIL_FIELD` | `x-forwarded-email` | email を受け取る header 名 | direct | 通常値 | 指定 header から email が読み取られ、identity へ反映されることを確認する |
| `KJ_ATLAS_AUTH_NAME_FIELD` | `x-forwarded-name` | display name を受け取る header 名 | direct | 通常値 | 指定 header から display name が読み取られ、identity へ反映されることを確認する |
| `KJ_ATLAS_AUTH_SUBJECT_FIELD` | `x-auth-subject` | subject を受け取る header 名 | direct | 通常値 | 指定 header から subject が読み取られ、identity へ反映されることを確認する |
| `KJ_ATLAS_JWT_ALGORITHMS` | `RS256,ES256` | JWT 署名検証の algorithm allowlist（カンマ区切り）。HMAC 系および `none` は常に拒否。 | direct | 通常値 | 許容外 algorithm の JWT が 401 で拒否されることを確認する |
| `KJ_ATLAS_TENANT_CLAIM_NAME` | `tenant_ref` | JWT 内の tenant 外部識別子を運ぶ claim 名。`tenant_identity_providers.external_tenant_ref` と照合する。 | direct | 通常値 | 指定 claim が存在しない JWT が 401 で拒否されることを確認する |
| `KJ_ATLAS_TRUSTED_PROXIES` | （空） | header 認証の信頼できるプロキシ CIDR のカンマ区切りリスト。未設定時は全オリジン許可（開発用・警告ログ出力）。本番では `10.0.0.0/8` 等でプロキシを限定すること。`saas-multitenant` では JWT 認証必須のため不要。 | direct | 通常値 | 非信頼 IP からの forwarded auth header が 403 で拒否されることを確認する |
| `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER` | `user_id` | reviewerRef 解決 adapter。`user_id` または `sso_subject` | direct | 通常値 | reviewerRef の解決方式が選択値（`user_id`/`sso_subject`）どおりであることを確認する |
| `KJ_ATLAS_CE4_EQUIVALENCE_MODE` | `equivalence_and_bundle_hash` | CE4 同値性判定 mode | fixed | 通常値 | 既定値以外を設定すると起動時に拒否されることを確認する |
| `KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT` | `true` | CE4 dry-run が副作用なしであることを強制する | fixed | 通常値 | `false` 設定時に起動が拒否されることを確認する |
| `KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS` | `true` | CE4 の query/bundle/proposal/apply audit 欠損を fail-closed にする | fixed | 通常値 | `false` 設定時に起動が拒否されることを確認する |
| `KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK` | `true` | `sourceBundleHash=mock:<hash>` を許容する | direct（CE4系だが validator 未強制） | 通常値 | `false` 設定時に `mock:` prefix の sourceBundleHash が拒否されることを確認する |
| `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS` | `true` | 未確定 CE4 契約を stub 応答で隔離し、成功扱いにしない | direct（validator 未強制） | 通常値 | `false` 設定時に未確定 CE4 契約が stub 応答ではなくエラーになることを確認する |

## Compose and frontend build keys

| Key | Default | Purpose |
| --- | --- | --- |
| `KJ_ATLAS_WEB_PORT` | `8080` | Compose の web 公開 port |
| `KJ_ATLAS_POSTGRES_DB` | `kj_atlas` | Compose PostgreSQL の database 名 |
| `KJ_ATLAS_POSTGRES_USER` | `kj_atlas` | Compose PostgreSQL の user 名 |
| `KJ_ATLAS_POSTGRES_PASSWORD` | `kj_atlas` | Compose PostgreSQL の password |
| `KJ_ATLAS_RUNTIME_PROFILE` | `local-dev`（Composeは`evaluation`を注入） | frontend entry mode。既存3 profileはsingle-tenant、予約中の`saas-multitenant`だけtenant session必須。未知値は起動UIをblockedにする |
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
| `KJ_ATLAS_SCREENSHOT_HOST` | `capture_release_screenshots.mjs` 等のscreenshot capture script | `127.0.0.1` | screenshot撮影用に起動するvite preview serverのhost |
| `KJ_ATLAS_SCREENSHOT_PORT` | screenshot capture script | `4173` | screenshot撮影用vite preview serverのport |
| `KJ_ATLAS_SCREENSHOT_BASE_URL` | screenshot capture script | `http://<host>:<port>/?locale=ja`（host/portから導出） | 撮影対象ページのbase URL |
| `KJ_ATLAS_SCREENSHOT_OUTPUT_DIR` | screenshot capture script | `04_Documentation/assets/screenshots` | 生成画像の出力先 |
| `KJ_ATLAS_SCREENSHOT_BROWSER_PATH` | screenshot capture script | 未設定（Playwright管理browserを使用） | 同梱Chromiumが利用できない環境向けのbrowser実体パス代替 |

## Validation rules

- LLMのbase URLはcredential/query/fragment、空白・制御文字・backslashを含まないHTTPS、またはloopback HTTPだけを受理します。model IDは256文字以下で空白・制御文字・backslashなしとします。
- `KJ_ATLAS_LLM_PROVIDER=large-scale`, `large_scale`, `external` は `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true`、`KJ_ATLAS_LLM_ESCALATION_ENABLED=true`、base URL、model、allowlistの完全セットを必須にします。allowlistはcanonical hostだけを受理し、URL、wildcard、port、path、空要素、重複を拒否します。base URLのhostnameがallowlistにない構成も起動時に拒否します。
- `KJ_ATLAS_RUNTIME_PROFILE` は `local-dev`, `evaluation`, `enterprise-production`, `saas-multitenant` だけを名前として認識し、`saas-multitenant`は`SAAS-TENANT-01`完了まで起動を拒否します。
- trusted SaaS identity resolver、tenant resolver、active tenant session persisterは環境変数やrequest headerから選択せず、application起動前の同一adapter bundleとしてのみ注入します。3要素の部分設定、起動後の差し替え、未検証のstate objectは拒否し、bundle非注入時はsession APIをfail-closedに保ちます。SaaS bundle有効化時はDocument resource resolverもserver-owned metadata＋trusted binding resolverへ切り替えます。application lifespan終了時は3 adapterをApp stateから同時に無効化し、Document resource resolverもsingle-tenant互換へ戻します。再起動時もruntime profileとの照合を通過するまで再有効化しません。
- `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` は `noop`, `mock`, `external_http` だけを許可します。
- `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` は `read_only`, `deny` だけを許可します。
- `KJ_ATLAS_AUDIT_TRANSPORT`は`noop`, `http`だけを許可します。監査HTTPと外部PDPのendpointはcredential/query/fragment、空白・制御文字・backslashを含まないHTTPS、またはloopback HTTPだけを受理し、port不正も拒否します。`http` / `external_http` を明示選択した場合は対応endpointを必須とし、欠損時はnoopへfallbackせず起動を拒否します。HTTP連携を無効にしたままendpoint/API keyを残すことや、endpointなしでbearer/IdP issuerだけを設定することも拒否します。
- 監査HTTPと外部PDPのtimeoutは`0 < value <= 30`、監査queueは1以上を必須にします。固定bearerは空値・空白・制御文字を、IdP issuer header値は2,048文字超・前後空白・制御文字を拒否し、validation errorへ入力値を反射しません。
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
| `external_http` endpoint 未設定時の挙動 | `ADR-0062`でfail-fastを採択。明示した外部HTTP連携はendpointを必須とし、欠損時は起動拒否する。 | 既定 `noop` は維持し、完全設定された連携の実行時障害は既存fail-safe/fail-openへ委譲する。 |
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
   - frontend build は `envPrefix: "KJ_ATLAS_"` とし、`KJ_ATLAS_RUNTIME_PROFILE`と`KJ_ATLAS_FRONTEND_API_BASE`だけを読み取る。旧frontendキーの互換shimは設けない。

### Plan → Execute → Verify → Proceed gate

- Plan: 変更前に `Naming / Defaults / Boundary / Profiles` の4観点を固定する。
- Execute: 公開契約の更新を先に行い、実装・deploy・docs を追随させる。
- Verify: docs-check + settings validation + compose config で同一キー集合を確認する。
- Proceed: 4観点がすべて pass の場合のみ進行し、1つでも fail なら停止して Issue/ADR へ戻す。

### Failure budget（3回失敗で停止）

- 同一論点で Verify が3回連続失敗した場合、4回目の試行に進まず **Stop** とする。
- Stop 時は「失敗原因」「再開条件」「要追加判断（ADR/Issue）」を `01_Plans/issues/` に記録する。
