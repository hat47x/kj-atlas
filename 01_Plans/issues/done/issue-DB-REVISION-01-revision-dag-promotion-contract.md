# Issue: DB-REVISION-01 revision DAGのVerified DB promotion契約を共通化する

- Type: Test / Portability
- Status: Done
- Source Issue: DATA-GENERATION-01, DB-PORTABILITY-01
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/tests/database_portability_contracts.py`, `03_Implement/backend/tests/test_*_portability.py`, `03_Implement/backend/tests/test_document_access_rls_postgres.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0066-database-portability-capability-registry.md`, `01_Plans/adr/ADR-0070-content-addressed-generation-dag-and-git-adapter.md`, `02_Architecture/database_portability.md`
- Expected verification level: `integration`

## 課題

- 現在の問題: content-addressed revision DAG、AI generation lineage、retention pin、head compare-and-swapのrepository testはSQLiteへ集中していた。他のVerified DB promotion matrixはfresh migrationとDocument CRUD、tenant複合FK、LOB、transaction、backup/restoreを検証する一方、revision系tableは「migrationできる」ことしか実証していなかった。
- 利用者または開発への影響: 複合FK、Boolean check、複合primary key、CAS updateのいずれかにDB方言差が生じても、SQLite以外では本番利用時まで検出できない。DB別testへ同じfixtureを複製すると、対応製品追加に比例して保守対象が増える。

## 対応方針

- DB固有SQLを持たない共通revision contractを一つ定義し、全Verified DBの既存promotion matrixから呼び出す。
- 共通contractはtenantとDocumentも自己完結して準備し、既存promotion fixtureのデータ件数や実行順序へ依存させない。
- 同一digestをtenantごとに分離したblob、human base revision、AI runとAI proposal、source/parent edge、pin、headを保存し、head CAS成功とstale writer拒否、別tenant不変を確認する。
- 製品別分岐をrepositoryやcontract helperへ追加しない。方言差が必要な場合は既存migration／DDL portability境界で解決する。

## 受入条件

- [x] SQLite、PostgreSQL、MySQL、MariaDB、SQL Server、CockroachDB、Oracleの全Verified DBで同一contractが実行対象になる。
- [x] blob、AI run、base/proposal revision、source、parent、pin、headの複合FK付き保存が成功する。
- [x] head compare-and-swapがversion一致時だけ成功し、stale writerを拒否する。
- [x] tenant Aのhead更新がtenant Bの同名revisionへ影響しない。
- [x] contractは既存backup/restore件数fixtureから独立し、DB別の重複実装を持たない。

## 検証計画

- SQLiteで共通contract単体testを実行する。
- PostgreSQL 16、MySQL 8.4、MariaDB 11.4、SQL Server 2022、CockroachDB 26.2、Oracle Free 23.26の一時containerで、既存promotion／RLS matrix全体を実行する。
- Ruff、format、差分検査を通し、各DB固有testが共通helper以外のrevision fixtureを持たないことを確認する。

## 完了記録（2026-08-11）

- `database_portability_contracts.py`へ自己完結した共通contractを追加し、SQLite単体testと6種類のserver DB matrixへ接続した。
- 実測結果: SQLite `1 passed`、PostgreSQL 16 RLS suite `4 passed`、MySQL 8.4／MariaDB 11.4 matrix `2 passed`、SQL Server 2022 `1 passed`、CockroachDB 26.2 `1 passed`、Oracle Free 23.26 `1 passed`。
- 各server DBではfresh migration、guarded downgrade/re-upgrade、transaction、native backup/restore等を含む既存promotion matrix全体も同時に成功した。共通contractにDB製品分岐は追加していない。
