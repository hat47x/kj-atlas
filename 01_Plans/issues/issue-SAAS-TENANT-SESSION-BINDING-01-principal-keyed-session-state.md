# Issue: SAAS-TENANT-SESSION-BINDING-01 active tenant stateが認証セッションではなくprincipalへ束縛されている

- Type: Security / Data Design
- Status: Open
- Source Issue: `SAAS-TENANT-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/active_tenant_session.py`, `03_Implement/backend/src/kj_atlas_api/saas_auth_state.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/saas_request_context.py`, `03_Implement/backend/src/kj_atlas_api/routes/session.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`, `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（Accepted 2026-08-13）, `02_Architecture/api.md` §10
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

### Implementation checkpoint 2026-08-13: モックIdPの3点整備（着手前提の充足）

上記3点を`tests/level2/mock_idp.py`へ追加した。いずれもopt-in設計とし、既存の呼び出し元（`test_saas_oauth_login_e2e.py`等、`client_id="mock-client"`を無登録のまま使う）の挙動は変更していない。

- **`sid` claim**: `authorize_approve`が`mock_idp_session` cookie（`login_submit`が発行）を読み、無ければ新規発行して`_pending_codes[code]["sid"]`へ格納する。`token_exchange`はこれを claims へ含めて`_issue_jwt`へ渡す。同一ブラウザ session（cookie）から複数tokenを発行しても`sid`は一致し、別sessionでは一致しないことをtestで固定した。
- **confidential client検証**: `POST /admin/register-client-secret`で`client_id`ごとに`client_secret`を登録できるようにした。`/oauth/token`は登録済み`client_id`だけ`client_secret`必須（`secrets.compare_digest`で比較、不一致・欠損は`401 invalid_client`）とし、未登録`client_id`（既定の`mock-client`を含む）は従来どおりpublic client + PKCEのまま検証しない。
- **Back-Channel Logout**: OIDC Back-Channel Logout 1.0準拠のLogout Token（`events`claim必須、`nonce`禁止、`sub`/`sid`のいずれかを含む）を構築する`_issue_logout_token`を追加した。`POST /admin/register-backchannel-logout-uri`で`client_id`ごとの配送先を登録でき、`POST /admin/trigger-backchannel-logout`がLogout Tokenを構築し、配送先が登録済みならhttpxで実際にPOSTする（未登録なら`delivery.attempted=false`を返すのみ）。配送失敗（到達不能URI等）は例外を投げず`delivery.ok=false`＋`error`として返す設計とし、ADR-0074決定6が要求する「back-channel logoutが届かない場合は全session失効へフォールバックする」経路をテスト側で組み立てられるようにした。

**検証**: 新規`tests/test_mock_idp_backchannel_logout.py`12件（sid一貫性・sid分離・confidential client成功/失敗3種・Logout Tokenの`events`/`nonce`/署名検証・配送成功/失敗）を追加し全pass。既存の呼び出し元3ファイル（`test_saas_oauth_login_e2e.py`・`test_saml_broker_jwt_coordinated_flow.py`・`test_auth_federation_level2.py`、計20件）に回帰なし。配送成功のtestは`test_access_control_adapter_contracts.py`と同じ実ローカルHTTPサーバ（`http.server.HTTPServer`+`threading.Thread`）パターンを踏襲した。`ruff check`・`ruff format --check`両方pass。backend全体回帰は1,003 passed・34 skipped・8 deselected・failed 1（`test_alembic_has_single_head`、原因は本checkpointとは無関係な他セッションの未コミットmigrationによる一時的なhead不一致で、後続checkpointで解消）で確認した。

**まだ実装していないもの**: kj-atlas backend側の`/backchannel-logout`受信endpoint（このissue本体のAC-1〜9）、BFF、confidential clientとしての実token交換、cookieベースsession。今回はテスト基盤の整備のみである。

### Implementation checkpoint 2026-08-13: `saas_auth_sessions`のexpand migration（AC-2の器のみ）

ADR-0074決定3の列構成で、server-owned auth sessionテーブルを追加した。`SAAS-TENANT-01`が`documents`等で使った「まずexpand、cutoverは後」の手順を踏襲する: 既存`saas_tenant_sessions`（principal単位）はそのまま残し、`DatabaseActiveTenantSessionPersister`も引き続きそちらを使う。新テーブルは**何からも読み書きされない**——AC-1（trusted auth edgeのsession識別子解決）が先に要る。

- `SaasAuthSessionRow`（`models.py`）: PK`session_key_hash`（cookie生値ではなくkeyed hashを想定、hashingとkey rotationはcookie発行側の実装時に追加）、`principal_id`/`issuer`/`subject`/`active_tenant_id`（nullable、`tenants.id`へFK、`ON DELETE SET NULL`）/`tenant_session_version`/`created_at`/`last_used_at`/`absolute_expires_at`/`revoked_at`。`issuer`+`subject`を`principal_id`と別に持つのは、決定6のback-channel logoutフォールバック（`issuer + subject`索引での全session失効）がjoinなしで引けるようにするため。
- Alembic `20260813_0027`（`upgrade`/`downgrade`とも実装、他consumerが無いためdowngradeにデータ損失リスクなし）。
- **他セッションとの migration chain 調整**: 作業時点のalembic headは他セッションが未コミットで追加した`20260813_0026`（`inquiry_bundles.revision`列追加、本issueと無関係）だった。競合するbranchを作らないよう、本migrationはその上に`down_revision`を明示的に繋いだ。コミット順序が入れ替わっても、両方が揃った時点のheadは`20260813_0027`になるよう設計している。
- **`models.py`の編集分離**: 同ファイルに他セッションの未コミット変更（`InquiryBundleRow.revision`列）が既に存在したため、`git diff`のhunk境界を確認した上で`git apply --cached`で自分の hunk だけをindexへ適用し、他セッションの変更は working tree に未コミットのまま残した（`git add`による全体ステージは行っていない）。

**検証**: 新規`tests/test_saas_auth_sessions_migration.py`2件（テーブル構造・FK・NOT NULL制約・PK重複拒否・downgradeでの`saas_tenant_sessions`非破壊を確認）を追加し全pass。`test_alembic_lineage.py`（他セッションが並行して`20260813_0027`へ更新済みだったheadの期待値、既存の历史順序assertionを含む）とtenant foundation migration近接、計7件pass。`ruff check`・`ruff format --check`（新規ファイルのみ、pre-existingな`models.py`の無関係フォーマット差分は変更していない）pass。

**まだ実装していないもの**: AC-1（trusted auth edgeのsession識別子解決）〜AC-9の全て。今回は器（テーブル）を追加しただけであり、このテーブルへ実際に書き込む経路（BFF cookie発行、hashing、CAS更新）は未着手。

### 記録の是正 2026-08-20: AC-1はすでに大部分が実装済みだった

着手時に実装状態を確認したところ、**上記2件のcheckpointが「まだ実装していないもの: AC-1〜AC-9の全て」と
記録した後、別セッションがAC-1の大部分を実装・コミットしていた**（`f37ef851`、11ファイル）。本節はその
記録の齟齬を是正する。

**すでに実装・コミット済み（HEAD時点）**:

- `oauth_bff.py`: BFFのOAuth経路（`GET /session/login`のauthorization-code+PKCE開始、
  `GET /session/callback`のcode交換・token検証・`Kj-Atlas-Auth-Session` cookie発行）。
- `auth_session_hash.py`: `derive_session_key_hash()`（cookie生値ではなくkeyed HMAC-SHA256を保存）。
- `DatabaseSaasAuthSessionStore`（`saas_auth_state.py`）: `create_auth_session` /
  `resolve_auth_session`（revoked・絶対期限12h・idle 60minをfail-closedで判定し`last_used_at`をslide）/
  `revoke_auth_session` / `preflight`。
- `JwtSaasIdentityContextResolver._resolve_from_auth_session_cookie()`（`trusted_auth_edge.py`）:
  bearer token不在時にcookieから session を解決するfallback経路。
- settings・preflight・`main.py`の結線（`KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY`等）。

**AC-1の文言に対して残っている欠落**: AC-1は「principalとは別のserver-trusted認証セッション識別子を
**解決する**」ことを要求するが、現状は解決した`session_key_hash`を**store照会に使った直後に捨てている**。
`ResolvedIdentity`（`auth_context.py`）にも`TrustedSaasRequestSession`（`saas_request_context.py`）にも
session識別子のフィールドが無く、`resolve_active_tenant_session_version()`は依然`principal_id`だけで
呼ばれる。したがってAC-2以降（session単位でのactive tenant保存・version共有）へ接続する導線が無い。

**その他の未達**:

1. bearer token経路は session 識別子を一切解決しない。`sid` claimは`src/`のどこでも読まれていない
   （mock IdP側は発行済み）。`resolve()`はbearer headerがあればcookieを見ないため、
   bearer優先の現行SPAでは新経路が使われない。
2. `SaasAuthSessionRow.tenant_session_version`は書き込み専用で、`resolve_auth_session`は返さず、
   rotateする経路も無い。`revoke_auth_session`は呼び出し元がゼロ。
3. `POST /session/logout`は`Kj-Atlas-Auth-Session` cookieを削除せず`revoke_auth_session`も呼ばないため、
   logout後もBFF sessionが生存する。
4. **`oauth_bff`・cookie-fallback経路・`DatabaseSaasAuthSessionStore`のテストがゼロ**
   （`test_oauth_broker_client.py`のみ）。`DatabaseActiveTenantSessionPersister`にも単体テストが無い。
5. callbackは version を principal単位storeから取るため、同一principalの2 sessionが同じ
   `tenant_session_version`で開始する（AC-5と矛盾する）。

**あわせて是正した実装側の欠陥**: 上記コミットは、リポジトリに存在しない設計文書
`ac1_final_design.md`のSS2〜SS7を、出荷コードのコメント11箇所から参照していた（前セッションの
作業用ファイルと推測される）。参照先を実在の正本（`ADR-0074`の決定番号・回答案）へ振り替えた。

## 検証計画

- DB storeを共有する2 app/worker instanceで、同一sessionのCAS競合と切替後contextを確認する。
- 同一principal・異なるsession IDの2 clientで、tenant切替とlogoutの非干渉を確認する。
- tenant A/Bに同じdocIdを作り、旧version requestがresource lookup・監査mutation前に停止することを確認する。
