# ADR-0059: SaaSテナント分離と認可境界を構造化する

- Status: Accepted
- Date: 2026-07-16
- Deciders: Project Maintainer
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/frontend/`, `03_Implement/mcp/`, runtime/deploy configuration

## Context

現行kj-atlasは、外部認証と外部PDPへ接続できる単一デプロイ／単一組織向け構成である。`documents.id`はDB全体の主キーで、永続行、`AuthContext`、`AccessRequest`、ブラウザ保存にtenant境界がない。access-controlは構成により`noop`へ退避でき、PDP不達時の`read_only`はreadを許可する。これらは単一組織内の可用性選択肢にはなりうるが、相互に信頼しない複数顧客を同じサービスへ収容する境界にはならない。

SaaS対応を画面上のtenant選択や外部PDPのpolicy追加だけで行うと、IDOR、一覧・検索・キャッシュからの存在漏えい、workerやobject storageでのscope欠落、管理者権限の過大化が起きうる。tenantはroleの一種ではなく、データの所在と認可の評価範囲を決める構造境界として扱う必要がある。

本ADRは、既存のsingle-tenant利用を維持しながら、将来の共有SaaS profileを安全に実装するためのD5〜D10を固定する。ただし、AcceptedはSaaS実装完了を意味しない。Implementation gateをすべて満たすまで、現行`enterprise-production`をSaaS対応済みと解釈しない。

## Decision

### D5: TenantContextは信頼済み入力から解決する

requestごとに、backendが次の最小contextを確定する。

```text
TenantContext
  tenantId
  membershipId
  resolvedBy = verified_claim | trusted_host_mapping
