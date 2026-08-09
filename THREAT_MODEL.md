# Threat Model / 脅威モデル（簡易）

この文書は本アプリケーションの現実的なリスクを、公開OSS運用向けに短く整理したものです。

## 対象範囲 / Scope

主に以下を対象とします。

1. ZIP import
2. Markdown rendering
3. Supply chain（npm/pip依存）
4. データプライバシー（エクスポート挙動を含む）
5. サポート診断バンドル
6. 外部エージェント向けMCP投影
7. 標準Composeのネットワーク公開境界
8. SaaSを想定したテナント分離（現行非対応の適用限界を含む）
9. Backend JSON request boundary

## 資産 / Assets

- ユーザーが作成したドキュメント（カード・メモ・配置情報）
- インポート入力（ZIP/markdown/JSON）
- ビルド・配布成果物
- 依存ライブラリ由来の実行コード
- 認証主体、テナント所属、外部エージェント登録とtoken

## 脅威とリスク / Threats

### 1) ZIP import

- Zip bomb による過大展開（CPU/メモリ/ディスク枯渇）
- `../` を含むパスによる path traversal
- 想定外の巨大ファイル・大量エントリ投入

**想定対策**

- 圧縮前後サイズ・エントリ数・1ファイル上限の cap
- 正規化パス検証（ルート外書き込み禁止）
- タイムアウト/中断可能な処理設計

### 2) Markdown rendering

- スクリプト埋め込みや危険属性による XSS
- URLスキーム悪用（`javascript:` など）

**想定対策**

- サニタイズのデフォルト適用
- 許可タグ/属性の allowlist 管理
- レンダリング前の危険スキーム除去

### 3) Supply chain

- npm/pip 依存の悪性アップデート
- 乗っ取り済みパッケージ混入
- トランジティブ依存経由の脆弱性流入

**想定対策**

- lockfile の利用と差分レビュー
- CI で lint/test を常時実行
- 依存更新PRの分離、最小権限でのレビュー

### 4) データプライバシー

- エクスポート物に不要な個人情報が混入
- 共有時に機微情報が漏えい

**想定対策**

- `safeMode` をエクスポート既定値として **ON**
- 既定でPIIを含めない運用（必要時のみ明示的に含める）
- 共有前の人手確認（human-in-the-loop）

### 5) サポート診断バンドル

- raw UserAgent、Document識別子、error message、ログや本文が診断JSONへ混入する
- SafeMode OFF時だけ露出項目が増え、共有境界を迂回する
- プレビューと実際のコピー/ダウンロード内容が異なる

**想定対策**

- `ADR-0053` の `diag-bundle.v1` allowlistだけから新規オブジェクトを構成し、未知キーを拒否
- SafeMode ON/OFFで露出境界を変えず、raw UserAgent、Document id/title、entity id/ref、message/stack、URL、秘密情報、本文を常時除外
- 明示操作・全文プレビュー必須・ローカル生成に限定し、自動送信、永続保存、生成時の追加通信を禁止
- プレビューとコピー/ダウンロードに同一の不変JSON文字列を使用

### 6) 外部エージェント向けMCP投影

- MCP SDKの依存追加によるsupply-chain面の拡大
- read-onlyと称したsurfaceにwrite/sampling/elicitation capabilityが混入する
- 未レビューentityや原文由来fingerprintがSafeMode投影から漏れる

**想定対策**

- MCPをfrontendから独立したprivate packageへ隔離し、SDK/peer dependencyを正確なversionでpinしてlockfileをレビュー
- capability allowlistと `tools/list` / `resources/list` の固定テストでwrite/ingest/apply/publish/sampling/elicitationを禁止
- 外部結線前に、全constraintで未レビューentity/refの既定除外と、SafeMode出力に原文由来hashが無いことを検証

### 6-1) HTTP transport / OAuth 2.1 resource server（Subslice C, ADR-0054）

stdio段階では listen port を開かず外部到達不可だったが、streamable-HTTP transport（`KJ_ATLAS_MCP_TRANSPORT=http`）は本リポジトリ初の公開ネットワークリスナーであり、リスクの質が変わる。

