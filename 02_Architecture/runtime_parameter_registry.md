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

この表は、代表的な実行環境ごとの operating condition を示します。`KJ_ATLAS_RUNTIME_PROFILE`でprofile名を明示し、未指定時は`local-dev`を使います。`Startup-required conditions` はそのprofileを起動するために満たす hard gate、`Recommended / conditional settings` は安全・標準として推奨する値または特定機能を使う場合だけ必要な値です。profile名だけで秘密値や接続先を補完しません。実装既定値を変更する場合や、公開設定キーを追加・改名する場合はADRで扱います。

| Profile | Purpose | Startup-required conditions | Recommended / conditional settings | Notes |
|---|---|---|---|---|
| `local-dev` | 開発者の手元で最小起動する | なし（追加のprofile固有hard gateなし） | 推奨: `KJ_ATLAS_DATABASE_URL=sqlite:///./kj_atlas.db`, `KJ_ATLAS_LLM_PROVIDER=none`。条件付き: ヘッダー由来の未登録ユーザーを JIT 自動作成する場合だけ `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` | 実装既定値だけでも起動可能。外部サービスを使わずに動作確認し、共有・export の安全境界は緩めない。 |
| `evaluation` | Docker Compose で利用者評価や検証を行う | なし（追加のprofile固有hard gateなし） | 推奨: `KJ_ATLAS_DATABASE_URL=postgresql+asyncpg://...`, `KJ_ATLAS_LLM_PROVIDER=none`, `KJ_ATLAS_AUDIT_TRANSPORT=noop`, `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=noop` | 標準 Compose での評価構成。外部監査/外部PDPは必要な場合だけ明示有効化する。 |
| `enterprise-production` | 企業・行政の本番相当で運用する | `KJ_ATLAS_ADMIN_API_KEY=<secret>`, `KJ_ATLAS_API_KEY=<secret>` | 推奨: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`, `KJ_ATLAS_LLM_PROVIDER=none`, `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=read_only` または `deny` | 2つのAPI keyは別値で必須。未設定なら `Settings()` 構築時に起動拒否する。HTTP連携を使う場合は接続先、timeout、fail-safe、秘密情報管理を同時に確認する。 |
| `saas-multitenant` | 相互に信頼しない複数tenantを同じサービスへ収容する | `KJ_ATLAS_ADMIN_API_KEY=<secret>`, `KJ_ATLAS_DATABASE_URL=<PostgreSQL URL>`, `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`, `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http`, `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT=<HTTPS URL>`, `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=deny`, `KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER=external_http`, `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT=<HTTPS URL>`, `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER=external_http`, `KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT=<HTTPS URL>`, `KJ_ATLAS_JWT_ALGORITHMS` の非空allowlist（未指定は既定 `RS256,ES256`、設定時は既知の非HMAC asymmetric algorithmのみ）, `KJ_ATLAS_TENANT_CLAIM_NAME=tenant_ref`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT=<HTTPS URL>`, `KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY=<64 lowercase hex>` | OAuth BFF request時の条件付き設定: `/session/login` 開始には `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID`。`/session/callback` の code 交換には `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID`, `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET` の4項目完全セット | `TrustedSaasRuntimePolicy.validate()` と lifespan preflight がstartup hard gateを検証する。active IdP の存在はDB初期化後に診断するが、0件でもprocess startupは拒否せずwarningを出す。control-plane credentialで最初のproviderを登録でき、登録までは認証requestが失敗する。login開始用2項目の欠損は`/session/login`を503、callback用4項目の欠損は`/session/callback`を503でfail-closedする。 |

Profile に関係なく、利用者が設定する公開環境変数は例外なく `KJ_ATLAS_*` で始めます。サードパーティが別名を要求する場合は、実装または deployment adapter が内部で写像します。

### Profile default vs recommendation（既定値と推奨値）

運用ドリフトを防ぐため、実装既定値（未設定時）と profile 推奨値（運用上の標準）を区別して扱います。

