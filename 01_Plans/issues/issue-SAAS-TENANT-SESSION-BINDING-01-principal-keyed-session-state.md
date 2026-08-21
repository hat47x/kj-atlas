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

- [x] AC-1: trusted auth edgeが、principalとは別のserver-trusted認証セッション識別子を解決する。
  — 2026-08-20、BFF cookie経路で `ResolvedIdentity.auth_session_key_hash` として解決・公開する。
  bearer経路はNoneのまま（ADR-0074決定1/2がbrowserからbearerを廃す方針のため意図的）。
- [ ] AC-2: 共有ストアが認証セッション識別子、active tenant、`tenantSessionVersion`を同一行または同一原子境界で保持する。
- [x] AC-3: tenant切替後の次の`GET /session/context`とtenant-scoped APIが、再発行されていない旧tenant claimではなく保存済みactive tenantを正本として選択先tenantを解決する。
  — 2026-08-22、cookie/BFF経路（`auth_session_key_hash`が解決される経路）に限り達成。読み取り側はAC-1時点で`VerifiedTenantClaim`が`SaasAuthSessionRow.active_tenant_id`から毎request再構築されていたため既に成立、書き込み側（switch時の書き戻し）を本checkpointで配線した。bearer経路は`sid` claim読取が未着手のため対象外のまま（別限界として既記載）。
- [x] AC-4: 同じ認証セッションの複数タブはversionを共有し、一方の切替で他方のstale requestがresource lookup前に409となる。
  — 2026-08-22、cookie/BFF経路（`auth_session_key_hash`が解決される経路）に限り統合テストで確認。
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

### Implementation checkpoint 2026-08-20: auth-session store と cookie hashing のテストを追加

上記「記録の是正」で欠落として挙げた「`oauth_bff`・cookie-fallback経路・auth-session storeのテストが
ゼロ」のうち、**store層とcookie hashing層を `tests/test_saas_auth_session_store.py`（9件）で被覆した**。
ADR-0074 決定2/3 の fail-closed 契約を凍結する。

- `derive_session_key_hash()`: 決定性・鍵依存性（別鍵→別hash）・生cookie値がhash出力に残らないこと。
- `resolve_auth_session()` の fail-closed 4経路: 未知hash / revoked済み / 絶対期限（12h）超過 /
  idle timeout（60min）超過 のいずれも `None` を返す。
- sliding idle window: 期限内の resolve が `last_used_at` を更新し、次の idle 窓が延びること。
- **ADR-0074 決定3の核心的性質**: 同一 principal の独立した2 login のうち一方を revoke しても他方は
  生存する（行の同一性が principal ではなく login session であること）。AC-5 の前提にあたる。
- `preflight()` が未migration DBで `OperationalError` を送出すること。

**変異検査で有効性を確認した**: 3つの fail-closed guard（revoked判定・絶対期限判定・idle判定）を1つずつ
無効化すると、それぞれ対応するテストだけが失敗することを確認した（無効化しない状態では9件全pass）。
関連5ファイル計30件の回帰なし。

**あわせて是正した記録の齟齬**: `SaasAuthSessionRow` の docstring が「Expand-only: nothing constructs
or reads this table yet」と記載していたが、`DatabaseSaasAuthSessionStore` が既に読み書きしており事実と
異なっていた。現状（BFF loginで書き込み・cookie fallbackで読み取り）と残作業（CAS active-tenant更新・
anti-CSRF・logout revocation・cutover）を記す内容へ改めた。

**引き続き未着手**: `oauth_bff` のHTTP経路（login/callback）と `_resolve_from_auth_session_cookie()` の
テスト、および AC-1 本体の欠落（解決した session 識別子を `ResolvedIdentity` へ伝播させる導線）。

### Implementation checkpoint 2026-08-20: cookie-fallback 経路のテストを追加

前記 checkpoint で「引き続き未着手」とした `_resolve_from_auth_session_cookie()` を
`tests/test_trusted_auth_edge_cookie_fallback.py`（10件）で被覆した。ADR-0074 決定2/3 の
fail-closed 契約——提示された cookie が「生存中で tenant に束縛された session」を指さない場合は
identity ではなく 401 で終わること——を凍結する。

