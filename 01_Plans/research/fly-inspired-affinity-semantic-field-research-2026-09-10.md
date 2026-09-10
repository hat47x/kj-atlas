# ハエ脳由来の疎連想認知と親和図法の深層意味近接 — 調査・仮説整理

- Status: Research / Non-normative
- Date: 2026-09-10
- Scope: 親和図法における束ね・島形成に必要な「訴えの近さ」を、LLMとは異なる認知機構でどこまで支援できるか
- Related: `00_Prompt/kj_technique.md`, `00_Prompt/cognitive_frame_and_evolution_criteria.md`, `00_Prompt/ai_kj_execution_procedures.md`, `01_Plans/issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md`, `01_Plans/issues/issue-COGNITIVE-DOGFOOD-01-product-development-cognitive-workbench.md`

> Relatedに含まれる`kj_*`は既存ファイルの参照識別子であり、本書の一般名称ではない。

## 1. 結論

現時点では、**FlyHashそのものを親和図の島作りへ用いても要求水準には届かない**。FlyHashは、与えられた特徴空間の近傍を疎な高次元表現へ写して類似検索を効率化する技術であり、入力特徴に存在しない深層意味を新たに獲得する機構ではない。

一方、ハエのmushroom bodyに着想を得た研究はFlyHashからBioHash、FlyVec、Complyへ進み、固定ランダム射影だけでなく、データからの局所学習、単語・文脈の意味表現、文系列の疎な意味表現まで射程を広げている。したがって「ハエ脳型では深層意味を扱えない」とも結論しない。

検証すべき仮説は次である。

> **一般言語から獲得した疎な意味表現と、親和図作業で人間が行う束ね・分離・違和感・保留の履歴を局所的に統合すれば、表層語彙が異なっていても「一緒に置いて読んでみる価値がある」2〜3枚の候補を、LLMなしまたはLLMより軽量な経路で再現性をもって浮上させられるか。**

この研究仮説を、本書では仮に **Affinity Semantic Field** と呼ぶ。製品名称でも採用済みアーキテクチャでもない。

## 2. 親和図法が要求する「近さ」は通常の文章類似より深い

既存の実行手順では、束ねを分類ではなく**訴えの類似性**で行い、初期の束を2〜3枚程度とする。したがってSemantic Textual Similarityや言い換え検出と同一視しない。

必要な性質は少なくとも次の通りである。

1. **表層を越えた近接** — 語彙や具体例が違っても、背後の問題構造・経験上の訴えを近く読める。
2. **高表層類似の拒否** — 同じ語彙でも、話者・時点・因果方向・肯否・役割が違えば安易に一束へしない。
3. **文脈依存性** — 探究テーマや周囲のカードによって距離感が変わり得る。
4. **集合としての立ち上がり** — pairwise similarityの推移だけで島を決めず、2〜3枚を一緒に読んだときに立ち上がる共通の訴えを扱う。
5. **残余の保持** — どこにも入らないカード、混ぜたくない感覚、まだ言語化できない違和感を誤差として消さない。

PoCの目的は正しい自動クラスタを作ることではなく、**人間の親和図作業前に探索空間を閉じず、読むべき組合せを増やせるか**である。

## 3. 関連研究

### 3.1 FlyHash

Dasgupta, Stevens, Navlakha (Science, 2017) はショウジョウバエ嗅覚回路を類似検索として形式化し、疎な高次元表現によるFlyHashへつなげた。

直接支持されるのは、既に有意味な入力空間が与えられたとき、その局所近傍を軽量に保持・検索する能力である。文字列特徴だけから語彙を越えた「訴え」を自発的に獲得するとは言えない。

Reference: https://pubmed.ncbi.nlm.nih.gov/29123069/

### 3.2 BioHash

Ryali et al. (ICML 2020) はFlyHashのrandom projectionを拡張し、局所的な可塑性則で疎な高次元codeをデータから学ぶBioHashを提案した。

将来、人間が明示的に行った束ね・分離を局所教師信号として使う可能性を示すが、BioHash自体はunsupervised similarity searchであり、親和図法の「訴え」理解を実証したものではない。

Reference: https://proceedings.mlr.press/v119/ryali20a.html

### 3.3 FlyVec

Liang et al. (ICLR 2021) はmushroom bodyに着想を得た数理モデルをword-context相関の学習へ適用し、疎なbinary codeで意味表現を学習した。

この結果は、疎な高次元回路motifが単なる表層hashに限定されず、言語コーパスから意味構造を学習し得ることを支持する。

Reference: https://research.ibm.com/publications/can-a-fruit-fly-learn-word-embeddings

### 3.4 Comply

Figueroa et al. (2025) のComplyはFlyVecへ位置情報を組み込み、single-layer networkでsequence representationを学習する。短文カードへの適用可能性は高まるが、**親和図の島形成に必要なlatent advocacy / set-level coherenceを直接評価した研究ではない**。日本語の親和図カードに対する実証もない。

Reference: https://arxiv.org/abs/2502.01706

### 3.5 APLの局所抑制

Amin et al. (eLife, 2020) は、APL neuronからKenyon cellへのfeedback inhibitionが空間的に局所化されることを示した。