- 未認証／偽造／期限切れbearer tokenによる `POST/GET/DELETE /mcp` への到達
- 他リソース向けに発行されたtoken（audience違い）や、信頼していないissuerが発行したtokenの受理（confused deputy）
- 本サーバーが誤って authorization server 相当の機能（token発行・client登録・consent）を持ってしまうscope creep
- 単純なリクエスト洪水によるCPU/メモリ枯渇（DoS）
- 認証エラー応答から到達可能性・内部実装がfingerprintされる情報漏えい
- `/.well-known/oauth-protected-resource` のような未認証で公開する必要があるエンドポイントが、意図せず認証必須のエンドポイントにも認証バイパスの糸口を与える

**想定対策**

- ADR-0054/ADR-0020方針どおり、本サーバーは OAuth 2.1 **resource serverのみ**として実装し、token発行・client登録・authorization endpointは一切持たない（そのコードパス自体が存在しない）
- `jose`の`jwtVerify`でtoken署名・`iss`（`KJ_ATLAS_MCP_TRUSTED_ISSUER`と厳密一致、prefix/wildcard一致は行わない）・`aud`（`KJ_ATLAS_MCP_RESOURCE_URL`）・`exp`を検証し、失敗経路はすべて`InvalidTokenError`にfail-closedで正規化（未知の失敗が既定で通過することはない）
- SDKの`requireBearerAuth`により、認証失敗は常に401 + `WWW-Authenticate: Bearer ... resource_metadata=...`ヘッダーで応答し、tokenの有効性以外の情報（存在確認・詳細な失敗理由）を返さない
- `/.well-known/oauth-protected-resource`（RFC 9728）は仕様上未認証公開が前提のdiscovery文書であり、`resource`/`authorization_servers`/`bearer_methods_supported`など非秘匿情報のみを返す。`/mcp`自体の認証要件は変えない
- 全route（metadata含む）に60 req/min/IPのrate limitを適用し、単純な洪水要求を早期にthrottleする
- transportはstateless（`sessionIdGenerator: undefined`）とし、session固定化やsession storageに起因する攻撃面を持たない
- request bodyは1MBに制限し、過大payloadでのメモリ消費を防ぐ

### 6-2) Backend JSON request boundary（SEC-DOC-BOUND-03）

- 構文的に妥当でも過度に深いJSONがparserの再帰上限を超え、未捕捉例外や500を発生させる
- `ContextQuery.constraints` の再帰構造がCPU・メモリ・canonical hash処理を無制限に消費する
- validation errorへraw inputやsecret相当値が混入する

**想定対策**

- backendの `application/json` / `application/*+json` request bodyを、JSON parserより前の反復的scannerで検査し、構造ネスト64超過を `400 json_nesting_too_deep` でfail-closedに拒否する
- `ContextQuery.constraints` をJSON互換値、深さ8以下、総ノード数1024以下、canonical UTF-8 64 KiB以下に制限し、違反を `400 invalid_constraints` で拒否する
- 境界エラーは安定したcodeだけを返し、raw input、validation context、parser例外を反射しない
- API key認証をbody検査より外側に維持し、認証失敗をrequest bodyの走査より先に拒否する
- 浅い巨大JSON全般のbyte上限は本issueでは追加しない。Document/identityの値長上限は `SEC-DOC-BOUND-01`、公開面のrate/body上限は各transport境界で扱う

### 7) 標準Composeのネットワーク公開境界（DEPLOY-NET-01）

`http://localhost:8080` という案内は、サービスがloopbackだけでlistenすることを意味しない。host IPを省略したDockerのport公開（`"${KJ_ATLAS_WEB_PORT:-8080}:80"`）はホストの全interfaceを対象にし、同一LANや誤設定されたport forwardingから到達できる未認証主体に、評価環境そのものを公開してしまう。

- 保護資産: document本文、レビュー情報、設定・診断情報
- 攻撃者: 同一LAN、共有ホスト、誤設定されたport forwardingから到達する未認証主体
- 入口: nginx配信面（`web`サービス）と、そこから転送される`/api`
- 誤解しやすい非対策: SafeMode（share/exportの漏洩抑制であり、ネットワーク経由の到達を認証しない）、`KJ_ATLAS_API_KEY`（同梱SPAが`X-API-Key`を送らないため、通常のブラウザ利用を保ったまま既定露出を補う認証にはならない）、URLに`localhost`と表示すること

