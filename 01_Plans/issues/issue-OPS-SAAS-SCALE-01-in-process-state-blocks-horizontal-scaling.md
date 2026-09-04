# Issue: OPS-SAAS-SCALE-01 SaaS認証sessionの水平スケール準備

- Type: Operations / Security
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/active_tenant_session.py`, `03_Implement/backend/src/kj_atlas_api/saas_auth_state.py`, `03_Implement/backend/src/kj_atlas_api/main.py`, `04_Documentation/operations.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`, `01_Plans/adr/ADR-0064-saml-oidc-broker-jwt-coordinated-auth-flow.md`, `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（**Accepted 2026-08-13**: 案2 server-owned BFF session）
- Expected verification level: `integration`

## 現在の課題

当初はtenant session versionがprocess内にあり、その後のPostgreSQL共有化も`principal_id`単位のversion共有に留まっていた。`SAAS-TENANT-SESSION-BINDING-01`とADR-0074の実装により、現在のBFF Cookie経路では`saas_auth_sessions`が認証session単位の正本となり、active tenant、`tenantSessionVersion`、期限、失効を同一行で扱う。

2026-09-04の再監査では、従来の「2 worker」証拠が同一SQLite DBへ向けた2つのstore objectであり、本issueのAC-7が明示する実PostgreSQL・複数app HTTP境界を満たしていないことが分かった。そこで隔離PostgreSQLへ実migrationを適用し、別々のSQLAlchemy engineを持つ複数FastAPI appから同じBFF sessionをHTTPで処理する回帰テストを追加した。

この実証により、session正本の水平共有そのものは確認できた。残る主な課題は、DB切断時にtenant-scoped resource lookupより前で確実に停止することと、clientが失敗したtenant切替を別tenantへ自動再送しないことを一続きの障害テストで固定する点である。

また、実証用engineを`pool_size=1 / max_overflow=0`へ絞ると、request用DB sessionを保持したまま認証session storeが別sessionを開く現行経路でpool timeoutとなることも観測した。これは共有正本の誤りではないが、水平スケール時の接続pool設計に必要な運用条件として`operations.md`へ反映する。

## Bearer replay防御との境界

通常のBearer access tokenは有効期間中に複数requestで再利用され、`jti`は任意のtoken識別子である。同じaccess-token `jti`をworker横断で一回使用化する旧ACは撤回する。強いreplay防御の方式判断は`AUTH-ONE-TIME-JWT-01`と`ADR-0074`を正本とし、本issueでは独自のJWT replay ledgerを導入しない。

JWKS cacheはinstanceごとでよい。これはBrokerへの取得負荷には影響するが、署名検証の安全境界をprocess共有状態へ依存させない。取得集中、cooldown、max-staleの運用検証が必要になれば別issueで扱う。

## 受入条件

- [x] AC-1: PostgreSQL共有storeで、独立する2 store instanceが同じprincipal単位versionを参照し、CAS競合で一方だけが成功する。
- [x] AC-2: 共有表が未migrationまたはDB不達ならSaaS startupを拒否し、稼働中のsession version解決・切替も503へfail-closedしてin-memoryへfallbackしない。
- [x] AC-3: 運用・API・認証architecture文書が、現行保証をprincipal単位version共有までに限定し、本番利用gate未充足と明記する。
- [x] AC-4: `ADR-0074`で採択された認証session正本を最低2 worker／2 app instanceが共有し、active tenant、version、期限、失効を一貫して解決する。
  - 2026-09-04: `test_saas_auth_session_postgres_multi_instance.py`で、別engineを持つ2 FastAPI appが同じPostgreSQL上のBFF sessionをHTTPで共有し、tenant/version、logout失効、idle expiryを同じ正本から解決することを確認した。
- [x] AC-5: 同一sessionの複数tabはworkerをまたいでもversionを共有し、同じprincipalの別sessionは切替・logout・idle expiryで相互干渉しない。
  - 2026-09-04: app Aで切り替えたversionをapp Bが直後に観測し、app Bから旧versionを送ると409となること、同一principalの別loginはtenant/versionを維持し、一方のlogout後も継続することを確認した。
- [ ] AC-6: DB切断、CAS競合、rolling restart、key rotation中に旧tenant requestをresource lookup前に拒否し、新tenantへ自動再送しない。
  - 2026-09-04進捗: CAS競合、別engineで作り直したappへのrolling restart相当、hash key変更時の401 fail-closedは実PostgreSQLで確認済み。DB切断をtenant-scoped resource lookupと組み合わせたHTTP障害テスト、およびclient側の非自動再送の一続きの証拠が残る。
- [x] AC-7: migration upgrade/downgradeと、最低2 workerのHTTP integration testをCIで固定する。単に2つのrepository objectを同じSQLite DBへ向けるtestで代替しない。
  - 2026-09-04: committed PostgreSQL testで`20260813_0027`へのupgrade、`0026`へのdowngrade、`head`への再upgradeと複数app HTTP matrixを固定し、branch-only GitHub Actions Run `33864904968`（PostgreSQL 16）で成功を確認した。常設workflowを置かないrepository運用とは分離し、テスト本体をCIから再利用できる形で保持する。
- [x] AC-8: `04_Documentation/operations.md`にdeployment topology、migration順序、rolling restart、session失効、障害時runbookを記載する。
  - 2026-09-04: PostgreSQL共有session正本、sticky session非依存、migration/rollback順序、hash key rotation、DB/pool障害、409/401/503時の初動を現行実装へ同期した。

## 依存関係

- `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（**2026-08-13 採択済み**。AC-4〜8 は着手可能）
- `01_Plans/issues/done/issue-SAAS-TENANT-SESSION-BINDING-01-principal-keyed-session-state.md`（認証session正本の実装）

## 非目標

- access token `jti`の一回使用化を復活させない。
- sticky sessionを共有正本の代替にしない。
- JWKS responseや秘密鍵をDBへ保存しない。
- single-tenant profileへ共有sessionを強制しない。

## 検証

- `python -m pytest tests/test_saas_auth_state.py tests/test_active_tenant_session_persister.py -q`
- `python -m pytest tests/test_tenant_session_precondition.py tests/test_saas_e2e_tenant_isolation.py -q`
- `KJ_ATLAS_RUN_PG_TESTS=1 KJ_ATLAS_TEST_POSTGRES_CONTAINER=<container> KJ_ATLAS_DATABASE_URL=<postgresql-url> python -m pytest -m postgres tests/test_saas_auth_session_postgres_multi_instance.py -q`
- PostgreSQL 16 branch-only GitHub Actions Run `33864904968`: 上記実証 `1 passed`、関連session/CSRF回帰 `50 passed`
- migration `20260813_0027` upgrade → `20260813_0026` downgrade → `head` upgradeを同じ隔離DBで確認

## 経緯

- D1: 既にSaaS必須のPostgreSQLを共有storeに採用し、Redis依存は追加しなかった。
- D2: 共有store未設定・未migration・不達はfail-fast／fail-closedとした。
- 旧D3: access-token `jti` ledgerは通常のBearer再利用を壊すため実装を撤回した。
- 共有化後の再監査で、principal単位version共有と認証session単位のactive tenant正本は別要件だと判明したため、本issueを後者の複数worker運用検証へ再基準化した。
- D4: 2026-09-04、SQLite上の2 store objectをcluster-level証拠とは扱わず、実PostgreSQL＋複数FastAPI appのHTTP実証へ置き換えた。実証中に観測したconnection pool余力も水平スケールの運用条件として記録した。
