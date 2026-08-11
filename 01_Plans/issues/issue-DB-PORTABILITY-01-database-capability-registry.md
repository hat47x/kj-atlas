# Issue: DB-PORTABILITY-01 DB能力レジストリと段階的な多DB対応

- Type: Architecture / Feature
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: User request 2026-08-09
- Priority: P2
- Scope: `03_Implement/backend/`, Alembic migration, database CI, configuration documentation
- Related ADR/Spec: `ADR-0066`, `ADR-0059`, `02_Architecture/database_portability.md`, `02_Architecture/runtime_parameter_registry.md`
- Expected verification level: integration / real database

## 課題

- SQLAlchemyが認識するdialectを、そのままkj-atlasの正式対応DBとは扱えない。
- 現行の無制限`TEXT`主キー・索引とSQLite/PostgreSQL専用migrationは、MySQL/MariaDB等で成立しない。
- DB追加ごとにruntime・migration・CIへ個別条件を散らすと、将来候補が増えるほど保守不能になる。

## 対応方針

- DB backendの対応状態、family、migration strategy、共有SaaS可否を単一レジストリへ集約する。
- 未検証candidateは資格情報を反射せず、engine生成・migration開始前に拒否する。
- 次段階でdata-shape inventoryを行い、identifier、bounded descriptive text、content objectを分離する。identifierの上限はDB製品都合ではなく、生成規則・外部契約・索引要件から決める。
- content objectはDB保存を既定互換としつつ、将来のobject storage実装を`ContentStore` portの背後へ追加できるよう、参照metadataと障害時状態遷移を先に設計する。
- SQL Server、Oracle、CockroachDBは同じ昇格手順を再利用し、需要に応じて順序を変更できるようにする。

## 受入条件

- [x] AC-1: SQLite/PostgreSQLのverified状態とmigration strategyが一か所で定義される。
- [x] AC-2: 未検証DBがcandidateとして分類され、runtimeではfail-fastになる。MySQL/MariaDB、SQL Server、CockroachDB、Oracleは個別昇格証跡を伴ってVerifiedへ移行した。
- [x] AC-3: DB URLエラーがcredentialやURL全体を反射しない。
- [x] AC-4: 全永続列がidentifier／bounded descriptive text／content objectへ棚卸しされ、identifierの意味別最大長と受入規則が定義される。
- [x] AC-4a: identifier/index文字列が棚卸し結果に基づくbounded portable型へ移行され、SQLite/PostgreSQL回帰が通る。
- [x] AC-4b: `ContentStore` portとinline DB実装が設計・接続される。外部object metadata／GCはDB対応の昇格条件から外し、`DATA-GENERATION-01`のrevision／blob設計後に再評価する。
- [x] AC-5: MySQL/MariaDBでfresh migration、roundtrip、複合制約、upgrade/downgradeが実DBで通る。
- [x] AC-6: 公開文書でMySQL/MariaDBをverifiedへ昇格し、driver optional dependencyとCIを追加する。
- [x] AC-7: 将来candidateの追加が既存repository/APIへDB固有分岐を増やさず、同じ検証契約を再利用できる。
- [x] AC-8: shared-schema SaaSはPostgreSQL限定を維持し、candidate追加で安全条件を緩和しない。

## 検証計画

- capability registryとURL validationのunit test。
- SQLite/PostgreSQLの既存migration・roundtrip回帰。
- candidate昇格時は一時的な実DB containerでfresh/upgrade/downgrade/constraint/CRUDを検証する。
- SafeMode、proposal-only、share/export/importには変更を加えない。

## Phase 2 design correction 2026-08-09

- `TEXT`主キーの解消を単なるMySQL互換化として扱わず、ID体系の見直しを先行させる。UUID/ULID等の内部生成ID、IdP subject、URI、利用者入力値を同じ上限へ押し込まない。
- `documents.payload_json`、`inquiry_bundles.payload_json`、`merge_decision_logs.payload_json`はcontent object候補であり、identifier migrationとは別トラックにした。本文をDB可搬性のために切り詰めない。
- 保存先は当面DBを維持する。将来S3互換storageまたはfile serviceへ移せるportを設計するが、DB/object間の原子的commitを仮定せず、pending／ready／deleting／failed等の状態遷移、再試行、digest検証、orphan回収を決めるまでruntime切替を公開しない。
- object本体を外部化しても、tenant scope、object key、byte size、digest、schema version等のmetadataはDBに保持し、一覧・認可・整合性の正本を分散させない。

## Phase 2 inventory checkpoint 2026-08-09

