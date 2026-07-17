# Issue: SAAS-TENANT-01 TenantContext・保存境界・越境防止の実装

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security / Feature
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: User request 2026-07-16 / `01_Plans/research-2026-07-16-saas-tenant-authorization-boundary.md`
- Priority: P1
- Owner: Maintainer
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/frontend/`, `03_Implement/mcp/`, deploy/runtime settings and tests
- Related ADR/Spec: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `THREAT_MODEL.md`, `02_Architecture/schemas.md`, `02_Architecture/api.md`, `02_Architecture/runtime_parameter_registry.md`
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
7. **UI gate**: session contextとnegative matrixが通った後だけRound 8 R8-E/Fを実装候補へ昇格する。

各段階でtenant context欠落、backfill不整合、複合FK不整合、RLS context残留、PDP fail-openのいずれかを検出した場合は次段階へ進まない。

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

## 検証計画

- 実行する確認:
  - migrationのfresh DB / existing DB / rerun / rollback rehearsal。
  - repository・API・PDP adapterのunit/integration test。
  - PostgreSQL RLSでtenant A/Bを切り替える直接SQL testとconnection pool再利用test。
  - 同一docIdでGET/PUT/list/search/count/export/share/import/context/MCP/webhook/job/audit/agent credentialを試すnegative matrix。
  - tenant切替後のDOM、memory、query cache、recent、QueryPreset、object URLの残留確認。
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
