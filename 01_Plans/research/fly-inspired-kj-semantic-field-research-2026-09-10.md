# ハエ脳由来の疎連想認知とKJ法の深層意味近接 — 調査・仮説整理

- Status: Research / Non-normative
- Date: 2026-09-10
- Scope: KJ法の束ね・島形成に必要な「訴えの近さ」を、LLMとは異なる認知機構でどこまで支援できるか
- Related: `00_Prompt/kj_technique.md`, `00_Prompt/cognitive_frame_and_evolution_criteria.md`, `00_Prompt/ai_kj_execution_procedures.md`, `01_Plans/issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md`, `01_Plans/issues/issue-COGNITIVE-DOGFOOD-01-product-development-cognitive-workbench.md`

## 1. 結論

現時点では、**FlyHashそのものをKJ法の島作りへ用いても要求水準には届かない**。FlyHashは、与えられた特徴空間における近傍を疎な高次元表現へ写し、類似検索を効率化する技術であり、入力特徴に存在しない深層意味を新たに生成する機構ではない。

一方で、ハエのmushroom bodyに着想を得た研究は、FlyHashからBioHash、FlyVec、Complyへ進み、固定ランダム射影だけでなく、データからの局所学習、単語・文脈の意味表現、文系列の疎な意味表現まで射程を広げている。このため、**「ハエ脳型では深層意味を扱えない」とも結論できない**。

kj-atlasで検証すべき仮説は、ハエ脳の忠実な再現ではなく、次である。

> **一般言語から獲得した疎な意味表現と、KJ作業で人間が行う束ね・分離・違和感・保留の履歴を局所的に統合すれば、表層語彙が異なっていても「一緒に置いて読んでみる価値がある」2〜3枚の候補を、LLMなしまたはLLMより軽量な経路で高い再現性をもって浮上させられるか。**

この研究仮説を、本書では仮に **KJ Semantic Field** と呼ぶ。製品名称・採用済みアーキテクチャではない。

## 2. KJ法が要求する「近さ」は通常の文章類似より深い

`ai_kj_execution_procedures.md` は束ねを「分類」ではなく**訴えの類似性**で行い、初期の束を2〜3枚程度とする。したがって、評価対象を単なるSemantic Textual Similarity（STS）や言い換え検出と同一視しない。

KJ法の近接には少なくとも次が含まれる。

1. **表層を越えた近接**  
   使用語彙や具体例が異なっても、背後で同じ問題構造・経験上の訴えを示すカードを近く読めること。
2. **高表層類似の拒否**  
   同じ語彙を使っていても、話者、時点、因果方向、肯否、役割が違えば安易に一束へしないこと。
3. **文脈依存性**  
   二枚だけなら近く見えるが、探究テーマや周囲のカードによって距離感が変わり得ること。
4. **集合としての立ち上がり**  
   pairwise similarityの推移律だけで島を決めず、2〜3枚を一緒に読んだときに初めて見える共通の訴えを扱えること。
5. **残余の保持**  
   どこにも入らないカード、混ぜたくない感覚、まだ言語化できない違和感を誤差として消さないこと。

したがって、PoCの目的は「正しい自動クラスタを作ること」ではない。**人間のKJ操作前に探索空間を閉じず、読むべき組合せを増やせるか**である。

## 3. 関連研究から分かること

### 3.1 FlyHash: 近傍保存はできるが、意味獲得の機構ではない

Dasgupta, Stevens, Navlakha (Science, 2017) は、ショウジョウバエ嗅覚回路を類似検索の観点から形式化し、従来のLSHと異なり疎な高次元表現を用いるFlyHashへつなげた。

ここから直接言えるのは、**既に有意味な入力空間が与えられたとき、その局所近傍を軽量に保持・検索する能力**である。カード本文を文字列特徴へ変換しただけでは、語彙を越えた「訴え」をFlyHashが自発的に獲得するわけではない。

Reference: https://pubmed.ncbi.nlm.nih.gov/29123069/

### 3.2 BioHash: ランダム射影からデータ駆動の疎表現へ進める

Ryali et al. (ICML 2020) は、FlyHashの弱点を「random projectionsでありdataから学べない」と明示し、局所的な可塑性則で疎な高次元codeを学習するBioHashを提案した。

これはkj-atlasにとって重要である。将来、人間が明示的に行った束ね・分離を局所的な教師信号として使う可能性を示す。ただし、BioHash自体の目的はunsupervised similarity searchであり、KJ法の「訴え」理解が実証されたわけではない。

Reference: https://proceedings.mlr.press/v119/ryali20a.html

### 3.3 FlyVec: 疎な回路motifでも分布意味を学べる

Liang et al. (ICLR 2021) は、mushroom bodyに着想を得た数理モデルを、非構造化text中のword-context相関の学習へ適用した。疎なbinary codeでstatic/context-dependent word representationを学習し、word similarity、word-sense disambiguation、document classificationで評価している。

この結果から、**疎な高次元回路motifが単なる表層hashに限定されず、言語コーパスから意味的構造を学習し得る**ことまでは支持される。