**想定対策**

- 標準`docker-compose.yml`の`web.ports`をloopback（`127.0.0.1:${KJ_ATLAS_WEB_PORT:-8080}:80`）へ明示bindし、`KJ_ATLAS_WEB_PORT`はport番号だけを変え、bind範囲を拡張しない契約にする
- 別端末・LAN・Internetからの利用が必要な場合は、TLS終端・SPAとAPIの双方を覆う認証proxy・接続元制限・secret管理を伴う明示的な別deployment profileとして分離し、base Composeの直接書き換えでは対応しない
- READMEとinstallation/deployment文書で、標準Composeを「同一ホストからだけ使う評価構成」と明記する
- contract testで、標準Composeのweb port mappingがhost IP省略・`0.0.0.0`・loopback以外へ戻らないことを検証する

### 8) SaaSテナント分離

- docIdの差し替えによる他テナント文書へのIDOR
- list/search/count/cacheからのタイトル・更新日時・利用状態の越境漏えい
- client指定のtenant/visibility/policy header偽装
- PDP不達時のread-only許可、adapter欠損時のnoop退避による他テナントread
- Admin API、agent token、API key、signed linkの他テナント再利用
- worker/job、監査、object storage、backup/restoreでtenant contextが欠落する
- 同一ブラウザのrecent/QueryPreset/選択状態がtenant切替後に残る
- 別タブでactive tenantを切り替えた後、古いタブの本文・payload・docIdが新しいserver session scopeでread/write/export/importされる
- bfcache、遅延response、worker完了、欠落したcross-tab通知により旧tenantの本文・metadata・downloadが再表示またはcommitされる
- trusted endpointの3xx redirectで接続先検証を迂回し、固定bearer、tenant context、policyRef、promptを別hostへ転送する
- 外部PDPの巨大・非object・拡張field付き応答でmemoryを圧迫する、または未検証値を認可判断・client errorへ混入させる
- 外部PDP・監査HTTPの非TLS／credential入りendpoint、孤立したbearer/issuer、負または過大timeoutにより秘密漏えい・誤接続・起動後障害を生じる
- 外部PDP・監査HTTPを明示選択してもendpoint欠損時にnoopへ縮退し、認可の全許可や監査停止を運用者が有効な連携と誤認する
- LLM HTTP providerの巨大・非object・拡張field付き応答でmemoryを圧迫する、または未検証値をproposal処理へ混入させる

**SaaS提供前に必要な対策**

