# Cognitive Dogfood Case 001 — Round 2 External Source Manifest

- Status: Pre-registered / sealed until all Round 1 arms are fixed
- Prepared: 2026-08-29
- Case: `cognitive-dogfood-case-001-product-purpose.md`
- Rule: このmanifestの内容はRound 1のA〜Dへ渡さない。Round 1成果を保存した後、全armへ同一条件で追加する。

## 目的

Round 2では、KJ Atlas内部資料だけから立ち上がった価値仮説を、隣接する実践・製品・研究へ当てて維持/修正/棄却する。

競合の機能表を作ることが主目的ではない。次を検査する。

1. KJ Atlasが独自価値だと思っているものが、既存製品ですでに一般化していないか。
2. KJ Atlasが重視する「早く閉じない・根拠へ戻る・人間が決める」が、隣接実践ではどのような形で実装されているか。
3. local/offline/self-hostを単なる配備方式ではなく、data ownership/agencyとして考える必要があるか。
4. AI支援が思考を助ける場合と、過剰依存・認知オフロードを起こす場合をどう分けるか。
5. 「誰が意味を決めるか」「誰の資料か」「誰が影響を受けるか」という統治問題が、分析ツールの設計へどう関係するか。

## S1 Miro — AI clustering / sticky-note synthesis

- Source: Miro Help Center, “Clustering”
- URL: https://help.miro.com/hc/en-us/articles/4409706795410-Clustering
- Retrieved: 2026-08-29
- Source type: current official product documentation

### Manifest reason

Miroは付箋をkeywords/sentiment等でAIクラスタリングできる。KJ Atlasが「AIでカードを束ねること」自体を差別化と誤認していないかを検査するための直接隣接製品。

### Questions

- KJ Atlasの束ねがMiroのkeyword clusteringと異なる価値を持つなら、その差は操作名ではなく何か。
- uncategorized/孤立/異論の扱い、人間の再編成、根拠保持、KJ表札などに実質差があるか。

## S2 ATLAS.ti — quotation level / delayed coding / visual networks

- Source: ATLAS.ti 26 Windows User Manual, “The ATLAS.ti Quotation Level”
- URL: https://manuals.atlasti.com/Win/en/manual/Quotations/QuotationLevel.html
- Retrieved: 2026-08-29
- Source type: current official manual

### Manifest reason

ATLAS.tiはquotationを先に保持し、すぐcodeへ押し込まず後からconceptualiseでき、quotationをnetwork上で扱える。したがって「早い分類を避ける」「原資料へ戻る」「視覚空間で意味を扱う」はKJ Atlasだけの発想ではない。

### Questions

- KJ Atlasが既存CAQDASを超えるのはどの利用仕事か。
- カード/表札/空白/多層図解はquotation/code/networkと何が実務的に違うか。
- 質的研究者にとってKJ Atlasへswitchする理由が本当にあるか。

## S3 Dovetail — evidence-backed AI for product research

- Source: Dovetail, “Product Research”
- URL: https://dovetail.com/solutions/product-research/
- Retrieved: 2026-08-29
- Source type: current official product page

### Manifest reason

Dovetailは顧客証拠へtraceできるAI回答、theme/insight、PRD等への変換、人間によるtheme validationを製品価値としている。KJ Atlasの「根拠接地＋AI＋意思決定への変換」がどこまで差別化になるかを厳しく見る。

### Questions

- evidence-grounded AIはKJ Atlas固有か。
- KJ Atlasの強みがあるなら、顧客インテリジェンスの自動化ではなく、未確定・対立・意味形成の過程にあるのか。
- Dovetailのような強い自動化とKJ Atlasのproposal-onlyは、どのタスクでどちらが価値を持つか。

## S4 Dovetail — persistent evidence-grounded docs

- Source: Dovetail, “AI Docs”
- URL: https://dovetail.com/product/ai-docs/
- Retrieved: 2026-08-29
- Source type: current official product page

### Manifest reason

AIがraw feedbackからevidence-grounded deliverableを作り、元の顧客発話へtraceできる。KJ AtlasのB型叙述/共有成果物の価値を、現在の市場水準と比較する。

### Questions

- KJ Atlasの叙述は単に証拠付きレポートを生成する以上の何を守るか。
- 最終docへ変換した後も、対立・残差・構造変更可能性を保持することにswitch reasonがあるか。

## S5 Ink & Switch — local-first software

- Source: Kleppmann et al., “Local-first software: You own your data, in spite of the cloud”
- URL: https://www.inkandswitch.com/essay/local-first/
- Publication: 2019
- Retrieved: 2026-08-29
- Source type: research/technical essay

### Manifest reason

local-firstをoffline機能だけでなく、ownership、agency、privacy、long-term preservation、collaborationとの両立として位置づける基準線。

### Questions

- KJ Atlasのoffline/self-hostは利用仕事の中心価値か、導入条件か、安全境界か。
- 分析途中の未成熟/機微情報を扱うためのuser controlと、共同分析の利便をどう両立するか。

## S6 Design Justice Network — directly impacted people and accountable process

- Source: Design Justice Network, “Read the Principles”
- URL: https://designjustice.org/read-the-principles
- Retrieved: 2026-08-29
- Source type: practice principles

### Manifest reason

