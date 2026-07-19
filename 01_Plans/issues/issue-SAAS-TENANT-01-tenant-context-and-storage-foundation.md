# Issue: SAAS-TENANT-01 TenantContext・保存境界・越境防止の実装

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security / Feature
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: User request 2026-07-16 / `01_Plans/research-2026-07-16-saas-tenant-authorization-boundary.md`
- Priority: P1
- Owner: Maintainer
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/frontend/`, `03_Implement/mcp/`, deploy/runtime settings and tests
- Related ADR/Spec: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`, `THREAT_MODEL.md`, `02_Architecture/schemas.md`, `02_Architecture/api.md`, `02_Architecture/runtime_parameter_registry.md`
- Expected verification level: integration / e2e

## 課題

- 現在の問題: 現行DB、AuthContext、AccessRequest、browser storageにはtenant境界がなく、`documents.id`は全体主キーである。access-controlのnoop/read-only fallbackも共有SaaSのread分離には使えない。
- 利用者または開発への影響: 現行`enterprise-production`を共有SaaSとして運用すると、IDOR、list/cache/job/storage/auditからの越境漏えい、管理権限の過大化が起きうる。`ADR-0059`はAcceptedだが、実装ゲートは未充足である。

## 対応方針

- 実施すること:
  1. tenant/identity-provider/membershipをexpand migrationで追加し、既存データを内部`local-default`へidempotentにbackfillする。
  2. Documentと全従属行を`tenant_id + id`で識別し、複合unique/FKを適用する。docIdだけのrepository操作を廃止する。
  3. verified claimまたはtrusted host mappingからTenantContextを解決し、active membershipを必須確認する。
  4. resource metadataをserver-sideで読み、主体tenantと資源tenantの不一致をPDP前にdenyする。
  5. `saas-multitenant` profileを明示選択できる設定契約を追加し、external adapter、deny fail-safe、PostgreSQL DB guard、tenant resolverが欠ければ起動をfail-fastにする。
  6. shared schemaではPostgreSQL RLS等のDB側tenant guardを導入し、connection pool再利用時にもtenant contextを漏らさない。
  7. session context / active tenant APIとtenant-scoped `effectiveCapabilities`を実装する。
  8. browser cache、recent、QueryPreset、request cache、MCP、agent credential、job、audit、object-storage keyをtenant/user別に分離する。
  9. 同じdocIdを持つtenant A/Bの越境negative matrixをintegration/E2Eへ固定する。
  10. active tenantを認証セッション単位で直列化し、server-issued `tenantSessionVersion`で複数タブ、同時切替、bfcache、遅延responseのstale requestをresource lookup前に拒否する。
- 実施しないこと:
  - 実装ゲート完了前のtenant switcher、Tenant Admin、Platform Control Plane有効化。
  - 汎用role editor、tenant横断文書検索、support impersonation、恒久的super-reader。
  - 課金、SCIM、tenant削除、保持期限、地域配置。
  - tenantIdやmembershipをDocumentV1 payloadまたはexport/import権限として扱うこと。

## 実装順序と停止条件

1. **Contract**: `schemas.md` / `api.md` / runtime registryとmigration設計が一致する。
2. **Expand**: nullable tenant列と新規表を追加し、`local-default`をbackfillする。この段階ではSaaS profileを有効化しない。
3. **Scoped repository**: TenantContext必須のread/writeへ切り替え、tenantなしqueryを検査で禁止する。
4. **Constraint / DB guard**: NOT NULL、複合unique/FK、RLS等を有効化する。connectionごとのtenant設定はtransaction終了時に確実に破棄する。
5. **Auth / PDP**: membership、local tenant一致、SafeMode、PDPの順にenforceし、SaaSはdeny-onlyにする。
6. **Consumers**: MCP、worker、cache、audit、agent registrationへtenant contextを伝播する。
7. **UI gate**: session context、`tenantSessionVersion`、複数タブ・bfcacheを含むnegative matrixが通った後だけRound 8 R8-E/F/G/Hを実装候補へ昇格する。

各段階でtenant context欠落、backfill不整合、複合FK不整合、RLS context残留、PDP fail-openのいずれかを検出した場合は次段階へ進まない。

## 予算申告

- 複雑性予算（`ADR-0043` CB-1..4）: 初期表示への純増=`+1`（検証済みSaaS session時だけ、active tenantを誤認しないための`TenantSessionControl`をcore toolbarへ表示） / 保留操作の距離=不変（カード・島の保留導線は変更しない） / 取り消し導線=あり（切替前confirmationの取消、切替後はallowlist内のtenantを同じselectorから再選択）。CB-1/CB-3は安全境界を利用者へ常時示すための限定的な純増として許容する。
- 性能予算（`ADR-0046` PB-1..5）: 代表規模でのKJ主要操作=bootstrap完了後は不変 / 100ms超同期処理=追加なし。PB-2初期表示はruntime policy確認とsession context取得を逐次実行するため**要改善（所要時間未計測）**。現在は両待機中に`aria-busy`付きloading viewを表示してPB-5の無反応状態を避ける。AC-12の実ブラウザ検証で、代表環境の操作可能化時間を計測し、数秒超なら段階表示または待機理由の具体化を行う。
- 触れるUQ次元（`ADR-0044`）: UQ-1（active tenantの理解）、UQ-2（切替・取消の操作）、UQ-3（keyboard/focus）、UQ-4（390/768/1440px）、UQ-5（loading/blocked/switching状態）、UQ-6（ja/en）。

## 受入条件

- [x] AC-1: `tenants`、`identity_providers`、`tenant_identity_providers`、`tenant_memberships`が実装され、identityは`identity_provider_id + subject`で一意になる。
- [x] AC-2: 既存データが`local-default`へ損失なくbackfillされ、再実行しても結果が変わらない。
- [x] AC-3: `documents`と全Document従属表がtenant複合制約を持ち、docIdだけのDB query/joinが静的検査またはtestで検出される。
- [ ] AC-4: SaaS profileでtenant不明・不一致、membership停止、adapter欠損、PDP不達をreadも含めてdenyする。
- [ ] AC-5: shared schemaでDB側tenant guardが有効で、別tenant contextを使った直接SQLも行を取得・更新できない。
- [ ] AC-6: `GET /session/context`とactive tenant変更がmembership allowlistだけを返し、自由入力tenantの発見・切替を許可しない。
- [ ] AC-7: Workspace、Tenant Admin、Platform Control Planeのcapability/audienceが分離され、Platform operatorに文書readが暗黙付与されない。
- [ ] AC-8: cache、job、MCP、agent credential、audit、storage keyにtenantIdが伝播し、欠落時は処理を停止する。
- [ ] AC-9: exportはtenant権限を移送せず、importはactive tenantで再認可・検証・人手レビューされる。
- [ ] AC-10: tenant A/Bへ同じdocIdを作成した越境negative matrixが、API/MCP/worker/browser cacheを含めて成功する。
- [x] AC-11: single-tenantのlocal-dev/evaluation/enterprise-production互換テストが維持され、SafeMode既定ON、proposal-only、provider=`none`を弱めない。
- [ ] AC-12: Round 8 R8-E/FはAC-1〜11完了後だけ有効化され、390/768/1440px、ja/en、keyboard/focus、tenant切替時の旧DOM/cache破棄を検証する。
- [ ] AC-13: 同じ認証セッションの複数タブ、同時tenant切替、bfcache復帰、遅延responseで古い`tenantSessionVersion`を持つGET/PUT/export/import/Admin更新がresource lookup前に拒否され、client通知が欠落しても新tenantへ自動再送・commitされない。

## 検証計画

- 実行する確認:
  - migrationのfresh DB / existing DB / rerun / rollback rehearsal。
  - repository・API・PDP adapterのunit/integration test。
  - PostgreSQL RLSでtenant A/Bを切り替える直接SQL testとconnection pool再利用test。
  - 同一docIdでGET/PUT/list/search/count/export/share/import/context/MCP/webhook/job/audit/agent credentialを試すnegative matrix。
  - tenant切替後のDOM、memory、query cache、recent、QueryPreset、object URLの残留確認。
  - 同じ認証セッションの2タブでtenant A/B切替を競合させ、stale GET/PUT/export/import/Admin更新、BroadcastChannel無効、bfcache復帰、遅延worker/responseを再現する。
  - 現行single-tenant回帰、SafeMode/share/export/import/AI proposal-only回帰。
- 期待結果: tenant contextが欠落または不一致の経路はすべてfail-closedとなり、同一tenant内の許可済み操作と既存single-tenant利用だけが成功する。

## 補足

- 依存: `ADR-0059` Accepted、PostgreSQL test環境、外部PDP test double、Round 8 design input。
- 主なリスク: backfill失敗、repository filter漏れ、RLS session変数のpool越し残留、capability cacheのtenant混在。
- ロールバック: SaaS profileを有効化せず、expand列・新規表を残したままsingle-tenant adapterへ戻せる段階を維持する。tenant列をdropする破壊的rollbackは行わない。

