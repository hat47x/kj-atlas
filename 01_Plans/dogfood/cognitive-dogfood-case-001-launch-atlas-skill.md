# Case 001 Launch Packet — KJ Atlas + cultural-substrate-weaving

- Status: Frozen before first raw run
- Evidence bundle ID: `case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Skill snapshot: `hat47x/cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`
- Starter document: `doc_cognitive_case_001_starter.json`

## Context boundary

このtaskは、operatorから与えられたsanitized evidence bundleのfrozen sourceから、KJ Atlasの存在目的と現在の実証状態を分析する。

製品についての証拠として使用してよいのは、evidence bundle内の20件の製品資料だけである。`_experiment/bundle-manifest.json` はファイル同一性確認のために参照してよいが、bundle外のKJ Atlas repository、近隣plan、PR discussion、Case 0監査、外部競合/研究資料を探索しない。operator用のsource manifestを探したり開いたりしない。

方法としては、operatorから別途与えられた上記commitの `cultural-substrate-weaving` canonical sourceだけを使用する。skill repositoryを追加探索せず、PR #5 discussionやCase 001向け共進化protocolを読まない。

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

## cultural-substrate-weaving boundary

- 文化体系を製品カードや論点の分類器にしない。
- 対象単独では出にくい位置・関係・状態・遷移・空白を探索するために体系を用いる。
- 体系由来の問い/仮説は来歴を保ち、対象sourceへ戻して検証する。
- 体系語を除去しても成立する所見だけを最終成果へ残す。
- baselineでも同じ所見が出る、または別体系へ置換しても差がない場合は、その体系固有の増分と数えない。
- 方法が増分を生まない場合は `no increment` を許容する。
- 新しい対象側の意味単位・関係・問いが増えなくなったら停止する。
- frameworkがKJ Atlasの束・表札・配置を先に決めないようにする。

実行中にactivation判定、候補体系、採用/不採用理由、removal/substitution結果、最終的に対象側へ残った所見を作業記録として保持する。

## KJ Atlas collaboration mode

KJ Atlasを、完成後の清書ではなく**分析中の外部表象**として使う。人間operatorがUI操作と最終採否を行う。分析AIはproposalを出せるが状態変更の最終権限を持たない。

### 1. 生材料

- frozen sourceから、生カード候補を作る。
- 一つのカードへ無理に複数論点を詰めないが、同じ体感・意味を持つ材料を機械的に細切れにしない。
- 各候補にsource path / stable identifier / evidence timeを付ける。
- 可能な範囲で `fact / inference / uncertainty` を区別する。
- 初期カテゴリ名や最終結論をカードへ先取りしない。
- 後段で訂正された古い状態も、誤情報として消すのではなく「当時そう見えていた」材料として時点を保つ。
- framework由来の問いや仮説は、通常カードと同じ確定度へ自動昇格させず、対象sourceへ戻すまで候補として扱う。

human operatorが最初の生カード集合を確認し、KJ Atlasへ入れた後にInquiryJourneyのoriginを作ることを標準とする。

### 2. KJ統合

- 訴え・意味の近さから束ね候補を出す。
- 表札は一般カテゴリ名ではなく、束全体が何を訴えているかを表す候補として出す。
- 対立は無理に「両方重要」へ溶かさない。
- 孤立カード、空白、未確定材料を残す。
- framework由来の材料も他の生材料と同様に扱い、体系が束の構造を先に決めないようにする。
- AIが束ね・表札・反対視点・要約を提案した場合、人間が採用・修正・棄却・保留する。
- 採用後も元カード/出典へ戻って検査する。

### 3. InquiryJourney

- experimentのRound番号をW型stageへ機械対応させない。
- 人間が意味上の節目と判断したときだけsnapshot/handoffを作る。
- 問いの理解が変わった、主要構造が組み替わった、反証で判断が変わった、中断時に未解決点を残した、などの節目を優先する。
- 自然な中断点があれば、一度だけ保存→再読込→resume briefを使い、問い・未解決点・次の確認・以前の成果が復元できるかを見る。
- 必要ならcard lineage / round compare / non-destructive branchを使うが、機能を使うこと自体を成功条件にしない。
- framework探索のためだけにstage/iterationを不必要に増やさない。

### 4. A型→B型

- 空間構造・束・関係・対立・空白を確認してから、required outputへ文章化する。
- 文章化後、元カードへ戻り、孤立・異論・不確実性・時点差が消えていないか確認する。
- framework名を消すと成立しない結論を、対象側の確定所見として残さない。
- カード枚数、島数、操作回数は成果ではない。

## Candidate source request format

必要な追加資料がある場合、最後に次の形式で列挙する。

| Candidate source | Why needed | Which claim could change |
|---|---|---|
|  |  |  |
