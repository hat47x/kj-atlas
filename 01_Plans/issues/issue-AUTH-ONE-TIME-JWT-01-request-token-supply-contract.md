# Issue: AUTH-ONE-TIME-JWT-01 Bearer access tokenのreplay防御方式が未決

- Type: Architecture / Security / Frontend
- Status: Open
- Source Issue: `SEC-AUTH-REPLAY-01`
- Priority: P1
- Owner: Maintainer
- Scope: auth edge, frontend auth client, Broker/BFF integration, `ADR-0064`
- Related ADR/Spec: `ADR-0064`, `ADR-0074`（Accepted）, `OPS-SAAS-SCALE-01`, `SEC-AUTH-REPLAY-01`
- Expected verification level: integration

## 課題

直前の実装はaccess token自身の`jti`を要求単位nonceとして消費し、同じBearer tokenの2回目以降を拒否した。しかしRFC 6750のBearer tokenは、所持者が有効期間中にresource serverへ提示するcredentialであり、現行frontendも同じ短命tokenを複数API要求へ使用する。RFC 7519の`jti`はJWTの一意識別子で、通常のBearer access tokenをone-time credentialへ変える規定ではない。

このため、access token `jti`だけをDBへ一度登録して再送を拒否する方式は、正規clientと窃取者を区別できず、通常操作、並列fetch、network retryを壊す。sender-constrained tokenなしに「窃取Bearer tokenの再利用だけを拒否する」ことはできない。誤ったone-time実装は撤回し、通常のtoken再利用を復元した。

## 三要素牽制

- 業務設計: 利用者は一度のlogin後に複数の閲覧・保存要求を行える必要がある。要求ごとの再認証やtoken交換を通常業務へ持ち込まない。
- データ設計: 生token、秘密鍵、生`jti`を永続化・log出力しない。sender constraintを採る場合も公開鍵thumbprintと短命proof replay stateだけを最小保持する。
- 機能設計: Bearer方式を維持する間は署名、issuer、audience、期限、TLS、module-memory保持で防御する。強いreplay防御が必要ならaccess tokenの`jti`ではなく、HTTP method/URI/token hashへ結び付く要求単位proofを検証する。

## 対応方針

- 候補A: RFC 9449 DPoP。client鍵へaccess tokenをsender-constrainし、要求ごとのDPoP proof `jti`、`htm`、`htu`、`ath`を検証する。
- 候補B: same-origin BFF session。Bearer tokenをbrowserへ渡さずBFFへ閉じ込め、browser要求はHttpOnly sessionとCSRF防御で扱う。
- 候補C: 現行Bearer方式を維持し、短い有効期限、TLS、module-memory保持、audience制限を保証範囲として明記する。
- 比較判断は`ADR-0074`へ集約し、2026-08-13にAcceptedとなった。同ADRはactive tenant正本化とtoken replay露出縮小を同じserver-owned session境界で解く案B（server-owned BFF session）を採用した。DPoPを別系統で並行実装せず、BFF採択後もBearer access token自体へ未実装のreplay防御があるかのようには表明しない。

## 受入条件