### Implementation checkpoint 2026-07-16: expand foundation

- Alembic `20260716_0006`を追加し、`tenants`、`identity_providers`、`tenant_identity_providers`、`tenant_memberships`を作成した。
- `documents`と`merge_decision_logs`へ`tenant_id`とtenant-aware indexを追加し、既存行を`local-default`へbackfillした。現段階では既存API互換のため`local-default` server defaultを維持する。
- 既存Userを`local-default` membershipへbackfillし、新規JIT/strict provisioningでも同membershipを冪等に作成する。
- Documentの全体PK、判断ログのdocId FK、`provider + external_uid`identityはまだ切り替えていない。RLS、TenantContext、SaaS profile、session API、frontendは未着手であり、共有SaaSは引き続き禁止する。
- 検証: Ruff pass、新規ファイルformat check pass、backend全体298件pass・PostgreSQL等の条件付き24件skip、docs-check pass。Docker/PostgreSQLを利用できない環境のため、PostgreSQL migration/RLS検証は次段階へ残す。

### Implementation checkpoint 2026-07-16: tenant-scoped Document repository

- 内部`TenantContext`と`single_tenant_adapter`用`LOCAL_DEFAULT_TENANT_CONTEXT`を追加した。anonymousを許容する現行互換のためmembershipIdは未設定であり、SaaSのverified contextとしては扱わない。
- Document取得・一覧、判断ログのgroup/snapshot取得をtenant必須repositoryへ集約し、docs routeの作成・取得・判断ログ追加でも`tenant_id`を明示するようにした。
- review attribution backfillは`local-default`のDocumentだけを対象にし、将来tenant追加後の無条件全件走査を防止した。
- tenant A/Bで異なるdocIdと同じgroup/snapshotを使うrepository negative testを追加した。同一docId fixtureは現行のglobal PKを複合PKへ移行するまで作成できない。
- 検証: Ruff pass、Document roundtrip/access-control/backfill/repository近接45件pass、backend全体300件pass・条件付き24件skip、docs-check pass。verified TenantContext、PDP payload、同一docId、RLSは未実装のため共有SaaSは禁止を継続する。

### Implementation checkpoint 2026-07-16: runtime profile fail-fast

- 公開`KJ_ATLAS_RUNTIME_PROFILE`を追加し、`local-dev`、`evaluation`、`enterprise-production`を正規化して受理する。backend直接起動の既定は`local-dev`、Composeの既定は`evaluation`とした。
- `saas-multitenant`は予約値として認識するが、`SAAS-TENANT-01`の安全ゲート未完了を理由にsettings validationで常に起動拒否する。未知値や旧`RUNTIME_PROFILE`もfail-fastにする。
- runtime registry、deployment、Compose、利用者向けConfigurationを同じ公開キーへ同期した。
- 検証: Ruff pass、settings/API-key近接26件pass、backend全体304件pass・条件付き24件skip、公開キー正本を含むdocs-check pass。Dockerがないため`docker compose config`は未実施。

### Implementation checkpoint 2026-07-17: identity provider binding expand

- Alembic `20260717_0007`で`user_identities.identity_provider_id`と`subject`をnullable expand列として追加し、既存providerラベルごとの決定的な互換IdP、`local-default`のIdP binding、既存identityのsubjectをbackfillした。`identity_provider_id + subject`の一意indexを追加し、rerunとdowngradeをSQLiteで確認した。
- JIT provisioningと`/admin/provision/users`は、既存の`provider + external_uid`に加えて`identity_provider_id + subject`を二重書きする。旧列と既存APIはsingle-tenant互換のため維持し、検証済みissuer/audienceからIdPを解決するまで互換IdPをSaaS認証に使用しない。
- PostgreSQLでは`identity_provider_id`外部キーを追加し、SQLiteはlocal/evaluation用途のためアプリmetadata上の外部キーと一意indexに留める。共有SaaSは引き続き禁止する。
- 検証: Ruff pass、identity migration・tenant migration・JIT/strict provisioning近接19件pass。PostgreSQL migrationは利用可能な環境がないため未検証であり、次のcontract/NOT NULL化条件に残す。

### Implementation checkpoint 2026-07-17: active membership TenantContext

- single-tenant互換resolverを追加し、認証済み利用者についてUser、`local-default` Tenant、TenantMembershipのactive状態をrequestごとに検証する。いずれかの停止・欠損は同一の`tenant_membership_inactive`で拒否し、tenantの存在や状態を応答で区別しない。匿名経路は現行互換のためmembershipなしを維持する。
- Documentのread/write、判断ログ、類似候補、polygon handoffはresolverが返したTenantContextをrepositoryへ明示伝播する。`x-tenant-id`等のclient入力はresolverに渡さない。
- AccessRequest/ResourceへTenantContextとresource tenantを追加し、外部PDP adapterへserver-resolved値だけを送る。view/export/context auditへ本文・title・membershipを含めず`tenantId`を追加した。
- 検証: Ruff pass、TenantContext・PDP payload・JIT/strict・Document roundtrip/access-control/repository近接71件pass、PostgreSQL条件付き21件skip。verified claim/host mapping、session/capability API、複合Document key、RLSは未実装のためSaaS profileの起動拒否を継続する。

### Implementation checkpoint 2026-07-17: structured identity lookup

- 認証と事前登録のidentity lookupを共通化し、決定的な互換`identity_provider_id + subject`を第一検索キー、旧`provider + external_uid`をbounded fallbackに変更した。同一requestで両keyが異なる行へ一致する場合は一律`identity_mapping_conflict`とする。
- 旧行のexpand列が両方とも空の場合は、fallback成功後に互換IdP bindingとsubjectを補完する。既存の新bindingが入力provider/subjectと不一致の場合は上書きせず拒否する。
- 検証: Ruff pass、JIT/strict・AuthContext・federation fixture・identity migration近接27件pass。検証済みissuer/audienceによるIdP選択は未実装であり、互換IdPをSaaS信頼根として扱わない。

### Implementation checkpoint 2026-07-17: tenant-scoped Document keys

- Alembic `20260717_0008`で`documents`を`PRIMARY KEY (tenant_id, id)`へ、`merge_decision_logs`を`UNIQUE (tenant_id, doc_id, decision_id)`および`FOREIGN KEY (tenant_id, doc_id)`へ移行した。Documentのtenant_idはTenantへの外部キーとなり、tenant A/Bで同じdocIdとdecisionIdを保持できる。
- SQLite migrationは既存Documentのtenant欠損と判断ログのtenant不一致をupgrade前に拒否する。downgradeはtenant間でdocIdが重複している場合に停止し、データを暗黙に統合・破棄しない。ORMの直接取得2か所も複合identityへ更新した。
- 検証: Ruff pass、upgrade/downgrade・複合FK・同一docId negative matrix・repository・backfill・lineage近接12件pass、Document roundtrip/access-control/audit/recovery/index/polygon/realistic journey 77件pass・PostgreSQL条件付き21件skip。
- PostgreSQL用constraint移行は実装したが、利用可能なPostgreSQL環境がないため未実地検証。RLS/connection contextと全consumerのtenant伝播も未完了であり、SaaS profileの起動拒否を継続する。

### Implementation checkpoint 2026-07-17: MCP SaaS fail-fast

- 独立起動できるMCP processでも`KJ_ATLAS_RUNTIME_PROFILE`を検証し、single-tenant 3 profileだけを受理する。`saas-multitenant`はtenant-bound MCP/agent credentialが未実装のため起動前に拒否し、未知profileも拒否する。
- MCP tool inputや任意headerへtenantIdを追加しない。現行MCPはAPI keyによるsingle-tenant read-only互換に限定し、tenant credentialの代替として扱わない。
- 検証: TypeScript typecheck pass、MCP全26件pass。検証環境はNode 24でpackage指定のNode 20とは異なるため、正式なNode 20 CI確認は継続する。

### Implementation checkpoint 2026-07-17: verified claim resolver and tenant allowlist service

- auth edgeで署名・issuer・audienceを検証済みという型付き`VerifiedTenantClaim`を受け取る内部resolverを追加した。resolverはDB上のIdP issuer/audience/lifecycle、tenant-IdP binding、`identity_provider_id + subject`、認証済みUserとの一致、tenant/User/membershipのactive状態を再確認する。HTTP headerやqueryをclaimへ直接変換する経路は追加しない。
- active membershipだけを返すtenant候補列挙と、利用者入力tenantIdをmembership allowlistへ再照合する切替選択serviceを追加した。不明、他利用者、停止tenantは同じ404応答とし、tenant検索には使用できない。
- `effectiveCapabilities`と公開`GET /session/context` / active-tenant routeは未実装のため、UIと公開APIは閉じたままにする。auth edge接続とtrusted host mappingも残課題。
- 検証: Ruff pass、verified claimのissuer/audience/IdP/subject/user/tenant negative matrix、allowlist・切替、single-tenant/JIT近接32件pass。

### Implementation checkpoint 2026-07-17: Document API tenant resolver boundary

