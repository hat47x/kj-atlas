# Issue: OPS-SAAS-SCALE-01 SaaS認証sessionの水平スケール準備

- Type: Operations / Security
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/active_tenant_session.py`, `03_Implement/backend/src/kj_atlas_api/saas_auth_state.py`, `03_Implement/backend/src/kj_atlas_api/main.py`, `04_Documentation/operations.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`, `01_Plans/adr/ADR-0064-saml-oidc-broker-jwt-coordinated-auth-flow.md`, `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（Proposed）
- Expected verification level: `integration`

## 現在の課題

当初はtenant session versionとJWT `jti` replay cacheがprocess内にあり、複数workerで状態を共有できなかった。2026-08-11にPostgreSQL共有store、CAS更新、startup preflight、DB障害時fail-closedを実装し、process-local state自体は解消した。

ただし共有行は`principal_id`を主キーとしてversionだけを保持する。認証session IDとactive tenantを保存しないため、次の意味で水平スケール対応は未完了である。

- 切替後の次requestで、Bearer tokenのtenant claimから元tenantへ戻り得る。
- 同じprincipalの別browser/device sessionが同じversionを共有し、切替やlogoutが相互干渉する。
- version cookieはDB lookupで照合されず、session ownershipやanti-forgeryを証明しない。
- 複数store instanceで同じprincipal/versionを参照できるtestは、認証session単位の継続性を証明しない。

詳細なデータ/API修正は`SAAS-TENANT-SESSION-BINDING-01`、方式判断は`ADR-0074`を正本とする。本issueは複数worker・複数replicaという運用条件で、そのsession正本が共有・失効・障害処理まで成立することを検証する。

## Bearer replay防御との境界

通常のBearer access tokenは有効期間中に複数requestで再利用され、`jti`は任意のtoken識別子である。同じaccess-token `jti`をworker横断で一回使用化する旧ACは撤回する。強いreplay防御の方式判断は`AUTH-ONE-TIME-JWT-01`と`ADR-0074`を正本とし、本issueでは独自のJWT replay ledgerを導入しない。

JWKS cacheはinstanceごとでよい。これはBrokerへの取得負荷には影響するが、署名検証の安全境界をprocess共有状態へ依存させない。取得集中、cooldown、max-staleの運用検証が必要になれば別issueで扱う。

## 受入条件

- [x] AC-1: PostgreSQL共有storeで、独立する2 store instanceが同じprincipal単位versionを参照し、CAS競合で一方だけが成功する。
- [x] AC-2: 共有表が未migrationまたはDB不達ならSaaS startupを拒否し、稼働中のsession version解決・切替も503へfail-closedしてin-memoryへfallbackしない。
- [x] AC-3: 運用・API・認証architecture文書が、現行保証をprincipal単位version共有までに限定し、本番利用gate未充足と明記する。
- [ ] AC-4: `ADR-0074`で採択された認証session正本を最低2 worker／2 app instanceが共有し、active tenant、version、期限、失効を一貫して解決する。
- [ ] AC-5: 同一sessionの複数tabはworkerをまたいでもversionを共有し、同じprincipalの別sessionは切替・logout・idle expiryで相互干渉しない。
- [ ] AC-6: DB切断、CAS競合、rolling restart、key rotation中に旧tenant requestをresource lookup前に拒否し、新tenantへ自動再送しない。
- [ ] AC-7: migration upgrade/downgradeと、最低2 workerのHTTP integration testをCIで固定する。単に2つのrepository objectを同じSQLite DBへ向けるtestで代替しない。
- [ ] AC-8: `04_Documentation/operations.md`にdeployment topology、migration順序、rolling restart、session失効、障害時runbookを記載する。

## 依存関係

- `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（採択が前提）
- `01_Plans/issues/issue-SAAS-TENANT-SESSION-BINDING-01-principal-keyed-session-state.md`（認証session正本の実装）

## 非目標

- access token `jti`の一回使用化を復活させない。
- sticky sessionを共有正本の代替にしない。
- JWKS responseや秘密鍵をDBへ保存しない。
- single-tenant profileへ共有sessionを強制しない。

## 検証

- `python -m pytest tests/test_saas_auth_state.py tests/test_active_tenant_session_persister.py -q`
- `python -m pytest tests/test_tenant_session_precondition.py tests/test_saas_e2e_tenant_isolation.py -q`
- PostgreSQL、最低2 API worker、同一session／別sessionのHTTP matrix
- migration upgrade → downgrade → upgrade

## 経緯

- D1: 既にSaaS必須のPostgreSQLを共有storeに採用し、Redis依存は追加しなかった。
- D2: 共有store未設定・未migration・不達はfail-fast／fail-closedとした。
- 旧D3: access-token `jti` ledgerは通常のBearer再利用を壊すため実装を撤回した。
- 共有化後の再監査で、principal単位version共有と認証session単位のactive tenant正本は別要件だと判明したため、本issueを後者の複数worker運用検証へ再基準化した。
