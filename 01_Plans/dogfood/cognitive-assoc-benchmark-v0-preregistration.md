# COGNITIVE-ASSOC-01 KJ Semantic Field benchmark v0 — 事前登録

- Status: Pre-adjudication frozen
- Date: 2026-09-10
- Issue: `COGNITIVE-ASSOC-01`
- Source manifest: `cognitive-assoc-benchmark-v0-source-manifest.json`
- Rule: **この文書とsource manifestを凍結した後、contrast labelの人間判定が完了するまでsemantic baselineを実行しない。**

## 1. 目的

KJ法の束ね・島形成に必要な「訴えの近さ」を、Fly-inspired sparse representation、一般的なlocal sentence encoder、将来のKJ-specific association layerで比較する。

ここで測るのは自動クラスタリング精度ではない。人間が意味を立ち上げる前に、**一緒に置いて読んでみる価値のある2〜3枚を候補として回収できるか**を測る。

モデル結果を見てからbenchmarkを有利な形へ調整することを防ぐため、入力source・観測済みpositive・残余・challenge subset・contrast pool生成規則を先に固定する。

## 2. v0をretrospective observational benchmarkとする理由

新しい「正解島」をAIが作って評価すると、評価対象と教師が同じ認知系になりやすい。そこでv0は、今回のFly-inspired研究より前に存在し、`textReviewed=true`で保存されているdogfood文書の島形成を**過去の観測**として使う。

ただし、既存の島を普遍的な正解とは扱わない。

- 同じ島だった → `observedPositiveSet`
- 単独で残っていた → `observedResidual`
- 違う島だった → **hard negativeとはまだ言わない**

KJ法では、別島のカード間にも意味ある関係が存在し得る。したがってcross-island組合せは`contrast pool`とし、モデル出力を見る前に人間が次のいずれかへ判定する。

- `hard_negative`: 表層上は引き寄せられやすいが、訴え・時点・因果方向・立場等が違い、一束として寄せないことが重要
- `related_but_separate`: 関係はあるが、同じ束にすることとは別
- `ambiguous_or_held`: 現時点では近い/遠いを閉じない
- `exclude`: v0の判定素材として不適切

## 3. source snapshot

v0のモデル入力候補は次の2文書だけとする。blob SHAはsource manifestを正本とする。

### 3.1 Meta R1

`doc_cognitive_dogfood_meta_r1`

- reviewed cards: 17
- 既存島: 5つの複数カード島 + 1つの単独島
- 特徴:
  - 内部dogfoodの有用性と帰属不能性
  - 時点差・訂正履歴
  - 評価汚染
  - 自己強化と第三者接地
  - 文化体系の独立増分
  - 制御が価値保護と摩擦の両方になり得る残余

語彙が離れた具体例から共通する評価構造を立ち上げた島を含み、deep-semantic candidateの初期検査に向く。

### 3.2 Dogfood R3

`doc_kj_atlas_dogfood_r3`

- reviewed cards: 12
- v0で確実に読み取れた既存島: 4つ
- 特徴:
  - 文書追従失敗の複数原因
  - 方法論の存在と強制力の欠如
  - 警告・自律性・全か無かgateを「空白の資源化不足」として束ねる
  - 検出から修正へのfeedback/責任主体不足

特に`c07/c08/c09`は、表層トピックが「warning」「自律性」「UI gate」と離れている一方、既存KJでは同じ思考習慣の島に置かれている。FlyHash的表層近傍と、より深いsemantic representationの差を観察しやすい。

`c12`は取得済みexcerptから完全な島/残余状態を確定できなかったため、推測で補わずv0 labelから除外する。

## 4. モデルに見せるもの / 隠すもの

### 見せる

- `documentId`
- `cardId`
- `text`

### 隠す

- x / y
- island ID / title / geometry
- relation edge
- reading order
- narrative
- claim type
- source metadata

座標や島タイトルを与えると、意味表現ではなく既存配置を復元するだけでpositiveを当てられるためである。

## 5. challenge positiveの事前固定

全observed positiveに加え、「単なる固有名詞一致だけでは取り切れないか」を見るchallenge subsetをモデル実行前に固定する。

### Meta R1

- `c01 + c03 + c04`
  - 内部dogfoodが状態を残していること、対照条件がないこと、段階的問いが交絡することを、**認知増分を独立に帰属できない**という一つの問題として読む。