- Document routeのTenantContext供給をapplication lifecycleで設定する`TenantContextResolver`境界へ移し、既定は既存`SingleTenantContextResolver`とした。request header/query/path/payloadからresolverやtenantIdを選択する分岐は設けない。
- integration testでは信頼済みresolverをtenant A/Bへ切り替え、同一`/docs/shared-doc`が各tenant固有の本文だけを返し、PUTが選択tenantの複合key行だけを更新することを固定した。membership外tenant相当では同じ404となる。
- 検証: Ruff pass、同一docId GET/PUT matrix、repository、Document roundtrip/access-control近接46件pass・PostgreSQL条件付き21件skip。production verified resolverのauth edge接続は未実装のためSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-17: PostgreSQL transaction-local RLS guard

- Alembic `20260717_0009`でPostgreSQLの`documents`と`merge_decision_logs`へENABLE/FORCE RLS policyを追加した。policyは`current_setting('kj_atlas.tenant_id', true)`と行tenantが一致する場合だけUSING/WITH CHECKを許可し、setting欠落・空値はread/writeとも不許可になる。SQLite migrationはno-opとする。
- tenant-scoped repositoryは各操作前にparameter bindingされた`set_config('kj_atlas.tenant_id', tenantId, true)`を実行する。第3引数`true`によるtransaction-local設定のためcommit/rollback後のpool再利用へtenant値を持ち越さない設計とし、任意tenant文字列をSQLへ連結しない。
- 検証: Ruff pass、DB guard parameter binding/SQLite no-op/blank拒否、migration lineage、SQLite upgrade/downgrade、同一docId repository/API近接14件pass。PostgreSQL直接SQL・connection pool実地テストは環境不在のため未実施であり、AC-5とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-17: pre-PDP tenant boundary guard

- access-control層へtenant境界guardを追加し、必須modeではTenantContext欠損、resource tenant欠損、tenant不一致をfail-safe modeに関係なくdenyする。いずれも外部PDP adapterを呼ばないため、tenant一致を外部policyへ委譲しない。
- Document routeはaccess-control adapterの有無にかかわらず必須modeを適用する。既存の単一テナントadapter契約は既定の互換modeで維持し、SaaS profileの起動許可には使用しない。
- 検証: Ruff pass、欠損・不一致でadapter未呼出し、一致時だけ呼出し、単一テナント互換、Document access-control/tenant isolationを含む近接30件pass。
- resourceのtenant/visibility/policyRefを`tenantId + resourceId`でserver-side lookupする実装は未完了であり、現行header由来visibility/policyRefはSaaS認可根拠にできない。AC-4とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-17: server-owned Document resource resolver boundary

- Document access resourceの組立てをapplication lifecycleで設定するresolverへ分離した。既定の`SingleTenantHeaderResourceResolver`は現行single-tenantのvisibility/policyRef header契約だけを維持する。
- 将来SaaS用`ServerOwnedDocumentResourceResolver`は公開headerを無視し、`tenantId + docId`のtenant-scoped repository lookupで既存資源のtenantを取得する。他tenant・不明resourceはread/export等でPDP前に404とし、新規writeはactive TenantContextへserver-sideでscopeする。
- server-owned policy metadata storeが未実装の間はvisibilityを`Restricted`、policyRefを欠損として返す。SaaS必須のdeny fail-safeでは外部PDPへ進まず安全側に停止するため、client headerでPublicやpolicyRefを偽装できない。
- 検証: Ruff pass、legacy header互換、client header無視、既存resource lookup、PDP前404、新規write active tenant scope、Document access-control/tenant isolationを含む近接25件pass。
- SaaS runtimeへのresolver配線、policy metadataの永続化・管理、実PDP capability評価は未完了であり、AC-4とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-17: browser storage tenant namespace foundation

- `deployment + tenantId + principalId`をpercent-encodeしたbrowser storage prefix生成と、選択scopeだけを安全に列挙・削除するutilityを追加した。空値、前後空白、制御文字を含むscopeは拒否する。
- recent document ID、view/pack visibility、view mode、view locale、QueryPreset、reviewer ref、empty-canvas onboarding、minimap、advanced UI preferenceはoptional scopeを受け取り、scope指定時はtenant/principal/deployment別keyへ保存する。QueryPreset panelはscope変更時に保存済み一覧を再読込し、入力中の名称・scope・depth・filterを初期化する。scope省略時は現行single-tenant keyを維持する。production codeのlocalStorage直接利用はstorage moduleへ集約し、sessionStorage直接利用はない。
- 検証: tenant/principal/deployment分離、delimiter衝突防止、不正scope拒否、scope限定削除、recent/view visibility/QueryPresetのtenant A/B分離・旧key互換・正規化15件、view mode/localeのtenant A/B分離・旧key互換10件、reviewer/onboarding/minimapのscope分離11件、advanced UIのscope分離・storage unavailable 3件、UI regression 32件pass、frontend typecheck pass。
- 公開session contextからのscope配線、tenant切替時のDOM・memory・request cache・object URL破棄は未実装であり、AC-8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-17: session context response boundary

- 計画中の`TenantSessionContextV1`へserver-managed opaque `principalId`を追加した。表示名、email、外部IdP subjectをbrowser storage scopeへ使わず、認証済みUser IDだけを供給する契約とした。
- 公開routeより先に内部session context builderを追加した。builderは認証済みprincipal、active TenantContextとmembership allowlistの再一致、明示注入されたtrusted capability resolverのsnapshotを必須とし、tenant候補を検索入力やclient値から組み立てない。
- capability IDとversionの空値、前後空白、制御文字、resolver例外は`503 capability_resolution_unavailable`へ正規化し、欠損・不正snapshotを成功応答として誤認させない。匿名と停止・不一致tenantではpolicy resolverを呼ばない。
- 検証: session contextの正常系、匿名、停止tenant、snapshot不正、resolver例外、tenant切替の11件、verified tenant serviceとの近接20件、Ruff、backend全体352件pass・PostgreSQL等の条件付き24件skip。
- frontendへsession response validatorとbrowser storage scope変換を追加した。active tenantがmembership allowlist候補に含まれ、表示metadataも一致する場合だけ`deployment + tenantId + principalId`へ変換する。重複tenant ID、不一致表示名、非canonical identifier/capabilityは拒否する。検証はsession validator 8件、tenant scopeとの近接14件、frontend typecheck pass。
- active tenant切替の内部builderを追加した。現在のcontextがverified claimまたはtrusted host mapping由来で、現在tenantのmembershipもactiveな場合だけ要求tenantをallowlistへ照合する。不明・停止tenantは同じ404とし、成功時だけ切替先tenantのcapability resolverを呼ぶ。single-tenant互換contextをSaaS切替根拠には使わない。
- 公開`GET /session/context` / active-tenant route、auth edge接続、実PDP capability resolver、token期限に連動したcache invalidationは未実装であり、AC-4/6/7とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-17: server-owned Document access metadata

- Alembic `20260717_0010`で`document_access_metadata`を追加した。`tenant_id + doc_id`を主キーかつDocument複合外部キーとし、visibility、非秘密`policy_binding_id`、`policy_version`、更新時刻だけを保持する。`Org/Restricted`は非空binding IDを必須とし、生のpolicyRef・token・URL・assertionは保存しない。
- PostgreSQLではmetadata表にもENABLE+FORCE RLSを設定し、transaction-local `kj_atlas.tenant_id`と一致する行だけをread/write対象とする。SQLiteはmigration/単一テナント互換検証用でRLSを適用しない。
- SaaS用Document resource resolverはclientのvisibility/policyRef headerを無視し、tenant-scoped metadataを取得する。binding ID/versionはtrusted runtime resolverへ渡し、返されたpolicyRefだけをrequest内で使用する。metadata欠損、不正binding、resolver例外は`Restricted + policyRef欠損`へ倒し、deny fail-safeを維持する。Public/Unlistedはbindingなしを許可する。
- 同一docIdを持つtenant A/Bでmetadataとruntime policyRefが混線しないこと、複合FK、visibility/binding制約、downgrade、client header無視、binding resolver障害を近接17件で検証した。Ruff pass、backend全体358件pass・PostgreSQL等の条件付き24件skip。
- metadata管理API/UI、binding IDをsecret store/PDP参照へ解決する実adapter、PostgreSQL直接RLS検証、SaaS runtime配線は未実装であり、AC-4/5/7/10と起動拒否を継続する。
- UI/UX構想とClaude Design指示へR8-G「文書アクセス設定」を追加した。Tenant Adminの`document.policy.manage`専用面とし、docId/visibility/binding状態/version/updatedAtだけを扱う。タイトル・本文・raw policyRef・URL・token・secret・bulk公開を禁止し、metadata未登録／binding不達はRestricted blocked stateとして設計する。管理API・実binding resolver・監査・negative matrix完了までimplementation gatedとする。

### Implementation checkpoint 2026-07-17: frontend tenant transition cleanup boundary

