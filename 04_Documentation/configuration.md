# Configuration

対象読者: kj-atlas を起動・運用する管理者、検証担当者。

目的: すべての公開環境変数、安全な既定値、設定変更後の確認方法を示します。

範囲外: 組織固有の秘密管理、未公開ネットワーク情報、承認履歴。

公開区分: 運用者向け公開候補。ここでは利用者が設定する `KJ_ATLAS_*` と既存の既定値だけを扱い、内部 adapter の秘密値や未承認の設定変更は扱いません。

## 基本方針

- kj-atlas の利用者・運用者が設定する環境変数は、すべて例外なく `KJ_ATLAS_` で始まります。
- 接頭辞のない旧キーや、別接頭辞の互換キーは使いません。
- Docker Compose や build tool が内部的に別名を必要とする場合も、利用者が設定する公開キーは `KJ_ATLAS_*` だけです。
- 既定では LLM 連携は無効です。
- 外部サービスとの共有や large-scale LLM の利用は、明示的な opt-in と宛先 allowlist がある場合だけ有効にします。


## 起動面ごとの配送範囲（重要）

このページの `export KJ_ATLAS_*` 例は、backend を直接起動する場合の設定例です。標準 Docker Compose (`docker-compose.yml`) は `KJ_ATLAS_DATABASE_URL` と `KJ_ATLAS_LLM_PROVIDER` の2キーだけを `api` コンテナへ配送します。他のキー（`KJ_ATLAS_API_KEY` や `KJ_ATLAS_ALLOW_JIT_PROVISIONING` を含む）は、Compose の `api.environment` に明示的に追加しない限り、`export` しても標準 Compose 経由では `api` へ届きません。キーごとの配送範囲は [runtime_parameter_registry.md の Backend settings 表](https://github.com/hat47x/kj-atlas/blob/main/02_Architecture/runtime_parameter_registry.md#backend-settings)（`Delivery surface` 列）で確認してください。

## 公開設定と内部adapter境界

| 区分 | 利用者が設定するか | 例 | 取り扱いルール |
| --- | --- | --- | --- |
| 公開設定（public contract） | はい | `KJ_ATLAS_DATABASE_URL`, `KJ_ATLAS_WEB_PORT`, `KJ_ATLAS_POSTGRES_DB`, `KJ_ATLAS_POSTGRES_USER`, `KJ_ATLAS_POSTGRES_PASSWORD` | `KJ_ATLAS_*` のみを設定対象とします。 |
| 内部adapter設定（private boundary） | いいえ | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | third-party コンテナ内部でのみ使用します。公開設定としては受け付けません。 |

## 設定を変える前に

設定は「値を増やす」より先に「何を許可するか」を決めると安全です。

| 確認すること | 例 |
| --- | --- |
| データはどこに保存するか | SQLite か PostgreSQL か |
| 外部サービスと共有する必要があるか | LLM、audit HTTP、access control |
| 失敗したとき安全側に倒れるか | LLM disabled、access control read-only |
| 秘密値をどこで管理するか | shell history や Git に残さない |

## ここで出る用語

| 用語 | 意味 |
| --- | --- |
| 環境変数 | 起動時や build 時にアプリへ渡す設定値です。 |
| 既定値 | 何も設定しないときに使われる値です。 |
| opt-in | 明示的に有効化することです。large-scale LLM は opt-in なしでは使えません。 |
| allowlist | 接続してよい宛先だけを並べた一覧です。 |


## Runtime profiles（推奨プロファイル）

実装既定値（未設定時に使われる値）と、運用で推奨する値は異なる場合があります。
迷った場合は GitHub 上の [runtime_parameter_registry.md](https://github.com/hat47x/kj-atlas/blob/main/02_Architecture/runtime_parameter_registry.md) を参照してください。

- `local-dev`: SQLite + `KJ_ATLAS_LLM_PROVIDER=none` で最小起動。
- `evaluation`: Compose + PostgreSQL で検証。監査HTTPと外部PDPは原則 `noop`。
- `enterprise-production`: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` を基本に、fail-safe を `read_only` または `deny` で固定。
- `saas-multitenant`: PostgreSQL共有認証状態、外部PDP、外部document binding、外部tenant capability、JIT無効、deny fail-safeをすべて満たす場合だけ起動します。

`KJ_ATLAS_RUNTIME_PROFILE`でprofile名を指定します。Docker Composeの既定は`evaluation`、backendを直接起動したときの未指定既定は`local-dev`です。

> 注意: `KJ_ATLAS_ALLOW_JIT_PROVISIONING` の実装既定値は **`false`（fail-closed、2026-08-13 変更）**です。`local-dev` / `evaluation` でヘッダー由来のユーザー自動作成を使う場合は明示 `true` を設定してください。既定 `false` は未認証の未知ヘッダーからのユーザー自動作成（濫用可能）を防ぎます（SEC-RATE-LIMIT-01）。
> 補足: `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` は実装既定値 `read_only` ですが、`enterprise-production` では `read_only` と `deny` のどちらを採るかを事前に固定してください。

## 最小設定

Docker Compose の既定値で起動する場合、通常は追加設定なしで動きます。明示するなら次を使います。

```bash
export KJ_ATLAS_LLM_PROVIDER=none
export KJ_ATLAS_RUNTIME_PROFILE=evaluation
export KJ_ATLAS_DATABASE_URL='postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas'
export KJ_ATLAS_FRONTEND_API_BASE=/api
export KJ_ATLAS_WEB_PORT=8080
```

ローカル SQLite で backend を直接起動する場合:

```bash
export KJ_ATLAS_DATABASE_URL='sqlite:///./kj_atlas.db'
export KJ_ATLAS_RUNTIME_PROFILE=local-dev
export KJ_ATLAS_LLM_PROVIDER=none
```

最初の確認では `KJ_ATLAS_LLM_PROVIDER=none` を推奨します。AI 機能は使えませんが、意図しない外部サービスとの共有を避けながら、保存・表示・受け入れ確認の基本動作を確認できます。

## Backend 環境変数

次の表は backend が受け付ける全環境変数です。

| 変数 | 既定値 | 用途 |
| --- | --- | --- |
| `KJ_ATLAS_RUNTIME_PROFILE` | `local-dev` | `local-dev`, `evaluation`, `enterprise-production`, `saas-multitenant`。SaaSは共有認証表を含む最新migrationと必須policyを起動前検査。 |
| `KJ_ATLAS_DATABASE_URL` | `sqlite:///./kj_atlas.db` | backend が使うSQLAlchemy接続URL。正式対応DB、検証済みdriver、single-tenant／shared-schema SaaSの範囲は[DB対応表](../02_Architecture/database_portability.md)を正本とする。driver省略URLと対応済みasync URLは検証済み同期driverへ正規化され、未検証driverと未知DBはengine生成前に拒否される |
| `KJ_ATLAS_LLM_PROVIDER` | `none` | `none`, `local`, `local_http`, `large-scale`, `large_scale`, `external` |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL` | 未設定 | local LLMのHTTPSまたはloopback HTTP base URL |
| `KJ_ATLAS_LOCAL_LLM_MODEL` | 未設定 | local LLMで使う256文字以下のmodel ID |
| `KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL` | 未設定 | large-scale LLMのHTTPSまたはloopback HTTP base URL |
| `KJ_ATLAS_LARGE_SCALE_LLM_MODEL` | 未設定 | large-scale LLMで使う256文字以下のmodel ID |
| `KJ_ATLAS_LLM_ESCALATION_ENABLED` | `false` | large-scale への昇格許可 |
| `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN` | `false` | large-scale 利用の明示 opt-in |
| `KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST` | 未設定 | large-scale接続を許可するhostのカンマ区切り。URLやwildcardは不可 |
| `KJ_ATLAS_LLM_FALLBACK_TO_NONE` | `true` | LLM 失敗時に `none` へ退避する |
| `KJ_ATLAS_DEEPSEEK_API_KEY` | 未設定 | DeepSeek API 認証キー。`KJ_ATLAS_LLM_PROVIDER=deepseek` 時は必須 |
| `KJ_ATLAS_DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | DeepSeek API のbase URL |
| `KJ_ATLAS_DEEPSEEK_MODEL` | `deepseek-chat` | DeepSeek API に渡すmodel ID |
| `KJ_ATLAS_LLM_TASK_MODEL_MAP` | 未設定 | タスク別モデル割当（`task=model,...`）。未設定タスクは既定モデル |
| `KJ_ATLAS_LLM_HIGH_REASONING_MODEL` | 未設定 | final_judgement系タスク（check_narrative / detect_contradiction / assess_card_importance）の既定モデル。未設定時は既定モデルへフォールバック（AI-ROUTE-01 MMR-04） |
| `KJ_ATLAS_API_KEY` | 未設定 | `/healthz` 以外の API を `X-API-Key` で保護 |
| `KJ_ATLAS_LOG_LEVEL` | `INFO` | アプリケーションログの出力レベル |
| `KJ_ATLAS_LOG_JSON` | `true` | ログを1行1JSONで出力。`tenantId` / `docId` / `requestId` はこの経路で出力される |
| `KJ_ATLAS_APP_REVISION` | 未設定 | 稼働中のビルド識別子。`GET /version` と診断バンドルに現れる |
| `KJ_ATLAS_ADMIN_API_KEY` | 未設定 | 管理面（`/admin/provision/**`）を `X-Admin-Api-Key` で保護。業務面キーでは到達不可。`enterprise-production` / `saas-multitenant` では**必須**（未設定なら起動しない） |
| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | 監査イベントを HTTP の接続先に連携する |
| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | `noop` または `http` |
| `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` | 未設定 | 監査ログ連携の接続先 URL。`KJ_ATLAS_AUDIT_TRANSPORT=http` 時は必須 |
| `KJ_ATLAS_AUDIT_HTTP_API_KEY` | 未設定 | 監査ログの HTTP 連携用 API key |
| `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS` | `2.0` | 監査ログの HTTP 連携の timeout 秒数 |
| `KJ_ATLAS_AUDIT_QUEUE_SIZE` | `100` | 監査ログキューの上限 |
| `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE` | `false` | SafeMode 中に監査ログの HTTP 連携を許可 |
| `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` | `noop` | `noop`, `mock`, `external_http` |
| `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` | `read_only` | `read_only` または `deny` |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` | 未設定 | `external_http` adapter で使う必須のPDP接続先 URL |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS` | `1.5` | `external_http` adapter の timeout 秒数 |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE` | `none` | `none`, `oidc`, `saml` |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN` | 未設定 | `external_http` adapter の固定 bearer token |
| `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` | 未設定 | `external_http` adapter で使う IdP issuer |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER` | `none` | 文書の非秘密binding IDを外部policy参照へ解決するresolver。`none`, `external_http`。現行releaseではSaaS runtime未配線 |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT` | 未設定 | binding resolverのHTTPS接続先。ローカル検証だけloopback HTTP可 |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY` | 未設定 | binding resolver専用bearer token。Git、DB、監査へ保存しない |
| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_TIMEOUT_SECONDS` | `1.5` | binding resolverのtimeout秒数（0より大きく30以下） |
| `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER` | `none` | tenantごとの有効権限を解決するresolver。`none`, `external_http`。現行releaseではauth edge未配線 |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT` | 未設定 | capability resolverのHTTPS接続先。ローカル検証だけloopback HTTP可 |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY` | 未設定 | capability resolver専用bearer token。Git、DB、監査へ保存しない |
| `KJ_ATLAS_TENANT_CAPABILITY_HTTP_TIMEOUT_SECONDS` | `1.5` | capability resolverのtimeout秒数（0より大きく30以下） |
| `KJ_ATLAS_ALLOW_JIT_PROVISIONING` | `false` | 未登録 identity の JIT provisioning を許可（既定は fail-closed。SEC-RATE-LIMIT-01・2026-08-13 変更） |
| `KJ_ATLAS_MAX_DOCUMENT_BYTES` | `20971520` | DocumentV1 保存ペイロードの UTF-8 バイト上限（20 MiB・SEC-DOC-BOUND-01） |
| `KJ_ATLAS_MAX_DOCUMENT_CARDS` | `10000` | DocumentV1 のカード件数上限（SEC-DOC-BOUND-01） |
| `KJ_ATLAS_ALLOW_UNREVIEWED_AI_TEXT` | `false` | AI リクエストの `allowUnreviewedText` 緩和を許可するか（SEC-AI-SAFEMODE-01・ADR-0068） |
| `KJ_ATLAS_AUTH_PROVIDER_FIELD` | `x-auth-provider` | auth provider を受け取る header 名 |
| `KJ_ATLAS_AUTH_USER_FIELD` | `x-forwarded-user` | user id を受け取る header 名 |
| `KJ_ATLAS_AUTH_EMAIL_FIELD` | `x-forwarded-email` | email を受け取る header 名 |
| `KJ_ATLAS_AUTH_NAME_FIELD` | `x-forwarded-name` | display name を受け取る header 名 |
| `KJ_ATLAS_AUTH_SUBJECT_FIELD` | `x-auth-subject` | subject を受け取る header 名 |
| `KJ_ATLAS_JWT_ALGORITHMS` | `RS256,ES256` | JWT 署名検証の algorithm allowlist（カンマ区切り）。HMAC 系および `none` は常に拒否。 |
| `KJ_ATLAS_TENANT_CLAIM_NAME` | `tenant_ref` | JWT 内の tenant 外部識別子を運ぶ claim 名。`tenant_identity_providers.external_tenant_ref` と照合。 |
| `KJ_ATLAS_TRUSTED_PROXIES` | （空） | header 認証の信頼できるプロキシ CIDR（カンマ区切り）。未設定時は全オリジン許可（開発用、警告ログ）。本番では設定を推奨。 |
| `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER` | `user_id` | reviewerRef 解決 adapter。`user_id` または `sso_subject` |
| `KJ_ATLAS_CE4_EQUIVALENCE_MODE` | `equivalence_and_bundle_hash` | CE4 同値性判定 mode |
| `KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT` | `true` | CE4 dry-run が副作用なしであることを強制 |
| `KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS` | `true` | CE4 audit 欠損を fail-closed にする |
| `KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK` | `true` | `sourceBundleHash=mock:<hash>` を許容 |
| `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS` | `true` | 未確定 CE4 契約を stub 応答で隔離 |

## Compose / frontend build 環境変数

次の表は Docker Compose と frontend build で利用者が設定できる全環境変数です。これらもすべて `KJ_ATLAS_` で始まります。

| 変数 | 既定値 | 用途 |
| --- | --- | --- |
| `KJ_ATLAS_WEB_PORT` | `8080` | web の loopback（`127.0.0.1`）port。port 番号だけを変え、LAN など他ホストからの到達可否は変えない |
| `KJ_ATLAS_POSTGRES_DB` | `kj_atlas` | Compose PostgreSQL の database 名 |
| `KJ_ATLAS_POSTGRES_USER` | `kj_atlas` | Compose PostgreSQL の user 名 |
| `KJ_ATLAS_POSTGRES_PASSWORD` | `kj_atlas` | Compose PostgreSQL の password |
| `KJ_ATLAS_RUNTIME_PROFILE` | `evaluation`（Compose） | backendとfrontendへ同じ実行profileを渡す。`saas-multitenant`はPostgreSQL共有認証表と必須外部adapterが必要 |
| `KJ_ATLAS_FRONTEND_API_BASE` | `/api` | frontend が呼び出す API base path |

PostgreSQL image や frontend build tool の内部名は、kj-atlas の公開設定キーではありません。利用者は上の `KJ_ATLAS_*` だけを設定します。

サードパーティイメージや build tool が内部的に別名を要求する場合でも、利用者が設定する kj-atlas の公開設定は `KJ_ATLAS_*` だけに統一します。

## よく使う構成例

### ローカル評価

```bash
export KJ_ATLAS_DATABASE_URL='sqlite:///./kj_atlas.db'
export KJ_ATLAS_RUNTIME_PROFILE=local-dev
export KJ_ATLAS_LLM_PROVIDER=none
```

### Docker Compose 評価

```bash
export KJ_ATLAS_LLM_PROVIDER=none
export KJ_ATLAS_RUNTIME_PROFILE=evaluation
export KJ_ATLAS_WEB_PORT=8080
export KJ_ATLAS_FRONTEND_API_BASE=/api
```

### API key 付き検証

```bash
export KJ_ATLAS_API_KEY='change-me'
```

この値は例です。実運用では推測しにくい値を使い、Git にコミットしないでください。

## Frontend の API 接続先

frontend の API 接続先は `KJ_ATLAS_FRONTEND_API_BASE` で指定します。未設定なら `/api` を使います。値は `/` で始まる path のみ受理し、それ以外を指定した場合は frontend 側で `/api` にフォールバックします。

ローカル開発サーバーと Docker Compose の標準構成では `/api` が backend へ proxy されるため、通常は変更不要です。

直接frontend buildを実行する場合は、build前に`KJ_ATLAS_RUNTIME_PROFILE`と`KJ_ATLAS_FRONTEND_API_BASE`を設定します。profile未指定時はlocal-firstの`local-dev`相当です。空文字、未知値、前後空白を含む値はsingle-tenantへfallbackせずblocked画面になります。

```bash
export KJ_ATLAS_RUNTIME_PROFILE=local-dev
export KJ_ATLAS_FRONTEND_API_BASE=/api
npm run build
```

## API キーを有効にする

```bash
export KJ_ATLAS_API_KEY='change-me'
```

`/healthz` は API キーなしで確認できます。それ以外の API には次のヘッダーを付けます。

```bash
curl -H "X-API-Key: change-me" http://localhost:8080/api/docs/example
```

ブラウザで動く同梱の画面（SPA）は `X-API-Key` を付与しません。そのため `KJ_ATLAS_API_KEY` を設定すると画面からの読み込み・保存は 401 になります。API キーは `curl` などプログラムからのアクセス保護を想定したものです。ブラウザでの動作検証では未設定（既定）のまま使い、ブラウザ配信自体を保護する場合は前段に認証 proxy を置いてください（[security.md](security.md) 参照）。

> 注意: 標準 Docker Compose はこのキーをホスト環境から pass-through 配送します（ホスト側で未設定の場合はコンテナ内でも未設定のままで、既定の無効状態を維持します。[runtime_parameter_registry.md](https://github.com/hat47x/kj-atlas/blob/main/02_Architecture/runtime_parameter_registry.md#backend-settings) 参照）。

## local LLM を使う

local provider は `<base_url>/generate` に JSON を POST します。応答は `{ "text": "..." }` を返す必要があります。

```bash
export KJ_ATLAS_LLM_PROVIDER=local
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
```

base URLにはcredential、query、fragment、空白、制御文字、backslashを含められません。HTTPS、または`localhost`、`127.0.0.1`、`::1`へのHTTPだけを使用できます。model IDは256文字以下で、空白・制御文字・backslashを含められません。

providerへ送るrequestはUTF-8 JSONで1MiB以下です。task、temperature、max token数も安全な範囲へ検証され、過大promptや不正な数値は接続前に`provider_validation`として拒否されます。この検証エラーはfallbackで`none`へ置き換えられません。

> 注意: 上記は direct 起動時の例です。標準 Docker Compose はこれらのキーを配送しません。Compose 上で `local` provider を検証する場合は、検証専用の `docker-compose.llm-stub.yml` overlay を使ってください（`docker compose -f docker-compose.yml -f docker-compose.llm-stub.yml up -d`）。また `api` コンテナ内から見た `http://localhost:8001` はホストではなく `api` コンテナ自身を指すため、Compose 環境ではこの例をそのまま転記しないでください。

## large-scale LLM を使う

large-scale provider は既定で無効です。利用する場合は、昇格許可、明示 opt-in、allowlist をすべて設定します。

```bash
export KJ_ATLAS_LLM_PROVIDER=large-scale
export KJ_ATLAS_LLM_ESCALATION_ENABLED=true
export KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true
export KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL='https://llm.example.com'
export KJ_ATLAS_LARGE_SCALE_LLM_MODEL='model-name'
export KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST='llm.example.com'
```

large-scaleではbase URL、model、allowlistをすべて設定し、base URLのhostをallowlistへ含める必要があります。allowlistはhost名またはIPアドレスだけをカンマ区切りで指定し、scheme付きURL、wildcard、port、path、空要素、重複は起動時に拒否されます。base URLとmodelにはlocal providerと同じcanonical値制約を適用します。

## アクセス制御を使う

既定の `noop` は、認可判定を外部の PDP に任せません。外部 PDP を使う場合は、方式（adapter）、失敗時の扱い（fail-safe）、接続先（endpoint）をセットで設定します。

```bash
export KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http
export KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=read_only
export KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT='https://pdp.example.com/decide'
```

アクセス制御で`external_http`を指定する場合、接続先（endpoint）は必須です。空の場合は`noop`へ縮退せず、設定エラーとして起動を拒否します。外部PDPを使わない場合は、adapterを明示的に`noop`へ戻してください。endpointはcredential、query、fragment、空白、制御文字、backslashを含まないHTTPS URLにし、HTTPはloopbackだけで利用できます。固定bearerやIdP issuerだけが残る不完全設定、0以下または30秒超のtimeoutも起動時に拒否されます。

監査HTTPも同じendpoint・bearer・timeout制約を適用します。`KJ_ATLAS_AUDIT_TRANSPORT=http`ではendpointが必須で、欠損時はnoopへ縮退せず起動を拒否します。`noop`のまま監査endpoint/API keyを残す設定や、`http`でendpointなしのままAPI keyだけを設定する構成も拒否されます。送信先を完全設定した後の一時的な監査送信失敗は、従来どおり本体機能を止めないfail-open方針です。

### 文書policy binding resolver（将来SaaS用）

`document_access_metadata`に保存する値は非秘密のbinding IDとversionだけです。`external_http` resolverはこれらをactive tenant IDとともに信頼済みサービスへPOSTし、応答の`policyRef`をそのrequest内だけで利用します。raw policyRefやAPI keyをDB、監査、export、diagnosticsへ保存しません。

```bash
export KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER=external_http
export KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT='https://binding.example.com/v1/resolve'
export KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY='set-in-secret-store'
export KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_TIMEOUT_SECONDS=1.5
```

接続先はcredential、query、fragmentを含まないHTTPS URLにします。HTTPは`localhost`、`127.0.0.1`、`::1`だけで利用できます。現行releaseではadapterと検証境界までの実装で、予約中の`saas-multitenant` profileにはまだ配線されていません。この設定だけでSaaSや文書アクセス設定UIが有効になることはありません。

### Tenant capability resolver（将来SaaS用）

`external_http` resolverは、server-resolved `principalId`、`tenantId`、`membershipId`だけを信頼済みpolicy serviceへPOSTし、既知の`effectiveCapabilities`と`capabilityVersion`を取得します。role/group名やclient指定tenantを送信・保存しません。

```bash
export KJ_ATLAS_TENANT_CAPABILITY_RESOLVER=external_http
export KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT='https://capability.example.com/v1/resolve'
export KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY='set-in-secret-store'
export KJ_ATLAS_TENANT_CAPABILITY_HTTP_TIMEOUT_SECONDS=1.5
```

接続先とAPI keyにはbinding resolverと同じ制約を適用します。未知capability、重複、余分なroles/groups field、不正version、timeoutは成功扱いにせず、APIでは`503 capability_resolution_unavailable`へ倒します。adapterと`GET /session/context`はapplication lifecycleへ配線済みですが、trusted SaaS identity resolverが未接続の既定状態ではsession routeも503で閉じます。この設定だけでSaaS profileは有効になりません。

## 設定後の確認

```bash
curl -fsS http://localhost:8080/api/healthz
docker compose logs api --tail=100
```

直接 backend を起動している場合:

```bash
curl -fsS http://127.0.0.1:8000/healthz
```

設定ミスで backend が起動しない場合、`api` log に validation error が出ます。特に旧キー、provider 名、large-scale の opt-in 不足を確認してください。

## 関連文書

- [installation.md](installation.md)
- [data_handling.md](data_handling.md)
- [security.md](security.md)
- [local_llm_ops_guide.md](local_llm_ops_guide.md)
- [runtime_parameter_registry.md](https://github.com/hat47x/kj-atlas/blob/main/02_Architecture/runtime_parameter_registry.md)