Reference: https://research.ibm.com/publications/can-a-fruit-fly-learn-word-embeddings

### 3.4 Comply: 文系列の疎なcontextual representationへ拡張している

Figueroa et al. (2025) のComplyは、FlyVecに位置情報を組み込み、single-layer networkでsequence representationを学習する。論文はFlyVecを上回り、より大規模なstate-of-the-art modelと同程度の性能を示したと報告し、sentenceのsparse contextual representationを得ている。

これはKJカードのような短文への適用可能性を高めるが、**KJ法の島形成に必要なlatent advocacy / set-level coherenceを直接評価した研究ではない**。また、日本語KJカードに対する実証もない。この差をPoCで埋める必要がある。

Reference: https://arxiv.org/abs/2502.01706

### 3.5 APLの局所抑制: global rankingより局所競合を支持する

Amin et al. (eLife, 2020) は、APL neuronのKenyon cellへのfeedback inhibitionが空間的に局所化され、mushroom bodyの異なるcompartmentを異なる強さで抑制できることを示した。

これを製品へ直接模倣する必要はないが、設計motifとしては、文書全体で一つのglobal Top-Nを作るより、**現在のカード・島・viewport・探究文脈ごとに候補を競合させる**方が少数テーマを押し流しにくいという仮説につながる。

Reference: https://elifesciences.org/articles/56954

## 4. 研究上の境界

### 4.1 生物学的模倣を目的にしない

採る候補は次の計算motifに限定する。

- sparse expansive representation
- winner-take-all / local competition
- local plasticity
- novelty / familiarityを分離可能な状態表現
- 複数compartment相当の独立した連想空間

全脳connectome、spiking simulation、生物学的parameter値そのものは採用理由にしない。

### 4.2 「ハエ脳型 = 非LLM」と「軽量 = 高品質」を混同しない

深層意味を得るには一般言語経験が必要であり、学習時には相応のcorpusと計算資源を要する可能性がある。評価では推論時CPU負荷だけでなく、学習・更新・配布・再現性の総コストを見る。

### 4.3 Dense semantic encoderを比較対象から外さない

目的はハエ脳方式を採用することではなく、KJ法の認知を拡張することにある。小型Transformer系sentence encoder等が同じlocal/offline条件で明らかに良い場合、それを隠してFly-inspired方式を採用してはならない。

## 5. KJ Semantic Field 仮説

### 5.1 二段構造

```text
General language experience
        |
        v
Sparse semantic encoder
(FlyVec / Comply inspired)
        |
        v
Sparse card representation
        |
        +-------------------------+
        |                         |
        v                         v
KJ-local association          structural channels
- grouped together            - relation graph
- separated again             - spatial context
- not_the_same                - provenance/time
- too_close / too_far         - current inquiry
- held                        - neighboring cards
        |                         |
        +------------+------------+
                     v
              KJ Semantic Field
                     |
                     v
     2-3 card "read-together" candidates
```

一般意味表現とKJ固有の学習を分ける。前者は「言葉として何が近いか」、後者は「この探究で何を一緒に読んだ／読まなかったか」を扱う。

### 5.2 初期段階では学習させすぎない

最初から利用者操作でprojection自体を書き換えない。Phase 1は固定表現・固定seedで完全再現可能にし、`grouped / separated / critique / held` を**学習せずledgerとして収集**する。

Phase 2で、そのledgerをoffline再生して適応型表現の増分を比較する。学習を製品の通常状態へ入れるのは、再現性・rollback・誤学習の検証後とする。

## 6. pairではなく2〜3枚の集合を評価する

KJ法では、A≈B、B≈CからA/B/Cを同一島と推移的に決めることはできない。そこでPoCはpair retrievalだけで終えず、**small-set coherence**を独立した課題とする。

評価対象を次の三種に分ける。

- **hard positive**: 表層語彙の重なりは小さいが、人が「一緒に読んでみる価値がある」と判断した2〜3枚。
- **hard negative**: 語彙・固有名詞・主題は似るが、訴え・因果方向・時点・立場が異なるため一緒にしない2〜3枚。
- **held / ambiguous**: 人間自身もまだ束ねを確定しない組合せ。モデル都合でpositive/negativeへ押し込まない。

正解ラベルは「同じ島である」ではなく、**candidateとして再提示する価値があるか**とする。これにより、人間の島形成を自動化する評価へずらさない。

## 7. PoC比較系

最低限、同じカード集合に対して次を比較する。

| 系 | 役割 |
|---|---|
| A. character/word n-gram + TF-IDF cosine | 表層類似の基準線 |
| B. conventional sparse/hash baseline | FlyHash導入が単なるhash高速化かを分離 |
| C. FlyHash-like sparse expansion | sparse expansion + WTA単体の寄与 |
| D. learned sparse semantic encoder | FlyVec/Comply系仮説の意味表現寄与 |
| E. strong local sentence encoder | 深層意味近接の現実的な比較基準 |
| F. KJ-specific multi-channel extension | 人間操作・graph・space・historyの増分 |
| G. current LLM proposal | 製品採用前提ではなく上限/性質比較用 |