- 検証済み`TenantSessionContextV1`だけを受け付けるtransition coordinatorを追加した。未検証responseやactive tenant/allowlist不一致では、cleanup、storage変更、navigationのいずれも開始しない。
- 正常遷移ではrequest abort、worker dispose、object URL revoke、memory state reset等のcleanup hookを先に実行し、旧`deployment + tenantId + principalId` scopeだけを削除してhard document replacementを行う。他tenant scopeとsingle-tenant旧keyは削除しない。
- cleanup hookやstorage列挙が一部失敗しても旧DOMを継続利用せず、hard replacementを必ず試行する。正常系、未検証response、cleanup/storage障害、principal変更の4件、session/storage近接18件、frontend全体1,100件・198 file、typecheck pass。
- 公開session/active-tenant API、Appの具体的なabort/dispose/revoke/reset hook配線、90/768/1440pxでの実ブラウザ切替検証は未実装であり、AC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-17: Document access metadata management boundary

- Tenant Admin向け`GET list/detail`と条件付き`PUT /tenant-admin/document-access/{doc_id}`を追加した。信頼済みSaaS identity resolver、verified/trusted TenantContext、active membership、`document.policy.manage`の全条件をrequestごとに再確認し、既定single-tenant context、`document.write`、Platform operator capability、role/group headerでは利用できない。auth/capability adapter欠損時は503で閉じる。
- 一覧はdocId、visibility、設定/binding状態、policy version、更新時刻、opaque revisionだけを返し、title、本文、card、review集計、tenantId、binding IDを含めない。詳細/更新も非秘密のopaque binding ID/versionだけを扱い、extra fieldやURL/token/raw policyRef形状は値をresponseへ反射せず422で拒否する。
- PUTは一覧/詳細由来の`If-Match`を必須とし、欠損428、不一致・同時更新409とした。metadata更新は旧値を条件にしたatomic updateまたは一意insertとし、成功時の監査追加と同一transactionで確定する。
- Alembic `20260717_0011`で`document_access_admin_audit_events`を追加し、PostgreSQL ENABLE+FORCE RLSを設定した。監査列はtenantId、opaque principal/doc ID、action/decision、policy/capability version、server-generated correlation ID、時刻だけで、binding ID、raw policyRef、title、本文、tokenを持たない。
- 検証: exact capability分離、single-tenant拒否、adapter欠損、tenant A/B同一docId list/update分離、本文非取得、秘密入力非反射、428/409、監査原子性・最小列、migration upgrade/downgradeを近接33件で確認した。実PostgreSQL RLS、trusted auth/PDP/binding adapter、frontend配線は未完了のためAC-4/5/7/10とSaaS起動拒否を継続する。
- Document、access metadata、管理監査のRLSを、pool再利用、context欠損read/write、tenant A contextからBへのread/writeで検証する条件付きPostgreSQL matrixを追加した。実行時はmigration ownerとは別の非superuser・非`BYPASSRLS` runtime roleを必須とし、同一資格情報では失敗させる。現行ComposeはDB所有者とAPI資格情報を分離しておらず、ローカルでは接続先未指定によりskipのため、runtime role/provisioningと実地合格まではAC-5を未完了のままとする。

### Implementation checkpoint 2026-07-17: trusted Document policy binding adapter

- 非秘密`bindingId + policyVersion`をserver-resolved tenantIdとともに信頼済みendpointへPOSTし、raw policyRefをrequest内だけで返す`external_http` resolverを追加した。応答は`policyRef`単独field、64KiB以下、2,048文字以下、前後空白・制御文字なしに限定し、余分なtoken等のfield、非JSON、4xx、timeout/transport障害はすべてfail-closed解決失敗にする。
- resolverは既定`none`で、endpoint/API keyだけが残る不完全設定を拒否する。endpoint内credential/query/fragmentと非loopback HTTP、空白・制御文字を含むAPI key、0以下または30秒超のtimeoutをSettingsで拒否し、API keyとraw応答値を例外、DB、監査へ反射しない。
- adapter request/response、size/shape/canonical制約、4xx/transport正規化、builder既定unavailable、設定guard・秘密入力非反射を近接24件で確認し、resource/settings近接56件とRuffがpassした。SaaS lifecycleへのauth/resource resolver配線、実binding service/PDP、secret manager注入は未完了のためAC-4/7/10と起動拒否を継続する。

### Implementation checkpoint 2026-07-17: trusted tenant capability adapter

- server-resolved principalId、tenantId、membershipIdだけをtrusted endpointへPOSTし、既知`effectiveCapabilities`とopaque `capabilityVersion`だけを受理する`external_http` resolverを追加した。未知・重複capability、roles/groups等の余分なfield、非canonical version、64KiB超、4xx、timeout/transport障害はfail-closedにする。
- resolverは既定unavailableとしてapplication lifecycleへ配線した。`none`や不完全設定では管理API/session builderが`503 capability_resolution_unavailable`となり、公開headerやDocument owner、`document.write`から管理capabilityを導出しない。endpoint/API key/timeoutとvalidation errorの秘密非反射にはbinding resolverと共通の設定guardを適用する。
- request/response、既知capability集合、size/shape/version、membership欠損時のtransport前停止、4xx/transport正規化、builder、設定guardを25件、session・管理API・binding近接70件で確認した。trusted SaaS auth edge、実policy service/PDP、公開session route、frontend配線は未完了のためAC-4/6/7/10と起動拒否を継続する。

### Implementation checkpoint 2026-07-17: fail-closed session context route

- SaaS identity、verified/trusted TenantContext、active membership、trusted capability snapshotをrequestごとに解決する共通境界を追加し、Document access管理APIと`GET /session/context`で共有した。identity resolver未注入、single-tenant互換context、停止membership、capability resolver欠損・例外では成功responseを返さない。
- responseはopaque `principalId`、active tenant、active membership由来のtenant候補、既知`effectiveCapabilities`、`capabilityVersion`だけに限定した。email、外部IdP subject、reviewer/owner ref、membership ID、role/groupを返さず、公開tenant/role/group headerを候補や権限へ昇格させない。成功時は`Cache-Control: no-store`と`Pragma: no-cache`を付ける。
- internal builderも未知capabilityを`503 capability_resolution_unavailable`へ正規化した。routeの正常系、秘密非反射、adapter欠損、匿名、single-tenant互換・未知resolution method、未知capability、停止membership、tenant resolver例外と、既存管理API回帰を近接31件で確認した。
- 検証はRuff、backend全体431件pass・PostgreSQL等の条件付き25件skip、docs-check、diff-checkを通過した。移行テストの子プロセスが仮想環境のAlembicを解決できるよう、全体検証では仮想環境の実行パスを明示した。
- `POST /session/active-tenant`は認証sessionへのactive tenant永続化契約が未確定のため追加していない。trusted auth edgeの実接続、frontend fetch／App cleanup hook、active tenant変更、token期限連動cache、完全negative matrixが残るためAC-4/6/7/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-17: strict frontend session fetch boundary

- frontend API clientへ`GET /session/context`のsame-origin・`no-store` fetchを追加し、AbortSignalを上位のlifecycleから渡せるようにした。requestへtenant ID、role、groupを付加せず、非2xxはbackendのstatusとstable error codeを`ApiError`へ保持する。
- response validatorを既知11 capabilityへ限定し、top-level／tenant summaryの余分なfield、未知capability、非JSON、不完全shapeを`InvalidTenantSessionContextError`として拒否する。response検証前にbrowser storage scopeや画面状態へ反映しない。
- 既存session validatorとclientの近接21件、frontend全体1,106件・198 file、typecheck、docs-check、diff-checkを通過した。App起動時のsession bootstrap、失敗時UI、実auth cookie連携、active tenant変更とcleanup hook配線は未実装のため、UIとSaaS runtimeは引き続き有効化しない。

### Implementation checkpoint 2026-07-17: membership evidence recheck

- session context builderとactive tenant切替内部境界で、resolver由来の`tenantId + membershipId + resolvedBy`をDBのactive User/Tenant/Membershipから再構成したTenantContextと照合するようにした。canonicalに見える差し替えmembership IDでも一致しなければ`tenant_context_untrusted`としてPDP/capability resolver呼出し前に拒否する。
- 共通SaaS request contextはresolverの元値ではなく再照合後のTenantContextだけを管理API、DB guard、capability resolverへ渡す。停止membership、未知resolution method、別membership証跡を権限なしのEmptyや成功responseへ変換しない。
- session builder／route／管理API／verified tenantの近接48件、backend全体433件pass・条件付き25件skip、Ruff、docs-check、diff-checkを通過した。auth edgeのcredential方式はcookie、bearer、forward-authの選択と検証責任が未確定なため推測実装せず、既定unavailableとSaaS起動拒否を維持する。

### Implementation checkpoint 2026-07-17: trusted outbound redirect refusal