- ORMの全74 `TEXT`列を列単位で分類し、identifier 36、bounded descriptive text 35、content object 3とした。新しい`TEXT`列が未分類ならcoverage testで停止する。
- 内部ID 128、外部発行ID 512、URI 2048、email 320、表示名 255、timestamp 40、closed-set state 32文字をmigration候補として記録した。既存データ分布とAPI入力契約の照合前にはDB制約へ適用しない。
- content objectは`documents.payload_json`、`inquiry_bundles.payload_json`、`merge_decision_logs.payload_json`の3列だけであることを固定した。文字数上限を持たせず、byte-size policyと保存先設計を別課題として維持する。
- `tests/test_persistence_shapes.py` 3件と対象Ruffを通過した。AC-4aの物理migrationとAC-4bのContentStore設計は後続工程として分離した。

## Phase 2 Content Store checkpoint 2026-08-09

- 汎用CRUDを避け、Documentのversion付き保存、Inquiry bundleの全置換・削除、merge decision logの追記専用保存を3つのportへ分離した。
- 現行3つのinline `payload_json`列を利用するDB adapterを追加し、既存repositoryとPUT／GET／append／delete経路をadapterへ接続した。API response、ETag、削除監査、commit位置は変更していない。
- `ContentBlob`でUTF-8 byte sizeとSHA-256 digestを共通化した。現行DBでは本文から算出し、外部保存時にmetadata列へ永続化するための契約境界とした。
- `journey_id`の既存API上限256文字を検出し、棚卸し候補128文字を256へ訂正した。物理型の候補値より既存入力契約を優先する回帰テストを追加した。
- adapter／分類／repository／API roundtrip／tenant分離の対象18件とRuffを通過した。外部参照metadata、状態遷移、移行・rollback、orphan回収は未実装のためAC-4bは未完了を維持する。

## Phase 2 external reference checkpoint 2026-08-09

- 保存方式を`database`／`nas`／`s3`へ分離した。NAS locatorは管理対象rootからの相対path、S3 locatorはbucket設定と分離したobject keyとし、資格情報や署名URLをDBへ保存しない。
- DB能力レジストリへinline contentの`verified`／`candidate`／`unsupported`分類を追加した。inline未対応DBは将来`nas`または`s3`を必須化できるが、外部保存を理由に未検証DB自体をruntime許可しない。
- `content_object_references` metadata tableとSQLite/PostgreSQL migrationを追加した。tenant、backend、locator、state、byte size、SHA-256 digest、schema version、時刻を保持し、backend／locator整合性をDB制約でも強制する。PostgreSQLではtenant RLSを有効化する。
- `pending`／`ready`／`deleting`／`failed`のfail-closed状態遷移を実装した。既存inline本文のbackfillやdomain row FKは行わず、移行・rollback設計まで正本を切り替えない。
- fresh SQLite migration、downgrade、制約、状態遷移、DB能力、分類網羅の30件とRuffを通過した。NAS/S3 adapter、domain row参照、orphan回収実装が残るためAC-4bは未完了を維持する。

## Phase 2 NAS/S3 adapter checkpoint 2026-08-09

- NAS adapterは管理root内の決定的locatorへ同一directory一時fileを書き、flush・fsync後にatomic replaceする。絶対path、`..`、root外解決を拒否し、中断した`.pending` fileを公開しない。
- S3 adapterはSDK非依存client portを利用し、bucketをruntime側、object keyをDB locator側へ分離した。AWS SDK等はまだoptional dependencyへ追加していない。
- locatorはtenant ID／content IDのSHA-256から生成し、生の識別子をpath/keyへ含めない。NAS/S3とも読取時にDB metadataのbyte sizeとdigestを検証し、不一致はfail closedとした。
- 外部adapter、digest、tenant別locator、path escape、tamper検出、冪等削除、inline DB adapter、状態機械の対象19件とRuffを通過した。metadata／object間coordinator、domain row FK、runtime設定、実S3 client、orphan回収が残るため、保存先切替は公開しない。

## Priority correction after generation DAG review 2026-08-09

- NAS/S3を独立したcontent正本として先行すると、content-addressed revision DAGのdigest blob、参照数、retention、orphan GCと二重管理になるため、外部storage coordinator／runtime設定／domain FKを本issueの昇格gateから外した。
- inline DB Content StoreをDB portabilityの標準経路として維持する。NAS/S3 adapterは削除せず実験的候補として凍結し、必要性が確認された場合に`DATA-GENERATION-01`の物理blob backendとして再開する。
- MySQL/MariaDB等の候補DBはinline LOB実地検証を先に行い、未対応と判明した場合だけ外部blob backendを必須化する。未検証段階で「外部保存せざるを得ない」と仮定しない。