- TenantContextをverified claimまたはtrusted host mappingから一意に解決し、自由入力headerを信頼しない
- すべてのtenant従属行、子テーブル、agent registration、job、cache、auditへtenantIdを持たせ、複合unique/FKで補強
- 主体tenantと資源tenantの不一致をPDP呼出前にアプリ内で常にdeny
- tenant/visibility/policyRefをサーバー正本から解決し、クライアント値を認可根拠にしない
- SaaS profileではPostgreSQL、JIT無効、external access-control、`deny` fail-safe、external document binding、external tenant capabilityの型付き非秘密policyと、構築済みPDP／capability／binding componentの実型をDB初期化前とadapter有効化前に再検証する。設定がexternalでも実体がnoop／unavailableへ退避した構成を拒否し、preflight済みの同一instanceだけをruntimeへ渡す。欠損、noop/mock、read-only、PDP不達、tenant不明をread許可へfallbackしない
- 外部PDP、監査HTTP、binding/capability resolver、LLMのoutbound HTTPはredirectを追跡せず、検証済みの元endpointだけへ送信する
- 外部PDP応答を64KiB以下のclosed-world `allow/readOnly/reason` objectへ限定し、不正応答は値を反射せずSaaS deny fail-safeへ倒す
- 外部PDP requestを64KiB以下、boundedな識別子・policyRef・roles/groups、canonicalなserver-composed値へ限定し、不正・過大requestはtransport前に値を反射せずSaaS deny fail-safeへ倒す
- binding/capability resolver requestを64KiB以下、boundedかつcanonicalなserver-owned tenant/principal/membership/binding IDへ限定し、不正・過大lookupはtransport前に値を反射せずfail-closedへ倒す
- session contextの成功・エラーresponseはfrontendでもstreamを64KiBまでしか読み取らず、超過時は後続chunkをcancelする。成功responseはboundedなprincipal/tenant/capability、重複なしのtenant・capability集合へ限定し、不正・過大responseからbrowser memoryやstorage keyを構成しない
- runtime bootstrap policyはvalidation済みserver profileだけからprofile名非公開の2値を作り、header/query/client payloadを判定根拠にしない。frontendはresponseを4KiBまでのclosed-world objectとして再検証し、未知・欠損mode、余分なfield、不正JSON/UTF-8をentry point判定へ使わない
- frontend build profileは既存3 profileだけをlocal-first entryへ写像し、`saas-multitenant`はserver policy一致とsession成功までAppをmountしない。未知・空・非canonical build値、policy不一致・取得失敗をsingle-tenant fallbackへ変換しない。公式Composeはbackendとfrontend buildへ同じprofile式を渡す
- active tenant変更は現在と選択先のmembershipをDBで再照合し、検証済みprincipal/TenantContextだけをtrusted session persisterへ渡す。persisterはanti-forgery検証とauth sessionへのbindingを担い、欠損・障害時は更新せずfail-closedにする。frontendも検証済みallowlist外を送信せず、応答のprincipal不変・要求tenant一致を再確認する
- active tenantは認証セッション単位で1つとし、trusted auth/session adapterが発行する`tenantSessionVersion`をconditional tenant switchと全tenant-scoped requestのpreconditionにする。古いversionはresource lookup前に本文を返さず拒否し、新contextへ自動再送しない。cross-tab通知は早期blockの補助に限り、通知欠落時もserver guardで停止する
- `pageshow.persisted`、長時間非表示からの復帰、遅延response/worker完了ではsessionを再確認し、旧本文を背景へ残さないblocked stateへ移す。旧contextのresponse、object URL、optimistic updateを新DOMへcommitしない
- trusted SaaS identity resolver、tenant resolver、active tenant session persisterはapplication起動前の単一bundleとしてのみ注入する。profile・runtime safety policy・bundle・started-stateを状態変更なしでpreflightし、部分設定、欠損、不正型、single-tenantへの注入、起動後差し替えをDB初期化前とadapter有効化前に拒否する。bundle有効化時はDocument resource resolverもserver-owned metadata＋trusted binding resolverへ切り替え、公開visibility／policy headerを無視する。bundle非注入時とshutdown時はidentity/persisterをunavailable、tenant resolverとDocument resource resolverをsingle-tenant互換に戻し、session APIをfail-closedに保つ
- `local-default`へ書き込む既存strict provisioning routeはsingle-tenant profileだけに限定し、SaaS／未知profileではDB処理前に閉じる。SaaS membership provisioningへ暗黙fallbackせず、別のverified IdP・active tenant・capability契約を必須にする
- tenant-scoped Appはsession responseの再検証とstorage scope構築が成功するまでmountせず、認証・認可・解決障害・不正responseを旧本文のないblocked stateへ分離する。error detailやprincipal/tenant値を表示せず、abort済みbootstrap結果を再利用しない
- tenant switcherはserver検証済みmembershipが複数ある場合だけallowlist selectとして表示し、自由入力・tenant検索・role/group解釈を提供しない。active tenant自身、allowlist外ID、invalid sessionから変更要求を発火しない
- tenant switch用App hostは注入sessionとbrowser storage scopeの完全一致を再検証し、切替確定後に旧本文をloadingへ、通信・応答障害時はblocked stateへ置換する。保存成功後だけsession変更へ進み、request/worker/object URL/timer cleanupと旧scopeだけのstorage削除をhard replacement前に実行する。raw localStorageはAppへ露出せずscope付きfacadeへ閉じる
- 外部PDP・監査HTTPの設定をtrusted HTTPS（loopbackだけHTTP可）、canonical secret/header、bounded timeoutへ限定する。`external_http` / `http` の明示選択時はendpointを必須とし、欠損をnoopへ縮退させず、DB初期化・request受付前に起動を拒否する
- 監査eventのtenantIdをserver-resolved必須fieldとし、64KiBの送信上限、bounded metadata、credential系redactionで欠落・過大・秘密混入eventを外部連携へ流さない
- LLM HTTP provider応答を1MiB以下のclosed-world `text` objectへ限定し、不正応答は値を反射せずprovider validationで停止する
- LLM HTTP requestを1MiB以下、canonical task、finite temperature、bounded max tokensへ限定し、過大prompt・不正数値はtransport前に値を反射せず停止する。validation失敗をfallbackで隠さない
- LLM base URLをtrusted HTTPSまたはloopback HTTPへ限定し、large-scaleは完全なmodel/host allowlist設定と宛先一致を起動時に検証してlocal-first・opt-in境界の設定迂回を防ぐ
- recent/QueryPreset等のApp永続状態をmount時に検証・snapshotしたdeployment origin + tenantId + userId scopeへbindingし、同一mount内のscope変更を拒否する。App unmountはrequest abort、task cancel、worker disposeを失敗分離して実行し、切替時はmemory/DOM/cacheを破棄してhard replacementする
- 2つのtenantへ同じdocIdを用意したnegative matrixで、全API・export・MCP・webhook・auditの越境拒否を統合検証