- `urllib`の既定redirect追跡で、設定検証済みendpoint／LLM host allowlistから別接続先へ遷移できる経路を閉じた。外部PDP、監査HTTP、Document policy binding、tenant capability、LLM providerは共通のtrusted HTTP openerを使い、3xxで後続requestを生成しない。
- 固定bearer、server-resolved tenant context、binding lookup、promptをredirect先へ転送しない。redirectは各adapterの既存HTTP／transport失敗として処理し、PDP・binding・capabilityのfail-safeや監査dispatcherのfail-open方針自体は変更しない。
- redirect handler単体と全adapter近接84件、backend全体435件pass・条件付き25件skip、Ruff、docs-check、diff-checkを通過した。trusted auth edge、PostgreSQL実地matrix、SaaS runtime配線は未完了のため起動拒否を維持する。

### Implementation checkpoint 2026-07-17: strict external PDP response

- 外部PDP応答を64KiB以下に制限し、`allow`必須、任意`readOnly/reason`だけのclosed-world objectとして検証する。非object、余分なfield、非UTF-8/非JSON、型不正、512文字超または制御文字を含むreasonを`AccessControlInvalidPolicyError`へ正規化し、raw値をclientやlogへ反射しない。
- 不正応答は既存の`policy_ref_invalid`へ写像し、SaaS deny modeでreadを含めて拒否する。SafeMode/readOnly優先順、single-tenant互換のfail-safe選択、外部PDPの評価内容自体は変更しない。
- 外部PDP／tenant境界／管理・session route近接44件、backend全体442件pass・条件付き25件skip、Ruff、docs-check、diff-checkを通過した。

### Implementation checkpoint 2026-07-18: trusted PDP and audit settings

- 外部PDPと監査HTTPへbinding/capability resolverと同じtrusted endpoint guardを適用した。credential/query/fragment、非loopback HTTP、空白・制御文字・backslash、不正portを拒否し、3xx拒否と組み合わせて検証済みの元endpoint以外へ送信しない。
- adapter/transportが無効なままendpoint・API keyを残す構成、endpointなしのbearer/IdP issuer、非canonical secret/header、0以下または30秒超のtimeout、0件queueを起動時に拒否する。endpoint未設定時の既存single-tenant noop fallbackは維持する。
- settings／外部PDP／監査／binding／capability近接114件、backend全体468件pass・条件付き25件skip、Ruff、docs-check、diff-checkを通過した。

### Implementation checkpoint 2026-07-18: bounded LLM provider response

- local/large-scale共通のHTTP provider応答を1MiB以下、`text`単独fieldのobjectへ限定した。非UTF-8/非JSON、非object、余分なtoken等のfield、size超過、text型不正は`provider_validation`へ正規化し、raw値をclient・logへ反射しない。
- trusted HTTPのredirect拒否と組み合わせ、tenant由来promptを別接続先へ転送せず、巨大・拡張応答をproposal処理へ渡さない。`KJ_ATLAS_LLM_PROVIDER=none`既定、local-first、明示opt-in、proposal-onlyは変更しない。
- LLM／AI契約近接48件、backend全体472件pass・条件付き25件skip、Ruff、docs-check、diff-checkを通過した。

### Implementation checkpoint 2026-07-18: tenant-required bounded audit event

- view/export/CE4 auditのtenantIdを自由形式metadataからevent envelopeの必須fieldへ移し、認可・repositoryと同じserver-resolved TenantContextだけを渡すようにした。欠損・空値・前後空白・制御文字・256文字超のtenantIdではeventを構築せず、client入力から補完しない。
- HTTP eventは64KiB以下、metadataは32 field、key 128文字、文字列値1,024文字、有限かつboundedな数値へ制限した。本文・prompt・email・token・secret・credential・assertion等のkeyを固定値へredactし、過大文字列・非finite numberをqueueや送信先へ保持しない。監査transport障害時の既存fail-open方針は維持する。
- 監査単体とDocument audit integrationの近接30件、backend全体477件pass・条件付き25件skip、Ruff、docs-check、active issue validator、diff-checkを通過した。MCP/worker/cache/storageを含む完全negative matrixが未完了のためAC-8とSaaS起動拒否は継続する。

### Implementation checkpoint 2026-07-18: fail-fast LLM destination settings

- local/large-scale LLM base URLへ他のtrusted HTTP連携と同じcanonical URL guardを適用し、credential/query/fragment、空白・制御文字・backslash、不正port、非loopback HTTPを起動時に拒否する。model IDも256文字以下、空白・制御文字・backslashなしへ限定した。
- large-scale providerは既存の明示opt-inとescalation許可に加え、base URL、model、canonical host allowlistの完全セットを必須にした。allowlistのURL、wildcard、port、path、空要素、重複と、base URL hostnameのallowlist不一致をfail-fastにし、tenant由来promptを未検証宛先へ送らない。
- LLM設定・provider・公開設定契約の近接81件、backend全体509件pass・条件付き25件skip、Ruff、docs-check、active issue validator、diff-checkを通過した。LLMは引き続き既定none、明示opt-in、proposal-onlyであり、SaaS起動拒否は変更しない。

### Implementation checkpoint 2026-07-18: bounded LLM provider request

- local/large-scale共通のHTTP requestをUTF-8 JSONで1MiB以下に制限し、taskを128文字以下のlowercase canonical ID、promptを非空文字列、temperatureをfiniteな0〜2、max tokensを1〜32,768へ限定した。過大prompt、`NaN`/`Infinity`、不正task/parameterはJSON化・transport呼出し前に`provider_validation`で停止し、入力値をerrorへ反射しない。
- request/responseの`provider_validation`は`KJ_ATLAS_LLM_FALLBACK_TO_NONE=true`でもfallback対象にせず、契約違反をprovider disabledの503へ変換しない。timeout/unavailableに対する既存fallback、既定none、明示opt-in、proposal-onlyは維持する。
- LLM provider・AI route近接56件、backend全体519件pass・条件付き25件skip、Ruff、docs-check、active issue validator、diff-checkを通過した。SaaS起動拒否は変更しない。

### Implementation checkpoint 2026-07-18: bounded external PDP request

- 外部PDPへ送るserver-composed requestをcompact UTF-8 JSONで64KiB以下に制限し、識別子を256文字以下、policyRefを2,048文字以下、roles/groupsを各64件以下の重複なしcanonical文字列へ限定した。subject/resource欠損、未知action/visibility、型不正、前後空白・制御文字、上限超過はtransport前に停止し、入力値をerrorへ反射しない。
- 不正requestを`adapter_error`へ正規化し、SaaS deny modeではreadを含めてfail-closedにする。PDPによるrole/group/policyRefの意味評価、既存SafeMode/readOnly優先順、single-tenant互換のfail-safe選択は変更しない。
- 外部PDP／tenant境界／管理・session route近接46件、backend全体527件pass・条件付き25件skip、Ruff、docs-check、active issue validatorと同validatorの13件、diff-checkを通過した。PostgreSQL実地matrix、trusted auth edge、active tenant変更、MCP/worker/cache/storageを含む完全negative matrixは未完了であり、SaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-18: bounded binding and capability requests

- Document policy binding lookupはtenantIdを256文字以下、bindingId/policyVersionを128文字以下、tenant capability lookupはprincipalId/tenantId/membershipIdを各256文字以下のcanonicalなserver-owned IDへ限定し、両requestをcompact UTF-8 JSONで64KiB以下に制限した。前後空白、制御・非表示文字、欠損、長さ・size超過はtransport前に停止し、入力値をerrorへ反射しない。
- binding lookupの不正contextはpolicyRef解決失敗として`Restricted + policy_ref_missing`へ、capability lookupの不正contextは`capability_resolution_unavailable`へ既存境界でfail-closedにする。API key、raw policyRef、role/groupはrequestへ追加せず、SafeMode、PDP、single-tenant互換方針は変更しない。
- binding/capability／resource／session／管理API近接100件、backend全体537件pass・条件付き25件skip、Ruff、docs-check、active issue validator、diff-checkを通過した。trusted auth edge、PostgreSQL実地matrix、active tenant変更とconsumer完全negative matrixが未完了のためSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-18: bounded session context response

- server-side session builderとresponse modelを、principal/tenant ID 256文字、tenant表示名256文字、capability version 128文字、available tenant 1〜256件、既知capability最大11件のclosed-world契約へ限定した。重複tenant/capability、前後空白、制御・非表示文字、上限超過は値を反射せず`session_context_unavailable`または`capability_resolution_unavailable`へfail-closedにする。active tenant内部切替もrequested tenant IDをDB照会前に同じcanonical上限で検証し、不正値は存在を推測させない404へ正規化する。
- frontend fetchは成功・エラーresponseのstreamを64KiBまでで打ち切り、超過時は後続chunkをcancelして全bodyを読み込まない。成功responseは厳密なUTF-8として同じfield・件数・長さ・重複禁止を再検証した値だけからbrowser storage scopeを構成する。scope keyもdeployment 2,048文字、tenant/principal/base key 256文字以下とし、制御・非表示文字や過大値をlocalStorageへ使用しない。公開UIとlegacy single-tenant key互換は変更しない。
- session用途のactive tenant候補queryは上限+1の257件で打ち切り、DB結果を無制限にmaterializeせず過大allowlistを判定する。
- session/capability/管理APIのbackend近接77件と最終response統合38件、backend全体552件pass・条件付き25件skip、DB query上限follow-up近接47件、frontend session/storage/transition/client近接47件、frontend全体1,122件・198 file pass、Ruff、frontend typecheck、docs-check、active issue validator、diff-checkを通過した。うちclient近接33件ではchunked responseの即時cancel、後続chunk非読取、過大エラーbodyのstatus fallback、非UTF-8拒否を確認した。App session bootstrap、active tenant永続化、logout/切替hook実配線が未完了のためAC-6/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-18: App browser storage scope binding