## Generation DAG dependency resolved 2026-08-10

- `DATA-GENERATION-01`は全受入条件を完了し、`ADR-0070`をAcceptedとした。`content_blobs`、revision DAG、adaptive codec、保持pin、監査付きGCが物理backend共通の境界として確定した。
- 1.15 MiB級20世代ではgzip fullが約11.79 MB、Git packが約0.69 MBだった一方、Git write＋GCは約12.95秒を要した。Gitはarchive／交換候補、database inlineはruntime標準という優先順位を維持する。
- NAS／S3の再開条件は「候補DBのinline LOB不成立」または「容量・複数instance共有要件の実測」とし、先行してruntime切替を公開しない。

## Phase 1 checkpoint 2026-08-09

- `database_support.py`へverified/candidate、DB family、migration strategy、shared-schema SaaS可否を集約した。
- Settings、engine生成、Alembicが利用するURL正規化を同じverified判定へ接続した。未知DBとcandidateはdriver接続前に停止し、エラーへ接続URL・user・passwordを含めない。
- MySQL/MariaDBを同一familyとして登録し、SQL Server、Oracle、CockroachDBも将来候補として同じ昇格手順へ載せた。現行TEXT主キー・索引がMySQL系で成立しないため、未検証のまま接続だけ許可する対応は行っていない。
- SQLite/PostgreSQLだけを正式対応、共有schema SaaSはPostgreSQLだけとする既存境界を維持した。AC-4〜7は後続段階として残す。
- 検証はdatabase registry／Settings／trusted SaaS runtime近接72件、SQLite tenant-key migration 2件、変更対象Ruff、Active issue validator 60件を通過した。backend全体は791件pass・25件skip・10件deselectで、今回と無関係な既存`ProposalDecisionAuditResponse` field不整合1件だけが単独再実行でもfailした。docs-checkも既存`KJ_ATLAS_LLM_TASK_MODEL_MAP`のruntime registry未登録1件でfailしており、本issueでは別領域の修正を混在させない。

## MySQL family promotion checkpoint 2026-08-10

- 文字列の意味別上限を`persistence_shapes.py`からORMとmigrationへ適用し、content objectだけは無制限のままMySQL/MariaDBで`LONGTEXT`へ写像した。OIDCのissuer 512文字・audience 255文字はAPI受入上限と物理制約を一致させた。
- MySQL 8.4とMariaDB 11.4の同一parameterized matrixでfresh migration、1 MiB超inline content、tenant複合FK、大文字小文字非依存IdP unique、duplicate docId付きguarded downgrade、解消後のdowngrade/re-upgradeを検証した。
- 両DBでlogical dumpを別databaseへ復元し、2文書と最大1,048,587文字のpayloadが一致することを確認した。PostgreSQL 16でもfresh、0020 downgrade/re-upgrade、RLS policy保存、既存PostgreSQL suite 18件を通過した。
- capability registry、optional PyMySQL dependency、GitHub Actions services、README、公開対応表を同時に更新した。repository/APIにMySQL専用経路を作らず、差分を物理型・migration strategy・共通検証fixtureに閉じ込めた。

## Declaration synchronization checkpoint 2026-08-10

- 全当初candidate昇格後、能力レジストリへoptional dependencyと実DBtest markerを集約した。Verified一覧を同レジストリから生成し、runtime error文の手書きbackend列挙を撤去した。
- `pyproject.toml`のdriver extra／marker、実test marker、GitHub Actionsのextra install／pytest command、公開support matrixを横断する契約testを追加した。次のDB追加で宣言更新が一つでも欠ければSQLite unit test段階で停止する。
- 公開表はDatabase名、SQLAlchemy backend、再利用familyを分離し、MariaDBのbackend=`mariadb`とfamily=`mysql`を曖昧にしない形へ改訂した。
- SQLite基準のbackend全体回帰は830件pass、3件skip、49件deselect。失敗3件は並行中のAI response model、外部LLM接続、公開LLM設定文書に限定され、DB宣言契約11件は通過した。

## Full verified database audit 2026-08-10

