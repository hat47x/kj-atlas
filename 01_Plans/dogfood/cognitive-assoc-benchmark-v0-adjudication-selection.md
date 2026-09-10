# COGNITIVE-ASSOC-01 benchmark v0 — contrast人間判定の事前抽出規則

- Status: Pre-model frozen
- Date: 2026-09-10
- Parent preregistration: `cognitive-assoc-benchmark-v0-preregistration.md`
- Source manifest: `cognitive-assoc-benchmark-v0-source-manifest.json`
- Rule: 本文書の抽出規則を固定した後も、semantic baseline / embedding / FlyHash候補を見るまで変更しない。

## 1. なぜ519件を全件判定しないか

v0の完全なcontrast母集団は、cross-island pair 173件と2+1 candidate 346件、計519件である。

この母集団は後からcandidateを都合よく作り直さないための**監査母集団**として全件保持する。一方、519件すべてを一人のMaintainerが連続して意味判定すると、単純な作業量が大きく、後半ほど判断基準が粗くなる危険がある。

そこでv0の人間判定は、semantic modelとは無関係な決定論的抽出でbounded review setを先に作る。

重要なのは、**semantic modelが難しいと感じた例を後から選ぶのではなく、人間判定対象もモデル実行前に固定すること**である。

## 2. 二つの抽出stratum

### U: uniform-hash stratum

candidate IDのSHA-256だけを使い、hash値の昇順から抽出する。

- pair: 16件
- 2+1: 16件

カード本文を見ずに選ぶため、特定テーマや語彙へ恣意的に寄せない。

これは母集団比率の厳密推定を目的とするrandom sampleではない。seed管理を不要にし、誰が実行しても同じ集合になる**再現可能な擬似一様抽出**である。

### L: lexical-stress stratum

表層的には近く見えるが、既存の親和図では別島だった例を意図的に多く含め、R2 `Surface-decoy rejection`へ圧力を掛ける。

選定に使うのはsemantic encoderではなく、次の固定した文字n-gram overlapだけとする。

1. Unicode NFKC正規化
2. Unicodeの英数字・日本語文字だけを残し、空白・句読点・記号を除く
3. 連続する3文字の集合を作る
4. pairはJaccard overlapを計算する
5. 2+1は、既存島内pairへ追加されたoutsiderと2枚それぞれのJaccardの大きい方を用いる
6. 値の降順、同値ならcandidate ID昇順で選ぶ

抽出数:

- pair: 16件
- 2+1: 16件

このoverlap値は**人間判定パケットへ表示しない**。判定者へ「この組合せは表層的に近いはずだ」と先入観を与えないためである。

## 3. dedupと最終件数

UとLで同じcandidateが選ばれた場合は一件へ統合する。

したがって最終human review setは最大64件、最小32件となる。実件数は選定scriptの出力で固定する。

選定理由はmachine-readable artifactには保持してよいが、人間がカード内容を判定する本文には原則表示しない。

## 4. このsamplingから言えること / 言えないこと

### 言えること

- 表層語彙に依存しない事前抽出(U)で、cross-island candidateをどう読むか。
- 表層類似が高いstress set(L)で、単純なsimilarityが親和的な束ねにおける分離を壊しやすいか。
- hard negative / related-but-separate / ambiguous-or-heldが実際に存在するか。
- semantic model比較前に、評価すべきcontrast caseを固定できる。

### 言えないこと

- 519件全体における各labelの母比率。
- 親和図カード一般のhard-negative発生率。
- L stratumの成績を通常データ分布での平均性能と読み替えること。

結果はU/Lを分けて報告し、単一のaccuracyへ畳まない。

## 5. 人間判定はモデルblindのまま行う

人間パケットには以下だけを出す。

- candidate ID
- document ID
- 2枚または3枚のcard ID
- card本文
- 4つの選択肢
- 任意のreason欄

次を出さない。

- U/Lどちらで選ばれたか
- lexical overlap値
- source island ID / title
- 座標
- relation edge
- semantic score / distance
- model ranking / explanation

## 6. 判定選択肢

- `hard_negative`
  - 一束へ寄せるとカードの訴えを壊す。特に表層類似へ引かれて混ぜないことが重要。
- `related_but_separate`
  - 関係・連続性はあるが、一束として代弁することとは別。
- `ambiguous_or_held`
  - 現時点で近い/遠いを閉じない。理由を言語化できなくてもよい。
- `exclude`
  - v0のcontrast評価に使うには条件が不適切。

この四値には優劣を置かない。

## 7. baseline gate

次がcommitされるまでsemantic baseline gateは閉じる。

1. full contrast pool 519件がsource manifest規則から再生成できる。
2. 本文書のU/L規則でbounded review setが決定論的に再生成できる。
3. bounded review setの人間判定が完了している。
4. 判定artifactのSHA-256と件数が凍結されている。

判定後に例を追加したくなった場合はv0を変更せず、v1または別のstress suiteへ追加する。
