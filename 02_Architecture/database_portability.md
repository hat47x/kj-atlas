# Database portability

DB対応の正本は本書とする。SQLAlchemyがdialectを提供していることは、kj-atlasがそのDBを正式対応していることを意味しない。

## Support matrix

| Backend | Family | 状態 | Migration strategy | Single-tenant | Shared-schema SaaS |
| --- | --- | --- | --- | --- | --- |
| SQLite | sqlite | Verified | table rebuild | 対応 | 非対応 |
| PostgreSQL | postgresql | Verified | named constraint DDL + RLS | 対応 | 対応 |
| MySQL 8.4 | mysql | Verified | named constraint DDL | 対応 | 非対応 |
| MariaDB 11.4 | mysql | Verified | named constraint DDL | 対応 | 非対応 |
| SQL Server 2022 | mssql | Verified | named constraint DDL | 対応 | 非対応 |
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

現行ORMの永続文字列列は列単位で`persistence_shapes.py`へ分類し、新しい文字列列が未分類ならテストで停止する。内部ID 128、外部発行ID 512、URI 2048、email 320、表示名 255、timestamp 40、closed-set state 32文字を基準とし、OIDC複合lookupはissuer 512＋audience 255をAPI受入上限とする。content object以外は同カタログから`VARCHAR(n)`へ変換し、SQLite/PostgreSQL/MySQL/MariaDBのmodelとmigrationで重複定義しない。

content objectはSQLite/PostgreSQLで`TEXT`、MySQL/MariaDBで`LONGTEXT`、SQL Serverで`VARCHAR(MAX)`へ写像する。MySQL 8.4、MariaDB 11.4、SQL Server 2022の実DBで1 MiB超のDocument roundtripを確認済みであり、これらのDBを理由にNAS/S3を必須化しない。

MySQL familyの昇格matrixはfresh、upgrade/downgrade、tenant複合FK、case-insensitive IdP unique、1 MiB超LOB、logical backup/restoreを含む。2026-08-10のMySQL 8.4とMariaDB 11.4で、復元先の2文書と最大1,048,587文字のpayloadを照合した。このmatrixはDB family単位のparameterized testとし、将来candidateの検証契約に再利用する。

SQL Server 2022も同じpromotion gateでfresh、guarded downgrade/re-upgrade、tenant複合FK、CI collation上のIdP unique、transaction rollbackとpool再利用、1 MiB超`VARCHAR(MAX)`、native backup/restoreを検証する。SQLの差分は`NO ACTION`、check expression、LOB型のportable DDL変換に閉じ込め、repository/APIにSQL Server分岐を持ち込まない。

外部IdPのsubject、audience、external tenant reference等は外部仕様が任意長を許し得るが、本製品が無制限入力を索引へ格納することまでは意味しない。超過時のhash代替は同一性・監査表示を損なうため暗黙には行わず、受入上限をAPIで明示して拒否する。内部生成IDと外部発行IDを同じ型aliasへ統合しない。

Content objectの保存先はrepositoryから直接選ばない。将来の`ContentStore` portを介し、少なくとも次の実装候補を同じ契約で扱う。

- `database`: 現行互換の既定。本文をDB transaction内に保持する。
- `nas`: NASまたは管理対象file service。DBにはserver-managed相対pathを保持し、共有rootや資格情報をlocatorへ含めない。
- `s3`: S3互換object storage。DBにはbucket設定と分離したserver-managed object keyを保持し、署名URLや資格情報を永続化しない。
- `hybrid`は独立した第三の永続方式にせず、size・tenant policy等により上記実装へ委譲するrouterとしてのみ検討する。

DB能力レジストリはinline content対応を`verified`／`candidate`／`unsupported`で表す。保存方式は次の順で決定する。

1. runtime DB自体がVerifiedでなければ、外部保存を選んでもDB backendは起動許可しない。metadata、constraint、transactionの検証は依然必要である。
2. `database`はinline content能力がVerifiedの場合だけ選択できる。
3. inline contentがUnsupportedのDBを将来Verifiedへ昇格する場合、`nas`または`s3`を必須構成とする。
4. `nas`／`s3`は保存adapter、資格情報、暗号化、health check、backup/restore、障害演習が完了するまで設定値として公開しない。
5. 自動fallbackで保存先を変えない。障害時にDBからNAS/S3へ暗黙退避すると正本・retention・監査境界が変わるため、fail closedとする。

