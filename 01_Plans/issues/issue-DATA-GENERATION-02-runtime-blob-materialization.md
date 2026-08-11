# Issue: DATA-GENERATION-02 revision blobの物理保存とDocument runtime移行を完成する

- Type: Bug / Architecture / Data
- Status: In Progress
- Source Issue: DATA-GENERATION-01
- Priority: P1
- Owner: Maintainer
- Scope: `content_blobs`, generation codec/repository, Document Content Store/API, migration/rollback, retention GC
- Related ADR/Spec: `ADR-0070`, `ADR-0066`, `02_Architecture/database_portability.md`, `01_Plans/issues/issue-DATA-GENERATION-01-content-generation-policy.md`
- Expected verification level: `integration`

## 三要素整合（ADR-0067）

- **業務設計（Business）**: 利用者が保存したKJキャンバスを世代から確実に復元でき、同時編集時に既存ETagの競合保護を失わないことが必要である。
- **データ設計（Data）**: `canvas_revisions`はdigestだけを参照しているが、現行`content_blobs`には本文bytes列がなく、`storage_backend=database`かつ`locator=NULL`のrowから内容を復元できない。現在の本文正本は引き続き`documents.payload_json`である。
- **機能設計（Function）**: codecとDAG/GC repositoryは存在する一方、Document GET/PUTはrevision/blobを読み書きせず、世代作成reason、head名、初回head作成、ETagとhead versionの関係も公開契約になっていない。

## 課題

- `content_blobs`はdigest、representation、base digest、byte数、backend、locatorを保存するが、database backendの`stored_bytes`を保持しない。この状態ではcodec出力を永続化できず、digest metadataだけがreadyになり得る。
- `PUT /docs/{doc_id}`は`documents.payload_json`だけを置換する。revision DAGはruntime hot pathの正本ではなく、schema/repository/benchmarkだけが独立して完成している。
- `DATA-GENERATION-01`のACは設計・schema・codec・GCの完成を示すが、Document runtime移行を受入条件に含めていなかった。ADRの「標準runtimeはgzip full＋DB metadata」という結論を実運用済みと解釈してはならない。
- `content_object_references`も暫定tableとして残り、本文正本、revision blob、旧external metadataの三境界を移行計画なしに並存させている。

## 対応方針

### Phase 1: 物理blob境界（判断不要・本Issueで実装）

- `content_blobs`へportable binary LOB列を追加する。database backendのready rowは本文必須、NAS/S3/Git rowは本文禁止かつlocator必須とする。
- migration前から存在する復元不能な`database + ready` metadataは本文を捏造せず`failed`へ移し、再materialize対象としてfail closedにする。
- codec出力を冪等保存し、同一tenant+digestの内容／metadata不一致を拒否するrepositoryと、delta baseをtenant内で辿ってdigest・sizeを検証して復元するrepositoryを追加する。
- 全Verified DB promotion contractで1 MiB超の圧縮blob roundtripを検証し、binary型をDB別runtime分岐なしで扱う。

### Phase 2: Document runtime移行（契約決定後）

- PUTを一transaction内でDocument互換projection、blob、revision、parent、headへ反映する。途中失敗時は全てrollbackする。
- autosave/manual save/import/AI proposal等のreasonを、既存PUTから暗黙推測せずAPIまたはserver-owned operation contextとして定義する。
- `If-Match`の本文digest互換、revision head CAS、初回作成、同一本文再保存、branch/merge、GETのfallback順序を決定する。
- rollout中は`documents.payload_json`を互換read projectionとして維持できるが、同期dual writeの不一致検出・修復・切戻し条件を必須とする。revisionから検証なしに旧本文を上書きしない。
- `content_object_references`は移行対象の有無を計測し、`content_blobs`へ変換するmigrationまたは未使用確認後の撤去を別checkpointで決定する。

## 受入条件

- [x] database backendのready blobは実本文なしに作成できず、external backendはinline本文を保持できない。
- [x] canonical JSONをencode→DB保存→DB読込→delta chain復元し、byte sizeとSHA-256改ざん検出が成功する。
- [x] SQLite、PostgreSQL、MySQL、MariaDB、SQL Server、CockroachDB、Oracleでbinary LOB migrationと1 MiB超roundtripが成功する。
- [x] 既存の復元不能ready metadataはupgrade時にfailedとなり、本文があるように見せない。
- [ ] Document PUTごとに定義済みreasonのrevisionがtransactionalに作成され、head CASとIf-Matchの競合意味が一意になる。
- [ ] Document GETは正本revisionからdigest検証後に復元し、互換projectionとの不一致を黙って許容しない。
- [ ] rollout、切戻し、backfill、旧`content_object_references`の扱いが運用手順に定義される。

## 停止基準

- Phase 1は既存の復元不能状態を閉じる加算変更として進める。
- Phase 2は保存reason、既定head、ETag互換、同一本文再保存の4点が決まるまでDocument APIへ配線しない。暫定値でrevisionを量産したり、旧本文と新正本を成功応答後に非同期dual writeしたりしない。

## 検証計画

- migration upgrade/downgrade、legacy ready rowのfailed化、backend/payload/locator shape制約をSQLiteと全server DBで確認する。
- repository unit/integrationでfull、delta、missing base、cycle、tampered bytes、digest衝突metadata、tenant越境を検証する。
- Phase 2ではDocument APIのcreate/update/no-op/競合/rollback/import/AI proposal matrixと、旧schemaからのrolling migration rehearsalを追加する。

## Phase 1完了記録（2026-08-11）

- `content_blobs.payload_bytes`をportable binary LOBとして追加した。SQLite/PostgreSQL/CockroachDBはBLOB/BYTEA、MySQL/MariaDBはLONGBLOB、SQL ServerはVARBINARY(MAX)、OracleはBLOBへ同じORM型から展開する。
- database ready rowはinline bytes必須、NAS/S3/Git rowはserver-managed locator必須かつinline bytes禁止とした。旧database ready metadataはupgrade時に`failed`へ遷移し、存在しない本文を捏造しない。
- codec出力の冪等保存とtenant-scoped復元repositoryを追加した。保存前・読込後のdigest/byte size検証、delta base再帰復元、depth上限、cycle、missing/tampered payload、同一digest metadata衝突をfail closedにする。
- 共通DB promotion contractへgzip後も1 MiB超となるdeterministic payloadの保存・復元を追加した。実測はSQLite 1件、PostgreSQL 16 RLS suite 4件、MySQL 8.4/MariaDB 11.4 2件、SQL Server 2022 1件、CockroachDB 26.2 1件、Oracle Free 23.26 1件がpassした。
- Phase 2のDocument API接続は未着手であり、本IssueはIn Progressを維持する。
