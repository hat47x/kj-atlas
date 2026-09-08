# ADR-0061: SaaS active tenantを認証セッション単位で直列化する

- Status: Accepted
- Date: 2026-07-19
- Deciders: Project Maintainer
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/frontend/`, trusted auth/session adapter

## Context

`ADR-0059`はactive tenantをbackendが再確認して認証セッションへ保存し、frontendがtenant切替後に旧DOM、memory、browser storage、worker、object URLを破棄する境界を固定した。現行の準備実装も、このsession persisterとhard replacementを前提にしている。

ただし、同じ認証セッションを複数タブで使う場合の並行性が未定義だった。タブAがtenant Aの文書を表示中に、タブBがactive tenantをtenant Bへ変更すると、タブAの表示、保持中の`docId`、未送信payloadはtenant Aのままでも、次のrequestを解決するserver sessionはtenant Bになりうる。両tenantに同じ`docId`が存在し、利用者が両方へ書込capabilityを持つ場合、tenant越境の権限違反ではなくても、旧tenantの内容を新tenantへ誤って送るscope confusionが成立する。

BroadcastChannel、storage event、focus時再読込は利用者体験を改善するが、通知欠落、background tab、bfcache、suspended process、network response競合を認可境界として防げない。逆に、active tenantをタブ単位へ変更するには、trusted session形式、request binding、CSRF、logout、capability cacheを含む別のcontext契約が必要になる。

## Decision

### D1: 1つの認証セッションにactive tenantは1つだけとする

- active tenant変更は同じ認証セッションを使う全タブへ影響する。異なるtenantを同時に操作したい場合は、別の認証セッションまたは将来の明示的なper-tab契約を使う。
- tenant switcherの確認には「このブラウザの他のタブも切り替わります」を文字で表示する。複数タブの存在を検出できる場合だけ出す条件付き注意にはしない。
- frontendは別タブで旧tenant本文を操作し続けられるように見せない。context変更を検知した時点で本文、Admin metadata、dialog、未送信previewを非表示にして再確認状態へ移す。

### D2: server-issued `tenantSessionVersion`をcontext整合のpreconditionにする

- trusted auth/session adapterは、認証セッションのactive tenant stateごとに予測不能でopaqueな`tenantSessionVersion`を発行する。値は1〜128文字のcanonical IDとし、active tenant変更時に必ず変更する。
- `GET /session/context`は`tenantSessionVersion`を返す。`POST /session/active-tenant`は現在値を`expectedTenantSessionVersion`として必須入力し、一致した場合だけ切替を保存して新versionを返す。同時切替や古いdialogからの確定は`tenant_session_changed`で拒否する。
- SaaS profileのtenant-scoped APIはread/write/list/export/share/import/MCP/webhook/job登録を含め、clientが最後に検証したversionをrequest preconditionとして要求する。backendはtrusted sessionからactive tenantと現versionを解決した後、resource lookupより前に一致を検証する。
- clientが送るversionはtenantやcapabilityを決める認可根拠ではない。欠損・不一致なら処理を停止するためのexpected-context guardであり、実tenant、membership、capabilityは従来どおりserver正本から解決する。
- versionをDocument、export、import payload、browser永続設定、URL、監査本文へ保存しない。監査には必要な場合も`tenant_session_changed`という結果だけを残し、生versionを記録しない。

### D3: stale contextはread-onlyや自動再送へ倒さない

- version欠損・不一致では本文を返さず、変更も適用せず、`409 tenant_session_changed`または同等のstable errorへfail-closedにする。他tenant資源の存在や現在tenant IDは応答へ反射しない。
- frontendはstale requestを新contextで自動再送しない。特にPUT、import、share、export、Admin更新は利用者が新しいscopeを確認した後にだけ再実行できる。
- 旧contextで開始したresponse、worker結果、object URL、optimistic updateは、versionが変わった後にDOM、cache、downloadへcommitしない。
- capability versionはpolicy snapshotのversionであり、active tenant sessionの並行制御には流用しない。

### D4: cross-tab通知とlifecycle再確認をUX層の補助境界にする

- tenant切替成功後、frontendはsame-originのBroadcastChannelまたは同等の一時通知で「session context changed」だけを伝える。tenant ID、principal ID、title、本文、capability、version生値を通知payloadへ含めない。
- 通知を受けたタブは旧本文を即時blocked stateへ置換し、進行中request/workerをabortして`GET /session/context`から再開する。通知の送受信自体は認可判定に使わない。
- `pageshow`の`persisted=true`、長時間非表示からの復帰、online復帰、認証更新後は、旧本文を操作可能にする前にsession contextを再確認する。SaaS app shellとsession responseは`no-store`を維持し、bfcacheから戻ったDOMを信頼済みcontextとして扱わない。
- 通知APIが利用不能でもserver-side version preconditionにより安全側へ停止できることを必須とする。

### D5: capability失効とtenant lifecycle変更も同じblocked UXへ収束させる

- membership停止、tenant停止、capability resolver不達、PDP不達、session version不一致はEmptyへ偽装しない。既存データを背景に残さないblocked stateとし、再試行、再認証、Workspaceへ戻るのうち安全に実行できる導線だけを示す。
- raw error、tenant ID、principal ID、policyRef、role/group、tokenをエラー表示へ反射しない。
- 再確認後に同じtenantへ戻った場合でも、旧未送信mutationを自動復元・送信しない。device-local入力の復元可否はデータ種別ごとに明示し、tenant-bound previewは破棄する。

## Implementation gate

共有SaaS profileを有効化する前に、`ADR-0059`のgateに加えて次を満たす。

1. trusted auth/session adapterがactive tenantと`tenantSessionVersion`を原子的に解決・更新できる。
2. session contextとactive tenant APIがversionのclosed-world validation、conditional update、no-storeを実装する。
3. すべてのtenant-scoped public APIと非同期開始点がversion preconditionをresource lookup前に検証する。未対応routeがある間はSaaS profileを起動拒否する。
4. tenant A/Bに同じ`docId`を用意し、2タブ同時操作、同時tenant切替、stale GET/PUT/export/import/Admin更新、遅延response、worker完了、bfcache復帰のnegative matrixを固定する。
5. cross-tab通知が欠落・無効でもserver guardが拒否し、通知成功時は旧DOMとfocusがblocked stateへ移ることを1440/390px、ja/enで検証する。

## Alternatives considered

1. **active tenantをタブ単位にする**: 複数tenantを並行利用しやすいが、tab-bound token、request binding、CSRF、logout、refresh、link-openの新契約が必要で、現行session persisterと整合しない。将来の別ADRなしには採用しない。
2. **BroadcastChannelだけで同期する**: 通知欠落や停止中タブを防げず、client通知を安全境界にしてしまうため不採用。
3. **`capabilityVersion`を並行制御に流用する**: tenant切替で必ず変わらず、policy lifecycleとsession lifecycleを混同するため不採用。
4. **tenantごとにhostを分け、switcherを廃止する**: 強い分離になりうるが、複数membership利用と現行Round 8構想を変更する。trusted host mappingを採用するdeploymentの選択肢としては残すが、共通契約にはしない。
5. **stale requestを新tenantへ自動再送する**: 旧scopeのpayloadを新scopeへ適用しうるため不採用。

## Consequences

- 別タブでtenantを切り替えると、他タブも再確認が必要になり、異なるtenantを同一sessionで並行編集できない。
- active tenant switchと全tenant-scoped APIへversion guardを追加する実装コストが発生する。
- client通知やUI cleanupが失敗しても、serverがstale requestとresponseを閉じる二重境界になる。
- Claude Designのtenant切替レッドラインには、他タブへの影響、scope失効、bfcache/復帰、stale save拒否の状態が必要になる。

## Three-Element Verification（ADR-0067 遡及適用）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | 1つの認証セッションにactive tenantは1つだけ。切替は全タブへ波及し、異なるtenantの同時操作は別セッションまたは将来のper-tab契約で対応する | 切替確認UIは「このブラウザの他のタブも切り替わります」を常時表示。context変更検知時に本文・Admin metadata・dialog・未送信previewを非表示にして再確認状態へ移す |
| **データ設計** | trusted auth/session adapterがactive tenant stateごとにopaqueな`tenantSessionVersion`を発行し切替時に必ず変更。versionはDocument・export・browser永続設定・URL・監査本文へ保存しない | versionは認可根拠ではなくexpected-context guard。実tenant・membership・capabilityはserver正本から解決。監査には`tenant_session_changed`結果だけを残し生versionを記録しない |
| **機能設計** | `GET /session/context`はversionを返し、`POST /session/active-tenant`は`expectedTenantSessionVersion`を必須入力として一致時だけ切替保存。全tenant-scoped APIはresource lookup前にversion一致を検証し、欠損・不一致は`409`へfail-closed | stale requestを新contextで自動再送しない。PUT・import・share・export・Admin更新は利用者が新scopeを確認後にだけ再実行可。旧contextのresponse・worker結果・object URLはcommitしない |

## Non-goals

- per-tab tenant session、複数tenant同時編集、support impersonationを導入しない。
- `tenantSessionVersion`を認証token、tenant selector、権限移送値として使用しない。
- single-tenant profileのoffline/local-first動作へversion guardを強制しない。

## Traceability

- Parent boundary: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`
- Implementation: `01_Plans/issues/done/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- API target: `02_Architecture/api.md` §10
- UI input: `02_Architecture/design/master-data-settings-ui-ux-concept.md`, `02_Architecture/design/design-request-2026-07-round8.md`
- Threat model: `THREAT_MODEL.md`
