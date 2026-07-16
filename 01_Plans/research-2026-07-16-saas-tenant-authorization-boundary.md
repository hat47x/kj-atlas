# リサーチ: SaaSを念頭に置いたテナント分離・権限制御境界

- Date: 2026-07-16
- Status: 調査・要件整理（Accepted契約ではない）
- Scope: 認証主体、テナント解決、データ分離、認可、Admin管理面、ブラウザ保存、監査、移行
- Related UI brief: `02_Architecture/design/master-data-settings-ui-ux-concept.md`
- Accepted ADR: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`

## 0. 結論

現行kj-atlasは、外部認証・外部PDPへ接続できる**単一デプロイ／単一テナント相当のOSS**であり、共有DB型SaaSのマルチテナント分離を保証していない。`enterprise_architecture.md`もSaaSマルチテナント管理を非目標としている。

SaaS対応では、テナントを単なる表示ラベルや外部PDPの判定条件にせず、アプリ本体が必ず守る**構造的なデータ境界**にする必要がある。具体的には、すべての永続データ・API・キャッシュ・非同期処理・監査・外部エージェント資格情報を`tenantId`でスコープし、主体テナントと資源テナントの不一致をPDP呼出前に必ず拒否する。

この変更はDBキー、identity一意性、API、認可失敗時の挙動、Admin責務、移行を横断する。`ADR-0059`はAcceptedだが、同ADRのImplementation gateを満たすまでSaaSを有効化してはならない。UIにテナント切替を追加するだけではSaaS対応にならない。

## 1. 現行実装の適用限界

| 領域 | 現状 | SaaSでの問題 |
| --- | --- | --- |
| Document | `documents.id`が全体主キー。tenant列なし | 同じdocIdをテナント別に持てず、IDORやクエリ漏れをDB構造で防げない |
| 子データ | `merge_decision_logs`は`doc_id`だけで従属 | tenantを失ったjoin・復旧・監査が起きうる |
| Identity | `provider + external_uid`が全体一意 | 複数IdPで`provider=oidc`等が衝突する。IdP issuerとtenant membershipを表現できない |
| AuthContext | user/roles/groupsはあるがtenant contextなし | どのテナントとして操作しているか確定できない |
| AccessRequest | docId/visibility/policyRefのみ | 主体tenantと資源tenantの一致を検証できない |
| 資源メタデータ | visibility/policyRefをrequest headerから受ける | 公開クライアントが書き換えられる構成では資源側の正本にならない |
| PDP障害 | 既定`read_only`はreadを許可。adapter不在・endpoint欠損は`noop`へ退避 | SaaSではread自体が越境漏えい。PDP不達時のread許可とnoop fallbackは不可 |
| Admin provisioning | globalな`POST /admin/provision/users`。専用の管理者認可なし | どのtenantのmembershipを作るか不明で、通常API keyだけでは管理主体を証明できない |
| Browser storage | recent/QueryPreset等がtenant/user名前空間を持たない | 同一ブラウザでtenantを切り替えた際に名前・条件・選択状態が混在する |
| Audit | docId中心でtenant相関なし | tenant別の追跡・保持・漏えい検知・証跡分離ができない |

したがって、現行の`enterprise-production` profileは組織内単一デプロイ向けであり、共有サービスとして複数顧客を同居させるprofileではない。

## 2. SaaS向け安全不変条件

1. **TenantContextは信頼済み入力から一意に解決する**。自由入力のtenantId、未署名header、localStorageの選択値を認可根拠にしない。
2. **主体tenantと資源tenantの一致をアプリ内で先に検証する**。roles/groupsの意味評価は外部PDPへ委譲してよいが、tenant不一致は委譲せず常にdenyする。
3. **すべてのtenant従属行はtenantIdを持つ**。子テーブル、agent registration、job、cache、object key、audit eventを例外にしない。
4. **tenant不明・不一致・PDP不達はdeny**。SaaS profileではread-only fallback、noop adapter、adapter欠損時allowを許可しない。
5. **資源のtenant/visibility/policyRefはサーバー正本から読む**。クライアントheaderやDocument payloadを信頼しない。
6. **認可はAPIで再実行する**。UIは許可された操作を説明するだけで、非表示・disabledを権限制御にしない。
7. **越境対象の存在を推測させない**。他tenantのIDへアクセスした場合、公開APIは原則としてnot found相当を返し、内部監査だけにdeny理由を残す。
8. **export/importはtenant権限の移送手段にしない**。exportにtenant membershipや権限を埋め込まず、import先tenantで新規に認可・レビューする。
9. **Supportの隠れた閲覧権限を作らない**。impersonationやbreak-glass閲覧は標準機能にせず、導入する場合は時間制限・理由・二者承認・監査を別ADRで扱う。

## 3. 推奨する論理モデル

### 3.1 TenantとIdentity

```text
Tenant
  id, displayName, lifecycleState, createdAt, updatedAt

