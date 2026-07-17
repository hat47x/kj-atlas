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

- [ ] AC-1: `tenants`、`identity_providers`、`tenant_identity_providers`、`tenant_memberships`が実装され、identityは`identity_provider_id + subject`で一意になる。
- [ ] AC-2: 既存データが`local-default`へ損失なくbackfillされ、再実行しても結果が変わらない。
- [ ] AC-3: `documents`と全Document従属表がtenant複合制約を持ち、docIdだけのDB query/joinが静的検査またはtestで検出される。
- [ ] AC-4: SaaS profileでtenant不明・不一致、membership停止、adapter欠損、PDP不達をreadも含めてdenyする。
- [ ] AC-5: shared schemaでDB側tenant guardが有効で、別tenant contextを使った直接SQLも行を取得・更新できない。
- [ ] AC-6: `GET /session/context`とactive tenant変更がmembership allowlistだけを返し、自由入力tenantの発見・切替を許可しない。
- [ ] AC-7: Workspace、Tenant Admin、Platform Control Planeのcapability/audienceが分離され、Platform operatorに文書readが暗黙付与されない。
- [ ] AC-8: cache、job、MCP、agent credential、audit、storage keyにtenantIdが伝播し、欠落時は処理を停止する。
- [ ] AC-9: exportはtenant権限を移送せず、importはactive tenantで再認可・検証・人手レビューされる。
- [ ] AC-10: tenant A/Bへ同じdocIdを作成した越境negative matrixが、API/MCP/worker/browser cacheを含めて成功する。
- [ ] AC-11: single-tenantのlocal-dev/evaluation/enterprise-production互換テストが維持され、SafeMode既定ON、proposal-only、provider=`none`を弱めない。
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
