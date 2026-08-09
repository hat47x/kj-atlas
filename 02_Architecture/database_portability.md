# Database portability

DB対応の正本は本書とする。SQLAlchemyがdialectを提供していることは、kj-atlasがそのDBを正式対応していることを意味しない。

## Support matrix

| Backend | Family | 状態 | Migration strategy | Single-tenant | Shared-schema SaaS |
| --- | --- | --- | --- | --- | --- |
| SQLite | sqlite | Verified | table rebuild | 対応 | 非対応 |
| PostgreSQL | postgresql | Verified | named constraint DDL + RLS | 対応 | 対応 |
| MySQL | mysql | Candidate | 未実装 | 未対応 | 非対応 |
| MariaDB | mysql | Candidate | 未実装 | 未対応 | 非対応 |
| SQL Server | mssql | Candidate | 未実装 | 未対応 | 非対応 |
| Oracle Database | oracle | Candidate | 未実装 | 未対応 | 非対応 |
| CockroachDB | cockroachdb | Candidate | 未実装 | 未対応 | 非対応 |

`Candidate`はロードマップ上の分類であり、接続許可や互換性保証ではない。candidate URLはengine生成・migration開始前に拒否する。

## Complexity boundary

- backend名ではなくfamilyを再利用単位にする。MySQL/MariaDBは、差が確認されるまで同じfamilyとして扱う。
- repositoryとAPIはDB非依存に保つ。DB差分は能力レジストリ、migration strategy、実DB fixtureへ閉じ込める。
- migration strategyは少数のclosed setとし、新DBごとにアプリ全体へbooleanや条件分岐を増やさない。
- identifier/index対象文字列とpayload/長文を区別する。可搬性のために本文を不必要に短いVARCHARへ変換しない。
- SQL方言のコンパイル成功だけでVerifiedへ昇格しない。

## Promotion gate

CandidateをVerifiedへ変更するには、対象versionを固定した実DBに対して次をすべて満たす。

1. fresh DBへのAlembic upgrade head
2. 対応対象revisionのupgrade/downgrade roundtrip
3. primary key、複合foreign key、unique、check、index、cascade/restrictの実制約検証
4. Documentと主要tenant従属データのCRUD roundtrip
5. transaction rollback、connection pool再利用、backup/restoreの代表演習
6. optional driver、CI、installation/configuration文書の同期

共有schema SaaSへの昇格は別判定とし、DB側tenant guard、contextなしdeny、tenant A/B越境、pool context残留のnegative matrixを追加で必須とする。single-tenant対応からSaaS対応を推論しない。

## Current next step

次の優先候補はMySQL/MariaDB familyである。先に主キー・外部キー・unique/indexへ使うidentifierをbounded型へ移行し、SQLite/PostgreSQLの互換性を確認する。その後にMySQL/MariaDBのmigration strategyと実DBmatrixを実装する。需要が変わった場合、同じpromotion gateを使ってSQL Server、Oracle、CockroachDBを先行させてもよい。
