# ADR-0066: DB対応を能力レジストリと実DB検証で段階化する

- Status: Accepted
- Date: 2026-08-09
- Deciders: Maintainer
- Scope: `03_Implement/backend/`, migration, runtime configuration, database verification

## Context

kj-atlasはSQLAlchemy ORMを利用しているが、ORMが接続可能なDBと、製品がschema migration・制約・transaction・tenant分離まで保証できるDBは同義ではない。現行migrationにはSQLiteのtable rebuild、PostgreSQLのconstraint DDLとRLSがあり、無制限`TEXT`を主キー・索引へ利用している箇所はMySQL/MariaDB、SQL Server、Oracle等へそのまま移植できない。

接続URLの種類ごとに場当たり的な条件分岐を追加すると、runtime、migration、CI、文書の対応表が乖離し、将来DBを追加するほど複雑性と誤認が増える。一方でSQLite/PostgreSQLだけへ永久固定する必要はなく、個人OSSとして需要に応じて優先順位を変更できる拡張点は先に用意したい。

## Decision

1. DB方言の判断は単一の能力レジストリへ集約し、各backendに`family`、`support_level`、`migration_strategy`、`shared_schema_saas`を持たせる。
2. `verified`はSQLite/PostgreSQLだけとする。MySQL/MariaDB、SQL Server、Oracle、CockroachDBは`candidate`として登録するが、実DBmatrix完了までruntimeとAlembicをfail-fastで拒否する。
3. driver差ではなくDB familyを拡張単位にする。MySQLとMariaDBは同じfamilyとして共通化し、差分が実証された箇所だけ個別capabilityへ分離する。
4. candidateの昇格には、fresh migration、upgrade/downgrade、複合PK/FK・unique/check/index、CRUD roundtrip、transaction、backup/restoreの実DB検証を必須とする。SQLAlchemyのmock dialectやSQL生成だけでは昇格しない。
5. 識別子・索引対象文字列は、全DBで成立するbounded型へ一度だけ再設計する。payloadや長文まで一律VARCHAR化せず、identifierとcontentを型レベルで分離する。
6. 共有schema型SaaSは、DB側tenant guardとpool再利用matrixを満たすDBだけに許可する。現時点ではPostgreSQL限定とし、single-tenant DB対応の追加からSaaS対応を推論しない。
7. 各DB専用repositoryやAPIを作らず、差分は能力レジストリ、少数のmigration strategy、検証fixtureへ閉じ込める。

## Consequences

- 未検証DBで途中まで起動してからmigrationや制約で壊れる状態を防げる。
- 将来DBの追加は候補登録ではなく、型・migration・実DB証跡を伴う明示的な昇格になる。
- MySQL/MariaDB対応前にbounded identifier型への移行が必要となり、即時のURL許可より作業量は増える。
- SQLite/PostgreSQLの既存利用、SafeMode、proposal-only、export/import境界は変更しない。

## Non-goals

- SQLAlchemyが提供する全dialectを一括して正式対応しない。
- DB固有機能を最小公倍数へ落としてPostgreSQL RLSを弱めない。
- candidate DB用driverを、実DB検証前に必須runtime依存へ追加しない。

## Traceability

- Implementation: `01_Plans/issues/issue-DB-PORTABILITY-01-database-capability-registry.md`
- Canonical matrix: `02_Architecture/database_portability.md`
- Related: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`
- Related: `02_Architecture/runtime_parameter_registry.md`