- AppのlocalStorage consumerをscope付きfacadeへ集約し、recent document、view mode/locale/visibility、reviewer、empty-canvas onboarding、advanced UIをmount時に検証・snapshotした単一`deployment + tenantId + principalId`へbindingした。MinimapとPatch WorkspaceのQueryPresetにも同じscopeを伝播する。facade外の直接利用をsource guardで検出し、入力scope objectの事後変更でも保存先を差し替えない。
- 同じApp mountの途中でscope identityが変化した場合は例外停止し、旧tenantの文書・選択・worker等のmemory stateを次tenantへ継続させない。正規の切替は既存transition coordinatorによるcleanupとhard document replacementを必須とする。scope省略時は既存single-tenant keyとUI挙動を維持し、SaaS UIは有効化しない。
- storage/session/UI regression近接57件、frontend全体1,127件・199 file、typecheck、production build、docs-check、active issue validator、diff-checkを通過した。App起動時のsession bootstrap、auth失敗UI、active tenant永続化、logout/切替cleanup hookの実配線、実ブラウザtenant A/B E2Eは未完了のためAC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-18: App runtime hard-replacement cleanup

- App unmount時に進行中のdiff・diagnostics・bundle AbortControllerを先にabortし、bundle task runnerをcancelしてからdiff・diagnostics workerをdisposeする共通cleanupを結線した。既存のsnapshot object URL revoke、diff effect abort、highlight timer clearと組み合わせ、hard document replacement後に旧tenant由来の非同期処理を継続させない。
- cleanupはnull resourceを無視し、個別のabort/cancel/disposeが例外でも後続resourceの破棄を続ける。cleanupの順序、失敗分離、空resource、App unmount配線を近接4件で固定し、worker・bundle・transition・storageを含む近接51件、frontend全体1,131件・200 file、typecheck、production build、docs-check、active issue validator、diff-checkを通過した。
- App起動時session bootstrap、logout/active tenant切替からtransition coordinatorとhard replacementを起動する実配線、実ブラウザでの旧DOM・memory・object URL非残留E2Eは未完了のためAC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-18: fail-closed active tenant change boundary

- `POST /session/active-tenant`を追加し、trusted identityと現在TenantContextをrequestごとに再解決してから、要求tenantを同じprincipalのactive membership allowlistで再照合する。成功responseをclosed-world・64KiB以下へ構築できた場合だけ、server検証済みprincipal、旧TenantContext、選択済みTenantContextをtrusted session persisterへ渡す。header、query、role/group、raw request tenant値を保存値に使わない。
- 認証基盤固有のsession形式とanti-forgery検証は注入adapterの責務とし、adapter欠損・予期しない保存障害は`503 active_tenant_update_unavailable`へ正規化する。未知・非canonical・他principal・停止membershipは保存前に404相当で拒否し、trusted adapterのanti-forgery拒否は維持する。frontend clientも現在の検証済みallowlist外を通信前に拒否し、成功応答のprincipal不変・要求tenant一致を再検証する。
- backend route近接24件、frontend session/storage/transition近接46件、backend全体561件pass・条件付き25件skip（追加のclosed-world request testは近接再実行）、frontend全体1,135件・200 file、Ruff、frontend typecheck、production build、docs-check、active issue validator、diff-checkを通過した。trusted auth edge／anti-forgery付きpersisterの実runtime接続、App session bootstrap、tenant switcherからtransition coordinatorとhard replacementを起動する配線、実ブラウザE2Eは未完了のためAC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-18: pre-App tenant session bootstrap gate

- tenant-scoped Appをmountする前にsession contextを取得・再検証し、成功時だけ`deployment + tenantId + principalId` browser storage scopeを構築するbootstrap境界を追加した。注入loaderが型を偽装してもclosed-world validatorを再実行し、lifecycle abort後の結果は利用しない。
- 401、403、session解決不能、不正session response、不正deploymentをstable reasonへ正規化し、旧App本文をmountしないretry可能なblocked stateへ分離した。blocked UIは日本語・英語、`role=status/alert`、見出しfocus、retryを備え、upstream error detail、principal、tenant値を表示しない。
- bootstrap／blocked UI／session／i18n近接64件、frontend全体1,146件・202 file、typecheck、production build、docs-check、active issue validator、diff-checkを通過した。安全なSaaS runtime mode signalが未確定のため現行`main.tsx`には接続せず、single-tenant起動を維持する。trusted auth edge／session persister、entry point、tenant switcher／logout実配線、実ブラウザE2Eが未完了のためAC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-18: allowlist-only tenant control

- Workspace用tenant controlを追加し、検証済みactive membershipが1件ならactive tenant名のlabelだけ、複数ならserver返却`availableTenants`だけをoptionとするselectを表示する。active tenantは表示名とaccessible nameで示し、色だけに依存しない。切替中はselectをdisabledにしてstatusを通知し、日本語・英語を同じ構造で提供する。
- 選択解決はsession contractを再検証し、active tenant自身、allowlist外の自由入力、invalid sessionでは変更callbackを発火しない。UIはrole/groupを解釈せず、tenant検索・text input・Platform横断候補を持たない。未保存変更の保存／破棄／取消確認、POST、transition coordinatorは親Appの責務として分離する。
- tenant control／bootstrap／session／i18n近接66件、frontend全体1,151件・203 file、typecheck、production build、docs-check、active issue validator、diff-checkを通過した。runtime mode signal、現行entry point、未保存変更確認、POST／hard replacement実配線、実ブラウザE2Eは未完了のためcontrolを実画面へ出さず、AC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-18: closed-world runtime bootstrap policy

- `GET /session/bootstrap-policy`を追加し、settings validation済みのserver runtime profileを起動時にsnapshotして、profile名やtenant情報を公開せず`single-tenant`／`tenant-session-required`の2値だけへ写像する。header、query、Document payloadを判定根拠にせず、未知・欠損profileは`503 runtime_policy_unavailable`として値を反射せず閉じる。現行settingsは予約中の`saas-multitenant`を引き続き起動前に拒否する。
- frontend clientはsame-origin・`no-store`でpolicyを取得し、成功・エラーresponseを4KiBまでで打ち切る。成功responseは単一fieldのclosed-world objectとして再検証し、未知mode、余分なfield、非JSON、非UTF-8、過大bodyをentry point判定へ渡さない。
- backend route近接32件、frontend policy/client近接29件、backend全体570件pass・条件付き25件skip、frontend全体1,162件・204 file、Ruff、frontend typecheck、production build、docs-check、active issue validator、diff-checkを通過した。local-first/offline起動を維持しつつSaaS側のpolicy取得失敗をblockedへ倒すentry point activation契約は未確定のため`main.tsx`へは接続しない。trusted auth edge／session persister、未保存変更確認、POST／hard replacement実配線、実ブラウザE2Eは未完了であり、AC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-19: profile-bound frontend entry activation

- frontend buildへ既存`KJ_ATLAS_RUNTIME_PROFILE`を渡し、未指定・`local-dev`・`evaluation`・`enterprise-production`はpolicy通信なしのlocal-first App、`saas-multitenant`だけはserver policy一致→session再検証→tenant scope付きAppの順でmountするentry pointを結線した。未知・空・前後空白を含むbuild値、policy取得失敗・不一致はsingle-tenantへfallbackせず、旧App本文のないblocked stateへ閉じる。
- 公式Composeはbackend environmentとfrontend buildへ同じ`${KJ_ATLAS_RUNTIME_PROFILE:-evaluation}`を渡し、契約testで両delivery surfaceの一致を固定した。現行backend settingsは`saas-multitenant`を引き続き起動前に拒否するため、frontend配線だけでSaaSを解禁しない。
- runtime entry／policy／session／UI近接27件、frontend全体1,209件・211 file、frontend typecheck、`saas-multitenant` production build、profile delivery契約4件、docs-check、active issue validator、diff-checkを通過した。実ブラウザではSaaS build＋policy未接続時にalertだけを表示して旧Appをmountしないこと、`evaluation` dev buildでは従来AppとSafeMode ONを表示することを確認した。trusted auth edge／session persister、未保存変更確認、tenant switch POST／transition／hard replacement実配線、tenant A/B実ブラウザE2Eは未完了であり、AC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-19: gated tenant switch request preparation

