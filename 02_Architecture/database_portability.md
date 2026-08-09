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
- identifier/index対象文字列、検索・表示用のbounded text、本文・bundle等のcontent objectを区別する。可搬性のために本文を不必要に短いVARCHARへ変換しない。
- SQL方言のコンパイル成功だけでVerifiedへ昇格しない。

## Data shape and content storage boundary

DB可搬性を理由に、現行の全`TEXT`列へ一律の桁数を設定しない。各列は次の3種類へ棚卸ししてから物理型を決める。

| 種類 | 例 | 方針 |
| --- | --- | --- |
| Identifier / key | tenant ID、document ID、principal ID、外部subject | ID生成規則・外部プロトコル・複合indexのbyte上限から意味別の最大長を定義し、bounded portable型にする |
| Bounded descriptive text | 表示名、email、URI、状態値 | 入力契約と業務上限を先に定義し、検索・索引要件に応じた型にする |
| Content object | `documents.payload_json`、inquiry bundle、判断ログpayload | 内容を切り詰めない。サイズ上限はDoS対策・運用容量として別途定義し、DB列長と混同しない |

Content objectの保存先はrepositoryから直接選ばない。将来の`ContentStore` portを介し、少なくとも次の実装候補を同じ契約で扱う。

- `database`: 現行互換の既定。本文をDB transaction内に保持する。
- `object`: S3互換object storageまたは管理対象file service。DBにはtenant、object key、content type、byte size、digest、schema version、作成・更新時刻等の参照メタデータを保持する。
- `hybrid`は独立した第三の永続方式にせず、size・tenant policy等により上記実装へ委譲するrouterとしてのみ検討する。

外部保存へ切り替える場合もDB metadataを認可・整合性の正本とし、object keyを利用者入力から直接組み立てない。tenant context欠落時はfail closed、読取時はdigestとschema versionを検証し、DB更新とobject操作の不一致を補償できる状態遷移・回収処理を必須とする。署名URL、暗号化、retention、backup/restore、orphan回収、SafeMode付きexportは実装前のpromotion gateで検証する。

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

次の作業はDB製品の昇格より先にdata-shape inventoryを行う。識別子は意味別の生成・受入規則を確定し、content objectは保存先非依存のport、参照metadata、障害時状態遷移を設計する。その結果に基づいてbounded identifier migrationを行い、その後にMySQL/MariaDBのmigration strategyと実DBmatrixへ進む。需要が変わった場合、同じpromotion gateを使ってSQL Server、Oracle、CockroachDBを先行させてもよい。