```

- `tenantId`は不変かつopaqueなserver-generated IDとする。表示名を識別子や認可keyに使わない。
- active tenantは、署名・issuer・audienceを検証したclaim、または外部入力を除去できるtrusted proxy/host mappingから解決する。
- browserのheader、query、path、localStorage値をそのまま認可根拠にしない。複数membership利用者のtenant選択はcontext変更要求にすぎず、backendがmembershipを再確認して新しいcontextを発行する。
- proxy連携でtenant headerを使う場合、外部から届いた同名headerを境界で削除し、検証済み値だけを再付与する。
- tenant不明、候補が複数で一意に解決できない、membership停止中の場合はreadを含めてdenyする。

### D6: IdentityとTenantMembershipを分離する

論理モデルは次を基準にする。

```text
Tenant(id, displayName, lifecycleState, ...)
IdentityProvider(id, issuer, audience, lifecycleState, ...)
TenantIdentityProvider(tenantId, identityProviderId, lifecycleState, ...)
User(id, lifecycleState, ...)
UserIdentity(userId, identityProviderId, subject, ...)
TenantMembership(tenantId, userId, lifecycleState, ...)
```

- `User`はグローバルなopaque principalとし、tenant所属は`TenantMembership`で表す。1人が複数tenantへ所属できる。
- identityの一意性は曖昧な`provider`文字列ではなく、検証済みの`identityProviderId + subject`で固定する。`IdentityProvider`は少なくともissuerとaudienceを含むtrust configurationを識別する。
- tenantが利用できるIdPは`TenantIdentityProvider`で明示し、issuerが同じという理由だけで別tenantへのmembershipを与えない。
- roles/groupsはIdP/PDPからのtransient入力を維持し、kj-atlas内にrole editorを作らない。アプリ側はmembershipの有効性とtenant一致を構造境界として保持する。
- API keyだけをSaaS利用者の主体・tenant証明に使わない。service/agent credentialは後述のtenant-bound registrationへ限定する。

### D7: tenant従属データをDB制約と物理境界で分離する

- `Document`は`tenantId, id`を識別境界とし、`unique(tenantId, id)`または複合主キーを持つ。公開Document payloadへtenantIdを利用者編集可能な値として追加しない。
- Document従属表はtenantIdを重複保持し、`(tenantId, docId)`の複合外部キーで親へ接続する。docIdだけのjoin、更新、削除をrepository APIで提供しない。
- agent registration、job/queue、idempotency key、pagination cursor、rate-limit key、検索index、object-storage key、暗号鍵参照、audit event、backup manifestにもtenantIdを伝播する。
- 共有schema型SaaSでは、すべての行のtenantIdと複合制約に加え、PostgreSQL RLS等のDB側tenant guardを必須とする。アプリ判定とDB判定のどちらか一方だけへ依存しない。
- 専用schema／DB／bucket型では物理分離をtenant guardとして利用できるが、requestとresourceのtenant一致検証は維持する。
- SQLiteおよびDB側tenant guardを提供できない構成は、共有schema型SaaS profileでは使用しない。

### D8: tenant一致をローカル不変条件、capability評価を外部PDP責務にする

認可は次の順序で行う。

1. AuthContextとTenantContextを信頼済み境界で解決する。
2. active membershipを検証する。
3. resourceを`tenantId + resourceId`でserver-side lookupする。
4. 主体tenantと資源tenantの一致をアプリ内で検証し、不一致・不明ならPDPを呼ばずdenyする。
5. SafeMode、read-only等のローカル安全guardを適用する。
6. 外部PDPで`document.read`等のcapabilityを評価する。
7. APIで最終enforceし、tenantIdを含む最小監査イベントを残す。

資源側のtenant、visibility、policyRefはサーバー正本から取得し、公開clientが指定したheaderやpayloadを認可根拠にしない。

SaaS runtime profileは、実判定可能なaccess-control adapterと`deny` fail-safeを必須とする。adapter欠損、`noop`、PDP timeout、無効応答、tenant解決不能では起動またはrequestをfail-closedにする。`read_only` fallbackでreadを許可しない。現行のsingle-tenant profileでは互換性のため従来選択肢を維持できるが、SaaS profileと混同できない名称・検証にする。

他tenant資源のIDを指定した公開APIは原則not-found相当とし、存在を推測させない。現在tenant内で認証済みだがcapability不足の場合はpermission deniedとしてよい。内部監査には正確なdeny理由、policy version、correlation IDを残し、本文・文書タイトル・tokenは残さない。

### D9: Data Plane、Tenant Admin、Platform Control Planeを分離する

| 面 | 代表capability | 範囲 | 文書本文・タイトル |
| --- | --- | --- | --- |
| Workspace Data Plane | `document.read/write/export/share` | active tenantの許可済み資源 | capabilityに従う |
| Tenant Admin | `membership.provision`, `agent.register/revoke` | active tenantだけ | 表示しない |
| Platform Control Plane | `tenant.provision/suspend`, system status | tenant lifecycleと非秘密の運用メタデータ | 表示しない |
| Audit | `audit.read` | 明示許可されたtenantの固定メタデータ | 表示しない |

- Platform Control PlaneはData Planeとroute surface、認可audience、capabilityを分離する。Platform operatorであることから文書readを暗黙付与しない。
- Tenant Adminは自tenantのmembershipとagent registrationだけを扱い、platform capabilityへ昇格できない。
- frontendはrole/group名を解釈せず、backendが返すtenant-scoped `effectiveCapabilities`と理由codeを表示に利用する。APIは同じ操作を必ず再認可する。
- capability cacheを持つ場合は`deployment + tenantId + principalId + policyVersion`でkeyを分け、token有効期限を越えて保持しない。membership停止・policy変更時に失効できる設計にする。
- 全tenantの文書一覧、tenant横断本文検索、隠れたsupport impersonation、恒久的なsuper-readerを標準機能にしない。break-glassを導入する場合は時間制限、目的、承認、通知、監査を別ADRで扱う。

### D10: single-tenant互換とSaaS移行を分ける

- 既存データは内部の`local-default` tenantへbackfillする。single-tenant adapterがTenantContextを内部注入し、公開Document契約と通常のローカル操作を維持する。
- `enterprise-production`は当面、単一組織デプロイ向けのままとする。共有SaaSは別runtime profileとし、tenant解決、外部PDP、deny fail-safe、DB tenant guardが欠ける構成を起動時に拒否する。
- exportへ内部tenantId、membership、capabilityを既定で含めない。importは移送されたtenant権限を採用せず、import先のactive tenantで新規入力として認可・検証・人手レビューする。
- browser保存は`deployment origin + tenantId + principalId`で名前空間分離する。tenant切替・logout時に文書、選択、検索、work mode、import preview、recent、QueryPreset、request cache、object URLを破棄する。
- active tenantは認証セッション単位で1つとし、複数タブ、同時切替、bfcache、遅延responseのstale contextは`ADR-0061`のserver-issued `tenantSessionVersion`でresource lookup前に拒否する。client間通知だけを安全境界にしない。
- agent credentialはtenantIdと許可対象docIdへ束縛し、他tenant、他文書、別用途へ再利用できない。token平文は作成時に一度だけ表示し、保存しない。

## Implementation gate

本ADRがAcceptedになった後も、次を順番に満たすまで共有SaaSを有効化しない。

1. `schemas.md`、`api.md`、`runtime_parameter_registry.md`へTenantContext、capability、SaaS profile、失敗応答を契約先行で反映する。
2. tenant/identity/membershipのmigrationと、全tenant従属表の複合制約を導入する。
3. repository、API、MCP、worker、object storage、auditへtenant必須contextを伝播する。
4. 共有schema profileではDB側tenant guardを有効化し、接続poolでcontextが漏れないことを検証する。
5. 同じdocIdを持つtenant A/Bを使い、GET/PUT/list/search/count/export/share/import/MCP/webhook/job/audit/cache/agent credentialの越境negative matrixをintegration/E2Eで固定する。
6. server-side `effectiveCapabilities`が利用可能になった後に、tenant switcher、Tenant Admin、Platform Control PlaneをUIへ導入する。

## Alternatives considered

1. **tenant分離を外部PDPだけへ委譲する**: DB query、cache、job、backupのscope欠落を防げないため不採用。
2. **tenantIdをDocument payloadへ追加する**: 利用者編集可能なimport/export値が認可境界になるため不採用。
3. **全資源IDをグローバル一意にしてtenant列を持たない**: 一覧・join・監査・storageの越境を構造的に防げず、ID秘匿も認可にならないため不採用。
4. **shared schemaでアプリfilterだけを使う**: filter漏れが直接越境になるため、SaaS profileではDB側guardとの二重化を必須とする。
5. **Platform operatorを全tenantのsuper-userにする**: 運用権限と顧客データ閲覧を不要に結合するため不採用。
6. **tenantごとにUserを複製する**: 複数tenant所属とidentity lifecycleが不自然になるため、global Userとmembershipの分離を採用する。

## Consequences

- tenantはUI filterではなく、DB、API、認可、cache、非同期処理、監査を横断する必須contextになる。
- 同じdocIdを複数tenantで安全に利用できる一方、docIdだけを受け取る既存DBアクセスは全面的な棚卸しが必要になる。
- shared schema SaaSではPostgreSQL RLS等が必要となり、SQLiteはローカルsingle-tenant用途に限定される。
- IdP接続、User identity、TenantMembershipを分離するmigrationと管理APIが必要になる。
- 可用性より機密性を優先し、SaaSでPDP障害時にreadを継続できない。運用上はPDP冗長化と障害表示が必要になる。
- Platform運用者が顧客文書を暗黙に読めないため、support手順はdiagnostics bundle等の本文非表示経路を基本とする。
- UIはbackend capability契約より先に有効化できない。Claude Design Round 8のSaaS画面は先行レッドラインとしてのみ扱う。

## Non-goals

- 本ADRだけでSaaS提供や実装完了を宣言しない。
- 課金、契約プラン、地域配置、tenant削除、保持期限、SCIMを定義しない。
- roles/groupsをkj-atlasの編集可能マスタにしない。
- support impersonationまたはbreak-glassを導入しない。
- Documentスナップショットの公開payloadをtenant単位テーブルへ正規化しない。

## Traceability

- Research: `01_Plans/research-2026-07-16-saas-tenant-authorization-boundary.md`
- Related: `02_Architecture/design/enterprise_architecture.html`
- Related: `02_Architecture/design/data_model_operations_overview.html`
- Related: `02_Architecture/runtime_parameter_registry.md`
- Related: `THREAT_MODEL.md`
- Related UI: `02_Architecture/design/master-data-settings-ui-ux-concept.md`
- Related design request: `02_Architecture/design/design-request-2026-07-round8.md`
- Implementation: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Related governance: `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Follow-up boundary: `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`