`E` や `G` に勝つこと自体を採用条件にしない。重要なのは、**常時localに動かせる負荷で、KJ固有のhard positiveを増やし、hard negativeと残余を壊さないか**である。

## 8. 評価軸

数値は研究内部では使用してよい。`DOM-CORE-04` が禁じるのは、内容を点数・順位・等級へ畳んで利用者へ提示することであり、アルゴリズム評価の測定値まで禁止するものではない。

### R1 deep-semantic candidate recall

hard positiveが候補集合へ入る割合。`Recall@K` 等を内部指標として使用する。

### R2 surface-decoy rejection

高い語彙類似を持つhard negativeを、近いという理由だけで繰り返し提示しないか。

### R3 residual survival

孤立・少数・heldカードが「どこかへ入るべきもの」として強制回収されないか。`COGNITIVE-EVAL-01` のM3と接続する。

### R4 set-level coherence

pair retrievalでは拾えないが2〜3枚を同時に読むと成立する候補を回収できるか。また、一枚の異質カードを混ぜたときに盲目的に三枚組を維持しないか。

### R5 paraphrase / wording stability

軽微な言い換え、助詞、語順、カード長で候補が不安定になりすぎないか。

### R6 KJ-feedback increment

一般意味表現だけの場合に対し、束ね・分離・Critique等の履歴を使うことで、hard positive / hard negativeの識別が改善するか。

### R7 continuous-local budget

代表カード規模でCPU常駐可能なlatency、memory、index更新コストに収まるか。既存`ADR-0046`の性能予算を超える場合は、実装前にR-3として設計判断へ戻す。

### R8 cognitive-control increment

`COGNITIVE-EVAL-01` のM1/M3/M4/M7/M9を用い、候補機構によって発見が増えたか、残余保持が壊れなかったか、早期収束が増えなかったか、有益な注意再配分と単なる通知ノイズを区別する。

## 9. 反証条件

以下のいずれかが観測された場合、Fly-inspired方式の製品導入を止める、または役割を縮小する。

- **F1**: hard positiveの回収がTF-IDF等の表層基準線から実質的に改善しない。
- **F2**: 意味回収を上げるほどhard negativeも一緒に増え、KJ法で必要な分離が保てない。
- **F3**: local sentence encoderと比べて品質・latency・memory・配布容易性のいずれにも実質的な利点がない。
- **F4**: KJ履歴による適応が、短期的な配置癖へ過学習して新規hard positiveを失う。
- **F5**: seed / algorithm version / learned stateを保存しても候補を再現できず、後からなぜ候補が変わったか追跡できない。
- **F6**: 候補提示が利用者の探索を広げず、むしろ最初の機械候補へのanchoringを強める。

F1〜F6は失敗ではなく、この研究仮説を縮小・棄却するための正規の出口とする。

## 10. 製品境界

PoCが成功しても、次は自動化しない。

- Island / Clusterを自動確定しない。
- 表札を自動確定しない。
- `related / negate / causal / mutual / equivalence` をこのkernelだけで確定しない。
- 内部距離やactivationを利用者向けimportance / confidence scoreとして表示しない。
- `held`, `pending`, `shelved`, Critiqueを解消対象として扱わない。
- 戻し検査、空白列挙、A/B照合等のverification scopeを候補kernelだけで削らない。

製品に入れる場合の出力は、原則として **「この2〜3枚を一緒に読んでみる」候補** または **`too_close / too_far / not_the_same / novelty` の検討契機** に留める。

## 11. 三要素牽制による研究段階の境界

| 次元 | 研究段階で固定すること | まだ固定しないこと |
|---|---|---|
| 業務設計 | 人間が意味を立ち上げるための候補生成であり、自動島形成ではない | 具体的UI導線・常時表示の有無 |
| データ設計 | benchmark/derived signature/実験ledgerはCanonical Graphとは別物 | 永続schema・同期方式・tenant境界 |
| 機能設計 | offline PoCで同一snapshotを各方式へ入力して比較する | 本番API、worker、provider設定 |

したがって、本研究だけを根拠に`schemas.md`、API、Canonical Graphへ新規型を追加しない。

## 12. 次の実行単位

1. `COGNITIVE-ASSOC-01` としてPoC Issueを起票する。
2. 既存dogfoodのカードから、small-set benchmark候補を**モデル出力を見る前に**作る。
3. hard positive / hard negative / heldを明示し、元カードと人間判断の根拠へ戻れるようにする。
4. A〜Gの比較のうち、まずA/C/Eを最小baselineとして動かす。
5. D/Fは、その結果から「意味表現自体が不足しているのか」「KJ固有feedbackが不足しているのか」を分離してから実装する。
6. 結果を`COGNITIVE-EVAL-01`の既存測定軸へ接続する。
7. 既存性能・安全・データ境界で覆えない設計判断が初めて生じた場合のみ、`ADR-0047` R-1..R-4に従ってADR化を検討する。
