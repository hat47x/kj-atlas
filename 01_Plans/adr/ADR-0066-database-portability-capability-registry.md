# ADR-0066: DB対応を能力レジストリと実DB検証で段階化する

- Status: Accepted
- Date: 2026-08-09
- Deciders: Maintainer
- Scope: `03_Implement/backend/`, migration, runtime configuration, database verification

## Context

kj-atlasはSQLAlchemy ORMを利用しているが、ORMが接続可能なDBと、製品がschema migration・制約・transaction・tenant分離まで保証できるDBは同義ではない。現行migrationにはSQLiteのtable rebuild、PostgreSQLのconstraint DDLとRLSがあり、無制限`TEXT`を主キー・索引へ利用している箇所はMySQL/MariaDB、SQL Server、Oracle等へそのまま移植できない。

接続URLの種類ごとに場当たり的な条件分岐を追加すると、runtime、migration、CI、文書の対応表が乖離し、将来DBを追加するほど複雑性と誤認が増える。一方でSQLite/PostgreSQLだけへ永久固定する必要はなく、個人OSSとして需要に応じて優先順位を変更できる拡張点は先に用意したい。

## Decision

1. DB方言の判断は単一の能力レジストリへ集約し、各backendに検証対象名とCI image、`family`、`support_level`、`migration_strategy`、`shared_schema_saas`、検証済み同期driver、受理するSQLAlchemy drivername、optional driver、実DBtest marker、復旧testを持たせる。
2. `verified`はSQLite、PostgreSQL 16、MySQL 8.4、MariaDB 11.4、SQL Server 2022、CockroachDB 26.2.3、Oracle AI Database Free 23.26.2とする。今後の未検証DBは`candidate`として登録し、実DBmatrix完了までruntimeとAlembicをfail-fastで拒否する。
3. driver差ではなくDB familyを拡張単位にする。MySQLとMariaDBは同じfamilyとして共通化し、差分が実証された箇所だけ個別capabilityへ分離する。
4. candidateの昇格には、fresh migration、upgrade/downgrade、複合PK/FK・unique/check/index、CRUD roundtrip、transaction、backup/restoreの実DB検証を必須とする。SQLAlchemyのmock dialectやSQL生成だけでは昇格しない。
5. 物理型はDB都合で一律変換せず、identifier、bounded descriptive text、content objectへ分類する。識別子の上限はID生成規則・外部契約・索引要件から意味別に決め、payloadや長文を一律VARCHAR化しない。
6. 共有schema型SaaSは、DB側tenant guardとpool再利用matrixを満たすDBだけに許可する。現時点ではPostgreSQL限定とし、single-tenant DB対応の追加からSaaS対応を推論しない。
7. 各DB専用repositoryやAPIを作らず、差分は能力レジストリ、少数のmigration strategy、検証fixtureへ閉じ込める。
8. content objectは将来の`ContentStore` portの背後に置く。現行互換のDB保存を既定とし、object storage実装を追加してもrepository/APIのDocument契約へ保存先分岐を漏らさない。
9. object storage利用時もtenant・digest・schema version・size・object key等のmetadataはDBを正本とする。保存先の実行時切替やhybrid routingは、障害時状態遷移、移行・rollback、orphan回収が検証されるまで公開しない。
10. driver省略URLと対応済みasync URLは、各backendの検証済み同期driverへ正規化する。別driverを明示したURLはbackendがVerifiedでも許可せず、資格情報を含まないエラーでengine生成前に停止する。

## Three-Element Verification（ADR-0067 遡及適用）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | ORMが接続可能なDBと、schema migration・制約・transaction・tenant分離まで保証できるDBは同義ではない。個人OSSとして需要に応じて優先順位を変更できる拡張点を先に用意する | 機能: 未検証DBはcandidate登録とし実DB matrix完了までruntimeとAlembicをfail-fastで拒否。データ: SQLite/PostgreSQLの既存利用・SafeMode・proposal-only・export/import境界は変更しない |
| **データ設計** | DB方言の判断は単一の能力レジストリへ集約（family/support_level/migration_strategy/shared_schema_saas/検証済みdriver等）。物理型はidentifier・bounded descriptive text・content objectへ分類しpayloadや長文を一律VARCHAR化しない | 業務: MySQL/MariaDBは同一familyとして共通化し差分が実証された箇所だけ個別capabilityへ分離。機能: content objectは将来の`ContentStore` portの背後に置き保存先分岐をDocument契約へ漏らさない |
| **機能設計** | candidate昇格はfresh migration・upgrade/downgrade・複合PK/FK・CRUD roundtrip・transaction・backup/restoreの実DB検証必須。共有schema SaaSはDB側tenant guardとpool再利用matrixを満たすDB（現時点PostgreSQL限定）だけに許可 | 業務: driver省略URLと対応済みasync URLは検証済み同期driverへ正規化し資格情報を含まないエラーでengine生成前に停止。データ: object storage利用時もmetadataはDBを正本とする |

## Consequences

- 未検証DBで途中まで起動してからmigrationや制約で壊れる状態を防げる。
- 将来DBの追加は候補登録ではなく、型・migration・実DB証跡を伴う明示的な昇格になる。
- MySQL/MariaDBはbounded identifierと`LONGTEXT` content写像を適用し、single-tenant runtimeとして利用できる。共有schema SaaS対応は含まない。
- 大容量contentをDB外へ移せるが、DB/object間の原子的commitを仮定せず、補償処理と整合性検証を実装する必要がある。
- SQLite/PostgreSQLの既存利用、SafeMode、proposal-only、export/import境界は変更しない。

## Non-goals

- SQLAlchemyが提供する全dialectを一括して正式対応しない。
- DB固有機能を最小公倍数へ落としてPostgreSQL RLSを弱めない。
- DB固有driverを必須runtime依存へ追加せず、検証済みDBもoptional dependencyで導入する。

## Traceability

- Implementation: `01_Plans/issues/issue-DB-PORTABILITY-01-database-capability-registry.md`
- Canonical matrix: `02_Architecture/database_portability.md`
- Related: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`
- Related: `02_Architecture/runtime_parameter_registry.md`