- [x] 通常のBearer access tokenを連続API要求へ使用できる契約を回帰testで復元する。
- [x] `jti`欠損tokenをRFC 7519どおり通常Bearer JWTとして扱い、docstringとtestを一致させる。
- [x] DPoP、BFF、短命Bearer継続の業務・データ・機能trade-offを`ADR-0074`へ集約し、BFFを採用候補としてProposedにした。
- [x] `ADR-0074`をMaintainerがAcceptedまたはRejectedにし、本issueの実装方式を確定する（2026-08-13、Maintainer承認によりAccepted。**案2 server-owned BFF session** を採用。同ADRの実装要件Decision 7が本issueの方針を確定させる）。
- [x] 強いreplay防御を採る場合、別worker間でも要求proof再利用を拒否し、通常のaccess token再利用を壊さない。
  — 2026-09-04。B-model読み替え（本ファイル末尾の補正節）のもとで確認。CAS版数の陳腐化再利用は
  `tests/test_saas_auth_session_store.py::test_two_worker_instances_share_and_atomically_rotate_active_tenant`
  （2独立`DatabaseSaasAuthSessionStore`インスタンス＝別worker相当が同一DB行を共有し、片方のCAS成功後は
  もう片方の陳腐化versionでのCASが失敗する）で既存確認済み。本checkpointで欠けていた
  「一方のworkerでのrevoke（盗難/漏洩cookieの失効相当）がもう一方のworkerへ即時反映されるか」を
  新規テスト`test_revocation_on_one_worker_is_visible_to_another_worker_immediately`（同ファイル）で追加確認した
  ——worker_aでrevoke後、worker_bの`resolve_auth_session`は即座に`None`を返す（プロセスローカルcacheが
  存在せず毎回共有DBを読むため）。通常のcookie再利用（同一session cookieでの連続request）は
  `test_resolving_slides_the_idle_window`で非破壊を確認済み。anti-CSRF token（`session_csrf.py`）は
  session-bound HMACによるstateless検証のため、鍵を共有する任意のworkerで同一に検証され、
  worker間の追加同期を必要としない設計であることをソースで確認した。
  変異検査: `saas_auth_state.py::resolve_auth_session`のrevoked判定を一時的に無効化し、新規テストを含む
  3件（新規1件＋既存2件）が正しく失敗することを確認、復元後15件全pass。
  **2026-09-04 再同期**: その後mainへ入ったPR #2885では、実PostgreSQLと複数FastAPI appを使うHTTP integration test
  `test_saas_auth_session_postgres_multi_instance.py`が実際に追加された。migrationのupgrade / downgrade / re-upgrade、
  app間のactive tenant・version共有、別login非干渉、logout・idle expiry・hash key不一致時のfail-closedまで確認している。
  したがって、以前の「PR #2885は無関係で該当testも存在しない」という記録は現在のmainには当てはまらない。
  本ACは既存の共有DB/CAS/revoke検証で満たした判断を維持しつつ、cluster-levelの追加証拠としてPR #2885を参照する。
- [x] timeout、応答不明retryがfail-closedし、mutationを重複実行しない。
  — 2026-09-04。本issueのscope（auth edge、BFF統合）が対象とする状態変更操作はactive tenant切替・
  login・logoutの3つ。切替は既存の`tests/test_session_context_routes.py::test_active_tenant_change_uses_the_session_keyed_store_and_rejects_a_stale_second_tab`
  （precondition versionが古いまま再送されたら行を変更せず409で拒否）と単体テスト
  `test_rotate_active_tenant_fails_closed_on_stale_expected_version`で確認済み——応答不達後の再送は
  同じ古いprecondition versionを再提示するため、CASが自然に「二重適用しない」を保証する。
  login（`GET /session/callback`）は新規テスト`tests/test_oauth_bff_callback_retry_safety.py::test_retrying_the_same_code_after_success_does_not_create_a_second_session`
  で確認した——OAuth authorization codeは仕様上一回使用（mock IdPの`_pending_codes`も交換後に削除する）
  であり、応答不達後に同じcodeを再送すると2回目の`exchange_code_for_tokens`が失敗し、
  `SaasAuthSessionRow`が重複作成されないことを直接DB読取で確認した。logoutは
  `revoke_auth_session`が既に失効済みの行へ再度`revoked_at`を書いても副作用が増えない設計のため、
  再送は本質的に安全（既存`test_oauth_bff_logout_revocation.py`で個別確認済み）。
  変異検査: `oauth_bff.py`の`OauthBrokerInvalidResponseError`ハンドラを一時的に「失敗を握りつぶして
  session作成を続行する」よう書き換え、新規テストが正しく失敗する（`DID NOT RAISE`）ことを確認、
  復元後pass。
- [x] refresh tokenをSPAへ渡さず、XSS時のcredential露出範囲を拡大しない。
  — 2026-09-04。3層で構造的に確認した。(1) `oauth_broker_client.py::BrokerTokenResponse`は
  `access_token`/`token_type`/`expires_in`/`id_token`のみを持つデータクラスであり、
  brokerの応答に`refresh_token`が含まれていてもその値を保持するフィールドが存在しない——
  新規テスト`tests/test_oauth_broker_client.py::test_exchange_drops_the_refresh_token_even_when_the_broker_returns_one`
  でbroker応答に`refresh_token`を含めても`exchange_code_for_tokens`の戻り値に残らないことを固定した。
  (2) `oauth_bff.py::handle_callback`のredirect responseはHttpOnlyな`Kj-Atlas-Auth-Session`
  （opaque `secrets.token_urlsafe(32)`、broker tokenとは無関係な値）と非HttpOnlyなCSRF synchronizer
  token（認証credentialではない）の2 cookieのみを設定し、token値はheader/bodyのどこにも現れない——
  新規テストの`first.raw_headers`検査で直接確認した。(3) frontendの現行Bearer互換経路
  （`token_store.ts`はaccess tokenのみをmodule memoryへ保持しrefresh tokenを一切受け付けない設計、
  `oauth_callback.ts`はbroker応答に`refresh_token`キーが存在するだけで
  `oauth_refresh_token_not_allowed`エラーとして拒否する）は既存test
  `oauth_callback.test.ts::"rejects the whole response when a refresh token is exposed"`で確認済み。
  新BFF経路はSPAへtoken自体を一切渡さないためXSS時の露出範囲は旧Bearer経路より狭まり、拡大していない。
