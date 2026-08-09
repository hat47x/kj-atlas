# Issue: DB-PORTABILITY-01 DB能力レジストリと段階的な多DB対応

- Type: Architecture / Feature
- Status: In Progress
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
- [x] AC-2: MySQL/MariaDB、SQL Server、Oracle、CockroachDBがcandidateとして分類され、runtimeではfail-fastになる。
- [x] AC-3: DB URLエラーがcredentialやURL全体を反射しない。
- [x] AC-4: 全永続列がidentifier／bounded descriptive text／content objectへ棚卸しされ、identifierの意味別最大長と受入規則が定義される。
- [ ] AC-4a: identifier/index文字列が棚卸し結果に基づくbounded portable型へ移行され、SQLite/PostgreSQL回帰が通る。
- [ ] AC-4b: `ContentStore` port、DB実装、object参照metadata、digest検証、障害時状態遷移、orphan回収契約が設計される。object storageの実装・既定化は別issueで扱える。
- [ ] AC-5: MySQL/MariaDBでfresh migration、roundtrip、複合制約、upgrade/downgradeが実DBで通る。
- [ ] AC-6: 公開文書でMySQL/MariaDBをverifiedへ昇格し、driver optional dependencyとCIを追加する。
- [ ] AC-7: 将来candidateの追加が既存repository/APIへDB固有分岐を増やさず、同じ検証契約を再利用できる。
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

## Phase 1 checkpoint 2026-08-09

- `database_support.py`へverified/candidate、DB family、migration strategy、shared-schema SaaS可否を集約した。
- Settings、engine生成、Alembicが利用するURL正規化を同じverified判定へ接続した。未知DBとcandidateはdriver接続前に停止し、エラーへ接続URL・user・passwordを含めない。
- MySQL/MariaDBを同一familyとして登録し、SQL Server、Oracle、CockroachDBも将来候補として同じ昇格手順へ載せた。現行TEXT主キー・索引がMySQL系で成立しないため、未検証のまま接続だけ許可する対応は行っていない。
- SQLite/PostgreSQLだけを正式対応、共有schema SaaSはPostgreSQLだけとする既存境界を維持した。AC-4〜7は後続段階として残す。
- 検証はdatabase registry／Settings／trusted SaaS runtime近接72件、SQLite tenant-key migration 2件、変更対象Ruff、Active issue validator 60件を通過した。backend全体は791件pass・25件skip・10件deselectで、今回と無関係な既存`ProposalDecisionAuditResponse` field不整合1件だけが単独再実行でもfailした。docs-checkも既存`KJ_ATLAS_LLM_TASK_MODEL_MAP`のruntime registry未登録1件でfailしており、本issueでは別領域の修正を混在させない。