- 成功経路: 有効 cookie が principal / provider / subject と `VerifiedTenantClaim`
  （tenant_id・issuer・audience・subject・identity_provider_id）を解決すること。
- fail-closed 経路: cookie不在（`missing_token`）/ store未配線（`missing_token`）/
  未知cookie値・revoked済み・idle超過（いずれも `session_invalid`）/
  `active_tenant_id` がNULL（`session_invalid`）。
- **鍵依存性**: 別の鍵で発行された cookie は解決しない（keyed hash が実際に照会経路上にあることの
  確認。決定2）。
- **issuer解決不能は 503 `configuration_error`**（401ではない）——配備設定の誤りを per-request の
  認可失敗として扱わない。
- **bearer優先の固定**: bearer header がある限り `resolve()` は cookie 分岐に到達しない
  （前掲の「bearer優先の現行SPAでは新経路が使われない」という限界をテストとして明示した）。

**変異検査**: 本関数固有の guard（`active_tenant_id is None` の fail-closed 判定）を無効化すると
対応するテストだけが失敗することを確認し、復元後に作業ツリーがクリーンであることを検証した。
auth関連4ファイル計41件の回帰なし。

**引き続き未着手**: `oauth_bff` のHTTP経路（login/callback）のテストと、AC-1本体の欠落
（解決した session 識別子を `ResolvedIdentity` へ伝播させる導線）。

### Implementation checkpoint 2026-08-20: AC-1 完了（session識別子の公開）

前記 checkpoint で「AC-1本体の欠落」とした点を解消した。**解決した session 識別子を捨てずに
`ResolvedIdentity` へ公開する**。

- `ResolvedIdentity` へ `auth_session_key_hash: str | None = None` を追加した（末尾・既定値つきの
  純粋な加算であり、既存の構築箇所に変更を要さない）。
- `_resolve_from_auth_session_cookie()` がこれを設定する。`TrustedSaasRequestSession` は既に
  `ResolvedIdentity` を保持しているため、`session.identity.auth_session_key_hash` として
  そのまま到達でき、追加の配線を要さない。
- **意図的にAC-2の判断へ踏み込んでいない**: どのstoreを正本とするか（`saas_tenant_sessions` からの
  cutover）・CAS更新・anti-CSRF は本変更の範囲外。AC-1は「識別子を解決する」ことのみを要求しており、
  その利用先の設計はAC-2以降に属する。

**テスト（前掲のcookie-fallbackテストへ2件追加、計12件）**:

- 公開された識別子が keyed hash と一致し、かつ principal（`user_id`）と**異なる**こと。
- 同一principalの2 loginが**異なる**識別子を得ること（ADR-0074決定3・AC-5の前提）。
- 変異検査: 公開の配線（`auth_session_key_hash=session_key_hash`）を削除すると上記2件だけが
  失敗することを確認し、復元後に作業ツリーがクリーンであることを検証した。

**回帰**: auth / session / tenant / identity に該当する **419 passed・7 skipped・0 failed**
（`ResolvedIdentity` はauth全体の中核型のため広めに実行した）。

**引き続き未着手**: `oauth_bff` のHTTP経路（login/callback）のテスト、bearer経路での `sid` claim読み取り、
`POST /session/logout` でのcookie削除とrevoke、およびAC-2以降。

### Implementation checkpoint 2026-08-20: logout がBFF sessionを失効させるよう是正（決定6）

前記 checkpoint で挙げた「`POST /session/logout` が `Kj-Atlas-Auth-Session` cookie を削除せず
`revoke_auth_session` も呼ばないため logout 後も BFF session が生存する」を修正した。これにより
`revoke_auth_session` に初めて呼び出し元がついた。

- `oauth_bff.revoke_auth_session_cookie()` を追加し `logout_session` から呼ぶ。**行の失効と cookie の
  削除を両方行う**——行だけ失効させると死んだ credential を提示し続け、cookie だけ削除すると保持された
  複製で生存中の session を使える。どちらか片方だけでは穴が残る。
