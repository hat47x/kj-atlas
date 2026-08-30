# Case 003 Launch Packet — KJ Atlas external representation

- Status: Frozen before first valid Case 001 arm run
- Evidence bundle: `case-003-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Starter document: `doc_cognitive_case_003_starter.json`

## Context boundary

このtaskでは、与えられたsanitized evidence bundleだけをKJ Atlasについての共通証拠として使用する。

同じrepositoryの別ファイル、PR/issue discussion、他ケースの成果、評価メモ、外部Web資料を追加で読まない。資料外の一般知識を使う場合は、bundle由来の主張と明確に分ける。追加資料が必要なら、そのrunだけへ追加せず `Candidate source request` として挙げる。

cultural-substrate-weavingは使用しない。

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

## Collaboration mode

KJ Atlasを完成後の清書ではなく、分析中の外部表象として使う。human operatorがUI操作と最終採否を行い、分析AIは候補・批評・反対視点・空白等をproposalとして提示できるが、意味確定の最終権限を持たない。

### 1. 生材料

- evidence bundleから生カード候補を作る。
- architecture / operations / security / adoption / collaboration等の既成カテゴリを最初から束として与えない。
- source path / stable identifier / evidence timeを残す。
- 可能な範囲でfact / inference / uncertaintyを区別する。
- local execution / self-host / offline-first / local source of truth / P2P / E2EEを同義語化しない。
- Accepted ADR、実装済みissue、将来条件、実利用未確認の価値仮説を時点と状態を保って材料化する。

human operatorが最初の生カード集合を確認しKJ Atlasへ入れた後、InquiryJourneyのoriginを作る。

### 2. KJ統合

- 訴え・意味の近さから束ね候補を作る。
- 表札は一般カテゴリ名ではなく、束全体が何を訴えているかを表す候補とする。
- server-authoritativeとlocal/offline要求、data controlとcollaboration、運用容易性と主体性等の緊張を安易に「両立が重要」へ溶かさない。
- 対立・孤立・空白・未確定材料を残す。
- AIが束ね・表札・反対視点・要約等を提案した場合、人間が採用・修正・棄却・保留する。
- 採用後も主要主張を元カード/出典へ戻して検査する。

### 3. InquiryJourney

- experimentのRound番号をW型stageへ機械対応させない。
- 問い理解の変化、主要構造の組替え、反証による判断変更、中断時の未解決点など、人間が意味上の節目と判断したときだけsnapshot/handoffを作る。
- 自然な中断点があれば一度だけ保存→再読込→resume briefを使い、問い・未解決点・次の確認・以前の成果を復元できるかを見る。
- architecture/data/operations/adoptionの複数層をまたぐためだけにstageを機械分割しない。
- 必要ならcard lineage / round compare / non-destructive branchを使うが、機能利用自体を成功条件にしない。

### 4. A型→B型

- 空間構造・束・関係・対立・空白を確認してからrequired outputへ文章化する。
- 文章化後に元カードへ戻り、異論・不確実性・時点差・条件付き代替案・実利用未確認の価値が消えていないか検査する。
- カード枚数、島数、技術候補数、操作回数は成果として数えない。

## Candidate source request format

| Candidate source | Why needed | Which claim could change |
|---|---|---|
|  |  |  |
