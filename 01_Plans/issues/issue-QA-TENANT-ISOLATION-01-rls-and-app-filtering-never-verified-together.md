# Issue: QA-TENANT-ISOLATION-01 テナント分離の二層防御が、二つの独立に検証された半分でしかない

- Type: Quality / Security
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/tests/test_saas_e2e_tenant_isolation.py`, `03_Implement/backend/tests/test_docs_tenant_isolation.py`, `03_Implement/backend/tests/test_document_access_rls_postgres.py`, `.github/workflows/ci.yml`
- Related ADR/Spec: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0063-saas-multitenant-trusted-auth-edge.md`, `THREAT_MODEL.md`
- Expected verification level: `integration`

## 課題

テナント分離は意図的に二層で設計されている。

1. **アプリ層**: 全リポジトリ呼び出しが `TenantContext` を伴い `WHERE tenant_id = :tenant` を付与する（`document_repository.py:33-37` 他）。
2. **DB層**: `apply_database_tenant_context` がトランザクションローカルなGUCを設定し（`tenant_db_guard.py:12-30`）、13〜14テーブルのPostgreSQL RLSポリシー `USING/WITH CHECK (tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), ''))` がこれを消費する。

**両層はそれぞれ十分に検証されているが、一度も一緒には検証されていない。**

| 検証 | 実際に通る経路 | 通らない経路 |
|---|---|---|
| HTTP分離テスト（約20件。`test_saas_e2e_tenant_isolation.py:278-345` で同一 `docId` の別テナント解決、テナントAからテナントBの文書へ404、実RS256 JWT・OAuthコードフロー・SAML→broker連鎖まで） | アプリ層のフィルタ | **DB層。SQLiteで走るため `apply_database_tenant_context` は no-op**（`tenant_db_guard.py:22-23` が非PostgreSQL方言で即return）。`test_saas_e2e_tenant_isolation.py:191-193`、CI既定 `KJ_ATLAS_DATABASE_URL: sqlite:///./kj_atlas.db`（`.github/workflows/ci.yml:318-320`） |
| RLSテスト（`test_document_access_rls_postgres.py`。非superuser・`NOBYPASSRLS` ロール、`pg_class`/`pg_policies` でFORCE RLSと`WITH CHECK`を要求、テナントコンテキスト無しで可視0行、越境write `rowcount == 0`、テナント付替え拒否、プール残留確認。SQLAlchemyメタデータから対象表集合を導出するメタテストまである） | DB層 | **HTTP経路。ルートを一切通らない** |

したがって「**本番のリクエスト経路が、PostgreSQLに対してリクエストごとに `apply_database_tenant_context` を実際に呼んでいる**」ことを確かめるテストが存在しない。二層防御は、独立に検証された二つの半分として存在している。

`THREAT_MODEL.md:203` はこれを認めている——SaaSは「起動可能であるが、本番運用には残りの `SAAS-TENANT-01` 条件の検証を要する」。

### なぜ P1 か

- SaaSプロファイルの安全性の主張全体がこの二層防御に乗っている。
- **修正が安価である。** 新規テストの設計は不要で、既存のHTTP分離スイートをPostgreSQLフィクスチャに対しても走らせればよい。RLS側のテストインフラ（非superuserロール、FORCE RLS検証）は既に存在する。
- 現状はアプリ層の `WHERE` 句が1箇所欠けても、SQLite上のテストは全て緑のまま通過する。RLSが後段で止める設計になっているが、**RLSが実際に効いていることをその経路で確認していない**ため、二層目が保険として機能する保証がない。

### 併せて記録する周辺の観測

本issueの範囲外だが、同じ調査で確認した関連事項。

- **RLS適用外の制御プレーン表が2つある**（明示的な許可リスト、`test_document_access_rls_postgres.py:34-40`）: `tenant_memberships`、`tenant_identity_providers`。テナントコンテキスト確立前に読む必要があるため設計として妥当だが、ランタイムロールが侵害された場合にテナント↔利用者の全対応表が読める。`saas_tenant_sessions`（`models.py:329-339`）も `tenant_id` を持たずRLS対象外。
- **`x-auth-roles` / `x-auth-groups` が全プロファイルでクライアント供給のままPDPへ渡る**（`routes/docs.py:278-279`）。SaaSでも検証済みJWTから導出していない。テナント境界ガードがPDPより先に走るため越境は起きないが、**テナント内の権限昇格に対して、サーバが攻撃者供給の属性を自らの認可サービスへ主張している**構造になる。別issue化が必要。

## 対応方針

- 実施すること:
  1. 既存のHTTPテナント分離スイート（`test_saas_e2e_tenant_isolation.py` / `test_docs_tenant_isolation.py`）を、SQLiteに加えて**PostgreSQLフィクスチャでも実行する**。RLS側が使っている非superuser・`NOBYPASSRLS` ロールを流用する。
  2. その構成で「アプリ層のテナントフィルタを意図的に外すと、RLSが単独で越境を止める」ことを確認する能力テストを1本置く（`DOGFOOD-METRIC-01` 案Aの能力カナリアと同じ形式。二層目が実在することの直接証拠になる）。
  3. CIのDBマトリクスへ組み込む。既に `Backend Oracle Database matrix` 相当のジョブ構成があるため、PostgreSQL分離スイートを同じ枠に載せられる。
- 実施しないこと:
  1. `x-auth-roles` / `x-auth-groups` のサーバ側導出（別issue）
  2. RLS適用外テーブルの設計変更（`ADR-0074` 採択後に扱う）

## 受入条件

- [ ] AC-1: `test_saas_e2e_tenant_isolation.py` の全ケースがPostgreSQL（非superuser・`NOBYPASSRLS`）に対しても実行され、CIで緑になる。
- [ ] AC-2: アプリ層のテナントフィルタを外した状態でRLSが越境を止めることを、能力カナリアとして固定する（ミューテーションで実際にfailすることを確認する）。
- [ ] AC-3: CIのDBマトリクスに組み込まれ、SQLite専用だった分離検証がPostgreSQLでも回っている。
- [ ] AC-4: `THREAT_MODEL.md:203` の留保を、本件について解消済みとして更新する。

## 検証

```bash
KJ_ATLAS_DATABASE_URL=postgresql+psycopg://... python -m pytest 03_Implement/backend/tests/test_saas_e2e_tenant_isolation.py -v
python -m pytest 03_Implement/backend/tests/test_document_access_rls_postgres.py -v
```

## 補足

- 発見経緯: ドッグフーディングの方向性レビューで「複数テナント並行運用」を軸として調査した際に検出した。
- **在庫としてはこの軸が最も厚い**（`SAAS-TENANT-*` 13件 + ADR 6本）。にもかかわらず、その全体が乗っている一点が未検証で残っていた。厚さと検証の深さは別物である。
- 三要素牽制の観点: 機能設計（アプリ層フィルタ）とデータ設計（RLSポリシー）はそれぞれ設計・検証されているが、**両者の接合点**——リクエストごとにGUCが設定されること——が三要素のどの次元にも属さない隙間に落ちている。`ADR-0067` の三次元は各次元の設計を保証するが、次元間の接合が実行時に成立することは保証しない。この観測は `three-element-constraint-checklist.html` への追加提案となりうる。
- `DOGFOOD-METRIC-01` / `DX-DESIGN-CHECK-01` / `DX-CONTRACT-DRIFT-01` / `DX-CANON-INTENT-01` と同じ「保護の主張と保護の実効範囲の乖離」の系列に属する。これで4件目であり、**この乖離が単発の不注意ではなく再発する構造であること**を示している。
