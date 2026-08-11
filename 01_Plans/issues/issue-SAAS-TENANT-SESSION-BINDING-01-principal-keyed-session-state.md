# Issue: SAAS-TENANT-SESSION-BINDING-01 active tenant stateが認証セッションではなくprincipalへ束縛されている

- Type: Security / Data Design
- Status: Open
- Source Issue: `SAAS-TENANT-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/active_tenant_session.py`, `03_Implement/backend/src/kj_atlas_api/saas_auth_state.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/saas_request_context.py`, `03_Implement/backend/src/kj_atlas_api/routes/session.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`, `02_Architecture/api.md` §10
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

推奨候補は案B、次点は案Aである。どちらも認証フローとデータモデルへ影響するため、Maintainerが選択し、必要なら`ADR-0061`の補足ADRをAcceptedにしてから実装する。

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

## 検証計画

- DB storeを共有する2 app/worker instanceで、同一sessionのCAS競合と切替後contextを確認する。
- 同一principal・異なるsession IDの2 clientで、tenant切替とlogoutの非干渉を確認する。
- tenant A/Bに同じdocIdを作り、旧version requestがresource lookup・監査mutation前に停止することを確認する。