IdentityProvider
  id, issuer, audience, providerType, lifecycleState

TenantIdentityProvider
  tenantId, identityProviderId, lifecycleState

User
  id, displayName?, email?, lifecycleState

UserIdentity
  id, userId, identityProviderId, subject, createdAt

TenantMembership
  tenantId, userId, lifecycleState, createdAt, updatedAt
```

- `User`はグローバルなopaque principal、所属は`TenantMembership`で分離する。1人が複数tenantへ所属できる。
- identityの一意性は曖昧な`provider`文字列ではなく、信頼済み`identityProviderId + subject`で固定する。`IdentityProvider`はissuerとaudienceを含むtrust configurationを識別し、tenantが使用できる接続は`TenantIdentityProvider`で明示する。
- roles/groupsは現行方針どおり永続マスタにせず、IdP/PDPからのtransient入力とする。membershipの有効/無効だけをアプリ側の構造境界として持つ。
- `reviewerRef/ownerRef=user:<users.id>`のopaque参照は維持できるが、資源アクセスには必ずtenant membershipを追加確認する。

### 3.2 Tenant従属データ

```text
Document
  tenantId, id, version, updatedAt, payloadJson
  unique(tenantId, id)

MergeDecisionLog
  tenantId, docId, ...
  foreign key(tenantId, docId) -> Document(tenantId, id)

AgentRegistration
  tenantId, registrationId, docId, displayName, tokenHash,
  lifecycleState, createdBy, createdAt, revokedAt?
```

- tenantIdは`payload_json`へ埋め込まず、サーバー管理列に置く。利用者が編集できるDocumentの一部にしない。
- 文書IDは現状任意文字列のため、tenantをまたいだ全体一意性を仮定せず`(tenantId, id)`を識別境界にする。
- すべてのDocument従属表は複合外部キーを持ち、docIdだけのjoinを許さない。
- object storage、検索index、queue/job、rate limit key、暗号鍵参照、backup manifestにもtenantIdを伝播する。

### 3.3 物理分離の段階

| 水準 | 用途 | 必須条件 |
| --- | --- | --- |
| Shared DB / shared schema | 一般SaaSの基準線 | 全行tenantId、複合制約、repositoryのtenant必須、PostgreSQL RLS等のDB側guard、越境negative test |
| schema / DB / bucket分離 | 規制・高機密tenantの選択肢 | provisioning、migration、backup/restore、鍵、監査をtenant単位で運用 |

shared schemaではRLS等のDB側guardとアプリのtenant一致検証を二重化し、どちらか一方だけへ依存しない。SQLite等、DB側guardを提供できない構成は共有SaaS profileで使わない。UIへtenant名を出すだけでshared schemaを安全とみなさない。

## 4. TenantContextと認可

推奨するrequest context:

```ts
type TenantContext = {
  tenantId: string;
  membershipId: string;
  resolvedBy: "verified_claim" | "trusted_host_mapping";
};