NAS／S3のlocatorは`tenant_id`と`content_id`それぞれのSHA-256から決定的に生成し、生の識別子をpath/keyへ露出させない。locatorをAPI入力として受理せず、DB値が改変されても絶対path、`..`、管理root外symlinkを拒否する。NAS書込は同一directoryの一時fileへwrite・flush・fsyncした後にatomic replaceし、途中fileを公開しない。S3 adapterはbucketをruntime設定として保持し、DB locatorにはobject keyだけを保存する。

読取時はNAS/S3から得たUTF-8 bytesについてbyte sizeとSHA-256をDB metadataと照合し、一致しなければ本文を返さない。S3 object metadataのdigestが存在する場合もDB digestと一致させる。削除は冪等に扱うが、object不在をDB metadata削除成功と自動解釈しない。DB状態遷移と監査確定は後続coordinatorが担当する。

S3実装は特定SDKをContent Storeへ直結せず、`put_object`／`get_object`／`delete_object`のclient portを介する。AWS S3、MinIO等のS3互換製品、テストdoubleの差をこのportのadapterへ閉じ込め、core packageへ必須cloud dependencyを追加しない。

Content Store上の編集世代は物理backendと分離し、`ADR-0070`で採択したcontent-addressed revision DAGで扱う。論理revisionは共有可能な`tenant + digest` blobを参照し、database／NAS／S3／Gitはその物理backend候補とする。Git commit／branchをDB metadata、tenant認可、human reviewの正本にしない。schema version、ETag、Inquiry round snapshot、merge decision log、編集revisionは別概念を維持する。

Content Storeの操作契約は一つの汎用CRUDへ統合せず、次の3 portに分離する。

| Port | 更新特性 | DB実装の責務 |
| --- | --- | --- |
| `VersionedDocumentContentStore` | version付きcreate/update、ETagによる楽観的競合制御 | tenant-scoped rowのload/save。ETag判定とcommitはapplication側 |
| `ReplaceableBundleContentStore` | journey単位の全置換と明示削除 | tenant-scoped rowのload/replace/delete。削除監査とcommitは同じapplication transaction |
| `AppendOnlyLogContentStore` | immutable appendとgroup/snapshot別列挙 | append/listのみ。update/deleteを契約へ持たせない |

各portはUTF-8 byte sizeとSHA-256 digestを持つ`ContentBlob`を受け渡す。現行DB実装ではinline本文から都度算出し、schema migrationを発生させない。外部保存へ昇格するときはdigest、byte size、schema version、storage stateをDB metadataへ永続化する。adapterはtransactionをcommitせず、認可対象の更新、監査証跡、content metadataをapplication側が一つの処理単位として確定できるようにする。

`content_object_references`は外部化検討時の暫定metadataであり、最終正本とはしない。revision DAG導入時に論理revisionと物理digest blobへ責務分離し、互換migrationまたは撤去を判断する。既存inline payloadは自動backfillせず、現在の3列を正本として維持する。

状態は`pending -> ready|failed`、`ready -> deleting|failed`、`failed -> pending|deleting`を許可する。`deleting`からの物理削除完了は行削除とcontent-free監査証跡で表し、`deleting -> ready`の復活は許さない。NAS/S3への書込成功後にDB確定が失敗したobject、またはDB参照がなくなったobjectはorphan候補とし、tenant・content ID prefixと保留期間を確認する回収処理以外から削除しない。

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

`DATA-GENERATION-01`でrevision／blob設計は確定したが、外部storageのruntime接続優先度は引き続き低く保つ。inline DB Content Storeを標準経路とし、次のcandidateはOracleとCockroachDBから需要・CI負荷・ライセンス条件で選ぶ。inline LOBがUnsupportedと実証されたDB、または容量・共有要件が実測された環境だけ、NAS/S3等を`content_blobs`の物理backendとして再評価する。