影響を受ける人の声、designer intentよりcommunity impact、accountable/collaborative processを重視する。KJ Atlasの人間中心性を「操作の最終ボタンを人間が押す」だけで終わらせないための外部視点。

### Questions

- 誰がカード/表札/共有範囲を決めるのか。
- 分析対象となる人と分析者/組織の権力差をKJ Atlasはどこまで扱うべきか。
- 「human final authority」のhumanは誰か。

## S7 Global Indigenous Data Alliance — CARE Principles

- Source: GIDA, “The CARE Principles for Indigenous Data Governance”
- URL: https://www.gida-global.org/careprinciples
- Retrieved: 2026-08-29
- Source type: data-governance principles

### Manifest reason

FAIR的な共有容易性だけではなく、collective benefit、authority to control、responsibility、ethics、power differentials/historical contextsを扱う。provenance/portable dataだけでは十分でない統治視点を供給する。

### Questions

- 「データを持ち出せる」「出典へ戻れる」だけで資料所有者の統制は十分か。
- 調査対象者/コミュニティの資料をAI分析・共有するとき、誰のauthorityが必要か。
- universalな製品不変条件と、実践文化ごとに適応すべき統制を分けられるか。

## S8 Microsoft Research / CHI 2025 — GenAI and critical thinking

- Source: Lee et al., “The Impact of Generative AI on Critical Thinking: Self-Reported Reductions in Cognitive Effort and Confidence Effects From a Survey of Knowledge Workers”
- URL: https://www.microsoft.com/en-us/research/publication/the-impact-of-generative-ai-on-critical-thinking-self-reported-reductions-in-cognitive-effort-and-confidence-effects-from-a-survey-of-knowledge-workers/
- Publication: CHI 2025
- Retrieved: 2026-08-29
- Source type: empirical HCI research

### Manifest reason

319 knowledge workers / 936 examplesをもとに、GenAIへのconfidenceが高いほどcritical thinkingが少なくなる関連と、critical thinkingがverification/integration/task stewardshipへ移ることを報告する。

### Questions

- KJ AtlasはAIに思考を委譲するのか、verification/integration/stewardshipを支えるのか。
- provenance、proposal-only、戻し検査、反対視点が本当に依存校正へ寄与するか。

## S9 Microsoft Research / CHI 2025 — support thinking rather than recommend

- Source: Reicherts et al., “AI, Help Me Think—but for Myself: Assisting People in Complex Decision-Making by Providing Different Kinds of Cognitive Support”
- URL: https://www.microsoft.com/en-us/research/publication/ai-help-me-think-but-for-myself-assisting-people-in-complex-decision-making-by-providing-different-kinds-of-cognitive-support/
- Publication: CHI 2025
- Retrieved: 2026-08-29
- Source type: empirical HCI research

### Manifest reason

recommendation-centric AIと、利用者自身のrationaleを伸ばすExtendAIを比較し、後者がdecision processへ統合しやすい一方、recommendation型はよりnovelな洞察を少ない認知負荷で出すというtrade-offを報告する。

### Questions

- KJ AtlasのAIは「答えを出すAI」と「人間の思考構造を伸ばすAI」のどちらへ寄せるべきか。
- noveltyとhuman ownership/cognitive effortのtrade-offを一律に解消しようとしていないか。

## S10 Buçinca et al. — cognitive forcing and overreliance

- Source: Buçinca, Malaya, Gajos, “To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI in AI-Assisted Decision-Making”
- URL: https://www.eecs.harvard.edu/~kgajos/papers/2021/bucinca2021trust.shtml
- Publication: Proc. ACM Human-Computer Interaction, 2021
- Retrieved: 2026-08-29
- Source type: empirical HCI research

### Manifest reason

cognitive forcingがAIへのoverrelianceを減らし得る一方、主観的評価を下げるtrade-offを示す。KJ Atlasの「有益な摩擦」と「単なる使いにくさ」を分ける基準として使う。

### Questions

- AI案を読む前の自分の仮判断、戻し検査、出典確認などをforcingとして設計すべき箇所はあるか。
- 最も安全なUIが最も好まれるとは限らないとき、どこまで摩擦を保持するか。

## Round 2で追加しないもの

- 競合各社の価格表・網羅的機能一覧。
- SEO比較記事や出典不明のランキング。
- 「AIで生産性が何%上がる」だけを扱う一般的マーケティング資料。
- KJ Atlasの価値仮説を支持する資料だけを後から追加すること。
- 文化体系そのものを正しい社会モデルとして扱う資料。

## 各armへ要求するRound 2差分

Round 1成果を消さず、次を追記する。

1. External sourceによって**維持**されたRound 1所見。
2. External sourceによって**狭くなった/条件付きになった**所見。
3. **棄却**した所見。
4. Round 1にはなかった新しい反証・switch barrier。
5. 「KJ Atlas固有だと思ったが既存製品にもある」と判明した価値。
6. それでも残る可能性のある一次利用仕事。
7. 製品へ実装すべきでない外部知見。

## Manifest変更規則

Round 1実行後に本manifestを変更しない。

重大な事実誤認、URL消失、資料アクセス不能が判明した場合のみ、変更理由と旧manifest SHAを記録した新revisionを作る。特定armの結果を改善するためのsource追加は禁止する。