# Issue: DATA-GENERATION-01 KJキャンバス世代管理と保持ポリシー

- Type: Architecture / Data
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: User request 2026-08-09
- Priority: P2
- Scope: generation metadata, Content Store, persistence migration, AI provenance, optional Git adapter
- Related ADR/Spec: `ADR-0070`, `ADR-0057`, `ADR-0066`, `02_Architecture/database_portability.md`
- Expected verification level: contract / integration / storage benchmark

## 課題

- KJキャンバスの長期編集、分岐、人間・AI協働を追跡しつつ、full snapshot複製と全操作event sourcingの両極端を避ける。
- schema version、ETag、探究snapshot、判断log、編集revisionを混同しない。
- 全世代へactor、AI provider、model、prompt等を複製せず、説明責任が必要な節目だけに適切なmetadataを付ける。
- Gitのdelta圧縮と交換性を評価しつつ、tenant認可・削除・RDB transactionをGit固有実装へ拘束しない。

## 受入条件

- [x] AC-1: ephemeral／checkpoint／governedの3 tierとreason分類が定義される。
- [x] AC-2: AI proposalとhuman acceptanceが別revisionとして関連付けられ、AIがhuman reviewへ昇格できない。
- [x] AC-3: ephemeral revisionがactor／AI run metadataを持たない契約テストがある。
- [x] AC-4: revision DAG、content object参照、head更新のDB schemaとmigrationが実装される。
- [ ] AC-5: canonical JSON、full snapshot／delta選択、最大chain depth、復元検証が代表データでbenchmarkされる。
- [ ] AC-6: retention pin、ephemeral GC、governed保持、tenant-scoped orphan回収が実装される。
- [ ] AC-7: AI run metadataの最小契約、SafeMode、redaction、保持期間が実装される。
- [ ] AC-8: optional Git adapterを採否判断し、採用時はbare repo、hook禁止、tenant分離、GC、backup/restoreを検証する。
- [x] AC-9: revisionと物理blobの責務が分離され、object storage作業がrevision schema確定前に先行しない。

## 検証計画

- reasonからtierへの決定論的分類と不正metadataのfail-closed unit test。
- branch／merge／AI proposal／human acceptanceを含むDAG constraint test。
- 代表的な小・中・大キャンバスでfull JSON、圧縮full snapshot、delta chain、Git packを比較する。
- SafeMode付きshare/exportが元revisionを書き換えず、派生artifactだけを生成することを確認する。

## Phase 1 checkpoint 2026-08-09

- `generation_policy.py`へ3 tier、11 reason、4 origin、revision metadata、初期retention guardrailを定義した。
- autosaveはminimal metadata、AI proposalは別AI run参照、人間採用はsource proposal参照、人手reviewはopaque actor必須としてfail closedにした。
- 初期値はephemeral 50件／7日、delta chain 32、delta比率0.7だが、物理保存へ適用する前に代表データbenchmarkで確定する。
- Gitは標準runtime正本にせず、optional archive／exchange adapter候補とした。ADR-0070はProposedであり、Git adapter実装は未着手。

## Storage interaction checkpoint 2026-08-09

- 現行object referenceは「1 content ID = 1 locator」、revision DAGは「複数revision = 共有digest blob」であり、そのまま並行実装すると参照・retention・orphan GCが二重化すると確認した。
- 論理`canvas_revisions`と物理`content_blobs`へ責務を分離する方針へ修正した。database／NAS／S3／Gitはblob backend候補であり、revision正本の代替にはしない。
- NAS/S3 adapterは実験的実装として保持するが、runtime設定、coordinator、domain FKの優先度を下げて凍結する。大容量、複数instance共有、DB inline非対応等の実需が現れるまで外部storageは必須化しない。
- 合成300カード・100世代・5カード/世代更新の一次計測はraw 12,781,223 bytes、gzip full 476,633 bytes、gzip delta 41,446 bytes（初期full別）、Git aggressive GC後112,612 bytesだった。実データfixtureと復元時間を含まないため採用判定は保留する。
- 次はrevision／blob schema、branch headのcompare-and-swap、full／delta復元契約を先行する。既存`content_object_references`は最終schemaではなく、互換migrationまたは撤去候補として扱う。

## Revision DAG schema checkpoint 2026-08-09

- `content_blobs`を`tenant + SHA-256 digest`の物理identity、`canvas_revisions`を論理世代、`canvas_revision_parents`を順序付きDAG edge、`canvas_revision_heads`をdocument内branch headとして分離した。
- full JSON／gzip full／gzip deltaを区別し、deltaだけがbase digestと正のdepthを持つDB制約を追加した。既存Document本文は移動・backfillしていない。
- revision、blob、source revision、parent、head、Documentをtenant複合FKで接続し、PostgreSQLでは全4テーブルへFORCE RLSを追加した。
- headは`head_version`一致時だけ更新するcompare-and-swap repositoryを追加した。stale writerは`RevisionHeadConflict`で停止し、別tenantの同名document／headへ影響しない。
- ORM／lineage／分類／policy／CASの17件と、fresh SQLite upgrade／downgrade 2件を通過した。AC-4を完了し、次はAC-5のcanonical化・delta生成・復元benchmarkへ進む。

## Canonical full/delta codec checkpoint 2026-08-10

- JSONをUTF-8、key順、空白なし、NaN禁止でcanonical化し、そのSHA-256をrevisionのcontent identityとした。
- deterministic gzip fullと、base/currentの共通prefix・suffixに基づくgzip deltaを実装した。deltaがfullの設定比率以下で、chain depth上限未満の場合だけdeltaを採用する。
- 復元時はbase digest、復元後byte size、SHA-256をすべて照合し、圧縮破損、base不一致、改ざん、未知representationをfail closedにした。
- codec／policy／head CASの15件とRuffを通過した。合成fixtureでの可逆性は確認したが、実キャンバスfixtureの容量・復元時間benchmarkが残るためAC-5は未完了を維持する。

## Reproducible 300-card benchmark 2026-08-10

- `scripts/benchmark_generation_codec.py`を追加し、300カード、100世代、各世代5カード更新を再現可能にした。
- raw合計11,273,323 bytesに対しadaptive codecは447,181 bytes、encode約720ms、100世代restore合計約41msだった。
- full 100件、delta 0件となった。canonical JSON全体をgzipするだけで反復構造が十分圧縮され、このfixtureではdelta envelopeが比率閾値を満たさなかった。
- 当面はgzip fullを既定、deltaは有効性が実測された場合だけ使う。実利用由来fixture、branch／merge、1MiB級データ、Git pack同条件比較が残るためAC-5は未完了を維持する。
