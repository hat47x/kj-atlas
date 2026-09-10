# Issue: COGNITIVE-ASSOC-01 KJ Semantic Fieldの深層意味近接PoCを行う

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: In Progress
- Source Issue: `COGNITIVE-EVAL-01`
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/research/`, `01_Plans/dogfood/`, `01_Plans/issues/`, PoC用の非製品コード
- Related ADR/Spec: `ADR-0047`, `ADR-0046`, `ADR-0067`, `00_Prompt/domain.md`, `00_Prompt/kj_technique.md`, `00_Prompt/cognitive_frame_and_evolution_criteria.md`, `00_Prompt/ai_kj_execution_procedures.md`, `COGNITIVE-EVAL-01`, `COGNITIVE-DOGFOOD-01`
- Norms: `DOM-CORE-01`, `DOM-CORE-02`, `DOM-CORE-03`, `DOM-CORE-04`
- Expected verification level: docs-check + reproducible offline benchmark
- Working branch: `research/cognitive-assoc-01-kj-semantic-field-20260910`
- Research record: `01_Plans/research/fly-inspired-kj-semantic-field-research-2026-09-10.md`

## 三要素整合（ADR-0067）

- **業務設計（Business）**: KJ法の束ねでは、語彙類似ではなく「訴えの近さ」を2〜3枚の小さな集合として感じ取り、人間が表札を書く前の探索を支える必要がある。本PoCはその候補生成を検証し、自動島形成は行わない。
- **データ設計（Data）**: benchmark annotation、derived signature、実験結果は研究データであり、Document / Consensus Graphの正本ではない。PoCを理由にproduction schemaへ型を追加しない。
- **機能設計（Function）**: 最初はoffline harnessだけで比較する。本番API/UI/worker/provider契約は定義しない。既存境界を越える必要が出た場合だけ、`ADR-0047` R-1..R-4へ戻す。

## 課題

- 現在の問題:
  - `suggest_card_groups` は「分類ではなく訴えの類似性」で束ねることを要求するが、現在のAI実行経路は主にLLMを前提としている。
  - FlyHashは軽量な疎近傍検索として有望だが、それだけでは入力特徴に存在しない深層意味を獲得できない。
  - FlyVec / Comply等は疎な生物模倣motifから言語意味表現まで進める可能性を示すが、KJ法のlatent advocacy、hard negative、2〜3枚のset-level coherenceに届くかは未検証である。
  - 「軽量だから導入する」「ハエ脳だから独自性がある」という理由では、KJ法の要求水準を満たしたことにならない。
- 利用者または開発への影響:
  - 要求水準に届けば、provider=`none`でも常時localに候補関係・違和感の契機を浮上させ、LLMとは異なる認知経路を持てる可能性がある。
  - 届かなければ、Fly-inspired方式は近傍index等の限定用途へ縮小し、深層意味候補にはlocal sentence encoderまたはLLMを使う方が単純である。

## 検証仮説

> 一般言語から得たsemantic representationに、KJ作業のgroup/separate/Critique/hold等の局所文脈を重ねることで、表層語彙が異なるhard positiveを回収しつつ、高表層類似のhard negativeと、単独島・保留・残余を保護できる。

仮説を一度に全部実装せず、次の問いを順に分離する。

1. sparse expansionだけで表層baselineを超えるか。
2. 深層意味表現が必要なら、FlyVec/Comply-inspired encoderに研究価値があるか。
3. 一般sentence encoderに対し、KJ固有feedback / graph / space / historyを加えることに独立増分があるか。
4. その増分が利用者の探索を広げるのか、機械候補へのanchoringを強めるのか。

## 対応方針

### 実施すること

1. モデル結果を見る前に、既存dogfoodからsmall-set benchmarkを作成する。
2. benchmarkは次を含める。
   - hard positive: 表層語彙が離れているが、一緒に読んでみる価値がある2〜3枚
   - hard negative: 語彙は似るが、訴え・因果方向・時点・立場が異なる2〜3枚
   - held / ambiguous: 人間も確定しない組合せ
   - singleton island: 既存KJで一枚だけの島として成立したカード
3. 各annotationは元カードID、source snapshot、判断時点へ戻れるようにする。
4. 最初のbaselineを次の3系に限定して実行する。
   - A: character/word n-gram + TF-IDF cosine
   - C: FlyHash-like sparse expansion + WTA
   - E: strong local sentence encoder
5. A/C/Eの結果から、D（learned sparse semantic encoder）を作る意味があるかを判定する。
6. Dに進む場合も、FlyVec/Complyの論文実装を無批判に移植せず、日本語短文/KJカードの入力条件を明示する。
7. F（KJ-specific multi-channel extension）は、semantic channel単体を評価してから追加する。
8. 評価は`COGNITIVE-EVAL-01`のM1/M3/M4/M7/M9へ接続する。
9. PoCの全方式で同じsource snapshotと事前固定benchmarkを使う。
10. seed、algorithm version、parameter setを記録し、同一入力から候補を再生成できるようにする。

### 実施しないこと

- benchmark作成時にモデル候補を見てpositive/negativeを調整しない。
- Fly-inspired方式を採用すること自体を成功条件にしない。
- LLMまたはsemantic kernelにIsland / Cluster / Labelを自動確定させない。
- 内部similarity / activation / confidenceを利用者向け内容スコアとして表示しない。
- held / ambiguousを評価都合でpositive/negativeへ強制分類しない。
- 単独島をpending / held / shelvedへ読み替えない。
- kernel候補を理由に、戻し検査・空白列挙・A/B照合等の規範的verification scopeを削らない。
- PoCのためだけにDocument schema、Consensus Graph、production APIを変更しない。

## 実行タスク

- [x] **T1 Research**: FlyHash / BioHash / FlyVec / Comply / APL局所抑制とKJ要求の差を整理する。
  - 成果: `01_Plans/research/fly-inspired-kj-semantic-field-research-2026-09-10.md`
- [ ] **T2 Benchmark freeze**: dogfoodからsmall-set benchmark v0を作り、model実行前のcommitで固定する。
  - [x] T2a: `textReviewed=true`のMeta R1 / R3をblob SHAで固定し、29枚のblind input、既存複数カード島、単独島、challenge positiveを事前登録した。
  - [x] T2b: cross-island pair 173件 / 2+1 candidate 346件の生成規則と期待件数を固定した。
  - [x] T2c: 座標・島タイトル・edge・source等をmodel inputから除外し、未レビューcardやblob driftをfail-closedにする準備器とunit testを追加した。
  - [ ] T2d: contrast poolをモデル出力を見る前にMaintainerが`hard_negative / related_but_separate / ambiguous_or_held / exclude`へ判定し、benchmarkをadjudicated revisionとして凍結する。
- [ ] **T3 Baseline harness**: A/C/Eを同じinterfaceで実行できるoffline harnessを作る。T2d完了前はsemantic resultを生成しない。
- [ ] **T4 Baseline evaluation**: deep-semantic recall / surface-decoy rejection / singleton・residual survival / wording stability / CPU budgetを比較する。
- [ ] **T5 Learned sparse gate**: T4を根拠にDを実装する価値をProceed / Hold / Rejectで判断する。
- [ ] **T6 KJ-specific increment**: Proceed時のみFを追加し、group/separate/Critique/hold/graph/space/historyの寄与をablationする。
- [ ] **T7 Cognitive dogfood**: 候補提示あり/なしで探索の増分とanchoringを比較する。
- [ ] **T8 Architecture decision**: 結果を、`no adoption / retrieval-only / candidate-cognition layer / ADR trigger` のいずれかへ変換する。

## 評価軸

研究内部では数値を用いる。これは`DOM-CORE-04`の利用者向け内容序列化とは分ける。

- **R1 Deep-semantic candidate recall**: hard positiveの候補回収。
- **R2 Surface-decoy rejection**: hard negativeを語彙類似だけで近接扱いしないこと。
- **R3 Singleton / residual survival**: singleton / held / minority cardsを強制回収しないこと。v0の観測対象はsingleton islandであり、explicit held/pending/shelvedは将来caseで分ける。
- **R4 Set-level coherence**: pairの近さだけでなく2〜3枚集合としての適合を扱えること。
- **R5 Wording stability**: 軽微な言い換えで候補が崩れすぎないこと。
- **R6 KJ-feedback increment**: KJ固有履歴の追加に独立した改善があること。
- **R7 Continuous-local budget**: CPU/memory/index更新が常時local運用候補として現実的であること。
- **R8 Cognitive-control increment**: 発見・残余保持・早期収束耐性・注意再配分に実利用上の増分があること。

## 判定ゲート

### Gate A — 表層類似を越えたか

- CまたはDがAに対しhard positiveを改善していることを確認する。
- 改善と同時にR2/R3が崩れる場合は「深層意味到達」と判定しない。

### Gate B — Fly-inspired方式に独立した理由があるか

Eと比較し、品質・continuous-local負荷・更新容易性・説明可能性・KJ-feedbackへの適応の少なくとも一つに検証可能な利点があるかを見る。

Eの方が単純で同等以上なら、Fly-inspired方式を意味層として採用しない。

### Gate C — KJ固有情報に増分があるか

一般意味表現だけの場合とFを比較する。Fの改善がなければ、graph/space/historyをsemantic kernelへ混ぜず、既存KJ構造として別に保持する。

### Gate D — 認知拡張になっているか

offline精度が高くても、dogfoodで候補へのanchoring、残余消失、機械的な束ねが増えるなら製品導入しない。

## 受入条件

- [ ] model出力を見る前にsmall-set benchmark v0のcontrast判定までcommitで固定されている。
- [ ] A/C/Eが同じsnapshot・同じ候補数条件で比較できる。
- [ ] hard positiveだけでなくhard negative / held-or-ambiguous / singletonを含む結果が残る。
- [ ] pairwise retrievalと2〜3枚set-level評価を区別している。
- [ ] `COGNITIVE-EVAL-01`の該当軸へ結果を戻せる。
- [ ] seed / algorithm version / parameter setから再実行可能である。
- [ ] Fly-inspired方式が不利だった場合もReject/縮小判断をそのまま記録する。
- [ ] **AIまたは非LLM kernelが人間の明示操作なしに島・表札・関係を確定しない。**
- [x] production schema/APIを変更していない。必要になった場合は本issueを止め、`ADR-0047`の再起票条件を確認する。

## 2026-09-10 事前凍結時点の検証記録

- sourceは今回の研究より前に存在する`doc_cognitive_dogfood_meta_r1`と`doc_kj_atlas_dogfood_r3`を使用する。
- 両sourceの全29カードが`textReviewed=true`であることを確認した。
- Meta R1は5つの複数カード島 + 1つの単独島、R3は4つの複数カード島 + 1つの単独島としてsource blobを確認した。
- model-visible fieldは`documentId / cardId / text`だけに固定した。
- 既存の島外であることをhard negativeとみなさず、人間判定前のcontrast poolへ置く。
- 準備器のsynthetic unit testで、blind field限定、未レビュー拒否、blob SHA不一致拒否、co-island pair除外、異なるsingleton間のcontrast維持、challenge setの島跨ぎ拒否、membership漏れ拒否を確認した。
- この実行環境からGitHubへのDNS解決ができずremote branchをcloneできなかったため、実sourceを用いたCLI end-to-end実行は未実施。source blob自体はGitHub connectorで正本を確認した。T2d後のbaseline開始前に、通常の開発環境で実source prepを再実行する。
- **semantic baseline / embedding / FlyHash候補はまだ一度も生成していない。** benchmark labelはmodel-blindのままである。

## 責任分界

- 実行責任（R）: AI agent / Maintainer
- 受入判定（A）: Maintainer
- 契約チェックポイント: `DOM-CORE-01..04`, proposal-only, `ADR-0046`, `ADR-0047`, `ADR-0067`
- 停止基準: benchmark未固定のままモデル比較を始める、Canonical Graph変更が必要になる、既存性能予算を越える、または評価結果から都合よくannotationを変更する必要が生じた場合はProceedしない。

## AIレーン宣言

- Lane: N/A（主対象は非生成・local cognition PoC。LLMは比較用reference armのみ）
- データ境界: PoCはlocal/offlineを既定とし、dogfoodカードを外部providerへ送らない。外部LLM比較を行う場合は既存SafeMode/投影/送信境界に従い、別途許可された入力だけを使う。
- SafeMode/監査/人間レビュー境界: proposal-only、人間確定、非序列化を維持する。

## 検証計画

- 実行する確認:
  - benchmark固定commitの確認。
  - A/C/Eの同条件再実行。
  - hard positive / hard negative / held-or-ambiguous / singletonの誤り事例レビュー。
  - seed固定によるreproducibility確認。
  - CPU latency / memory / index sizeの実測。
  - `COGNITIVE-EVAL-01`への認知dogfood結果の戻し。
- 期待結果:
  - 「ハエ脳方式を採用できた」ではなく、KJ法の深層意味近接に対してどの層が必要かを反証可能な証拠で判断できる。

## 補足

本issueは新ADRを起票しない。`ADR-0047`のexecution-first方針に従い、先に実証する。PoCの結果として新しい永続状態、production API、provider、安全境界、性能予算超過等が必要になった場合のみR-1..R-4を確認して設計判断へ戻る。
