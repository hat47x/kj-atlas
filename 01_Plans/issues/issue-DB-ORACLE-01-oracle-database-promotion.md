# Issue: DB-ORACLE-01 Oracle Databaseを共通DB昇格契約へ追加する

- Type: Architecture / Feature
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: DB-PORTABILITY-01 follow-up
- Priority: P2
- Scope: `03_Implement/backend/`, Alembic migration, database CI, configuration documentation
- Related ADR/Spec: `ADR-0066`, `02_Architecture/database_portability.md`
- Expected verification level: integration / real database

## 課題

- OracleのCLOB、foreign key構文、DDL暗黙commit、Data Pumpを既存promotion gateで実証する。
- Oracle固有差分をrepository/APIへ漏らさず、compiler・migration・実DBfixtureに限定する。
- Free editionの制限とsingle-tenant対応範囲を明示し、enterprise editionやshared-schema SaaSへ保証を拡張しない。

## 受入条件

- [x] AC-1: Oracle AI Database Free 23.26.2のfresh migrationがheadまで通る。
- [x] AC-2: 1 MiB超CLOB、tenant複合FK、case-insensitive unique、transaction rollbackとpool再利用が実DBで通る。
- [x] AC-3: duplicate docId付きdowngradeはfail closedとなり、解消後のdowngrade/re-upgradeが通る。
- [x] AC-4: Data Pump exportを別schemaへimportし、row countと大容量payloadを照合できる。
- [x] AC-5: python-oracledb optional dependency、独立CI job、README、公開対応表が同期する。
- [x] AC-6: Oracle固有差分はDDL compilerとportable migration境界に限定する。
- [x] AC-7: shared-schema SaaSはPostgreSQL限定を維持する。

## 完了証跡 2026-08-10

- Oracle AI Database Free 23.26.2とpython-oracledb Thin modeでfresh migration、およびデータ付き`head -> 0007 -> head`を完了した。
- 1,048,587文字の`documents.payload_json` CLOB、cross-tenant複合FK拒否、function-based indexによる大小文字非依存identity重複拒否、rollback後のpool connection再利用を検証した。
- Data Pumpでschemaをexportし、別schemaへremap importして2文書と最大1,048,587文字のpayloadを照合した。
- `NO ACTION`句の省略とfresh schema上の冗長型変更回避だけを共通境界へ実装し、repository/APIは変更していない。
- 固定versionのOracle Free imageを用いる独立CI jobへ同じ約3分のmatrixを組み込んだ。