| Key | Implementation default | Enterprise recommendation | Rationale |
| --- | --- | --- | --- |
| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `false` | `false` | 未認証の未知ヘッダー由来ユーザー自動作成（濫用可能）を防ぐため既定は `false`（SEC-RATE-LIMIT-01・2026-08-13）。`local-dev` / `evaluation` でヘッダー由来ユーザーを使う場合は明示 `true`。本番は `false` 固定推奨。 |
| `KJ_ATLAS_MAX_DOCUMENT_BYTES` | `20971520`（20 MiB） | 任意の正整数 | DocumentV1 保存ペイロードの UTF-8 バイト上限（SEC-DOC-BOUND-01・2026-08-13）。inquiry bundle の 20 MiB と対称。超えると 413 `document_too_large`。 |
| `KJ_ATLAS_MAX_DOCUMENT_CARDS` | `50000` | 任意の正整数 | DocumentV1 のカード件数上限（SEC-DOC-BOUND-01。2026-08-17 のmeta-dogfoodingで数万枚規模へ達する累積型KJ canvasを踏まえ、20,000-card targetに余白を持たせて50,000へ拡張）。バイト上限の二次防御（小さいカード本文で 20 MiB 未満に収まる病態的件数を抑止）。超えると 413 `document_too_many_cards`。 |
| `KJ_ATLAS_ALLOW_UNREVIEWED_AI_TEXT` | `false` | `false` または `true` | SEC-AI-SAFEMODE-01（ADR-0068 D1=C）の緩和ゲート。`true` のときのみ、AI リクエストの `allowUnreviewedText: true`（未レビュー本文の送出許可）が有効になる。既定 `false` は fail-closed（未レビュー本文は常に 422 で拒否）。 |
| `KJ_ATLAS_ADMIN_API_KEY` | 未設定 | **必須** | ADR-0072 D3=A: `enterprise-production` / `saas-multitenant` では未設定なら `Settings()` 構築時に fail-fast する。`enterprise-production` は加えて `KJ_ATLAS_API_KEY` も必須（業務面の識別を前段proxyのheaderに依存するため）。`saas-multitenant` の業務面は trusted auth edge のJWTが担うため `KJ_ATLAS_API_KEY` は必須としない |
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
4. `saas-multitenant` を選ぶ条件
   - PostgreSQL共有認証状態、trusted SaaS auth edge、external access control、external document binding、external tenant capability、JIT無効、`deny` fail-safeなど、`TrustedSaasRuntimePolicy` の必須条件を満たす。
   - 起動前preflightのhard gateを通過できる。hard gateが1つでも欠ける場合はfail-fastし、single-tenant profileへfallbackしない。active IdP存在検査はpost-DB-initのwarning診断であり、provider 0件自体はstartup拒否条件ではない。

### SaaS profile implementation gate（ADR-0059）

