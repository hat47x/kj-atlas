# Issue: SAAS-RLS-02 PostgreSQL RLSの対象導出とCI実行をfail-closedにする

- Type: Security
- Status: Done
- Source Issue: SAAS-TENANT-01
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/tests/test_document_access_rls_postgres.py`, `.github/workflows/ci.yml`
- Related ADR/Spec: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`, `02_Architecture/contract-seam-integrity-2026-08-05.html`, `01_Plans/issues/issue-DATA-GENERATION-01-content-generation-policy.md`
- Expected verification level: `integration`

## 課題

- 現在の問題1: 「migrationでRLSを有効化する全表」を検証する契約testが、migration source内の固定SQL文字列だけを正規表現で収集していた。helper、定数、loopでRLSを設定するinquiry bundle、content object、revision DAG、generation lineageの10表は検出対象外であり、手書きの4 modelとの一致だけでgreenになっていた。
- 現在の問題2: CIのPostgreSQL jobは一般DB test用の`KJ_ATLAS_RUN_PG_TESTS`だけを設定し、RLS suiteが要求する`KJ_ATLAS_RUN_PG_RLS_TESTS`、分離runtime credential、非superuser roleを用意していなかった。このため実RLS testはPostgreSQL jobでもskipされていた。
- 利用者または開発への影響: 新しいtenant data-plane表でRLS migrationを忘れても通常testと実DB CIが成功し得る。現時点のmigrationには対象14表のRLSが存在するため、直ちに実データ越境が確認されたものではないが、多層防御の最下層を継続的に証明できない状態だった。

## 対応方針

- `tenant_id`列を持つ表をSQLAlchemy metadataから導出し、workspace context成立前に参照するcontrol-plane表だけを理由付きallowlistで除外する。
- 実PostgreSQLのcatalogを正本として、全導出対象表に`ENABLE ROW LEVEL SECURITY`、`FORCE ROW LEVEL SECURITY`、`USING`、`WITH CHECK`が存在することを検証する。
- 非superuser・非`BYPASSRLS`の専用runtime roleをCIで作成し、同roleでtenant contextなしの全対象表が不可視になることと、既存のtenant A/B越境negative matrixを毎回実行する。
- historical migrationから現在状態を正規表現で推測しない。migration再現性のため、過去migrationからruntime側の可変registryをimportさせない。

## 受入条件

- [x] ORMへtenant-scoped data-plane表を追加しRLSを追加しなかった場合、実PostgreSQL catalog testが失敗する。
- [x] control-plane除外は表名と理由が明示され、存在しない古い除外は通常testで失敗する。
- [x] revision/blob/generation/inquiryを含む全14表でRLS有効・強制とwrite checkを実DB確認する。
- [x] tenant contextなしのruntime roleから全14表の行が不可視である。
- [x] CIがRLS suiteをskipせず、migration roleとruntime roleを分離する。
- [x] 既存のpool再利用、tenant越境read/write、tenant reassignment拒否を後退させない。

## 検証計画

- 通常確認: metadata導出test、Ruff、format、workflow構文と差分検査を実行する。
- 実DB確認: PostgreSQL 16へfresh migrationを適用し、専用runtime roleを作成して`test_document_access_rls_postgres.py`全体を実行する。
- 期待結果: 14表のcatalog postureとcontextなし不可視性、既存4表のtenant越境behaviorがすべて成功する。

## 完了記録（2026-08-11）

- 固定SQL文字列の正規表現収集と4 modelの手書きlistを廃止し、SQLAlchemy metadataから16のtenant-scoped表を導出した。`tenant_identity_providers`と`tenant_memberships`はcontrol-plane用途を理由付きで除外し、残る14表をRLS必須範囲とした。
- PostgreSQL catalogの`relrowsecurity`、`relforcerowsecurity`、`pg_policies.qual`、`pg_policies.with_check`を検査し、runtime roleでtenant contextを設定しない全表readが0行になるtestを追加した。
- CIへ非superuser・非`BYPASSRLS` runtime roleと最小のschema/table/sequence権限を追加し、RLS専用suiteを明示的に有効化した。
- PostgreSQL 16の一時containerへfresh migrationを適用し、RLS test全3件passを確認した。通常のmetadata導出testも単独passし、Ruffとformat checkを通過した。
