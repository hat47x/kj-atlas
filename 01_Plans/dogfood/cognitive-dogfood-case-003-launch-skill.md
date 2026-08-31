# Case 003 Launch Packet — cultural-substrate-weaving without KJ Atlas canvas

- Status: Frozen before first valid Case 001 arm run
- Evidence bundle: `case-003-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Method snapshot: `hat47x/cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`, canonical `src/ja-JP` only

## Context boundary

このtaskでは、与えられたsanitized evidence bundleだけをKJ Atlasについての共通証拠として使用する。

同じrepositoryの別ファイル、PR/issue discussion、他ケースの成果、評価メモ、外部Web資料を追加で読まない。方法としては、指定commitのcultural-substrate-weaving canonical `src/ja-JP` bundleだけを使用し、maintainer docs、evals、PR discussion等は読まない。

資料外の一般知識を使う場合は、bundle由来の主張と明確に分ける。追加資料が必要なら、そのrunだけへ追加せず `Candidate source request` として挙げる。

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

KJ Atlasキャンバスは使わず、指定されたcultural-substrate-weavingを方法として適用する。

- 文化体系をdeploymentやarchitectureの分類器として使わない。
- 対象単独では出にくい位置・関係・状態・遷移・空白を探索するために体系を使う。
- 体系由来の問い/仮説は来歴を保ち、product evidenceへ戻して検証する。
- framework語を除去しても成立する所見だけを最終成果へ残す。
- baselineでも同じ所見が出る、または別体系へ置換して差がない場合は体系固有の増分と数えない。
- 方法が増分を生まない場合は `no increment` を許容する。
- 新しい対象側の意味単位・関係・問いが増えなくなったら停止する。
- local/cloud等の価値対立へframeworkを先に割り当てない。

実行中はactivation判定、framework候補、採用/不採用理由、removal/substitution結果、最終的に対象側へ残った所見を作業記録として保持する。最終required outputへ方法論の説明を無理に混ぜない。

## Candidate source request format

| Candidate source | Why needed | Which claim could change |
|---|---|---|
|  |  |  |
