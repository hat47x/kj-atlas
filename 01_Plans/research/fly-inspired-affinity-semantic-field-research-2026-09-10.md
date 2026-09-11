# 親和図法の深層意味近接を支える非LLM認知層 — 調査・仮説整理

- Status: Research / Non-normative
- Date: 2026-09-10
- Scope: 親和図法における束ね・島形成に必要な「訴えの近さ」を、LLMとは異なる認知機構でどこまで支援できるか
- Related: `00_Prompt/kj_technique.md`, `00_Prompt/cognitive_frame_and_evolution_criteria.md`, `00_Prompt/ai_kj_execution_procedures.md`, `01_Plans/issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md`, `01_Plans/issues/issue-COGNITIVE-DOGFOOD-01-product-development-cognitive-workbench.md`

> Relatedに含まれる`kj_*`は既存ファイルの参照識別子であり、本書の一般名称ではない。

## 1. 研究の起点

kj-atlasが支援したいのは、カードを意味カテゴリへ高速に分類することではない。

人間がまだ名前を付けていない関係を見つけ、複数カードを並べたときに初めて立ち上がる共通の訴えを感じ取り、必要に応じて離し、保留し、残余を残しながら探究を進めることである。

この営みでは、語彙類似が高いカードを近く置くだけでは不十分である。逆に、高性能なLLMへ全てを任せればよいとも限らない。常時localでの軽量動作、同一入力に対する再現性、LLMとは異なる探索経路、人間の判断を確定しないproposal-only性も同時に必要になる。

したがって本研究の中心的な問いは、次である。

> **人間の親和図作業を置き換えず、その前段で「一緒に読んでみる価値のある組合せ」を軽量かつ再現可能に浮上させる、LLMとは異なる認知層を構成できるか。**

ハエ脳由来の疎表現は、この問いに対する候補技術の一つとして検討する。研究の出発点そのものではない。

## 2. 親和図法から導かれる認知要件

親和図法における「近さ」は通常の文章類似より深い。少なくとも次の性質を必要とする。

1. **表層を越えた近接**  
   使用語彙や具体例が異なっても、背後にある問題構造・経験上の訴えを近く読めること。
2. **高表層類似の拒否**  
   同じ語彙でも、話者・時点・因果方向・肯否・役割が異なれば安易に一束へしないこと。
3. **文脈依存性**  
   二枚だけなら近く見えても、探究テーマや周囲のカードによって距離感が変わり得ること。
4. **集合としての立ち上がり**  
   pairwise similarityの推移律だけで島を決めず、2〜3枚を同時に読んだときに初めて見える共通の訴えを扱えること。
5. **残余の保持**  
   どこにも入らないカード、混ぜたくない感覚、まだ言語化できない違和感を誤差として消さないこと。
6. **人間確定の維持**  
   候補提示は行っても、島・表札・関係そのものを機械が確定しないこと。
7. **継続利用可能な軽量性**  
   local/offlineで常時利用し得る計算量・memory・更新コストに収まること。
8. **再現性**  
   seed、algorithm version、parameter set、必要ならlearned stateを残し、候補変化を追跡できること。

PoCの目的は「正しい自動クラスタを作ること」ではなく、**人間の探索空間を閉じずに、読むべき組合せを増やせるか**である。

## 3. 認知層を分解して考える

根幹要件を一つのモデルへ押し込まず、次の三層へ分けて考える。

### 3.1 一般意味表現

「言葉として何が近いか」を扱う。小型sentence encoder、学習済み疎意味表現などが候補になる。

### 3.2 親和図作業固有の連想

「この探究で何を一緒に読んだか／読まなかったか」を扱う。将来的には、grouped / separated / critique / held / too_close / too_far / not_the_same等の履歴が候補になる。

### 3.3 構造文脈

relation graph、空間配置、provenance/time、現在のinquiry、周辺カード等を扱う。

重要なのは、これらを最初から混ぜないことである。一般意味表現だけで足りないのか、親和図作業固有の情報に独立増分があるのかを分離して検証する。

## 4. 候補技術としてハエ脳由来の疎表現を見る理由

必要としているのは、生物学的忠実再現ではない。候補として興味があるのは、次の計算motifである。

