# Case 001 Launch Packet — Ordinary analysis

- Status: Frozen before first raw run
- Evidence bundle ID: `case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`

## Context boundary

このtaskは、operatorから与えられたsanitized evidence bundleのfrozen sourceから、KJ Atlasの存在目的と現在の実証状態を分析する。

製品についての証拠として使用してよいのは、evidence bundle内の20件の製品資料だけである。`_experiment/bundle-manifest.json` はファイル同一性確認のために参照してよいが、bundle外のrepository、近隣plan、PR discussion、Case 0監査、外部競合/研究資料を探索しない。operator用のsource manifestを探したり開いたりしない。

外部Web検索を行わない。資料外の一般知識を使う場合は、frozen source由来の主張と明確に分ける。追加資料が必要なら、そのrunだけへ追加せず `Candidate source request` として挙げる。

## Fixed question

KJ Atlasは、既存のAIチャット、ホワイトボード、質的分析ツール、文書/issue管理では十分に満たしにくい、どの利用仕事のために存在するべきか。現在の設計・実装・dogfoodは、その価値をどこまで実現し、何をまだ実証できていないか。

## Required output

次を必ず含める。

1. KJ Atlasが解こうとしている利用者の仕事。
2. 既存手段で十分な領域と、不十分になり得る領域。
3. 現在のKJ Atlasが既に実現している価値。
4. 実証されていない価値仮説。
5. 最重要の反証、またはKJ Atlasが不要かもしれない条件。
6. 次に実施すべき検証/issue。
7. 主要主張ごとの根拠と、その根拠が示す時点。
8. 資料の中で、古い状態・後で訂正された状態・相互に緊張する記述を見つけた場合は、そのまま並べず現在状態との関係を示す。
9. 判断を保留する箇所と、追加で必要な証拠。

主要主張には、可能な限りsource path / stable identifier / evidence timeを付ける。断定できない場合は推測で埋めず保留する。

結論をKJ Atlasに好意的にする必要はない。既存手段で十分、対象市場が狭い、価値仮説を棄却すべきという結論も許容される。

最終required outputでは、分析手順そのものを成果の価値として数えない。方法への自己言及は、製品証拠の理解に本当に必要な場合だけにする。

## Analysis mode

通常の分析として進める。

- KJ法の手順を追加方法として使用しない。
- KJ Atlasキャンバスを分析用の外部表象として使用しない。
- cultural-substrate-weavingを使用しない。
- 必要なメモ、見出し、比較表等は通常の分析作業として自由に使ってよい。
- 特定の方法論を模倣するためだけのカード化・束ね・framework探索は行わない。

資料同士が衝突している場合は、どちらかを早く選ぶのではなく、時点・訂正関係・適用範囲を確認してから判断する。

## Candidate source request format

必要な追加資料がある場合、最後に次の形式で列挙する。

| Candidate source | Why needed | Which claim could change |
|---|---|---|
|  |  |  |
