# Case 003 Launch Packet — Ordinary analysis

- Status: Frozen before first valid Case 001 arm run
- Evidence bundle: `case-003-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`

## Context boundary

このtaskでは、与えられたsanitized evidence bundleだけをKJ Atlasについての共通証拠として使用する。

同じrepositoryの別ファイル、PR/issue discussion、他ケースの成果、評価メモ、外部Web資料を追加で読まない。資料外の一般知識を使う場合は、bundle由来の主張と明確に分ける。追加資料が必要なら、そのrunだけへ追加せず `Candidate source request` として挙げる。

## Fixed question

KJ Atlasはoffline/local/self-hostによるデータ統制と、共同分析・共有・組織導入に必要な同期/collaborationをどの境界で両立するべきか。local-firstを中核価値、配備オプション、安全境界、または特定利用ケース向け要件のどれとして扱うべきか。

## Required output

次を必ず含める。

1. KJ Atlasにとってのlocal/offline/self-host/data-controlを分解し、同義語として扱わない境界案。
2. 個人・小チーム・組織・相互に信頼しないSaaS tenant等、利用形態ごとの必要条件と不要条件。
3. 現行server-authoritative / snapshot / tenant / ownership / sharing設計が既に解いている問題。
4. 現行設計では満たせない可能性が高いoffline・network partition・P2P・E2EE・portable ownership等の要求。
5. CRDT/local-first等へ進むために、先に観測されるべき実利用トリガー。
6. self-host/localがKJ Atlasのswitch reasonではなく単なるdeployment optionで十分かもしれない最強の反証。
7. 逆にcloud/SaaS中心では失う可能性がある中核価値または利用ケース。
8. collaborationを増やすことで、保留・違和感・少数意見・provenance・SafeModeが失われる失敗モード。
9. 次に実施すべき検証/issue。技術方式の採択より、利用要求・運用摩擦・データ境界の観測を優先する。
10. 主要主張ごとのsource path / stable identifier / evidence time、判断保留、追加証拠。

断定できない箇所は推測で埋めず保留する。local-first、cloud/SaaS、自前運用のどれかを価値語だけで優先しない。

## Analysis mode

通常の分析として進める。

- KJ法の手順を追加方法として使用しない。
- KJ Atlasキャンバスを分析用の外部表象として使用しない。
- cultural-substrate-weavingを使用しない。
- 必要なメモ、見出し、比較表等は通常の分析作業として自由に使ってよい。
- local execution / self-host / offline-first / local source of truth / P2P / E2EEを自動的に同じものとして扱わない。
- ADR/schemaの存在を、実運用・採用価値の実証と同一視しない。

## Candidate source request format

| Candidate source | Why needed | Which claim could change |
|---|---|---|
|  |  |  |
