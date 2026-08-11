# Issue: DATA-GENERATION-03 外部blob backendを需要起点で安全に昇格する

- Type: Architecture / Data / Operations
- Status: Draft
- Source Issue: DATA-GENERATION-02
- Priority: P3
- Owner: Maintainer
- Scope: `content_blobs`, generation repository, NAS/S3/Git adapter, migration, backup/restore, retention GC
- Related ADR/Spec: `ADR-0070`, `ADR-0066`, `02_Architecture/database_portability.md`
- Expected verification level: `integration`

## 三要素整合（ADR-0067）

- **業務設計（Business）**: DB容量、共有storage、archive交換などの実測需要が出た環境だけ外部backendを選べるようにし、通常構成へ不要な運用複雑性を持ち込まない。
- **データ設計（Data）**: revisionは`tenant + content_digest`だけを参照し、物理配置は`content_blobs.storage_backend/locator`へ閉じ込める。外部objectを別の論理正本やcontent ID体系にしない。
- **機能設計（Function）**: 現行Document hot pathは`database` blobだけを保存・復元する。schemaが許容する`nas/s3/git`をruntime対応済みと表示せず、adapterの能力検証後に個別昇格する。

## 課題

- `content_blobs`の制約とGC metadataは`nas/s3/git`を表現できるが、Document load/save repositoryはDB内payload専用であり、外部rowをheadから参照すると復元不能としてfail closedになる。
- 外部化にはatomic publish、read-after-write、locator秘匿、tenant越境防止、credential rotation、backup整合点、orphan回収、障害時切戻しが必要で、単純なpath保存だけでは正本要件を満たさない。
- Gitはarchive／交換候補であり、hot pathの物理backend候補と同列に自動昇格すると、commit／GC／lockingの運用負担が標準構成へ漏れる。

## 対応方針

- 当面の標準runtimeは`database`を維持し、外部backendを設定UIや一般運用手順へ露出しない。
- 容量、複数instance共有、archive交換のいずれかに具体的なSLOと実測値が出た時点で、NAS、S3互換、Git archiveを別々に評価する。
- adapter interfaceはcontent-addressedなput-if-absent、verified get、idempotent delete、health/capability reportに限定し、Document serviceへbackend別分岐を追加しない。
- migrationはDB blobを消す前に外部objectのdigest/sizeを再検証し、headから到達可能な全blobのcopy完了とrollback windowを記録する。locatorだけを先行commitしない。

## 受入条件

- [ ] 対象backendの採用需要、容量予測、可用性・復旧SLO、費用境界が記録される。
- [ ] tenant-scoped put/get/delete、digest改ざん、missing object、timeout、再送、credential失効を検証する共通contractが全て成功する。
- [ ] projection、revision、外部objectのatomicityまたは補償状態機械が定義され、成功応答後に復元不能なheadを作らない。
- [ ] backup/restore、key rotation、orphan GC、retention pin、legal hold、監査logのrunbookが完成する。
- [ ] database backendへの切戻しを含む段階移行rehearsalが成功する。
- [ ] 未昇格backendのrowを通常runtimeが新規作成できないことをtestする。

## 非目標

- 全backendを同時に実装しない。
- Firebase/DynamoDB等をRDB metadata正本の透過的代替として扱わない。
- Gitを共同編集の同期databaseまたはDocument PUTの既定保存先にしない。

## 停止基準

- 実測需要がない、整合したbackup点を作れない、または外部object公開後とDB commit間の失敗を安全に補償できない場合はDraftを維持する。