- future SaaS用に未保存変更の保存／破棄／取消を選ぶ`alertdialog`を追加した。取消へ初期focusを置き、Escapeを取消へ写像し、Tab focusをdialog内へ閉じ、処理中は3操作を無効化してstatusを読み上げる。ja/enの同一契約を持ち、表示にはserver返却のtenant表示名だけを使ってopaque tenant IDを出さない。
- request coordinatorはcurrent sessionを再検証し、active tenant自身は通信せず、allowlist外の自由入力、current sessionと旧browser scopeの不一致、欠損・未知の未保存変更decisionをPOST前に拒否する。保存失敗と取消ではPOST／cleanup／navigationを開始しない。POST成功後もprincipal不変・要求tenant一致を独立に再検証し、不正responseでは旧scope削除やhard replacementを開始しない。検証済みsession変更後はcomponent abortより旧DOM破棄とhard replacementを優先する。
- 切替／cleanup／control／dialog／i18n近接82件・13 file、frontend全体1,223件・213 file、frontend typecheck、`saas-multitenant` production build、docs-check、active issue validatorを通過した。安全ゲート未充足のためcontrol／dialog／coordinatorは現行Appへ接続せず、trusted auth edge／anti-forgery付きsession persister、App保存・runtime cleanup実配線、tenant A/B実ブラウザE2Eは未完了である。AC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-19: dormant App tenant switch host

- Appへ検証済み`TenantSessionContextV1`を任意注入できるtenant switch hostを追加し、注入時はsession由来のdeployment／principal／tenantとbrowser storage scopeの完全一致をmount前に再検証する。session非注入時のsingle-tenant動作は維持し、現行`main.tsx`は意図的にsessionを渡さないため、production entryではtenant controlをまだ表示しない。
- 切替確認の取消・保存失敗では旧Appを維持してtenant selectへfocusを戻し、切替開始後は旧tenant DOMをloading／blocked viewへ置換する。成功応答を再検証してから、進行中request・worker・task・object URL・timerの破棄、browser storage facade経由の旧scope削除、hard document replacementを順に実行する。Appからraw `window.localStorage`へは触れず、cleanup能力がない場合はPOST前にfail-closedとした。
- session／switch／cleanup／storage／UI近接54件・9 file、frontend全体1,233件・214 file、frontend typecheck、`saas-multitenant` production buildを通過した。実ブラウザではSaaS buildがalertだけでfail-closedとなり旧Canvas／tenant controlを表示しないこと、`evaluation` dev buildが従来CanvasとSafeMode ONを表示しtenant controlを出さないことを確認した。trusted SaaS auth edge、anti-forgery付きsession persisterの実runtime接続、PostgreSQL RLS実地検証、MCP／worker／cache／browserを含むtenant A/B negative matrix、production entryへのsession注入は未完了であり、AC-6/8/10/12とSaaS起動拒否を継続する。

### Implementation checkpoint 2026-07-19: atomic trusted SaaS runtime adapter bundle

- application起動前に限り、trusted SaaS identity resolver、tenant resolver、active tenant session persisterを単一の型付きbundleとして注入できる境界を追加した。3要素の欠損、未検証bundle state、起動後の注入、同一App上の別bundle差し替えを拒否し、main lifespanが3要素を同時にだけ適用する。
- bundle非注入時はidentity resolverとsession persisterをunavailable、tenant resolverを既存single-tenant互換へ毎起動時に戻すため、既存利用を維持しながらsession APIをfail-closedに保つ。環境変数やrequest headerからadapterを選ぶ経路は追加せず、実IdP／trusted proxyの検証方式、anti-forgery付きsession形式、SaaS profileの起動許可は行っていない。
- bundle境界、session route、Tenant Admin routeの近接49件、初回backend全体runの成功564件、環境PATH補正後のmigration 15件、条件付き25件skip、backend全体Ruffを通過した。全体一括実行では子processの`alembic`未検出を補正後に5分上限へ到達したため、初回成功分と該当migration再実行へ分割して確認した。実auth edge adapter／session persister、PostgreSQL RLS実地検証、完全なtenant A/B negative matrixは外部runtimeと検証環境が必要なため、AC-4/5/6/7/8/10/12とSaaS起動拒否を継続する。

### Design security checkpoint 2026-07-19: active tenant session concurrency

- active tenantを認証セッションへ保存する現行targetでは、別タブでの切替後に古いタブの表示・payload・`docId`とserver sessionのtenantが食い違うscope confusionが未定義だった。両tenantに同じ`docId`があり、同一利用者が両方へ書込可能な場合、旧tenant内容を新tenantへ誤適用できるため、UI cleanupだけでは不十分と判断した。
- `ADR-0061`でactive tenantを認証セッション単位の単一値とし、server-issued `tenantSessionVersion`をsession context、conditional tenant switch、全tenant-scoped APIのexpected-context preconditionへ追加する方針をAcceptedとした。client versionは認可根拠にせず、trusted session再解決後かつresource lookup前のstale guardに限る。欠損・不一致は本文を返さず、自動再送しない。
- master data UI構想へsingle-tenant Platform operatorとfuture SaaS Tenant Adminの権限分離、capability/route surface行列、別タブ・bfcache・遅延responseのblocked stateを追加した。Claude Design Round 8へR8-Hを追加し、他タブへの影響、旧本文を背景へ残さないscope再確認、stale save拒否、390px/ja-en/focus状態のレッドラインを要求する。
- これは設計・契約固定だけであり、`tenantSessionVersion` API、auth/session adapter、全route guard、cross-tab通知は未実装である。AC-13を追加し、既存AC-4/5/6/7/8/10/12とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-19: conditional tenant session version

- trusted auth/session adapter境界を、active tenant stateに束縛した1〜128文字のASCII opaque `tenantSessionVersion`解決と、expected versionの原子的比較・tenant更新・新version発行を担う契約へ拡張した。session contextはmembership再確認後のadapter値だけを返し、欠損・不正値・adapter例外を値非反射の`503 session_context_unavailable`へ閉じる。
- `POST /session/active-tenant`へ`expectedTenantSessionVersion`を必須化し、現versionとのconstant-time相当の事前比較とadapter内の原子的比較を二段で要求した。事前または同時更新競合は資源・現tenant・生versionを返さない`409 tenant_session_changed`とし、保存前に最大長versionでresponse上限を検証する。adapterが同じversion、不正version、予期しない例外を返す場合も成功扱いにしない。
- frontendのclosed-world session validator、active tenant client、request coordinatorを同期し、現在versionをPOSTし、principal不変・要求tenant一致・version変更をすべて確認するまでcleanup、旧scope削除、hard replacementを開始しない。backend近接86件（session 76件＋Tenant Admin 10件）と全体591件・条件付き25件skip、frontend近接84件と全体1,252件・217 file、frontend typecheck、backend全体Ruff、docs-checkを通過した。
- これはsession context／active tenant切替の基盤sliceである。実auth edge adapterとanti-forgery付きsession形式、全tenant-scoped APIのresource lookup前guard、BroadcastChannel、bfcache／resume再確認、stale response／worker commit拒否、SaaS runtime起動許可は未実装であり、AC-4/5/6/7/8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-19: browser tenant session coherence boundary

- future SaaS App hostへ、固定same-origin BroadcastChannelで`null`だけを通知するcoherence境界を追加した。channel名・payloadへtenant ID、principal ID、capability、本文、`tenantSessionVersion`を含めず、通知生成失敗・送信失敗でも検証済みlocal切替のcleanup／hard replacementを止めない。server preconditionを引き続き権威とする。
- 別タブ通知受信、`pageshow.persisted=true`、online復帰、5分以上の非表示からの復帰を一度だけのscope invalidationへ集約した。invalidation時はlistener／channelを先に破棄し、進行中request、task、workerを停止して旧Appをblocked viewへ置換する。local切替はserver応答のprincipal／tenant／新version検証後、cleanupとreplacementより前に通知する。
- coherence／App host／switch coordinator近接27件、frontend全体1,259件・218 file、frontend typecheck、docs-checkを通過した。現行production entryはsession contextを注入しないため境界はdormantで、実ブラウザの複数タブE2E、全APIのserver guard、stale response／worker resultの世代commit拒否は未完了である。AC-8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-19: tenant API session precondition guard

- SaaS profileでだけ有効になる共通request guardを追加し、`KJ-Atlas-Tenant-Session-Version`を単一headerとして固定した。trusted sessionの現versionを解決した後に照合し、欠損・重複・不正・不一致を値非反射の`409 tenant_session_changed`へ統一する。client headerはidentity、tenant、membership、capabilityの解決には使用しない。
- `/docs`の共通認可境界と`/tenant-admin/document-access`の管理認可境界へ組み込み、SaaS時は文書・metadataのlookupより先に停止する。既存のlocal／evaluation／enterprise profileはheaderを要求せず互換動作を維持し、不明runtime policyは`503 runtime_policy_unavailable`へfail-closedにする。
- 共通guard、文書のtenant分離／access control、Tenant Adminの近接31件、backend全体596件・条件付き25件skip、backend全体Ruff、docs-checkを通過した。export、share、import、MCP、webhook、その他Tenant Admin、非同期job開始点への横断適用、frontend API clientからのheader付与、CORS／proxy実配備検証、SaaS runtime起動許可は未完了であり、AC-4/5/6/7/8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-19: document client session precondition wiring

