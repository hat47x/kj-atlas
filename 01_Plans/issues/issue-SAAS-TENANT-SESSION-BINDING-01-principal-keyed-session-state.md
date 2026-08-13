# Issue: SAAS-TENANT-SESSION-BINDING-01 active tenant stateが認証セッションではなくprincipalへ束縛されている

- Type: Security / Data Design
- Status: Open
- Source Issue: `SAAS-TENANT-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/active_tenant_session.py`, `03_Implement/backend/src/kj_atlas_api/saas_auth_state.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/saas_request_context.py`, `03_Implement/backend/src/kj_atlas_api/routes/session.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`, `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（Proposed）, `02_Architecture/api.md` §10
- Expected verification level: `integration`

## 課題

`ADR-0061`はactive tenantと`tenantSessionVersion`を**認証セッション単位**で原子的に解決・更新するよう要求する。しかし、現在の共有DB実装は`saas_tenant_sessions.principal_id`を主キーとし、`session_version`だけを保存する。

このため、次の3つの契約違反が同時に存在する。

1. `DatabaseActiveTenantSessionPersister.persist()`は`selected_tenant`を受け取るが保存しない。`POST /session/active-tenant`直後のresponseは選択先tenantを返しても、次のrequestはBearer tokenのtenant claimから再解決されるため、auth edge側でtoken/sessionを更新しない限り元tenantへ戻り得る。
2. versionが`principal_id`単位なので、同じ利用者の独立した認証セッションまで同じactive tenant世代を共有する。一方のブラウザでの切替・logoutが別ブラウザのsessionを無効化し、ADRが意図する「同じ認証セッションの複数タブ」より広い範囲へ影響する。
3. DB persisterの`current_version()`はrequest cookieを読まず、`persist()`も既存cookieとの束縛やanti-forgery tokenを検証しない。cookieは切替成功時にversionを設定しlogout時に削除するだけで、認証session識別子にもrequest正当性の証拠にもなっていない。

現行testは`selected_tenant`がpersisterへ渡されたこととversionがrotateしたことだけを個別に確認しており、切替後の次requestが選択先tenantを返すこと、独立sessionが分離されることを確認していない。このため契約違反を検出できなかった。

## 設計判断が必要な点

実装前に、trusted auth edgeから得る安定した認証セッション識別子を固定する必要がある。これはclient自由入力、tenant claim、access tokenの`jti`を流用してはならない。

- 案A: Brokerが発行する検証済みsession ID claimを必須化し、`(issuer, subject, session_id)`を内部session keyへ正規化する。
- 案B: BFF/server-side login sessionを正本とし、そのopaque server session IDへactive tenantを束縛する。
- 案C: active tenant switchを廃止し、tenantごとにtokenを再発行する。これは現行UI/API契約の変更が大きい。

比較と三要素牽制を`ADR-0074`へ分離し、案B（server-owned BFF session）を採用候補として記述した。同ADRはProposedであり、現行のSPA Bearer方式をまだ変更しない。MaintainerがBFF責務、cookie/CSRF、timeout、token保管、logout連携を確認してAcceptedにした後だけ実装する。

## 受入条件

- [ ] AC-1: trusted auth edgeが、principalとは別のserver-trusted認証セッション識別子を解決する。
- [ ] AC-2: 共有ストアが認証セッション識別子、active tenant、`tenantSessionVersion`を同一行または同一原子境界で保持する。
- [ ] AC-3: tenant切替後の次の`GET /session/context`とtenant-scoped APIが、再発行されていない旧tenant claimではなく保存済みactive tenantを正本として選択先tenantを解決する。
- [ ] AC-4: 同じ認証セッションの複数タブはversionを共有し、一方の切替で他方のstale requestがresource lookup前に409となる。
- [ ] AC-5: 同じprincipalの異なる2認証セッションはactive tenantとversionを共有せず、一方の切替・logoutが他方を失効させない。
- [ ] AC-6: session ID欠損・不正・過大、共有ストア不達、保存tenantのmembership停止はfail-closedとなり、principal単位やtoken claimへfallbackしない。
- [ ] AC-7: migrationのupgrade/downgrade、複数worker CAS、tenant切替→次request、別session分離のintegration testが通る。
- [ ] AC-8: `SAAS-TENANT-01` AC-6/13、`OPS-SAAS-SCALE-01` AC-1、API/運用文書の達成表現を実際の保証へ同期する。
- [ ] AC-9: cookieを採用する場合はserver-side session ownershipとanti-forgery契約を固定し、未提示・別session・改ざん・cross-site要求を拒否する。採用しない場合は現在のversion cookieとanti-forgery達成表現を削除する。

## 非目標

- per-tab tenant sessionは導入しない。
- access token `jti`を一回使用nonceまたは認証セッションIDとして扱わない。
- clientが送るcookie/header値だけからprincipal、tenant、session ownershipを確定しない。

## 依存関係

- `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md` — **2026-08-13 Maintainer承認によりAccepted**。「Acceptance Gate 回答」節（BFF内蔵、cookie/CSRF/timeout、Broker logout連携、E2E/CORS移行範囲）が実装方針の正本となる。着手可能。

### テストハーネスの前提整備（2026-08-13、着手前に必要）

`tests/level2/mock_idp.py`をADR-0074の回答案③（Brokerごとのlogout連携）の検証に使うには、現状3点が不足している。実装着手前にこの節を満たすこと。

- **Back-Channel Logout未実装**: `/backchannel-logout`相当のendpointと、IdP側からLogout Tokenを能動的に送出する経路が無い。
- **`sid` claim未発行**: `_issue_jwt`（`mock_idp.py:71-108`）がclaimに`sid`を含まない。Logout Tokenと既存sessionの紐付けができない。
- **confidential client検証が無い**: `/oauth/token`（`mock_idp.py:368`）は`client_id`のみを見ており、`client_secret`を検証しない。現状はpublic client + PKCE（既存SPA直接方式）を模した設計であり、BFFが持つべきconfidential client契約のテストには使えない。

## 検証計画

- DB storeを共有する2 app/worker instanceで、同一sessionのCAS競合と切替後contextを確認する。
- 同一principal・異なるsession IDの2 clientで、tenant切替とlogoutの非干渉を確認する。
- tenant A/Bに同じdocIdを作り、旧version requestがresource lookup・監査mutation前に停止することを確認する。
