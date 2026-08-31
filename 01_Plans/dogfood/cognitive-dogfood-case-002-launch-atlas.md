# Case 002 Launch Packet — KJ Atlas external representation

- Status: Frozen before first valid Case 001 arm run
- Evidence bundle: `case-002-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Starter document: `doc_cognitive_case_002_starter.json`

## Context boundary

このtaskでは、与えられたsanitized evidence bundleだけをKJ Atlasについての共通証拠として使用する。

同じrepositoryの別ファイル、PR/issue discussion、他ケースの成果、評価メモ、外部Web資料を追加で読まない。資料外の一般知識を使う場合は、bundle由来の主張と明確に分ける。追加資料が必要なら、そのrunだけへ追加せず `Candidate source request` として挙げる。

cultural-substrate-weavingは使用しない。

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

## Collaboration mode

KJ Atlasを完成後の清書ではなく、分析中の外部表象として使う。human operatorがUI操作と最終採否を行い、分析AIは候補・批評・反対視点・空白等をproposalとして提示できるが、意味確定の最終権限を持たない。

### 1. 生材料

- evidence bundleから生カード候補を作る。
- 同じ意味を持つ材料を機械的に細切れにせず、一方で異なる主張を一枚へ混ぜない。
- source path / stable identifier / evidence timeを残す。
- 可能な範囲でfact / inference / uncertaintyを区別する。
- 「proposal-only」「human final authority」等の結論語を初期カテゴリとして先取りしない。
- 古い設計・後で訂正された状態・未実装契約も時点を残して材料化する。

human operatorが最初の生カード集合を確認しKJ Atlasへ入れた後、InquiryJourneyのoriginを作る。

### 2. KJ統合

- 訴え・意味の近さから束ね候補を作る。
- 表札は一般カテゴリ名ではなく、束全体が何を訴えているかを表す候補とする。
- 対立・孤立・空白・未確定材料を消さない。
- AIが束ね・表札・反対視点・要約等を提案した場合、人間が採用・修正・棄却・保留する。
- AIの提案に違和感がある場合、その違和感自体を作業材料として保持し、元sourceへ戻る。
- 採用後も主要主張を元カード/出典へ戻して検査する。

### 3. InquiryJourney

- experimentのRound番号をW型stageへ機械対応させない。
- 問い理解の変化、主要構造の組替え、反証による判断変更、中断時の未解決点など、人間が意味上の節目と判断したときだけsnapshot/handoffを作る。
- 自然な中断点があれば一度だけ保存→再読込→resume briefを使い、問い・未解決点・次の確認・以前の成果を復元できるかを見る。
- 必要ならcard lineage / round compare / non-destructive branchを使うが、機能利用自体を成功条件にしない。

### 4. A型→B型

- 空間構造・束・関係・対立・空白を確認してからrequired outputへ文章化する。
- 文章化後に元カードへ戻り、異論・不確実性・時点差・未実装境界が消えていないか検査する。
- カード枚数、島数、AI proposal数、操作回数は成果として数えない。

## Candidate source request format

| Candidate source | Why needed | Which claim could change |
|---|---|---|
|  |  |  |
