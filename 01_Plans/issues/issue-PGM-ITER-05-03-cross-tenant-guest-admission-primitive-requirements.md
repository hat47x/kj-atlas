# Issue: PGM-ITER-05-03 組織IdP外ゲスト受入プリミティブの要求確定

- Type: Design / Security
- Status: Open
- Source Issue: `02_Architecture/post-mvp-business-scope-design-program.html` §18（Maintainer直接指示、2026-08-25）, `01_Plans/issues/done/issue-PGM-ITER-05-02-cross-tenant-sharing-external-comparison.md`（外部比較調査）
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/adr/`, `03_Implement/backend/src/kj_atlas_api/guest_admission_models.py`, `03_Implement/backend/src/kj_atlas_api/guest_admission_repository.py`, `03_Implement/backend/src/kj_atlas_api/guest_auth_session_models.py`, `03_Implement/backend/src/kj_atlas_api/guest_auth_state.py`, `03_Implement/backend/src/kj_atlas_api/guest_request_auth.py`, `03_Implement/backend/src/kj_atlas_api/tenant_db_guard.py`, `03_Implement/backend/src/kj_atlas_api/trusted_auth_edge.py`, `03_Implement/backend/src/kj_atlas_api/routes/docs.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`, `01_Plans/adr/ADR-0080-idp-independent-guest-admission-primitive.md`, `02_Architecture/cross-tenant-sharing-external-comparison-2026-08-25.html`
- Expected verification level: `integration`

## 課題

`issue-PGM-ITER-05-02`（組織境界を越えた共有パターンの外部比較調査）完了の直後、Maintainerから実運用フィードバックを待たずに直接、次の4要求が確定要求として示された（`post-mvp-business-scope-design-program.html` §18）。

1. 組織間だけでなく、小規模の**個人間**利用もサポートする。
2. 行政・企業等が、市民や外部協力者のような**受入先テナント自身の企業IdPに属さないユーザー**を受け入れられる。— **2026-08-26補正**: 「受入先テナント自身のIdPは不要」という意味であり、「ゲスト自身がいかなるIdPも持たない」ことまでは求めない。ゲスト自身の所属組織のIdP、または汎用個人アカウント（Google/Microsoft/GitHub等）を持つことは前提としてよい。
3. 組織IdP外ユーザーの受付可否を、**テナント全体より詳細な単位**で制御できる。
4. **既定は拒否**。既定の共有対象ドキュメントは**0件**。

現行の`resolve_verified_claim_tenant_context()`（`tenant_context.py`）は`tenant_identity_providers`が(tenant, IdP)単位でactiveであることだけを要求する、単一の粗い信頼プリミティブしか持たない。要求2は既存の三要素分析（§15.1・§15.2）の射程を超える——これまでの分析は「別テナントのIdP全体を信頼する」プリミティブ（`tenant_identity_providers`の粒度を細かくする方向）を前提にしていたが、要求2（補正後）が求めるのは**受入先テナント自身のIdPとは独立に、ゲスト個人単位で信頼を表現できるプリミティブ**である。

## 対応方針

- 実施すること:
  1. 上記4要求を確定した受入条件として本issueに固定する（既に確定済みであり、再検討の対象ではない）。
  2. `AGENTS.md` §1.1（三要素牽制設計法、`ADR-0067`）に従い、業務設計・データ設計・機能設計の三次元から、受入先テナント自身のIdPとは独立した個人単位の招待・許可プリミティブを分析する。着工前チェックリスト（`02_Architecture/three-element-constraint-checklist.html`）を通す。
  3. 三要素分析の結果を新規ADRとして起票し、Maintainerの承認（Accepted）を経てから実装に着手する。
- 実施しないこと:
  1. 三要素分析・ADR化を経ないプリミティブの実装。
  2. 4要求自体の再検討・縮小（Maintainerが確定要求として直接指示したものであり、本issueの論点は「どう実現するか」であって「実現するかどうか」ではない）。

## 論点（三要素分析で扱うべき問い）

- **個人単位の信頼レコードの形**: `tenant_identity_providers`のような(tenant, IdP)単位ではなく、個人identity本体と対象ドキュメントへのgrantを分離する必要がある。`ADR-0080`は`guest_principals`＋`guest_document_grants`を採択した。
- **ゲスト本人確認方法**: 受入先テナント自身の企業IdPは要求しない一方、ゲスト自身は所属組織IdPまたは汎用個人アカウントを利用する。`ADR-0080`はA1/A2の多方式対応を採択し、認証結果をserver-owned sessionへ交換する境界を要求する。
- **既定拒否・既定ゼロ件の実装位置**: guest principalの存在だけでは文書アクセスを一切導出せず、`guest_document_grants`のexact matchがある場合のみ許可する。tenant-wide fallbackは設けない。
- **取り消し・失効**: リソース側テナントがguest principalまたは個別grantを相手側状態と無関係に単独でrevokeでき、次の認可判定から反映されることを要求する。

## 実装進捗

### R1: 永続化・認可プリミティブ（2026-09-06）

`lane-c/guest-admission-primitive-r1-20260906`で、`ADR-0080` D2/D3/D4の下層primitiveを実装した（PR #3018 / merge `cab0c3451bb6950e457c86faac17b384101a1a5c`）。

- `guest_principals`と`guest_document_grants`を独立tableとして追加し、guestを`TenantMembershipRow`へ混在させない。
- `(tenant_id, invited_email)`のdedup、安定した`guest_principal_id`、verified issuer/subjectの一意性、principal/grantのtenant複合FK、documentのtenant複合FKをDDL/ORM双方で固定した。
- principal作成、redeem、exact document grant、grant revoke、principal revoke、`guest_can_read_document()`をrepository primitiveとして追加した。
- pending principalはgrantがあってもdeny、active後もexact grant以外はdeny、grant/principal revoke後は次のauthorization predicateからdenyする。
- guest repositoryは通常member用`TenantContext`を捏造せず、内部tenant-id DB guardを使う。PostgreSQLでは両guest tableを`ENABLE/FORCE ROW LEVEL SECURITY`とし、tenant context未設定・別tenant accessをfail closedにした。
- guest modelは中央`PERSISTENT_TEXT_SPECS`とAlembic `target_metadata`へ正式登録し、専用moduleだけautogenerate/portable persistence governanceから抜ける状態を防止した。
- verification run `34036961877`と最終governance run `34037370856`で、Ruff、focused pytest、PostgreSQL 16 restricted runtime roleによるRLS、migration lineage、persistence shape、diff hygieneを確認した。

R1は**外部IdP/OAuthからguest identityを検証してserver-owned sessionへ交換し、HTTP requestのdocument read/writeへ接続するtrusted-auth-edge経路までは実装しない**。そのためAC-3/AC-4はこの時点では完了扱いにしない。

### R2a: server-owned guest session → exact document read（2026-09-06）

`lane-c/guest-admission-auth-edge-r2-20260906`で、R1のexact-grant predicateを実HTTP requestへ接続する第二段を実装した。

- member用`saas_auth_sessions`とは別に`guest_auth_sessions`を追加し、`Kj-Atlas-Guest-Session`のopaque valueは既存と同じkeyed-hash方式でサーバー側hashだけを正本にする。
- guest session rowはcookie hashから**tenant確定前**に引く認証状態であるため、それ自体をtenant RLS tableにはしない。rowからtenantを得た直後にtransaction-local tenant scopeを設定し、`guest_principals`・`guest_document_grants`・`documents`のFORCE RLS境界へ戻る。これはguestをmembershipへ昇格させる例外ではなく、pre-tenant authentication stateとtenant-scoped authorization stateを分離するための境界である。
- session作成時と各session解決時の双方で、active principalかつverified `(issuer, subject)`が完全一致することを再検査する。principal revoke後は、cookie自体が期限内でも次requestで401となる。
- guest cookieが存在するrequestはmember resolverへfall-throughしない。unknown / malformed / expired / revoked guest sessionは401、session persistence未構成は503でfail closedする。
- document routeではguest principalの存在だけを許可根拠にせず、**active exact non-revoked grant**があるreadだけを許可する。同tenant未付与文書と別tenant文書はいずれも404としてresource enumerationを避ける。
- R2aはguest write/export/shareを一般化しない。`action != read`は明示403とし、既存SafeModeより狭いread-only境界を維持する。member用PDP/capabilityへguestを偽装して通すこともしない。
- 実HTTP integration testで、exact grantのみ200、membership行0件、same-tenant ungranted/cross-tenantは404、grant revokeは同一live cookieの次GETで404、principal revokeは同一cookieの次GETで401、PUTは403を固定した。
- PostgreSQL 16 restricted runtime roleで、`guest_auth_sessions`がpre-tenant stateとして非RLS、`guest_principals`が引き続きFORCE RLSであること、session解決後だけtenant-scoped principalへ到達できることを固定した。
- 最終verification run `34039105022`でRuff、59 focused tests、PostgreSQL 16、migration lineage、persistence shapes、`docs_check`、`git diff --check`がすべて成功し、一時helper/workflowは成功後に自己退役した。

R2aは**sessionの消費側**を実HTTPまで固定した段階であり、外部IdP/OAuth callbackからそのsessionを安全に発行する入口はまだ実装していない。内部`issue_guest_auth_session()`も、active principalとverified issuer/subjectの完全一致を要求するだけで、client supplied tenant/principalを信頼する公開login endpointではない。

### R2b: host-bound redeem state → verified guest identity → guest session（2026-09-07）

`lane-c/guest-admission-redeem-r2b-20260906`で、R2aが残した「外部本人確認結果を、client自己申告のtenant/principalを信じずに招待へbindし、guest sessionへ交換する」入口を実装した。

- `guest_redeem_states`をpre-tenant authentication stateとして追加した。raw stateは返却時にだけ存在し、DB正本はdomain-separated keyed hashのみとする。stateは15分または招待期限の短い方で失効し、一度consumeしたstateは再利用できない。
- 公開`POST /session/guest/redeem`のrequest schemaは`state`と`identityCredential`だけを受け付け、`tenantId` / `guestPrincipalId` / `issuer` / `subject`等のclient自己申告を`extra=forbid`で拒否する。tenant・guest principal・verification methodはhost-created stateからのみ復元する。
- 本人確認結果はguest専用`VerifiedGuestIdentity(issuer, subject)`へ閉じ、member用`VerifiedTenantClaim`、`TenantMembershipRow`、`TenantIdentityProviderRow`へのfallbackを設けない。production verifierはdeployment adapterから明示注入する契約とし、未構成時は503でfail closedする。
- state rowを`FOR UPDATE`で一回性確認した後、pending principalのverified identity bind、`guest_auth_sessions` row発行、state consumeを**同一DB transaction**でcommitする。session persistence失敗を強制したintegration testではprincipal activation・state consume・session rowのすべてがrollbackされる。
- redeem成功後はR2aの`Kj-Atlas-Guest-Session`をそのまま利用し、既存exact document grantだけがreadを許可する。guest principalの存在だけでtenant内文書へ広がる経路は追加していない。
- SQLite HTTP integrationではstate非平文保存、redeem→cookie→exact grant GET、replay拒否、期限切れ拒否、identity verifier失敗、client tenant/principal/claim注入拒否、atomic rollback、membership/tenant-IdP行0件を固定した。
- PostgreSQL 16 restricted runtime roleでは、`guest_redeem_states`が意図したpre-tenant非RLS、`guest_principals`がFORCE RLSのままであることを確認し、state解決後だけtenant scopeへ戻ってprincipalをactivateし、state consumeとsession rowを同時commitできることを固定した。
- 最終verification run `34046511190`でRuff、focused HTTP/repository tests、PostgreSQL 16、migration lineage、persistence shapes、`docs_check`、`git diff --check`を確認する。

### R2cに残す境界

- `ADR-0080` D1=A1/A2の**実provider adapter**（home organization IdP / general personal account）をproduction deploymentへ接続し、署名/JWKS/issuer/audience等の検証を実際のprovider contractで固定すること。R2bはguest専用trusted verifier interfaceとfail-closed wiringを実装したが、member用OAuth adapterをguestへ流用してはいない。
- provider redirect/callback方式を採る場合は、R2bのone-time stateをcallback correlationへ接続し、provider固有nonce/PKCE等を必要に応じて追加すること。`identityCredential`を受ける現在のHTTP境界はtrusted verifier adapterへの最小交換面であり、特定providerのOAuth UI完了を意味しない。
- guest session logout / explicit revokeの公開境界が必要なら、そのCSRF・cookie属性・監査契約をmember cookieとは別に固定すること。
- R2aでread-onlyに閉じたguest writeを将来開く場合は、document grantのread/write意味、CSRF、PDPとの責務分離を別途設計してから扱うこと。

## 受入条件

- [x] AC-1: 上記4要求への対応方針が三要素分析（`ADR-0067`）で決定され、着工前チェックリストを通過する。— 2026-08-25、`ADR-0080`とこのADRを反映した`post-mvp-business-scope-design-program.html` §19、`three-element-constraint-checklist.html`の適用記録を参照。D1（ゲスト本人確認）・D2（信頼レコードの形）・D3（既定拒否・既定ゼロ件の保証層）・D4（取り消しの独立性）の4論点を、基本チェック・クロスチェックを通した三要素分析として決定した。2026-08-26、保守者の指示によりD1（単一方式→多方式対応）・要求2の文言・D2（関数従属性再検査による`guest_principals`への精緻化）を補正した。
- [x] AC-2: 決定内容が新規ADRとして起票され、Maintainerの承認（Accepted）を得る。— 2026-08-26、`ADR-0080`がAcceptedとなった（D1=多方式対応、D2=A、D3=A、D4=A）。
- [ ] AC-3: ADR承認後、個人単位・IdP不問の招待・許可プリミティブが実装され、既定拒否・既定ゼロ件がintegration testで固定される。— R1でstorage/repository/RLS、R2aでserver-owned guest session→実HTTP exact document read、R2bでhost-bound one-time redeem state→guest専用verified identity→session発行まで固定した。ただしproductionでhome-org IdP / general personal accountを実検証するprovider adapterはまだ未接続であり、「IdP不問の受入journey」全体の完了とはまだ扱わない。
- [ ] AC-4: 招待の取り消し・失効が、相手側（招待された個人の状態）と無関係にテナント側から単独で実行できることがtestで固定される。— R1のrepository predicate、R2aのlive-cookie HTTP revoke挙動に加え、R2bでhost-bound redeem→session入口まで到達した。revokeの技術挙動自体は固定済みだが、AC-3と同じproduction provider journeyを通したend-to-end受入・取消証跡がまだないため、親issue closeoutまでは未完了として維持する。

## 検証

- `python 01_Plans/docs_check.py`
- `cd 03_Implement/backend && python -m ruff check ...`
- `cd 03_Implement/backend && python -m pytest -q tests/test_guest_auth_session_store.py tests/test_guest_auth_session_postgres.py tests/test_guest_docs_http_authorization.py tests/test_guest_admission_repository.py tests/test_guest_admission_postgres_rls.py tests/test_tenant_db_guard.py tests/test_alembic_lineage.py tests/test_persistence_shapes.py tests/test_database_support.py`
- PostgreSQL 16 restricted runtime roleでguest principal/grantのFORCE RLSと、pre-tenant `guest_auth_sessions`→tenant scope設定→FORCE-RLS principal lookupの遷移を確認
- R1 verification: GitHub Actions run `34036961877`, governance re-verification run `34037370856`, final docs run `34038175292`
- R2a verification: GitHub Actions run `34039105022`（59 focused tests + docs/diff hygiene）
- R2b verification: GitHub Actions run `34046511190`（HTTP/repository + PostgreSQL 16 restricted runtime role + docs/diff hygiene）