- 現行commit上で固定versionの全Verified DBを再起動し、SQLite基準に加えて実DBmatrixを再実行した。
- PostgreSQL 16はfresh migrationとRLS suiteを含め19件pass・1件skip、MySQL 8.4/MariaDB 11.4はpromotion matrix 2件pass、SQL Server 2022は1件pass、CockroachDB 26.2.3は1件passとなった。
- Oracle AI Database Free 23.26.2は同じ現行系列でORM CLOB roundtripとData Pump restoreを含む1件pass（175.95秒）。これによりSQLite以外の全backendでfresh、constraint、LOB、transaction、migration往復、backup/restoreのprovider別契約が現行codeに対して成立することを再確認した。

## Driver URL hardening checkpoint 2026-08-10

- backend名だけのVerified判定では、`mysql://`、`mssql://`、`oracle://`等がoptional dependencyに含まれないSQLAlchemy既定driverを選び、engine生成時まで失敗を遅延させる不足があった。
- 能力レジストリへ検証済み同期driverと受理drivernameを追加した。driver省略URLと既存の`sqlite+aiosqlite`／`postgresql+asyncpg`は検証済み同期driverへ正規化し、明示された未検証driverは資格情報を露出せずfail-fastにした。
- 全backendのdriver契約整合性、URL構成要素の保存、未検証driver拒否をparameterized testで固定し、関連29件と変更対象Ruffを通過した。

## Verification target synchronization checkpoint 2026-08-11

- 能力レジストリと宣言契約はbackend名を照合していたが、実DBの検証対象名・versionとCI imageは対象外だった。このため、OracleのCI／昇格証跡が`Free 23.26.2`である一方、対応表と運用見出しが抽象的な`26ai`表記でも検査を通過していた。
- 各backendへ`verification_target`と`ci_image`を追加し、公開support matrixのDatabase列とCI workflowのimage tagを同じレジストリから静的照合する契約へ拡張した。SQLiteは標準library利用のためCI imageを持たず、外部Verified DBは全てimageを必須とする。
- 正本の対象をPostgreSQL 16、MySQL 8.4、MariaDB 11.4、SQL Server 2022、CockroachDB 26.2.3、Oracle AI Database Free 23.26.2へ揃え、README・運用文書・runtime registryの重複version列挙を正本参照または同じ表記へ修正した。関連32件と変更対象Ruffを通過した。

## Engine creation and installation checkpoint 2026-08-11

- 通常APIは正規化済みURLでengineを生成していた一方、Alembicとidentity backfill CLIはSQLAlchemyを直接呼び、Verified URL／driver境界と未導入extraの案内が分散していた。
- `create_verified_database_engine()`へengine生成を集約し、通常API、Alembic online migration、backfill CLIを接続した。未導入driver／dialectは接続URLや資格情報を表示せず、能力レジストリのoptional dependency名を使った導入方法を返す。
- 公開installationへ全Verified backendのpip extraと検証済み同期driverを追加し、能力レジストリとの静的契約testで記載漏れを防止した。diagnosticsにも同エラーからの復旧導線を追加した。

## MySQL transaction gate checkpoint 2026-08-11

- promotion gateはtransaction rollbackとconnection pool再利用を必須としていたが、MySQL/MariaDB共通matrixにはconstraint、LOB、migration往復、backup/restoreだけが実装され、transaction項目が欠落していた。
- pool size 1の同一engineで未commit行をrollbackし、connection返却後にpoolから再取得した接続で行が存在しないことを検証する処理を共通matrixへ追加した。MySQLとMariaDBで同じテストを実行し、DB family共通化の境界を維持する。
- 固定imageのMySQL 8.4.11とMariaDB 11.4.12で、fresh migration、rollback／pool再利用、constraint、LOB、migration往復、logical backup／別database restoreを含む各1件がpassした。一時containerは検証後に削除した。

## PostgreSQL recovery CI checkpoint 2026-08-11

- PostgreSQLの`pg_dump`／`pg_restore`隔離復元は`DATA-MAINT-02`の手動演習証跡に留まり、現行`postgres` marker／CIから退行を検出できなかった。
- CI service containerをtestへ明示注入し、1 MiB超の固有Documentをsourceへ作成、custom-format dump、別databaseへの`pg_restore --exit-on-error --no-owner`、Document version／本文長／Alembic revision照合、source rowと一時databaseのcleanupまでを自動化した。
- PostgreSQL 16.14の一時containerでfresh migrationと新しいrestore test 1件がpassし、test内cleanup後にcontainerも削除した。
- MySQLとPostgreSQLで復旧証跡の自動matrix追随漏れが続いたため、各Verified backendの`recovery_test`を能力レジストリへ追加した。宣言先file、restore処理、外部DB markerが欠ける場合は通常の宣言契約testで停止する。