- SaaS runtime entryでbootstrap済みsession contextと一致するbrowser storage scopeをAppへ同時注入するようにし、App側のclosed-world再検証を通過したcontextだけを文書clientへ渡す。単一テナントentryはsession未注入のままとし、既存requestへheaderを追加しない。
- `GET/PUT /docs/{doc_id}`と`POST /docs/{doc_id}/export-audit`へ単一の`KJ-Atlas-Tenant-Session-Version`を付与した。clientは呼出時にもsession contractを再検証し、不正contextは通信前に拒否する。serverの`409 tenant_session_changed`はDocument metadata競合として保存再試行へ流さず、runtime resourceをcleanupして旧Appをblocked化する。
- client／bootstrap／tenant switch／coherenceの近接62件、frontend全体1,263件・218 file、frontend typecheck、docs-checkを通過した。文書以外のtenant-scoped client、document request自体の共通abort／世代commit guard、実ブラウザ複数タブE2E、SaaS runtime起動許可は未完了であり、AC-8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-20: AI and context session precondition wiring

- 文書内容・source ID・proposal判断を扱う全`POST /ai/*`と`POST /context/*`へ共通dependencyを追加した。SaaS profileではtrusted identity／tenant sessionを再解決し、単一`KJ-Atlas-Tenant-Session-Version`をendpoint本体、LLM transport、audit記録、bundle生成より先に照合する。read-onlyな`GET /ai/provider-status`はtenant資源を扱わないため対象外とした。single-tenant profileは既存requestを維持する。
- frontendのlayout、merge、island summary、proposal audit、relation summary、narrative check／generationの7 mutationへ、bootstrap済みsessionのopaque versionだけを付与した。`tenant_session_changed`はprovider fallbackへ流さず、既存runtime cleanup後に旧Appをblocked化する共通ラッパーを通す。merge候補のlocal fallbackは404/405/501、network failure、または`provider_unavailable`の503だけに限定し、session/capability系503を処理継続へ変換しない。
- backend route dependency／AI／context近接48件と全体605件・条件付き25件skip、frontend client／App source guard近接64件と全体1,267件・218 file、backend Ruff、frontend typecheck、docs-check、active issue validatorを通過した。import、share、MCP、webhook、非同期job開始点、request／worker結果の世代commit guard、実ブラウザ複数タブE2E、SaaS runtime起動許可は未完了であり、AC-8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-20: stale network response generation guard

- App instanceごとのtenant session generation guardを追加し、runtime cleanupの開始時にgenerationを単調に無効化する。Document read／create／write、export監査、文書内容を扱うAI mutationは開始時generation内で成功した結果だけを呼出元へ返し、別タブ通知、bfcache／online／長時間非表示復帰、serverの`tenant_session_changed`後に到着した旧成功responseをDocument state、AI proposal、監査後続処理へcommitしない。
- guardはtenant、principal、capability、生`tenantSessionVersion`を保持・比較せず、client expected-contextの認可根拠化を避ける。single-tenantでも同じApp lifecycle整合性を得るが、request headerやserver認可契約は変更しない。server不一致時のcleanupは共通request wrapperだけが一度行い、Document conflictやprovider fallbackへ変換しない。
- 遅延Promiseの現generation成功／無効化後拒否／次generation分離をunit testで固定した。frontend近接39件と全体1,270件・219 file、typecheck、production build、docs-check、active issue validatorを通過した。workerのabort／dispose後の全結果、import処理、object URL、全tenant-scoped非ブラウザclientを同じgenerationで横断的にcommit拒否する境界、実ブラウザ複数タブE2Eは未完了であり、AC-8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-20: stale App worker result generation guard

- Document比較diff worker、outline診断worker、bundle生成task／workerのPromiseをnetwork responseと同じtenant session generation guardへ通した。既存abort／disposeに遅延成功結果のcommit拒否を重ね、旧generationのdiff／診断結果をstateへ適用せず、旧generationのbundle zipをdownloadへ渡さない。
- stale専用例外はblocked Appの状態表示へ上書きせず破棄し、それ以外のworker失敗契約は維持する。近接worker／bundle／App source guard 77件とfrontend全体1,270件・219 file、typecheck、production build、docs-check、active issue validatorを通過した。
- `InquiryJourneyPrototypePanel`等のApp外worker、File／zip／public pack import、PNG等の非worker非同期export、object URLの生成前後、全tenant-scoped非ブラウザclient、実ブラウザ複数タブE2Eは未完了であり、AC-8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-20: stale local import generation guard

- App内のDocument JSON、view metadata、comparison Document、review-pack zip、patch、patch baselineの全File読取をtenant session generation guardへ通した。scope失効後に完了した読取は解析・preview・comparison・patch stateへcommitせず、エラー表示でblocked viewを上書きしない。
- review-packはzip展開とintegrity検証、patchはfingerprint検証の各非同期境界もguardし、snapshot object URL生成を最後の非同期検証より後へ移した。これによりstale検証結果からURLを生成・保持しない。SafeMode、import validation、人手適用前previewの既存境界は変更しない。
- import／integrity／patch／App source guard近接69件とfrontend全体1,270件・219 file、typecheck、production build、docs-check、active issue validatorを通過した。server import、public pack、PNG等の非worker非同期export、App外worker、全tenant-scoped非ブラウザclient、実ブラウザ複数タブE2Eは未完了であり、AC-8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-20: stale asynchronous export generation guard

- abstract map Markdown／HTML snapshot、viewport／visible-bounds PNG、patch export、agent task Markdown／JSONの非同期生成結果をtenant session generation guardへ通した。scope失効後に完了したBlob、data URL、fingerprint付きpatch、task sheetはdownload／clipboard APIを呼ばず破棄する。
- 同期SVG／JSON exportは同一event turn内で生成・downloadするため今回の非同期結果境界の対象外とした。clipboard書込APIを呼び出した後のOS側commitは取消不能であり、生成結果の照合を呼出直前に置く境界までとする。
- export／patch／agent task／App source guard近接57件とfrontend全体1,270件・219 file、typecheck、production build、docs-check、active issue validatorを通過した。server import、public pack、App外worker、MCP等の非ブラウザclient、実ブラウザ複数タブE2Eは未完了であり、AC-8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-20: stale public pack generation guard

- public pack loaderをmanifest、Document、任意viewの全fetch／text decode／strict parseをtenant session generation guard内で完了してからApp stateへ一括commitする構造へ変更した。view取得前にDocumentだけをcommitする中間状態を廃止した。
- loader結果をloaded／not-found／staleのclosed unionへ分離し、stale時はDocument APIや組込みsampleへ自動fallbackしない。これにより旧scopeで開始したpack内容を新scopeの代替sourceとして再読込・commitしない。
- public pack／Document／view／App source guard近接64件とfrontend全体1,270件・219 file、typecheck、production build、docs-check、active issue validatorを通過した。server import、App外worker、MCP等の非ブラウザclient、実ブラウザ複数タブE2Eは未完了であり、AC-8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-20: child worker generation guard

- Appから問い合わせjourney panelとSidePanelへtenant session generation guardを注入し、子コンポーネント所有の問い合わせbundle import worker、trace／trace analytics workerの完了結果を同じscopeで照合する構造へ変更した。
- 問い合わせbundleはFile読込とworker parseを一つのguarded taskとして扱い、traceは結果照合後だけstate更新またはclipboard処理へ進む。既存のAbortController／worker disposeも併用し、stale時は利用者向けエラーへ変換せず破棄する。
- worker／tenant generation／App source guard近接46件とfrontend全体1,270件・219 file、typecheck、production build、docs-check、active issue validatorを通過した。将来のserver import／share endpoint、MCP等の非ブラウザclient、実ブラウザ複数タブE2Eは未完了であり、AC-8/10/12/13とSaaS profile起動拒否を維持する。

### Implementation checkpoint 2026-07-20: runtime profile and adapter bundle binding

- trusted SaaS identity／tenant／session adapter bundleをruntime profileのtenant-session modeと起動時に原子的に照合するよう変更した。single-tenant profileへのbundle注入、SaaS profileでのbundle欠損、未知profileをadapter有効化前に拒否する。
- これによりtrusted tenant resolverだけが有効で`tenantSessionVersion` preconditionは無効という混成構成を防止する。現行releaseの`saas-multitenant` settings起動拒否は変更せず、既存3 profileはbundle非注入時だけ従来のsingle-tenant resolverで起動する。
- profile／bundle・session近接57件とbackend全体610件pass・条件付き25件skip、backend全体Ruff、変更対象format check、docs-check、active issue validatorを通過した。repository全体のformat checkは既存71ファイルが未整形のため非変更範囲として除外した。実auth edge adapter、PostgreSQL実地matrix、MCP等の非ブラウザclient、実ブラウザ複数タブE2Eは未完了であり、AC-4/5/6/7/8/10/12/13とSaaS profile起動拒否を維持する。