- store 未配線（single-tenant profile）でも cookie 削除は行う（削除は常に安全）。
- 失効対象は**提示された session のみ**（決定6）。

**テスト5件**（`tests/test_oauth_bff_logout_revocation.py`）:

- logout が提示された session を失効させること。
- logout が cookie を削除すること（`Max-Age=0`・`HttpOnly`）。
- **同一 principal の別 login は失効しないこと**（決定6。1つのブラウザからの logout が全 device を
  ログアウトさせない）。
- cookie 不在時・store 未配線時にも例外を出さず cookie 削除を行うこと。
- 変異検査: revoke 呼び出しを無効化して元の欠陥を再現すると、失効系2件だけが失敗し cookie 削除系3件は
  通ることを確認した。

**回帰**: logout / oauth / session 該当 **178 passed・0 failed**（既存の
`test_saas_oauth_login_e2e::test_logout_clears_session` を含む）。

**引き続き未着手**: `oauth_bff` の login/callback 経路のテスト、bearer 経路での `sid` claim 読み取り、
AC-2以降（active tenant の session 単位保存・CAS更新・anti-CSRF・cutover）。

### Implementation checkpoint 2026-08-21: oauth_bff の login/callback 経路のテストを追加

前記 checkpoint で残していた `oauth_bff` のHTTP経路を `tests/test_oauth_bff_login_flow.py`（37件）で
被覆した。**テストのみの追加であり出荷コードは変更していない。**

- **open-redirect ガード**（`_validate_next_path`）: protocol-relative（`//evil`）・絶対URL・
  scheme付き（`javascript:`）・先頭スラッシュなし・CR/LF注入・過長・空 をいずれも `/` へ落とすこと。
  同一originの宛先（query・fragment付きを含む）は保持すること。
- **PKCE**（`_generate_pkce_pair`）: challenge が verifier の unpadded S256 であること（RFC 7636）。
  誤った導出はローカルでは失敗せずbroker側で全交換が拒否されるだけなので、構成を直接固定する。
  login ごとに verifier が再利用されないこと。
- **pending cookie の fail-closed パース**: 不正JSON・非dict・欠損/空/型違いのフィールドをすべて
  `None` にすること。
- **`GET /session/login`**: broker未設定で503。redirect が `code_challenge_method=S256` を持ち、
  **redirect の `state` が cookie に保存された `state` と一致すること**（不一致ならcallbackのstate検査が
  原理的に成立しない）。敵対的な `next` は破棄されること。
- **`GET /session/callback` のガード順序**: pending cookie不在 / broker拒否 / state不一致（None・空・
  別値）/ code欠落 → いずれも400。broker設定欠落は **503**（client error として扱わない）。
- state比較が `hmac.compare_digest` であること（早期リターンしない）をソース検査で固定。

**変異検査の所見（正直な記録）**: open-redirect ガードの1層目（先頭スラッシュ検査）を無効化すると
`evil.example/path` が素通りしてテストが落ちる。一方 **2層目（`parsed.scheme or parsed.netloc`）を
無効化しても何も落ちない**——1層目を通過した値は必ず「スラッシュ1個で始まる」ため scheme も netloc も
持ち得ず、この行は到達不能である（実測でも到達する入力は無かった）。将来1層目を変更した際の余裕として
残置し、到達不能である旨をテストファイルに明記した。**被覆済みとは主張しない。**

**引き続き未着手**: bearer経路での `sid` claim 読み取り、AC-2以降。

### Implementation checkpoint 2026-08-22: AC-2 のstore層CAS実装（呼び出し元の配線は次段）

利用者からAC-2以降着手の承認を得て着手した。**本checkpointはAC-2の文字どおりの要求（「共有ストアが認証セッション識別子、active tenant、tenantSessionVersionを同一行または同一原子境界で保持する」）をstore層で満たす。まだ呼び出し元（`saas_request_context.py`・`routes/session.py`）は配線していない**——AC-3（保存済みactive tenantを正本として選択先tenantを解決する）は次のcheckpointに分離する。schema自体は既存のexpand migration（`20260813_0027`）で`SaasAuthSessionRow`に`active_tenant_id`・`tenant_session_version`が既に同一行にあり、今回追加したのは、その行へ**原子的にCAS更新する経路**である。