- `c10 + c11 + c12`
  - 自己dogfoodの自己強化、第三者価値の未実証、第三者の「使わない」を改善要求へ翻訳する危険を、**内部自己確認を外部現実へ開く**という訴えとして読む。
- `c13 + c14 + c15`
  - 荘子/KJとの同型性、五行の限定利用、独立性検査候補を、**文化体系が本当に独立した探索増分を持つか**として読む。

### R3

- `c01 + c02 + c03`
  - 文書追従問題を、非強制プロセス・CI warningジレンマ・認知バイアスという異質な原因から読む。
- `c07 + c08 + c09`
  - warning、L1→L2移行条件、管理面UI gateという異なる対象を、**「空白」を構造的情報として扱わず停滞させる思考習慣**として読む。
- `c10 + c11`
  - 一方通行の開発過程と、検出後の修正責任主体不在を、feedback loop欠如として読む。

これらは「正解の意味」をモデルへ与えるための説明ではない。説明本文はモデル入力から除外し、評価者側だけが保持する。

## 6. residualの扱い

Meta R1 `c16`は既存文書で単独島として残っている。

> 「近いカードが見つからない = モデル失敗」とはしない。

v0では、候補器が`c16`を無理に他島へ吸収し続けないかを`residual survival`として別に観察する。

これは`DOM-CORE-01`保留、`DOM-CORE-02`違和感、`DOM-CORE-04`非序列化、および`COGNITIVE-EVAL-01` M3に接続する。

## 7. contrast poolの作り方

人間が都合のよいhard negativeだけを選ばないよう、候補母集団の生成規則も先に固定する。

### Pair pool

同一文書内のreviewed cardについて、既存島を共有しない全unordered pairを列挙する。

### 2+1 pool

複数カード島の中から2枚を選び、別島のreviewed cardを1枚足したtripletを全列挙する。

このpoolからどれをhard negativeへ採用するかは**モデル候補を見ずに**判定する。

島外であること自体はnegative labelの根拠にならない。既存relationが島間に張られている場合でも同じである。

## 8. 人間判定時に見る問い

contrast candidateごとに次を順に見る。

1. 一緒に置くと、各カードが言っている具体的な「何が起きているか」を潰さないか。
2. 共通の分類名ではなく、一つの訴えとして表札を書けそうか。
3. 表札を各カードへ戻したとき、どれか一枚が「それではない」と言いそうか。
4. 時点・因果方向・話者・対象・肯否の違いを、似た語彙が覆い隠していないか。
5. 違いは「別物」なのか、「関係はあるが別島」なのか、それともまだ保留すべきか。

理由を一文で書けない場合は`ambiguous_or_held`を許す。hard negativeへ無理に寄せない。

## 9. v0でまだ主張しないこと

- KJ熟練者一般の正解を表しているとは主張しない。
- 日本語KJカード全般へ一般化しない。
- island co-membershipをsemantic ground truthと同一視しない。
- observed positiveを全部近傍上位へ出すことを「良いKJ」と定義しない。
- Fly-inspired方式に有利なbenchmarkだとは主張しない。

v0は、方式の明白な不足を早期に反証するための**小さな内部benchmark**である。

## 10. baselineを実行してよい条件

次を満たすまでA/C/E baselineを走らせない。

- [x] source path / blob SHAが凍結されている。
- [x] `textReviewed=true`だけをモデル入力対象としている。
- [x] model-visible fieldsが凍結されている。
- [x] observed positive / residual / challenge subsetが凍結されている。
- [x] contrast pool生成規則が凍結されている。
- [ ] contrast poolの人間判定が凍結されている。
- [ ] 判定後のbenchmark revisionがcommitされ、以後変更しないことが明示されている。

最後の2項が満たされるまでは、baseline harnessを実装しても**semantic resultを生成しない**。

## 11. benchmark v1への拡張条件

v0結果を見てから同じファイルへ例を追加しない。次の拡張が必要なら`v1`を新設する。

- 別領域のKJ文書
- 人間が最初からbenchmark用に束ねたblind case
- 2〜3人の独立判定と不一致保持
- explicit `not_the_same / too_close / too_far / held`履歴を持つcase
- 文面paraphraseによるstability case

v0とv1は混ぜず、v0を履歴として残す。
