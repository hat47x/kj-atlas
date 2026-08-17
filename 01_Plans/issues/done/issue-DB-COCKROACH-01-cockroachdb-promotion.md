# Issue: DB-COCKROACH-01 CockroachDBを共通DB昇格契約へ追加する

- Type: Architecture / Feature
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: DB-PORTABILITY-01 follow-up
- Priority: P2
- Scope: `03_Implement/backend/`, Alembic migration, database CI, configuration documentation
- Related ADR/Spec: `ADR-0066`, `02_Architecture/database_portability.md`
- Expected verification level: integration / real database

## 課題

- PostgreSQL互換を名乗る分散SQL DBでも、schema lockやprimary key置換など固有のmigration制約がある。
- DB固有差分をrepository/APIへ漏らさず、既存promotion gateを再利用する。
- single-tenant対応からshared-schema SaaS対応を推論しない。

## 受入条件

- [x] AC-1: CockroachDB 26.2.3のfresh migrationがheadまで通る。
- [x] AC-2: 1 MiB超Document、tenant複合FK、case-insensitive unique、transaction rollbackとpool再利用が実DBで通る。
- [x] AC-3: duplicate docId付きdowngradeはfail closedとなり、解消後のdowngrade/re-upgradeが通る。
- [x] AC-4: native backupを別databaseへrestoreし、row countと大容量payloadを照合できる。
- [x] AC-5: optional dialect、CI、README、公開対応表が同期する。
- [x] AC-6: 固有差分は能力レジストリとportable DDL/migration層に限定する。
- [x] AC-7: shared-schema SaaSはPostgreSQL限定を維持する。

## 完了証跡 2026-08-10

- CockroachDB 26.2.3 single-node実DBでfresh migrationと、データ付き`head -> 0007 -> head`を完了した。同一docIdがtenant A/Bに存在する間のdowngradeは意図どおりfail closedとなった。
- 1,048,587文字の`documents.payload_json`、cross-tenant複合FK拒否、式indexによる大小文字非依存identity重複拒否、rollback後のpool connection再利用を検証した。
- native `BACKUP DATABASE`/`RESTORE DATABASE ... WITH new_db_name`で別databaseへ復元し、2文書と最大payloadを照合した。
- schema lock解除、原子的primary key置換、冗長な型変更回避をDDL/migration境界へ閉じ込め、repository/APIは変更していない。
- 同じmatrixを`cockroachdb` markerとGitHub Actionsの固定version containerへ組み込んだ。