- [ ] mock Broker、frontend統合、最低2 backend workerのE2Eで契約を固定する。
  — 2026-09-04 再同期。**未充足のまま**。周辺の実証は大きく進んだが、このACが要求する縦断経路はまだ1本につながっていない。

  PR #2885では、実PostgreSQLと複数FastAPI appを使ったHTTP integration testにより、migration往復、複数app間のsession共有、
  stale version拒否、別login非干渉、logout・idle expiry・hash key不一致時のfail-closedを確認した。続くPR #2893では、実PostgreSQLを
  切断した状態でもtenant-scoped resource lookupより前に503で停止することと、frontendが409/503を利用者操作なしに自動再送しないことを
  固定し、`OPS-SAAS-SCALE-01`の全ACを完了させた。以前の「OPS-SAAS-SCALE-01 AC-7も未実装」という記録は現在のmainには当てはまらない。

  一方、`03_Implement/frontend/e2e/tenant_session_multitab.spec.ts`は実ブラウザを使うものの、backend APIはPlaywrightの`context.route()`で
  `ServerState`へ差し替えており、実backendやmock Identity Brokerを起動しない。このため、PR #2885/#2893のbackend側実証と既存Playwright
  suiteは相互補完にはなるが、**mock Broker → 実frontend → 共有PostgreSQLを使う最低2 backend instance**という一続きのE2Eにはなっていない。

  残作業はこの縦断経路を1本固定することに限定する。`QA-E2E-SAAS-01`はSaaS UI全体のブラウザE2E台帳、
  `SAAS-TENANT-E2E-01`はAI mutation固有generation guardの観測精度を扱うため、本ACの代替とはしない。逆に、本ACで既に完了した
  PostgreSQL複数app実証を再実装しない。

## 暫定運用

`ADR-0074`のBFF方式と`SAAS-TENANT-SESSION-BINDING-01`、`OPS-SAAS-SCALE-01`の実装・実証は完了している。SaaSのBFF経路では、browserへaccess tokenを渡さず、認証session単位のactive tenantとversionをPostgreSQL正本として複数appから共有する。

ただし本issueの最後のACである「mock Broker → 実frontend → 最低2 backend instance」の縦断E2Eが未完のため、その一続きの経路まで検証済みとは表明しない。また、BFF採用を「Bearer access token自体のreplayを一般に防御した」と言い換えない。互換Bearer経路について表明できる保証は、短命、署名検証、issuer/audience制限、TLS、browser storage不使用の範囲に留める。

## 2026-09-04 ADR-0074採択後の補正

`ADR-0074`は候補B（同一origin BFF session）を採用し、候補A（RFC 9449 DPoP）は採らなかった。B採用下では、browserはaccess tokenそのものを保持・送信せず、HttpOnly cookieのopaque session IDだけを送る。したがってAC-5の「要求proof再利用」は、DPoP proof `jti`のような要求単位署名ではなく、B採用時にADR-0074 Decision 3〜5が定めるsession機構（`session_key_hash`主キー、CAS版数更新、session束縛anti-CSRF token）が担う。AC-5〜AC-8は、この読み替えのもとで現行実装（`SAAS-TENANT-SESSION-BINDING-01`、`OPS-SAAS-SCALE-01`）がどこまで満たしているかを確認し、未充足分だけを実装する。DPoPのための別実装は追加しない。

## 依存関係

- `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（採択が前提。DPoP/BFFの並行実装を避ける）
- `01_Plans/issues/done/issue-SAAS-TENANT-SESSION-BINDING-01-principal-keyed-session-state.md`（BFF採択時は同一session正本として実装・検証する）

## 根拠

- RFC 7519 §4.1.7: `jti`はJWTの一意識別子でありoptional。access tokenの一回使用を意味しない。
- RFC 6750 §1.2/1.3: Bearer tokenは所持者がresource serverへ提示するaccess credentialで、鍵所持証明を要求しない。
- RFC 9449 §4.2: replay防御対象の要求単位`jti`はaccess tokenではなく、`htm`/`htu`等へ結び付くDPoP proof JWTに置かれる。