- `ResolvedAuthSession`（`saas_auth_state.py`）へ`tenant_session_version`を追加した。`resolve_auth_session()`が既存のfail-closed判定（revoked・絶対期限・idle）を通過した行からこれを返す。
- `DatabaseSaasAuthSessionStore.rotate_active_tenant()`を追加した。`session_key_hash`と現在の`tenant_session_version`を条件にした単一`UPDATE`で`active_tenant_id`と`tenant_session_version`を同時に書き換える。`revoked_at IS NULL`も条件に含めるため、revoke後のCASは常に失敗する（AC-6の前提: revoke後は自己復活できない）。version不一致（他タブが先に切替済み）もCAS失敗として扱う（AC-4の前提）。

**テスト4件を追加**（`test_saas_auth_session_store.py`、既存9件+今回追加4件=13件）:

- 一致するversionでのCAS成功（両列が同時に更新されること）。
- 不一致versionでのCAS失敗（AC-4: 行が変化しないこと）。
- revoked済み行でのCAS失敗（AC-6: 一致するversionでも復活しないこと）。
- 同一principalの独立した2 sessionのうち一方をrotateしても他方に影響しないこと（AC-5前提）。

**変異検査**: CAS条件から`revoked_at.is_(None)`を一時的に除去し、revoked-session-CASテストのみが失敗することを確認した（他12件は無傷）。復元後に13件全pass。

**回帰**: auth/session/tenant/identity該当 **467 passed・7 skipped・0 failed**（15分47秒）。

**引き続き未着手**: AC-3（`resolve_trusted_saas_request_session()`が保存済みactive tenantを正本として使う配線）、AC-4〜5の実挙動確認（配線後でなければ統合的に確認できない）、AC-6の残り（session id欠損・不正・過大、store不達のfail-closed——現状は`resolve_active_tenant_session_version()`がまだ`principal_id`だけで呼ばれているため未達）、AC-7（integration test）、AC-8（文書同期）、AC-9（cookie/anti-CSRF方針）。

### Implementation checkpoint 2026-08-22（続き）: AC-3 配線 — 保存済みactive tenantを正本にする

前checkpointの続きとして着手した。**発見**: cookie-fallback経路（`trusted_auth_edge.py::_resolve_from_auth_session_cookie`）は、実は既に`VerifiedTenantClaim.tenant_id`を`SaasAuthSessionRow.active_tenant_id`から**毎request再構築**していた（AC-1実装時点から）。つまりAC-3の**読み取り側**はcookie経路に限りAC-1時点で既に成立していた。欠けていたのは(a)切替の**書き込み側**——`persist_active_tenant_selection()`が選択tenantを`SaasAuthSessionRow`へ書き戻していなかった——と、(b)version読み取り側の一貫性——`resolve_active_tenant_session_version()`が別テーブル（`saas_tenant_sessions`、principal単位）のversionを返していたため、CASの基準点が実際に更新される行と一致しなかった、の2点。

- `active_tenant_session.py`: `resolve_active_tenant_session_version()`/`persist_active_tenant_selection()`へ`auth_session_key_hash: str | None = None`を追加。非Noneの場合は`app.state.saas_auth_session_store`から直接読み書きする新経路（`_resolve_session_keyed_version`/`_persist_session_keyed_selection`）へ分岐し、既存のprincipal単位persisterには一切触れない（AC-6: fallback禁止）。store未配線・session不明はいずれも既存のエラーコード（503 `session_context_unavailable`/`active_tenant_update_unavailable`、409 `tenant_session_changed`）でfail-closed。session-keyed書き込みは別cookieを発行しない（提示された`Kj-Atlas-Auth-Session`自体が束縛のため）。
- `saas_request_context.py`/`routes/session.py`: `identity.auth_session_key_hash`を両関数へ配線。
- `oauth_bff.py::handle_callback`: 初期`tenant_session_version`の生成元を、principal単位store（`saas_auth_state_store.current_or_create_session_version`）から独立した`_new_session_version()`へ変更した。従来はprincipalが同じなら2つの独立loginが同じ初期versionを共有していた（AC-5の趣旨に反する残存結合）。`auth_state_store`はこの関数から完全に不要になったため削除した。

