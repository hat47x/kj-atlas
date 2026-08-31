# Case 002 Launch Packet — cultural-substrate-weaving without KJ Atlas canvas

- Status: Frozen before first valid Case 001 arm run
- Evidence bundle: `case-002-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Method snapshot: `hat47x/cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`, canonical `src/ja-JP` only

## Context boundary

このtaskでは、与えられたsanitized evidence bundleだけをKJ Atlasについての共通証拠として使用する。

同じrepositoryの別ファイル、PR/issue discussion、他ケースの成果、評価メモ、外部Web資料を追加で読まない。方法としては、指定commitのcultural-substrate-weaving canonical `src/ja-JP` bundleだけを使用し、maintainer docs、evals、PR discussion等は読まない。

資料外の一般知識を使う場合は、bundle由来の主張と明確に分ける。追加資料が必要なら、そのrunだけへ追加せず `Candidate source request` として挙げる。

## Fixed question

KJ Atlasのカード化、束ね、表札、反対視点、空白探索、配置、叙述などのAI支援について、どこまでを提案・自動化し、どこで人間の判断・確認・有益な摩擦を必須とするべきか。現在のproposal-only原則は、操作ごとの誤り方と利用価値に対して粗すぎないか、または十分に一般的な安全境界か。

## Required output

次を必ず含める。

1. AI支援操作を、誤り方・可逆性・意味確定への影響で分けた境界案。
2. 各操作でAIが自律実行してよい部分、proposalに留める部分、人間確認を必須にする部分。
3. 現行KJ Atlasが既に実現している適切な境界と、過剰/不足の可能性。
4. 「有益な摩擦」と「無駄な摩擦」を区別する判断基準。
5. human final authorityが形式化し、automation biasを防げない条件。
6. 最も強い反証。現在のproposal-only原則をほぼ維持すべき理由、または逆にもっと自律化すべき理由。
7. 次に検証すべき具体的な操作/issue。新ADRを先に作るのではなく、実使用で観測可能な検証を優先する。
8. 主要主張ごとのsource path / stable identifier / evidence time。
9. 古い状態、後で修正された状態、未実装の契約を区別する。
10. 判断保留と追加で必要な証拠。

断定できない箇所は推測で埋めず保留する。KJ Atlasに好意的な結論を求めない。現在の原則が十分である、特定操作だけ自律化すべき、あるいはAI支援自体を減らすべきという結論も許容される。

## Analysis mode

KJ Atlasキャンバスは使わず、指定されたcultural-substrate-weavingを方法として適用する。

- 文化体系をAI操作や論点の分類器として使わない。
- 対象単独では出にくい位置・関係・状態・遷移・空白を探索するために体系を使う。
- 体系由来の問い/仮説は来歴を保ち、product evidenceへ戻して検証する。
- framework語を除去しても成立する所見だけを最終成果へ残す。
- baselineでも同じ所見が出る、または別体系へ置換して差がない場合は体系固有の増分と数えない。
- 方法が増分を生まない場合は `no increment` を許容する。
- 新しい対象側の意味単位・関係・問いが増えなくなったら停止する。

実行中はactivation判定、framework候補、採用/不採用理由、removal/substitution結果、最終的に対象側へ残った所見を作業記録として保持する。最終required outputへ方法論の説明を無理に混ぜない。

## Candidate source request format

| Candidate source | Why needed | Which claim could change |
|---|---|---|
|  |  |  |
