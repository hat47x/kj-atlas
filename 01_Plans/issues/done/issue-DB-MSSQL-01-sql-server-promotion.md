# Issue: DB-MSSQL-01 SQL Serverを共通DB昇格契約へ追加する

- Type: Architecture / Feature
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: DB-PORTABILITY-01 follow-up
- Priority: P2
- Scope: `03_Implement/backend/`, Alembic migration, database CI, configuration documentation
- Related ADR/Spec: `ADR-0066`, `02_Architecture/database_portability.md`
- Expected verification level: integration / real database

## 課題

- SQL Serverを追加する際もrepository/APIへDB固有分岐を増やさず、MySQL familyで確立したpromotion gateを再利用する。
- `LIMIT`、`RESTRICT`、check constraint関数、LOB型、default constraint reflectionの方言差をmigration全体に散在させない。
- single-tenant対応からshared-schema SaaS対応を推論しない。

## 受入条件

- [x] AC-1: SQL Server 2022のfresh migrationがheadまで通る。
- [x] AC-2: 1 MiB超Document、tenant複合FK、CI unique、transaction rollbackとpool再利用が実DBで通る。
- [x] AC-3: duplicate docId付きdowngradeはfail closedとなり、解消後のdowngrade/re-upgradeが通る。
- [x] AC-4: SQL Server native backupを別databaseへrestoreし、row countと大容量payloadを照合できる。
- [x] AC-5: PyMSSQL optional dependency、CI service、README、公開対応表が同期する。
- [x] AC-6: migration strategyは能力レジストリから選択され、SQL Server専用repository/APIを追加しない。
- [x] AC-7: shared-schema SaaSはPostgreSQL限定を維持する。

## 検証計画

- SQL Server 2022 Linux containerでfresh、constraint、LOB、transaction、downgrade/re-upgrade、backup/restoreの一連matrixを実行する。
- SQLite、PostgreSQL、MySQL/MariaDBの既存回帰を実行する。
- SafeMode、proposal-only、tenant認可契約は変更しない。

## 完了証跡 2026-08-10

- SQL Server 2022 Linux containerでfresh migrationをheadまで実行し、データ付きの`head -> 0007 -> head`を完了した。tenant A/Bの同一docIdが存在する間はdowngradeが意図どおりfail closedとなった。
- 1,048,587文字の`documents.payload_json`、cross-tenant複合FK拒否、CI collation上のissuer/audience重複拒否、rollback後のpool connection再利用を検証した。
- native `BACKUP DATABASE`/`RESTORE DATABASE`で別databaseへ復元し、2文書と最大1,048,587文字のpayloadを照合した。この演習を`mssql` markerの自動testとGitHub Actions serviceへ組み込んだ。
- SQLite対象回帰56件、MySQL 8.4/MariaDB 11.4 promotion matrix 2件、PostgreSQL 16 freshと0020/RLS roundtripを再実行した。
- DB差分は能力レジストリ、constraint DDL strategy、portable check/LOB DDL、実DB fixtureに限定し、repository/APIを変更していない。