type AccessRequest = {
  action: "document.read" | "document.write" | "document.export" | "document.share"
    | "membership.provision" | "agent.register" | "agent.revoke" | "audit.read";
  auth: AuthContext;
  tenant: TenantContext;
  resource: { tenantId: string; kind: string; id: string; policyRef?: string };
  safeMode: boolean;
  readOnly: boolean;
};
```

評価順序:

1. 署名・proxy境界を検証しAuthContextを解決する。
2. host/path/verified claimからTenantContextを1つに解決する。
3. active membershipを確認する。
4. server-side resource lookupを`tenantId + resourceId`で行う。
5. `request.tenantId == resource.tenantId`をアプリ内で検証する。不一致・不明はdeny。
6. SafeMode / readOnlyのローカルガードを適用する。
7. 外部PDPへcapability判定を依頼する。PDP不達・無効応答はSaaSではdeny。
8. APIで最終的にenforceし、tenantIdを含む最小監査イベントを残す。

tenantIdをheaderで受ける場合、公開proxyは外部から届いた同名headerを必ず削除し、検証済み値だけを再付与する。ブラウザが指定した`X-Tenant-ID`をそのまま信頼しない。

### SaaS profileの必須条件

- `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http`等、実判定可能なadapterを必須化する。
- `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=deny`を必須化する。
- adapter endpoint欠損、`noop`、API keyだけの主体識別、tenant解決不能では起動またはrequestをfail-fastにする。
- `read_only` fallbackは単一組織内の可用性選択肢にはなりうるが、共有SaaSのtenant境界には使わない。

これらは新しいruntime profileと設定検証を伴うため、`runtime_parameter_registry.md`へ直接追加せずADRで先に決める。

## 5. 管理権限とUI責務

SaaSでは「管理者」を1種類にしない。

| 面 | 代表capability | 見える範囲 | 本文アクセス |
| --- | --- | --- | --- |
| Workspace | `document.read/write/export/share` | active tenantの認可済み文書 | capabilityに従う |
| Tenant Admin | `membership.provision`, `agent.register/revoke` | active tenantだけ | なし。docId等の固定メタデータのみ |
| Platform Control Plane | `tenant.provision/suspend`, system status | tenant lifecycleと非秘密の運用メタデータ | なし。文書タイトルも扱わない |
| Audit | `audit.read` | 明示許可されたtenantの固定メタデータ | なし |

- UIはrole名を解釈せず、backendが返す`effectiveCapabilities`で操作の有無と理由を表示する。APIは同じcapabilityを再検証する。
- Tenant Adminは自tenantのmembership/agentだけを扱い、Platform operator権限へ昇格できない。
- Platform Control PlaneとTenant Adminは別サーフェス・別認可とし、全tenantの文書一覧を持つ「スーパー管理画面」を作らない。
- 外部IdP/PDPで管理するroles/groupsはkj-atlas内で編集せず、必要なら外部管理先への案内を表示する。

### Tenant切替

- membershipが複数ある利用者だけに、選択肢がサーバーから与えられたtenant switcherを表示する。tenantId自由入力は不可。
- 切替時に未保存変更があれば、保存・破棄・取消を明示する。
- 確定後は文書、選択、検索、work mode、import preview、recent、QueryPreset、request cacheを一度破棄し、新tenantで再取得する。
- URL変更だけで切替完了とせず、backendが新TenantContextを確認するまで旧tenantのDOMを残さない。
- tenant mismatch / membership失効 / PDP不達はEmpty表示にせず、範囲を確認できないため表示しない状態にする。

## 6. ブラウザ保存・export・外部接続

- recent cacheとQueryPresetのstorage keyは少なくとも`deployment origin + tenantId + userId`で名前空間分離する。表示名やemailをkeyへ含めない。
- logout・tenant switch時に、memory cache、query cache、selection、clipboard補助、object URLを破棄する。
- View/Perspectiveの`view.json`はtenant bindingを権限として持たせない。別tenantへimportされた場合は、そのtenantの新規入力として検証・サニタイズする。
- export bundleへ内部tenantIdやmembershipを既定で含めない。必要なprovenanceはopaqueで明示opt-inかつ別契約にする。
- agent tokenはtenantIdとdocIdへ束縛し、他tenantのingestで使用できない。token hash・registration・ingest logのすべてにtenantIdを持たせる。

## 7. 必須の越境テスト

最低2tenant（A/B）と、同じ`docId`を両tenantへ作るfixtureで次を検証する。

- AのmemberがBの文書をGET/PUT/list/export/share/audit/merge-log/context/MCP/webhookで取得・変更できない。
- BのdocIdをURL、body、header、queryへ差し替えても存在を推測できない。
- list/search/count/paginationにBの件数・タイトル・更新日時が混入しない。
- recent/QueryPreset/view stateがtenant switch後に表示されない。
- background job、worker、audit、object storage、backup/restoreでtenant contextが欠落した場合は処理を停止する。
- PDP timeout、adapter例外、policy invalid、tenant mismatchでreadも拒否される。
- Platform Control Planeの主体が文書APIを暗黙に読めない。
- agent token、API credential、signed linkを別tenantへ再利用できない。

このnegative matrixを、単体のrole表示テストではなく、DBとAPIを含むintegration/E2Eで固定する。

## 8. 移行方式

推奨する段階移行:

1. **ADR/契約**: TenantContext、identity issuer、membership、tenant従属表、deny規則、SaaS profileを決定する。
2. **Expand**: `tenants` / `identity_providers` / `tenant_memberships`を追加し、tenant従属表へnullable tenantIdを追加する。
3. **Backfill**: 既存データを内部の`local-default` tenantへ割り当てる。exportされる利用者データへこの内部IDを埋め込まない。
4. **Dual read/write**: tenantId付きquery repositoryを導入し、docIdだけのDBアクセスを検出・禁止する。
5. **Constraint**: tenantIdをNOT NULL化し、複合unique/FKと必要に応じRLSを有効化する。
6. **SaaS profile**: noop/read-only fallbackを拒否し、tenant/PDP設定が不完全ならfail-fastにする。
7. **UI**: server-side capabilityとtenant contextが実装された後にswitcher/Tenant Admin/Control Planeを有効化する。

旧ローカル利用は`local-default`を内部注入するsingle-tenant adapterで互換を保つ。公開Document contractへtenantIdを必須追加しない。

## 9. ADR-0059で提案する判断（D5〜D10）

- **D5 Tenant resolution**: verified claim / trusted host mappingの採択と不一致時deny。
- **D6 Identity model**: issuer+subject、global User、TenantMembershipの関係。
- **D7 Data isolation**: tenantId列、複合unique/FK、RLS、regulated tenantの物理分離水準。
- **D8 Authorization**: tenant一致をローカル不変条件、roles/groups評価を外部PDP、SaaSはdeny-only。
- **D9 Control planes**: Tenant AdminとPlatform Control Planeの分離、support/break-glassの非目標。
- **D10 Compatibility**: `local-default` backfill、export非束縛、browser storage namespace、段階migration。

これらは長期的・横断的・破壊的な契約と安全境界を変えるため、`DATA-MODEL-OPS-02`のD1〜D4を暗黙に拡張せず、`ADR-0059`として採択した。実装順序と解禁条件は同ADRのImplementation gateに従う。

## Traceability

- `02_Architecture/enterprise_architecture.md`（現行はintegration readiness、SaaS multi-tenant非目標）
- `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`（Accepted）
- `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- `02_Architecture/api.md` §8、§9
- `02_Architecture/data_model_operations_overview.md` §2、§4、§5.2
- `02_Architecture/runtime_parameter_registry.md`（現行profilesとaccess-control設定）
- `THREAT_MODEL.md`
- `03_Implement/backend/src/kj_atlas_api/models.py`
- `03_Implement/backend/src/kj_atlas_api/auth_context.py`
- `03_Implement/backend/src/kj_atlas_api/access_control.py`
- `03_Implement/backend/src/kj_atlas_api/routes/docs.py`
- `03_Implement/backend/src/kj_atlas_api/routes/admin.py`