- sparse expansive representation
- winner-take-all / local competition
- local plasticity
- novelty / familiarityを分離可能な状態表現
- 複数compartment相当の独立した連想空間

これらは、軽量な常時local処理、局所競合、個別探究への適応という要件と部分的に接続し得る。

一方で「ハエ脳型 = 非LLM」「軽量 = 高品質」とはみなさない。深層意味を得るには一般言語経験が必要であり、学習・更新・配布まで含めた総コストを見る。

## 5. 関連研究から分かること

### 5.1 FlyHash: 近傍保存はできるが意味獲得そのものではない

Dasgupta, Stevens, Navlakha (Science, 2017) はショウジョウバエ嗅覚回路を類似検索として形式化し、疎な高次元表現によるFlyHashへつなげた。

ここから直接言えるのは、既に有意味な入力空間が与えられたとき、その局所近傍を軽量に保持・検索する能力である。文字列特徴だけから語彙を越えた「訴え」を自発的に獲得するとは言えない。

Reference: https://pubmed.ncbi.nlm.nih.gov/29123069/

### 5.2 BioHash: ランダム射影からデータ駆動へ

Ryali et al. (ICML 2020) はFlyHashのrandom projectionを拡張し、局所的な可塑性則で疎な高次元codeをデータから学ぶBioHashを提案した。

将来、人間が明示的に行った束ね・分離を局所教師信号として使う可能性を示す。ただし、BioHash自体はunsupervised similarity searchであり、親和図法の「訴え」理解を実証したものではない。

Reference: https://proceedings.mlr.press/v119/ryali20a.html

### 5.3 FlyVec: 疎な回路motifでも意味表現を学べる

Liang et al. (ICLR 2021) はmushroom bodyに着想を得た数理モデルをword-context相関の学習へ適用し、疎なbinary codeで意味表現を学習した。

これは、疎な高次元回路motifが単なる表層hashに限定されず、言語コーパスから意味構造を学習し得ることを支持する。

Reference: https://research.ibm.com/publications/can-a-fruit-fly-learn-word-embeddings

### 5.4 Comply: 文系列の疎なcontextual representation

Figueroa et al. (2025) のComplyはFlyVecへ位置情報を組み込み、single-layer networkでsequence representationを学習する。

短文カードへの適用可能性は高まるが、親和図の島形成に必要なlatent advocacy / set-level coherenceを直接評価した研究ではない。日本語の親和図カードに対する実証もない。

Reference: https://arxiv.org/abs/2502.01706

### 5.5 APLの局所抑制: global rankingではなく局所競合

Amin et al. (eLife, 2020) は、APL neuronからKenyon cellへのfeedback inhibitionが空間的に局所化されることを示した。

製品へ直接模倣する必要はないが、設計motifとしては文書全体で一つのglobal Top-Nを作るより、現在のカード・島・viewport・探究文脈ごとに候補を競合させる方が少数テーマを押し流しにくいという仮説につながる。

Reference: https://elifesciences.org/articles/56954

## 6. ここまでから導く研究仮説

FlyHashそのものを親和図の島作りへ用いても、要求水準には届かない可能性が高い。FlyHashは既存特徴空間の近傍を保存する技術であり、入力にない深層意味を生成する機構ではない。

一方、BioHash / FlyVec / Complyまで含めれば、疎表現が意味学習へ広がる余地はある。そこで検証すべき仮説を次のように置く。

> **一般言語から獲得した意味表現と、親和図作業で人間が行う束ね・分離・違和感・保留の履歴を局所的に統合すれば、表層語彙が異なっていても「一緒に置いて読んでみる価値がある」2〜3枚の候補を、LLMなしまたはLLMより軽量な経路で再現性をもって浮上させられるか。**

この仮説を、本書では仮に **Affinity Semantic Field** と呼ぶ。製品名称でも採用済みアーキテクチャでもない。

概念上は次の二段構造を想定する。