設計motifとしては、文書全体で一つのglobal Top-Nを作るより、現在のカード・島・viewport・探究文脈ごとに候補を競合させる仮説につながる。

Reference: https://elifesciences.org/articles/56954

## 4. 研究上の境界

生物学的な忠実再現は目的にしない。候補とするのは、sparse expansive representation、winner-take-all/local competition、local plasticity、novelty/familiarityを分離可能な状態、複数の独立した連想空間といった計算motifである。

また「ハエ脳型 = 非LLM」「軽量 = 高品質」とはみなさない。深層意味の獲得には一般言語経験が必要で、学習・更新・配布まで含めた総コストを評価する。

目的は親和図法による認知を支援することであり、Fly-inspired方式の採用自体ではない。小型Transformer系sentence encoder等が同じlocal/offline条件で明らかに優れるなら、それを比較結果として受け入れる。

## 5. Affinity Semantic Field 仮説

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

一般意味表現と親和図作業固有の学習を分ける。前者は「言葉として何が近いか」、後者は「この探究で何を一緒に読んだ／読まなかったか」を扱う。

Phase 1では固定表現・固定seedとし、`grouped / separated / critique / held`を学習せずledgerとして収集する。Phase 2でそのledgerをoffline再生し、適応型表現の独立増分を比較する。

## 6. pairではなく2〜3枚の集合を評価する

A≈B、B≈CからA/B/Cを同一島と推移的に決めない。pair retrievalに加えてsmall-set coherenceを独立評価する。

- **hard positive**: 表層語彙の重なりは小さいが、一緒に読んでみる価値がある2〜3枚。
- **hard negative**: 語彙・固有名詞・主題は似るが、訴え・因果方向・時点・立場が異なり一緒にしない2〜3枚。
- **held / ambiguous**: 人間自身もまだ束ねを確定しない組合せ。

正解を自動的な「同じ島」と定義せず、candidateとして再提示する価値を評価する。

## 7. PoC比較系

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

## 8. 評価軸

- **R1 deep-semantic candidate recall**: hard positiveを候補へ回収できるか。
- **R2 surface-decoy rejection**: 高表層類似のhard negativeを近いというだけで提示し続けないか。
- **R3 singleton/residual survival**: 孤立・少数・heldカードを強制回収しないか。
- **R4 set-level coherence**: 2〜3枚として成立する候補と異質カード混入を区別できるか。
- **R5 wording stability**: 軽微な言い換えで候補が崩れすぎないか。
- **R6 affinity-feedback increment**: 束ね・分離・Critique等の履歴に独立増分があるか。
- **R7 continuous-local budget**: CPU/memory/index更新が常時local運用に収まるか。
- **R8 cognitive-control increment**: 発見、残余保持、早期収束耐性、注意再配分に実利用上の増分があるか。

## 9. 反証条件

- **F1**: hard positive回収がTF-IDF等の表層基準線から実質的に改善しない。
- **F2**: 意味回収を上げるほどhard negativeも増え、親和的な束ねに必要な分離が保てない。
- **F3**: local sentence encoderに対して品質・latency・memory・配布容易性のいずれにも実質的な利点がない。
- **F4**: 親和図作業履歴への適応が短期的な配置癖へ過学習する。
- **F5**: seed / algorithm version / learned stateを保存しても候補を再現できない。
- **F6**: 候補提示が探索を広げず、最初の機械候補へのanchoringを強める。

これらは失敗ではなく、研究仮説を縮小・棄却するための正規の出口とする。

## 10. 製品境界

PoCが成功しても、Island / Cluster、表札、relationを自動確定しない。内部距離やactivationを利用者向けimportance/confidence scoreへ変換しない。`held / pending / shelved / Critique`を解消対象としない。戻し検査、空白列挙、A/B照合等のverification scopeを候補kernelだけで削らない。

製品出力は原則として「この2〜3枚を一緒に読んでみる」候補、または`too_close / too_far / not_the_same / novelty`の検討契機に留める。

## 11. 三要素牽制による研究段階の境界

| 次元 | 研究段階で固定すること | まだ固定しないこと |
|---|---|---|
| 業務設計 | 人間が意味を立ち上げる候補生成であり、自動島形成ではない | UI導線・常時表示 |
| データ設計 | benchmark/derived signature/実験ledgerはCanonical Graphとは別物 | 永続schema・同期方式・tenant境界 |
| 機能設計 | offline PoCで同一snapshotを比較する | 本番API、worker、provider設定 |

本研究だけを根拠にproduction schema/API/Canonical Graphへ新規型を追加しない。

## 12. 次の実行単位

1. `COGNITIVE-ASSOC-01`のPoC Issueで研究を管理する。
2. 既存dogfoodからsmall-set benchmarkをモデル出力を見る前に固定する。
3. hard positive / hard negative / heldを人間判断と元カードへ戻れる形で保持する。
4. まずA/C/Eを最小baselineとして比較する。
5. D/Fは、一般意味表現と親和図作業固有feedbackの不足を分離してから実装する。
6. 結果を`COGNITIVE-EVAL-01`の既存測定軸へ接続する。
7. 既存性能・安全・データ境界で覆えない判断が生じた場合だけ`ADR-0047` R-1..R-4へ戻る。
