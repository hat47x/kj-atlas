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
- [ ] AC-4: revision DAG、content object参照、head更新のDB schemaとmigrationが実装される。
- [ ] AC-5: canonical JSON、full snapshot／delta選択、最大chain depth、復元検証が代表データでbenchmarkされる。
- [ ] AC-6: retention pin、ephemeral GC、governed保持、tenant-scoped orphan回収が実装される。
- [ ] AC-7: AI run metadataの最小契約、SafeMode、redaction、保持期間が実装される。
- [ ] AC-8: optional Git adapterを採否判断し、採用時はbare repo、hook禁止、tenant分離、GC、backup/restoreを検証する。

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