```text
General language experience
        |
        v
semantic representation
        |
        v
card representation
        |
        +-------------------------+
        |                         |
        v                         v
affinity-local association     structural channels
- grouped together             - relation graph
- separated again              - spatial context
- not_the_same                 - provenance/time
- too_close / too_far          - current inquiry
- held                         - neighboring cards
        |                         |
        +------------+------------+
                     v
            Affinity Semantic Field
                     |
                     v
       2-3 card read-together candidates
```

Phase 1では固定表現・固定seedとし、利用者操作を学習へ即時反映せずledgerとして収集する。Phase 2でoffline再生し、適応型表現の独立増分を比較する。

## 7. 比較系

最低限、同じカード集合に対して次を比較する。

| 系 | 役割 |
|---|---|
| A. character/word n-gram + TF-IDF cosine | 表層類似の基準線 |
| B. conventional sparse/hash baseline | 単なるhash高速化との差を分離 |
| C. FlyHash-like sparse expansion | sparse expansion + WTA単体の寄与 |
| D. learned sparse semantic encoder | FlyVec/Comply系の意味表現寄与 |
| E. strong local sentence encoder | 深層意味近接の現実的な比較基準 |
| F. affinity-specific multi-channel extension | 人間操作・graph・space・historyの増分 |
| G. current LLM proposal | 上限・性質比較用 |

EやGに勝つこと自体を採用条件にしない。重要なのは、常時localに動かせる負荷で親和図上のhard positiveを増やし、hard negative・単独島・残余を壊さないかである。

## 8. 評価方法

pairだけではなく2〜3枚のsmall-set coherenceを評価する。

- **hard positive**: 表層語彙の重なりは小さいが、一緒に読んでみる価値がある2〜3枚。
- **hard negative**: 語彙・固有名詞・主題は似るが、訴え・因果方向・時点・立場が異なり一緒にしない2〜3枚。
- **held / ambiguous**: 人間自身もまだ束ねを確定しない組合せ。

正解を自動的な「同じ島」と定義せず、candidateとして再提示する価値を見る。

評価軸は次とする。

- R1 deep-semantic candidate recall
- R2 surface-decoy rejection
- R3 singleton / residual survival
- R4 set-level coherence
- R5 wording stability
- R6 affinity-feedback increment
- R7 continuous-local budget
- R8 cognitive-control increment

## 9. 反証条件

以下のいずれかが観測された場合、Fly-inspired方式の製品導入を止める、または役割を縮小する。

- **F1**: hard positive回収がTF-IDF等の表層基準線から実質的に改善しない。
- **F2**: 意味回収を上げるほどhard negativeも増え、親和的な束ねに必要な分離が保てない。
- **F3**: local sentence encoderに対して品質・latency・memory・配布容易性のいずれにも実質的な利点がない。
- **F4**: 親和図作業履歴への適応が短期的な配置癖へ過学習する。
- **F5**: seed / algorithm version / learned stateを保存しても候補を再現できない。
- **F6**: 候補提示が探索を広げず、最初の機械候補へのanchoringを強める。

これらは失敗ではなく、研究仮説を縮小・棄却するための正規の出口とする。

## 10. 製品境界

PoCが成功しても、次は自動化しない。

- Island / Clusterを自動確定しない。
- 表札を自動確定しない。
- relationをこのkernelだけで確定しない。
- 内部距離やactivationを利用者向けimportance / confidence scoreとして表示しない。
- `held / pending / shelved / Critique`を解消対象として扱わない。
- 戻し検査、空白列挙、A/B照合等のverification scopeを候補kernelだけで削らない。

製品に入れる場合の出力は、原則として「この2〜3枚を一緒に読んでみる」候補、または`too_close / too_far / not_the_same / novelty`の検討契機に留める。

## 11. 次の実行単位

1. 既存dogfoodからsmall-set benchmarkをモデル出力を見る前に固定する。
2. hard positive / hard negative / heldを人間判断と元カードへ戻れる形で保持する。
3. まずA/C/Eを最小baselineとして比較する。
4. D/Fは、一般意味表現と親和図作業固有feedbackの不足を分離してから実装する。
5. 結果を`COGNITIVE-EVAL-01`の既存測定軸へ接続する。
6. 既存性能・安全・データ境界で覆えない判断が生じた場合だけ`ADR-0047` R-1..R-4へ戻る。