**テスト8件を追加**（`test_active_tenant_session_keyed.py`、新規）: session-keyed版本読取の成功/store未配線/session不明（いずれもprincipal_idへfallbackしないことを明記）、session-keyed CAS書込の成功（行が実際に更新されること）/stale version拒否（行が変化しないこと）/store未配線/cookie未発行、および`auth_session_key_hash`省略時に既存persisterへ配線されることを固定する回帰1件。

**変異検査**: session不明時のfail-closed guardを一時的に無効化し、対応するテストのみが失敗することを確認、復元後23件（新規8+既存persister15）全pass。

**回帰**: auth/session/tenant/identity該当 **475 passed・7 skipped・0 failed**（新規8件を含む）。

**引き続き未着手**: AC-4（同一session複数タブでの実際のstale-request 409確認、統合テストとして）、AC-6残り（bearer経路でのsid claim読取自体は別限界として文書化済み・未着手）、AC-7（複数worker・複数instanceでのintegration test）、AC-8（文書同期）、AC-9（cookie/anti-CSRF方針の最終決定）。

### Implementation checkpoint 2026-08-22（続き）: AC-4 の統合テストを追加

`test_session_context_routes.py`へ、`auth_session_key_hash`を持つ識別子で`GET /session/context`→
`POST /session/active-tenant`（tab 1）→同じ旧versionでの`POST /session/active-tenant`（tab 2、stale）
を実際のroute stack経由で確認する統合テスト1件を追加した。`StaticIdentityResolver`に
`auth_session_key_hash`フィールドを追加し、`app.state.saas_auth_session_store`へ実際の
`DatabaseSaasAuthSessionStore`を配線した（既存の`RecordingActiveTenantPersister`等のstubは
`auth_session_key_hash=None`の既存テストに対して無変更）。

- tab 1のswitchが`SaasAuthSessionRow`のCASを実際に更新すること（`active_tenant_id`・
  `tenant_session_version`とも）を直接DB読取で確認。
- tab 2（旧versionを提示）が409 `tenant_session_changed`で拒否され、行が変化しないことを確認。

**変異検査で判明した所見（正直な記録）**: `_persist_session_keyed_selection`のCAS失敗判定
（`if not rotated: raise`）を無効化しても、この統合テストは失敗しなかった——`routes/session.py`の
`require_current_tenant_session_version()`が`persist_active_tenant_selection()`より**先に**呼ばれ、
提示versionと現在versionの不一致を検出して409を返すため、CAS層へ到達する前に拒否される。
一方、同じ無効化は`test_active_tenant_session_keyed.py`の単体テストでは正しく検出された
（そちらは`_persist_session_keyed_selection`を直接呼ぶため、事前check層を経由しない）。
したがって本統合テストは「連続した2 requestでstaleが409になる」というAC-4の文言を実際の
route経由で証明するが、**真の並行race（事前checkとpersistの間のTOCTOU窓）に対するCASの必要性は
単体テスト側が担っている**——両テストは異なる層を検証しており、統合テストがCAS層自体の
必要性を示さないのは想定どおり。復元後、両ファイル合計48件全pass。

**回帰**: auth/session/tenant/identity該当 **478 passed・7 skipped・0 failed**（新規1件を含む）。

## 検証計画

- DB storeを共有する2 app/worker instanceで、同一sessionのCAS競合と切替後contextを確認する。
- 同一principal・異なるsession IDの2 clientで、tenant切替とlogoutの非干渉を確認する。
- tenant A/Bに同じdocIdを作り、旧version requestがresource lookup・監査mutation前に停止することを確認する。
