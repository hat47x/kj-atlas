# COGNITIVE-ASSOC-01 Affinity Semantic Field benchmark v0 — 事前登録

- Status: Pre-adjudication frozen
- Date: 2026-09-10
- Issue: `COGNITIVE-ASSOC-01`
- Source manifest: `cognitive-assoc-benchmark-v0-source-manifest.json`
- Rule: **この文書とsource manifestを凍結した後、contrast labelの人間判定が完了するまでsemantic baselineを実行しない。**

## 0. 文書の位置づけ

この文書は研究の根幹を説明する上位文書ではなく、`COGNITIVE-ASSOC-01`で定めた検証方針を**評価データへ落とす下位の実施仕様**である。

研究の目的・守るべき原則・必要な認知能力・方式比較の意味は、先に次を読む。

1. `01_Plans/issues/issue-COGNITIVE-ASSOC-01-affinity-semantic-field-poc.md`
2. `01_Plans/research/fly-inspired-affinity-semantic-field-research-2026-09-10.md`
3. 本文書
4. `cognitive-assoc-benchmark-v0-adjudication-selection.md`
5. preparer / selector / adjudication packetの各実装

この順序により、benchmarkの件数やlabel定義といった詳細が研究目的そのものに見えないようにする。

## 1. 目的

親和図法における束ね・島形成で必要な「訴えの近さ」を、Fly-inspired sparse representation、一般的なlocal sentence encoder、将来のaffinity-specific association layerで比較するため、**モデル結果を見る前に評価条件を固定する**。

ここで測るのは自動クラスタリング精度ではない。人間が意味を立ち上げる前に、**一緒に置いて読んでみる価値のある2〜3枚を候補として回収できるか**を測る。

## 2. retrospective observational benchmarkとする理由

新しい「正解島」をAIが作って評価すると、評価対象と教師が同じ認知系になりやすい。そこでv0は、今回のFly-inspired研究より前から存在し、`textReviewed=true`で保存されているdogfood文書の島形成を**過去の観測**として使う。

ただし既存島を普遍的な正解とは扱わない。

- 同じ複数カード島だった → `observedPositiveSet`
- 一枚だけで島を形成していた → `observedSingletonIsland`
- 違う島だった → hard negativeとはまだ言わない

単独島を`held / pending / shelved`等の残余状態へ読み替えない。また、親和図では別島のカード間にも意味ある関係が成立し得るため、cross-island組合せは`contrast pool`として人間判定へ回す。

判定値は `hard_negative / related_but_separate / ambiguous_or_held / exclude` の四値とし、モデル出力を見る前に固定する。

## 3. source snapshot

モデル入力候補は次の2文書だけとし、blob SHAはsource manifestを正本とする。ここに現れる既存の文書ID・過去本文はhistorical evidenceであり、今回の用語一般化のために改変しない。

### Meta R1

`doc_cognitive_dogfood_meta_r1`

- reviewed cards: 17
- 既存島: 5つの複数カード島 + 1つの単独島
- 主な性質: 内部dogfoodの帰属不能性、時点差、評価汚染、自己強化と第三者接地、文化体系の独立増分、制御と摩擦

### Dogfood R3

`doc_kj_atlas_dogfood_r3`

- reviewed cards: 12
- 既存島: 4つの複数カード島 + 1つの単独島
- 主な性質: 文書追従失敗、方法論の強制力不足、空白の資源化不足、feedback/責任主体不足、段階的探究プロセスの自己言及的制約

特に`c07/c08/c09`は、warning、自律性、UI gateという表層上異なる対象が、既存の親和的な束ねでは同じ思考習慣として置かれており、表層近傍と深層意味表現の差を観察しやすい。

## 4. モデルに見せるもの / 隠すもの

モデルに見せるのは `documentId / cardId / text` だけとする。

次は隠す。

- x / y
- island ID / title / geometry
- relation edge
- reading order
- narrative
- claim type
- source metadata

座標や島タイトルを与えると、意味表現ではなく既存配置を復元するだけでpositiveを当てられるためである。

## 5. challenge positive

モデル実行前に次を固定する。

### Meta R1

- `c01 + c03 + c04`: 認知増分を独立に帰属できない問題
- `c10 + c11 + c12`: 内部自己確認を外部現実へ開く問題
- `c13 + c14 + c15`: 外部体系が本当に独立した探索増分を持つかという問題

### R3

- `c01 + c02 + c03`: 文書追従問題の異質な複数原因
- `c07 + c08 + c09`: 空白を構造的情報として扱わず停滞させる思考習慣
- `c10 + c11`: feedback loopと修正責任主体の不足

上記の説明は評価者側だけが保持し、モデル入力へは入れない。

## 6. 単独島

Meta R1 `c16`とR3 `c12`は、一枚だけの島として成立している。

> 「近いカードが見つからない = モデル失敗」とはしない。

ただし`held / pending / shelved`だったとも解釈しない。観測できるのは、複数カード島へ吸収されず一枚で島を形成していた事実だけである。候補器が単独島を機械的に吸収し続けないかを`singleton preservation`として観察する。

## 7. contrast pool

### Pair pool

同一文書内のreviewed cardについて、既存島を共有しない全unordered pairを列挙する。単独島も互いに独立した島として扱う。

### 2+1 pool

複数カード島の中から2枚を選び、別島のreviewed cardを1枚足したtripletを全列挙する。

島外であること自体はnegative labelの根拠にならない。

## 8. 人間判定時の問い

1. 一緒に置くと、各カードが言う具体的な「何が起きているか」を潰さないか。
2. 共通の分類名ではなく、一つの訴えとして表札を書けそうか。
3. 表札を各カードへ戻したとき、どれか一枚が「それではない」と言いそうか。
4. 時点・因果方向・話者・対象・肯否の違いを、似た語彙が覆い隠していないか。
5. 違いは別物なのか、関係はあるが別島なのか、それともまだ保留すべきか。

理由を一文で書けない場合は`ambiguous_or_held`を許す。

## 9. v0でまだ主張しないこと

- 親和図法の熟練者一般の正解を表すとは主張しない。
- 日本語の親和図カード全般へ一般化しない。
- island co-membershipをsemantic ground truthと同一視しない。
- observed positiveを全部近傍上位へ出すことを「良い親和的な束ね」と定義しない。
- 単独島を残余・保留・異常値と同一視しない。
- Fly-inspired方式に有利なbenchmarkだとは主張しない。

v0は方式の明白な不足を早期に反証するための小さな内部benchmarkである。

## 10. baselineを実行してよい条件

- [x] source path / blob SHAが凍結されている。
- [x] `textReviewed=true`だけをモデル入力対象としている。
- [x] model-visible fieldsが凍結されている。
- [x] observed positive / singleton island / challenge subsetが凍結されている。
- [x] contrast pool生成規則が凍結されている。
- [ ] contrast poolの人間判定が凍結されている。
- [ ] 判定後のbenchmark revisionがcommitされ、以後変更しないことが明示されている。

最後の2項が満たされるまではsemantic resultを生成しない。

## 11. benchmark v1への拡張条件

v0結果を見てから同じファイルへ例を追加しない。必要ならv1を新設する。

- 別領域の親和図文書
- 人間が最初からbenchmark用に束ねたblind case
- 2〜3人の独立判定と不一致保持
- explicit `not_the_same / too_close / too_far / held`履歴を持つcase
- 文面paraphraseによるstability case

v0とv1は混ぜず、v0を履歴として残す。