**現行の適用限界**

tenant/identity/membership、Document複合key、TenantContext/PDP/audit伝播、PostgreSQL RLS migrationとtransaction-local DB context、fail-closed bootstrap policy/session GET/active tenant POST route、runtime profileと相互必須化したtrusted auth adapterの原子的な起動前bundle、検証済みsession contextとscopeをAppへ同時注入するprofile別frontend entry、tenant switch App host、strict capability adapter、trusted outbound HTTPのredirect拒否、外部PDP request/responseとLLM応答のclosed-world・上限検証、外部PDP・監査HTTPの設定guardまでは実装済みである。session/capability境界ではresolverのmembership IDをDBのactive membershipから再生成した値と照合し、停止・差し替え証跡をPDP呼出し前に拒否する。frontendはruntime cleanupでtenant session generationを無効化し、Document read/write、export監査、AI mutation、diff／診断worker、bundle生成、ローカルFile／zip importの遅延成功結果を旧generationからcommitせず、旧bundleをdownloadしない。review-packのobject URLも最後の非同期検証後にだけ生成し、PNG／HTML snapshot、patch、agent taskは生成結果のgeneration照合後にだけdownload／clipboardへ渡す。public packも全fetch／parse後に一括commitし、stale時に別sourceへfallbackしない。子コンポーネント所有の問い合わせbundle／trace workerも同じguardを通り、stale結果からstate更新やclipboard処理を開始しない。ADR-0063 D9により auth edge から verified evidence を生成する実 resolver（`JwtSaasIdentityContextResolver`）と anti-forgery 付き session persister（`InMemoryActiveTenantSessionPersister`）への接続は実装済みである。ADR-0064 Phase 1 により mock OAuth 2.0 + PKCE ログインフローと JWT 検証の E2E テストも完了している。ただし PostgreSQL 実地検証、現存しない将来の import／share endpoint と MCP 等への `tenantSessionVersion` precondition、clipboard API 呼出し後の OS 側 commit 取消、cache/browser/storage を含む完全な越境 matrix は未完了である。`saas-multitenant` profile は `TrustedSaasRuntimePolicy.validate()` と lifespan preflight が必須設定を検証した上で起動可能であるが、本番運用には残りの `SAAS-TENANT-01` 条件の検証を要する。

## 検証・運用 / Verification

- import / sanitize / diff・merge 系の回帰テストを維持
- PRでセキュリティ影響を明示（必要時）
- 脆弱性報告フローは `SECURITY.md` を参照
- SaaS関連変更では、同一docIdを持つ2tenantの越境negative matrixを必須にする

## Out of Scope / 範囲外

- 完全オフライン運用時における、広域ネットワーク攻撃者モデル
- OS/ブラウザ/企業内基盤そのもののゼロデイ対策