- `KJ_ATLAS_RUNTIME_PROFILE`でprofileを明示選択する。`local-dev`、`evaluation`、`enterprise-production`は正規化して受理する。
- `saas-multitenant`は必須policy、実adapter、PostgreSQL共有認証表をすべて起動前検査し、不足時はfail-fastする。無視して`local-dev`やin-memory状態へfallbackしない。
- backendのtrusted SaaS adapter bundleは`saas-multitenant`と相互必須である。profile、非秘密runtime safety policy、bundleの型・欠損・相互必須、started-stateに加え、構築済みPDP／capability／binding componentの実型を状態変更なしでpreflightし、DB初期化前とadapter有効化前に同じ判定を再実行する。single-tenant profileへのbundle注入、SaaS profileでのbundle欠損、未知profile、設定はexternalでも実componentがnoop／unavailableとなる構成はDB接続前に起動拒否する。runtime safety policyはPostgreSQL、JIT無効、external access-control、`deny` fail-safe、external document binding、external tenant capabilityを必須とし、実componentも`ExternalPolicyAccessControlAdapter`、`ExternalHttpTenantCapabilityResolver`、`ExternalHttpDocumentPolicyBindingResolver`の完全セットを必須とする。SaaS profileを受理する現行実装でも、この完全セットが欠ける構成は起動しない。
- backendはvalidation済みprofileを起動時にsnapshotし、`GET /session/bootstrap-policy`でprofile名を公開せず`single-tenant`または`tenant-session-required`へclosed-worldに写像する。frontend buildも同じprofileを受け取り、既存3 profileはpolicy通信なしでlocal-first起動、`saas-multitenant`だけはserver policy一致とsession bootstrap成功までAppをmountしない。未知・空・非canonical build値、policy不一致・取得失敗はsingle-tenantへfallbackせずblocked stateへ閉じる。
- 現行実装はtenant解決、PDP、DB guardを含むcross-key validationとpreflightがすべて成立した場合だけSaaS起動を許可し、欠ける構成は起動拒否を維持する。
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
| `KJ_ATLAS_RUNTIME_PROFILE` | `local-dev` | Backend/MCPの実行profile。`local-dev`, `evaluation`, `enterprise-production`, `saas-multitenant`を受理する。SaaS backendはPostgreSQL共有認証表と必須policyを検査し、不足時は起動拒否。 | direct / base Compose | 通常値 | `GET /version` の `runtimeProfile` が設定後のvalidated profileと一致することを確認する。`/healthz` はliveness-onlyでprofileを返さない |
| `KJ_ATLAS_LOG_LEVEL` | `INFO` | OPS-OBSERV-01: アプリケーションログの出力レベル（`CRITICAL`/`ERROR`/`WARNING`/`INFO`/`DEBUG`）。不正値は `INFO` へ丸める。uvicorn のロガーも同じハンドラへ束ねる | direct | 通常値 | 起動ログが指定レベルで出ること、`DEBUG` で件数が増えることを確認する |
| `KJ_ATLAS_LOG_JSON` | `true` | OPS-OBSERV-01: ログを1行1JSONで出力する。`true` では caller-supplied `extra={...}` の `tenantId` / `docId` / `queueLength` / LLM `trace_id` などを構造化fieldとして出力する。`false` ではこれらextra fieldは出力せず、人間可読書式に correlation metadata の `requestId` / `actorRefHash` / `appRevision` を残す | direct | 通常値 | `true` でextra fieldがJSON fieldとして出ること、`false` で `requestId` / `actorRefHash` / `appRevision` が人間可読書式に残ることを確認する |
| `KJ_ATLAS_APP_REVISION` | `unknown` | OPS-OBSERV-01: 稼働中のcanonicalビルド識別子。1〜64文字のASCII `A-Za-z0-9._-` のみ受理し、それ以外（空文字、前後空白、slash、記号、改行、65文字以上）は `unknown` に丸める。backend は `GET /version` と全アプリケーションログの `appRevision` で返し、frontend は同じ規則で診断バンドルの `app.revision` に載せる。frontend へは build ARG として渡す（`vite.config.ts` の `envPrefix` 経由）ため、ビルド時に確定する | direct / base Compose | 通常値 | canonical値では `GET /version.revision`・ログ `appRevision`・診断バンドル `app.revision` が同値になること、不正値ではすべて `unknown` になることを確認する |
| `KJ_ATLAS_DATABASE_URL` | `sqlite:///./kj_atlas.db` | 永続化 DB 接続先。Verifiedの検証対象versionと利用範囲は`database_portability.md`を正本とする。candidate/未知DBはengine生成・migration前に拒否する | direct / base Compose | 資格情報を含み得る（URL に password を埋め込む場合がある） | `GET /readyz` が 200 `status=ready` かつ `checks.database=ok` / `checks.schema=ok` を返すことを確認する。`/healthz` はliveness-onlyでDBを検査しない。URL値は出力しない |
| `KJ_ATLAS_LLM_PROVIDER` | `none` | LLM provider 種別。`none`, `local`, `local_http`, `large-scale`, `large_scale`, `external`, `deepseek`。起動時fail-fastの対象となる**プロセス既定/フォールバック transport**であり、`model` を指定しないAI呼び出しに使う。AI-MODEL-GOVERNANCE-03以降、`model` を指定するAI呼び出しはmodel自身のregistry上の `providerKind` へ動的dispatchするため、この値と一致しないproviderへも（その `providerKind` 自身の設定が完全なら）到達し得る。`none` は無条件のkill switchであり、この場合は動的dispatchを含め一切のAI呼び出しを行わない | direct / base Compose | 通常値 | `GET /ai/provider-status` の `providerKind` で実際に解決されたcanonical runtime kindを確認する。aliasは `local_http`→`local`、`large_scale`/`external`→`large-scale`。`/healthz` はliveness-onlyでproviderを返さない |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL` | 未設定 | local LLM のbase URL。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 | direct / llm-stub overlay のみ | 通常値（接続先ホスト名。認証情報は含まない） | overlay 使用時、`local` provider 経由のリクエストが stub へ到達すること（成否のみ確認、payload は出力しない） |
| `KJ_ATLAS_LOCAL_LLM_MODEL` | 未設定 | local LLM に渡す256文字以下のcanonical model ID | direct / llm-stub overlay のみ | 通常値 | stub 側ログの model 欄が設定値と一致することを確認する |
| `KJ_ATLAS_LLM_TASK_MODEL_MAP` | 未設定（空文字） | ADR-0065: タスク別モデル割当（`task=model,...`）。未設定タスクは既定モデル。 | direct | 通常値 | 指定 task のリクエスト model が設定値と一致することをログで確認する |
| `KJ_ATLAS_LLM_HIGH_REASONING_MODEL` | 未設定 | AI-ROUTE-01 MMR-04: final_judgement系タスク（check_narrative/detect_contradiction）の既定モデル。未設定時は既定モデルへフォールバック。 | direct | 通常値 | final_judgementタスクのリクエスト model が設定値と一致することをログで確認する |
| `KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL` | 未設定 | large-scale LLM のbase URL。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 | direct | 通常値（接続先ホスト名。認証情報は別キー） | allowlist 外ホストを設定した場合に呼び出しが拒否されることを確認する |
| `KJ_ATLAS_LARGE_SCALE_LLM_MODEL` | 未設定 | large-scale LLM に渡す256文字以下のcanonical model ID | direct | 通常値 | 呼び出しペイロードの model フィールドが設定値と一致することを確認する |
| `KJ_ATLAS_LLM_ESCALATION_ENABLED` | `false` | 互換名は escalation だが、現行実装では large-scale provider kind の実行gate。primary `large-scale`/`external` の起動readiness、registered large-scale providerの構築、`LargeScaleProvider.generate()` の全経路で `true` が必要。別途 `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true` も必須 | direct | 通常値 | `false` で primary large-scale設定がreadiness失敗し、registered large-scale providerがunavailable、直接large-scale実行も `provider_unavailable` になることを確認する |
| `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN` | `false` | large-scale LLM 利用の明示 opt-in | direct | 通常値 | `false` のとき `large-scale`/`external` provider 指定が起動時に拒否されることを確認する（validator で既に強制） |
| `KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST` | 未設定 | large-scale接続を許可するcanonical hostのカンマ区切り。URL、wildcard、port、path、重複は不可 | direct | 通常値（ホスト名リスト。認証情報を含まない） | allowlist 外ホストへの接続が拒否されることを確認する |
| `KJ_ATLAS_LLM_FALLBACK_TO_NONE` | `true` | `provider_unavailable` / `provider_timeout` を成功応答へ切り替えず、`none` metadata（`fallback_to_none=true`, `execution_path=<provider>->none`）付き `ProviderDisabledError` としてfail-closedする。`provider_validation` はfallback対象外。`false` では元の `ProviderRequestError` を維持する | direct | 通常値 | unavailable/timeoutを模擬し、`true` では `provider_kind=none`・`fallback_to_none=true`・`<provider>->none` を持つ `ProviderDisabledError`、`false` またはvalidationでは元エラーになることを確認する |
| `KJ_ATLAS_DEEPSEEK_API_KEY` | 未設定 | DeepSeek API 認証キー。primary `KJ_ATLAS_LLM_PROVIDER=deepseek` では起動readinessの必須値。registered DeepSeek providerでは `api_key_ref=KJ_ATLAS_DEEPSEEK_API_KEY` のrequest-time credential sourceとして使い、解決不能なら provider unavailable へfail-closedする | direct | 秘密値 | 未設定時、primary deepseekは起動拒否されること。registered DeepSeek + `api_key_ref=KJ_ATLAS_DEEPSEEK_API_KEY` は credential unavailable となり、設定時だけ構築可能になることを確認する（秘密値は出力しない） |
| `KJ_ATLAS_DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | DeepSeek API のbase URL。credential/query/fragmentなしのHTTPS | direct | 通常値（接続先URL。認証情報は別キー） | リクエストが正しいURLへ送信されることを確認する |
| `KJ_ATLAS_DEEPSEEK_MODEL` | `deepseek-v4-flash` | DeepSeek API に渡すmodel ID。256文字以下のcanonical | direct | 通常値 | 呼び出しペイロードの model フィールドが設定値と一致することを確認する |
| `KJ_ATLAS_DEEPSEEK_THINKING_MODE` | `disabled` | DeepSeek V4 Chat Completionsのthinking mode。`disabled` / `enabled`。旧 `deepseek-chat` のnon-thinking semanticsを保つため既定はdisabled | direct | 通常値 | DeepSeek送信payloadの `thinking.type` が設定値と一致することを確認する |
| `KJ_ATLAS_API_KEY` | 未設定 | business-plane APIを `X-API-Key` で保護する。`/healthz` / `/readyz` / `/version` は運用probeとして常に対象外。`/admin/*` もbusiness keyの対象外で、`X-Admin-Api-Key` またはprovision capabilityによるcontrol-plane認可へ分離する | direct / base Compose | 秘密値 | business-plane routeでキーなし/誤りが401、正しいキーが成功すること。3つの運用probeはキーなしで到達でき、`/admin/*` はbusiness keyではなくcontrol-plane資格情報で認可されることを確認する |
| `KJ_ATLAS_ADMIN_API_KEY` | 未設定 | ADR-0072 D1=A+B: control-plane の Stage A bootstrap 資格情報。`X-Admin-Api-Key` で提示する。Stage B では trusted SaaS session の `tenant.provision` capability でも認可でき、request に admin bearer は不要。**業務面の `KJ_ATLAS_API_KEY` はどちらの Stage でも受理せず、同じ秘密値の設定も起動時に拒否する**。`enterprise-production` / `saas-multitenant` では設定自体が起動必須。`local-dev` / `evaluation` では未設定時だけ development 用に control plane を開く。IdP未登録 bootstrap では Stage B を使えないため Stage A が production の経路 | direct | 秘密値 | 業務面キーで `/admin/provision/*` が 401、正しい `X-Admin-Api-Key` が成功、trusted SaaS session + `tenant.provision` も admin bearer なしで成功することを確認する。併せて両キー同値がSettings構築で拒否されることを確認する（秘密値自体は出力しない） |
| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | audit export のmaster gate。`false` では configured transport に関係なく dispatcher は無効化され `NoopAuditTransport` を使い、外部送信しない。`true` のときだけ `KJ_ATLAS_AUDIT_TRANSPORT` が実送信transportを選ぶ | direct | 通常値 | `false` ではtest doubleへ1件も到達しないこと、`true` + `http` では監査イベントがtest doubleへ到達することを確認する |
| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | audit transport。`noop` または `http`。実送信transportとして作用するのは `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true` の場合だけで、export無効時は `http` 指定でも dispatcher は `NoopAuditTransport` を使う | direct | 通常値 | transport名の正常時startup self-reportはない。`AUDIT_EXPORT_ENABLED=true` + `http` + test doubleでPOST到達を確認し、export無効時は到達しないことを確認する |
| `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` | 未設定 | 監査ログHTTP連携の接続先。`KJ_ATLAS_AUDIT_TRANSPORT=http` 時は必須 | direct | 通常値（接続先URL。認証情報は別キー） | test double への到達確認（実サービスへは送らない） |
| `KJ_ATLAS_AUDIT_HTTP_API_KEY` | 未設定 | 監査ログHTTP連携用 API key | direct | 秘密値 | 送信ヘッダにキーが付与されることを確認する（値はマスクして確認） |
| `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS` | `2.0` | audit HTTP timeout 秒数 | direct | 通常値 | timeout 超過時に監査送出が失敗として扱われることを確認する |
| `KJ_ATLAS_AUDIT_QUEUE_SIZE` | `100` | audit queue 上限 | direct | 通常値 | 上限到達時の drop 挙動をログで確認する |
| `KJ_ATLAS_AUDIT_DEDUP_WINDOW_SECONDS` | `5.0` | 監査イベントの同一論理操作dedupウィンドウ（SEC-AUDIT-DUP-01）。`0` で無効化 | direct | 通常値 | 同一論理操作の二重POSTで外部シンクへ1件のみ送出されることを確認する |
| `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE` | `false` | SafeMode 中の監査ログHTTP連携を許可する | direct | 通常値 | SafeMode 中に `false` のとき監査HTTP送出が抑止されることを確認する |
| `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` | `noop` | access control adapter。`noop`, `mock`, `external_http` | direct | 通常値 | adapter名のstartup self-reportはない。`saas-multitenant` では起動前preflightが `ExternalPolicyAccessControlAdapter` の実型を要求し、`external_http` の個別配送はPDP test doubleへの到達で確認する |
| `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` | `read_only` | access control 障害時の動作。`read_only` または `deny` | direct | 通常値 | 外部PDP障害を模擬し、`read_only`/`deny` いずれの挙動になるか確認する |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` | 未設定 | `external_http` adapter が利用する必須のPDP接続先 | direct | 通常値 | test double への到達確認（実 PDP へは送らない） |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS` | `1.5` | `external_http` adapter の timeout 秒数 | direct | 通常値 | timeout 超過時に fail-safe mode の挙動が発火することを確認する |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | `external_http` adapter がPDPへ渡す認証方式metadata。`none`, `oidc`, `saml` を `x-acl-auth-mode` headerへ写す。この値自体は `Authorization` headerを生成・変更せず、固定bearerは別設定 `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` が担う | direct | 通常値 | PDP test doubleで `x-acl-auth-mode` が設定値と一致することを確認する。`Authorization` はこの値だけでは付与されないことも確認する |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` | 未設定 | `external_http` adapter の固定 bearer token | direct | 秘密値 | PDP リクエストに Bearer ヘッダが付与されることを確認する（値はマスク） |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | 未設定 | `external_http` adapter がPDPへ渡すIdP issuer metadata。canonical header valueとして検査し、設定時は `x-idp-issuer` headerへ写す。この設定自体はJWT/SAML issuerのローカル検証を行わない | direct | 通常値 | PDP test doubleで `x-idp-issuer` が設定値と一致することを確認する。issuer検証の結果を示すProbeとしては扱わない |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER` | `none` | server-owned binding IDを一時的なpolicyRefへ解決するresolver。`none`, `external_http`。`saas-multitenant` では `external_http` が必須で、起動前にexternal componentを検査し、`ServerOwnedDocumentResourceResolver` の policy binding resolver として配線 | direct | 通常値 | resolver名のstartup self-reportはない。`saas-multitenant` では起動前preflightが `ExternalHttpDocumentPolicyBindingResolver` の実型を要求し、`external_http` の個別配送はbinding service test doubleへのlookup到達で確認する |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT` | 未設定 | binding resolverの接続先。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 | direct | 通常値（接続先URL。認証情報は別キー） | test double への到達確認（実サービスへは送らない） |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY` | 未設定 | binding resolver専用の固定bearer token。DB・監査・diagnosticsへ出力しない | direct | 秘密値 | 送信ヘッダにキーが付与されることを確認する（値はマスクして確認） |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_TIMEOUT_SECONDS` | `1.5` | binding resolverのtimeout秒数。`0 < value <= 30` | direct | 通常値 | timeout 超過時に resolver が fail-closed へ倒れることを確認する |
| `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER` | `none` | tenant-scoped effective capability resolver。`none`, `external_http`。`saas-multitenant` では `external_http` が必須で、起動前にexternal componentを検査し、runtimeの tenant capability resolver として配線 | direct | 通常値 | resolver名のstartup self-reportはない。`saas-multitenant` では起動前preflightが `ExternalHttpTenantCapabilityResolver` の実型を要求し、`external_http` の個別配送はcapability service test doubleへのlookup到達で確認する |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT` | 未設定 | capability resolverの接続先。credential/query/fragmentなしのHTTPS、またはloopback HTTPだけを許可 | direct | 通常値（接続先URL。認証情報は別キー） | test double への到達確認（実サービスへは送らない） |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY` | 未設定 | capability resolver専用の固定bearer token。DB・監査・diagnosticsへ出力しない | direct | 秘密値 | 送信ヘッダにキーが付与されることを確認する（値はマスクして確認） |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_TIMEOUT_SECONDS` | `1.5` | capability resolverのtimeout秒数。`0 < value <= 30` | direct | 通常値 | timeout 超過時に resolver が fail-closed へ倒れることを確認する |
| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `false` | single-tenant の forwarded-header identity path にだけ作用するJIT provisioning gate。未登録 provider/subject で `true` の場合は user・identity binding・local-default membership を作成し、`false` では 403 `identity_not_provisioned`。`saas-multitenant` は起動policyで `false` を必須とし、trusted JWT/cookie identity resolver はこの設定を参照せず未登録subjectを常に403で拒否する（SEC-RATE-LIMIT-01） | direct / base Compose | 通常値 | single-tenant header pathで `false` 時は未登録identityが403かつ新規作成されず、`true` 時だけ作成されること。SaaSでは `true` が起動拒否され、未登録subjectが設定値に関係なく403になることを確認する |
| `KJ_ATLAS_MAX_DOCUMENT_BYTES` | `20971520` | DocumentV1 保存ペイロードの UTF-8 バイト上限（20 MiB・SEC-DOC-BOUND-01） | direct | 通常値 | 超えるペイロードで 413 `document_too_large` を確認する |
| `KJ_ATLAS_MAX_DOCUMENT_CARDS` | `50000` | DocumentV1 のカード件数上限（SEC-DOC-BOUND-01） | direct | 通常値 | 超えるカード件数で 413 `document_too_many_cards` を確認する |
| `KJ_ATLAS_ALLOW_UNREVIEWED_AI_TEXT` | `false` | AI リクエストの `allowUnreviewedText` 緩和を許可するか（SEC-AI-SAFEMODE-01 / ADR-0068） | direct | 通常値 | `false` 時、未レビュー本文を含む `/ai/*` リクエストが 422 で拒否されることを確認する |
| `KJ_ATLAS_AUTH_PROVIDER_FIELD` | `x-auth-provider` | single-tenant の forwarded-header identity path で external identity provider を受け取る header 名。trim・lowercase正規化し、欠損/空値は `header`。`saas-multitenant` の trusted JWT/cookie path では使用しない | direct | 通常値 | single-tenant header pathで指定値が正規化され `AuthContext.provider` へ反映され、欠損時は `header` になることを確認する |
| `KJ_ATLAS_AUTH_USER_FIELD` | `x-forwarded-user` | single-tenant の forwarded-header identity path で `AUTH_SUBJECT_FIELD` 欠損時の external UID/subject fallback を受け取る legacy header 名。内部 `users.id` を直接指定しない。`saas-multitenant` の trusted JWT/cookie path では使用しない | direct | 通常値 | subject header欠損時だけ指定 header が `AuthContext.external_uid` へ反映され、内部 `users.id` はidentity mappingから解決されることを確認する |
| `KJ_ATLAS_AUTH_EMAIL_FIELD` | `x-forwarded-email` | single-tenant の forwarded-header identity path でJIT provisioning時に新規 `UserRow.email` を初期化する header 名。既存user属性は更新しない。`saas-multitenant` の trusted JWT/cookie path では使用しない | direct | 通常値 | JITで新規userを作る時だけ指定値が `UserRow.email` に入り、既存user requestでは属性が上書きされないことを確認する |
| `KJ_ATLAS_AUTH_NAME_FIELD` | `x-forwarded-name` | single-tenant の forwarded-header identity path でJIT provisioning時に新規 `UserRow.display_name` を初期化する header 名。既存user属性は更新しない。`saas-multitenant` の trusted JWT/cookie path では使用しない | direct | 通常値 | JITで新規userを作る時だけ指定値が `UserRow.display_name` に入り、既存user requestでは属性が上書きされないことを確認する |
| `KJ_ATLAS_AUTH_SUBJECT_FIELD` | `x-auth-subject` | single-tenant の forwarded-header identity path で external UID/subject の第一候補を受け取る header 名。欠損時だけ `AUTH_USER_FIELD` へfallbackする。`saas-multitenant` の trusted JWT/cookie path では使用しない | direct | 通常値 | subject headerがあれば `AUTH_USER_FIELD` より優先して `AuthContext.external_uid` へ反映されることを確認する |
| `KJ_ATLAS_JWT_ALGORITHMS` | `RS256,ES256` | trusted OIDC/JWT 署名検証の algorithm allowlist（カンマ区切り）。受理値は `RS256`, `RS384`, `RS512`, `ES256`, `ES384`, `ES512`, `PS256`, `PS384`, `PS512`。空list、HMAC 系、`none` を含む未知値は Settings validation で起動時に拒否する | direct | 通常値 | 非defaultの既知algorithmを設定でき、設定allowlist外のalgorithmで署名されたJWTが401、HMAC/未知値は起動時に拒否されることを確認する |
| `KJ_ATLAS_TENANT_CLAIM_NAME` | `tenant_ref` | JWT 内の tenant 外部識別子を運ぶ claim 名。`tenant_identity_providers.external_tenant_ref` と照合する。 | direct | 通常値 | 指定 claim が存在しない JWT が 401 で拒否されることを確認する |
| `KJ_ATLAS_TRUSTED_PROXIES` | （空） | header 認証の信頼できるプロキシ CIDR のカンマ区切りリスト。未設定時は全オリジン許可（開発用・警告ログ出力）。本番では `10.0.0.0/8` 等でプロキシを限定すること。`saas-multitenant` では JWT 認証必須のため不要。 | direct | 通常値 | 非信頼 IP からの forwarded auth header が 403 で拒否されることを確認する |
| `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER` | `user_id` | reviewerRef 解決 adapter。`user_id` または `sso_subject` | direct | 通常値 | reviewerRef の解決方式が選択値（`user_id`/`sso_subject`）どおりであることを確認する |
| `KJ_ATLAS_CE4_EQUIVALENCE_MODE` | `equivalence_and_bundle_hash` | CE4 同値性判定 mode | fixed | 通常値 | 既定値以外を設定すると起動時に拒否されることを確認する |
| `KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT` | `true` | CE4 dry-run が副作用なしであることを強制する | fixed | 通常値 | `false` 設定時に起動が拒否されることを確認する |
| `KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS` | `true` | CE4 の query/bundle/proposal/apply audit 欠損を fail-closed にする | fixed | 通常値 | `false` 設定時に起動が拒否されることを確認する |
| `KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK` | `true` | docs CE4 の `POST /docs/{doc_id}/context-audit` で `sourceBundleHash=mock:<hash>` を許容する。proposal / CE4 resolve の受理契約は各 API 正本に従い、この switch の対象外 | direct（docs CE4 policy） | 通常値 | `false` 設定時に `/docs/{doc_id}/context-audit` の `mock:` prefix が `422 mock_source_bundle_hash_disabled` で拒否されることを確認する |
| `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS` | `true` | 未確定 CE4 契約を stub 応答で隔離し、成功扱いにしない安全契約。未確定 stub trigger の runtime 契約が実装されるまで `true` 固定 | fixed | 通常値 | `false` 設定時に起動が拒否されることを確認する |
| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT` | 未設定 | BFF が authorization code 交換の前にリダイレクトする IdP の authorize endpoint（SAAS-TENANT-SESSION-BINDING-01 / ADR-0074）。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可し、必須性は TrustedSaasRuntimePolicy が担う | direct | 通常値（接続先URL。認証情報は別キー） | saas-multitenant で OAuth フローが開始されることを確認する |
| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT` | 未設定 | BFF が authorization code を token へ交換する IdP の token endpoint（ADR-0074）。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可。process startup hard gateではないが、`/session/callback` の code 交換では redirect URI / client ID / client secret と4項目完全セットで必要で、欠損時は503でfail-closed | direct | 通常値（接続先URL。認証情報は別キー） | token 交換リクエストが正しい endpoint へ送信されること、欠損時にcallbackが503になることを確認する |
| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI` | 未設定 | OAuth フローの redirect URI（ADR-0074）。credential/query/fragment なしの HTTPS、または loopback HTTP だけを許可し、path は `/session/callback` 固定。process startup hard gateではないが、`/session/login` 開始時は client ID とともに必要で、callbackの code 交換では token endpoint / client ID / client secret と4項目完全セットで必要。欠損時は該当requestを503でfail-closed | direct | 通常値（接続先URL。認証情報は別キー） | login開始とcallback code交換で設定値が使われ、欠損時に該当requestが503になることを確認する |
| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID` | 未設定 | confidential-client OAuth の client ID（ADR-0074）。process startup hard gateではないが、`/session/login` 開始時は redirect URI とともに必要で、callbackの code 交換では token endpoint / redirect URI / client secret と4項目完全セットで必要。欠損時は該当requestを503でfail-closed | direct | 通常値 | 認可リクエストの client_id が設定値と一致し、欠損時に該当requestが503になることを確認する |
| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET` | 未設定 | confidential-client OAuth の client secret（ADR-0074）。process startup hard gateではないが、`/session/callback` の code 交換では token endpoint / redirect URI / client ID と4項目完全セットで必要で、欠損時は503でfail-closed | direct | 秘密値 | 設定後にtoken交換が成功し、欠損時にcallbackが503になることを確認する（値自体は出力しない） |
| `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TIMEOUT_SECONDS` | `5.0` | OAuth broker の HTTP タイムアウト秒（0 < x ≤ 30） | direct | 通常値 | タイムアウト超過時にエラーへ倒れることを確認する |
| `KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY` | 未設定 | auth-session cookie 値の HMAC-SHA256 ハッシュ用キー（ADR-0074 decision 2、64文字 lowercase hex = 32 bytes）。生値を平文保存しない。ローテーション時は新キー設定＋再起動で既存セッションを無効化する | direct | 秘密値 | キー変更で既存セッションが無効化され再ログインへ導かれることを確認する |

## Compose and frontend build keys

| Key | Default | Purpose |
| --- | --- | --- |
| `KJ_ATLAS_WEB_PORT` | `8080` | Compose の web 公開 port |
| `KJ_ATLAS_POSTGRES_DB` | `kj_atlas` | Compose PostgreSQL の database 名 |
| `KJ_ATLAS_POSTGRES_USER` | `kj_atlas` | Compose PostgreSQL の user 名 |
| `KJ_ATLAS_POSTGRES_PASSWORD` | `kj_atlas` | Compose PostgreSQL の password |
| `KJ_ATLAS_RUNTIME_PROFILE` | `local-dev`（Composeは`evaluation`を注入） | frontend entry mode。`local-dev` / `evaluation` / `enterprise-production` はsingle-tenant、`saas-multitenant` はtenant session必須。未知値は起動UIをblockedにする |
| `KJ_ATLAS_FRONTEND_API_BASE` | `/api` | frontend build 時に埋め込む same-origin API base path。標準 Compose は同梱 Nginx の固定 `location /api/` と一致させるため `/api` を固定注入し、host 側のこの値では変更しない。直接 frontend build / 独自 reverse proxy では `/` 自体または単一の `/` で始まる path を受理する。`//host`、backslash、query、fragment、相対 path は `/api` にフォールバック |


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
| `KJ_ATLAS_E2E_REAL_BACKEND` | Playwright e2e (`ai_model_ux_available_models_reason.spec.ts`) | 未設定 | 実backend（mockではない）必須のE2E specを明示的に実行するopt-in flag（`"1"`で有効化）。未設定時は該当specをskipし、backend未起動でも既定の`npm run e2e`を壊さない |
| `KJ_ATLAS_E2E_BACKEND_URL` | Playwright e2e (`ai_model_ux_available_models_reason.spec.ts`) | `http://127.0.0.1:8000` | 上記specがfixture設定（`/admin/provision/models/**`）を直接叩く先のbackend base URL |

## Validation rules

- LLMのbase URLはcredential/query/fragment、空白・制御文字・backslashを含まないHTTPS、またはloopback HTTPだけを受理します。model IDは256文字以下で空白・制御文字・backslashなしとします。
- `KJ_ATLAS_LLM_PROVIDER=large-scale`, `large_scale`, `external` は `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true`、`KJ_ATLAS_LLM_ESCALATION_ENABLED=true`、base URL、model、allowlistの完全セットを必須にします。allowlistはcanonical hostだけを受理し、URL、wildcard、port、path、空要素、重複を拒否します。base URLのhostnameがallowlistにない構成も起動時に拒否します。
- `KJ_ATLAS_RUNTIME_PROFILE` は `local-dev`, `evaluation`, `enterprise-production`, `saas-multitenant` だけを名前として認識し、SaaSは安全条件が欠ける場合だけ起動を拒否します。
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
4. **Profiles**: `local-dev` / `evaluation` / `enterprise-production` の推奨差分が変更理由と整合し、`saas-multitenant`は必須policy・componentが完備した場合だけ起動可能で、不足時はfail-fastすること。
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
