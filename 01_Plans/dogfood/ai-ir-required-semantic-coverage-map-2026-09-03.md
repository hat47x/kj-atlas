# AI route 必要意味coverage対応表

- Date: 2026-09-03
- Scope: `AI-IR-SCALE-01` / `AI-IR-PROJECTION-01` の内部検証
- Status: R17 dogfood observation
- External evidence: No

## 1. 目的

R16で、LLM入力IRのcoverageを「IRに存在する全フィールドが最終promptへ出たか」で判定しないことを決めた。

本表では、移行済み4 routeについて、**既存のADR・仕様・受入条件がそのtaskに必要だと明示している意味**を先に整理し、300枚代表規模で現在どこまで測れているかを対応づける。

ここで新しい入力要件を追加しない。実装がたまたま運んでいる情報と、route契約が必要としている情報を区別する。

## 2. 判定語彙

- **必須**: ADR、仕様、既存IssueのACが、そのrouteの目的達成または人間判断の保護に必要だと明示している。
- **補助**: 現行promptが運んでいるが、それ単独を欠陥判定の基準にはしない。
- **対象外**: 当該routeでは使わないことが仕様で明示されている。
- **代表規模で測定済み**: 300カード・30島fixtureで source → IR → final prompt の件数差を測れている。
- **未測定**: 小規模integration testでは検証していても、300枚代表規模で必要意味の保持を確認していない。

## 3. detect-contradiction

### 利用仕事

対象2カードが本当に矛盾するかを提案しつつ、人間がすでに確定または保留した矛盾を新規発見として再提示しない。

### 必要意味

| 意味 | 根拠 | 現在のscale確認 | 判定 |
| --- | --- | --- | --- |
| `cardA` / `cardB` のid・本文 | route入力そのもの | promptでは直接保持される | 必須 |
| 対象2カード間の `evidenceLinks` | `AI-IR-PROJECTION-01` AC-1 | 300枚の対象カード選外ケースは未測定 | 必須 |
| `contradictionState` の `confirmed` / `held` | AC-1 / IR spec §2.2B rule 6 | 300枚の対象カード選外ケースは未測定 | 必須 |
| 対象2カードに接するcard relation | IR prompt context | 代表規模で対象pairを固定した測定なし | 補助 |
| 対象2カードが属する島 | 現行prompt context | 代表規模で対象pairを固定した測定なし | 補助 |
| coordinates | IR spec §2.2.1 | 渡さない | 対象外 |

### R17で検出した欠落

現行 `_detect_contradiction_ir()` は、対象2カードがDocument内に存在する場合、その2枚を通常カードより優先しない。`MAX_CARDS=200` の中心性選択で対象カードが落ちると、そのカードを端点に持つevidence linkも `_prune_references()` で落ちる。

したがって、カード本文はroute入力としてprovider promptへ残っていても、**人間の `confirmed` / `held` 判断だけが消える**経路がある。

これはAC-1の必要意味欠落なので `AI-IR-FOCUS-PRESERVATION-01` としてP1起票した。

## 4. suggest-card-groups

### 利用仕事

カードの訴えの近さから新しい島候補を提案しつつ、人間がすでに確定した島構造や保留カードを無視して再編しない。

### 必要意味

| 意味 | 根拠 | 300枚での現状 | 判定 |
| --- | --- | --- | --- |
| grouping候補カードのid・本文 | routeの主入力 | 200/300が最終promptに見える | 必須・欠落あり |
| 既存島のmembership | AC-2 | 完全membershipは20/30 | 必須・欠落あり |
| `parentIslandId` | AC-2 | 代表規模fixtureに階層がなく未測定 | 必須・未測定 |
| `holdState` | AC-2 / IR spec §2.1 rule 8 | 代表規模fixtureにhold cardがなく未測定 | 必須・未測定 |
| card relation | IR spec §2.2.1「既存の島・階層・関係・hold_stateで足りる」 | typed relation 199/300 | 必須・欠落あり |
| coordinates | IR spec §2.2.1 | 渡さない | 対象外 |
| evidence link全件 | 現行ACに要求なし | evidence scenarioでは0/30がpromptに見える | 必須とは認定しない |

### 現時点の判断

`card_texts 200/300`、完全な島membership `20/30`、relation `199/300` は、taskの必要意味に直接かかるscale lossである。

一方、`holdState` と島階層は小規模ACでは固定されているが、300枚規模で保持されるかをまだ測れていない。scale戦略を決める前に、少なくともこの2軸を代表規模へ追加する必要がある。

## 5. generate-narrative

### 利用仕事

reading orderを骨格としてB型の叙述案を作り、カード間の因果・対立を捏造せず、既存の論理構造を叙述の節として使う。

### 必要意味

| 意味 | 根拠 | 300枚での現状 | 判定 |
| --- | --- | --- | --- |
| reading order | route契約 / AC-3の前提 | Document由来で30/30島が見える | 必須・保持 |
| reading-order各項のcard text | 現行prompt契約 | 300/300 | 必須・保持 |
| `causal` relation | AC-3 / `_narrative_spine_lines()` | 現fixtureはrelationが全件 `related` のため未測定 | 必須・未測定 |
| `negate` relation | AC-3 / `_narrative_spine_lines()` | 同上 | 必須・未測定 |
| evidence / contradiction relation | 現行promptが論理骨格として描画 | evidence scenarioで20/30 | 補助。ただし人間判断との関係は別途確認余地あり |
| coordinates | IR spec §2.2.1 | 渡さない | 対象外 |

### R17で検出した測定穴

現在の300枚fixtureは300 relationすべてを `related` としている。そのため `typed_relations 199/300` は一般的な構造欠落を示すが、AC-3が特に要求する `causal` / `negate` のscale coverageを直接検証していない。

次の測定更新では、relation型を決定論的に混在させ、少なくとも `causal` / `negate` を個別に source → IR → final prompt で数える。

## 6. suggest-layout

### 利用仕事

全カードの代替配置を返しつつ、現在の絶対位置だけではなく、正規化した相対布置と論理関係、島構造を使って関係の近さ・対立を配置へ反映する。

### 必要意味

| 意味 | 根拠 | 300枚での現状 | 判定 |
| --- | --- | --- | --- |
| 全カードid | response parserが全カードexactly onceを要求 | 300/300 | 必須・保持 |
| 現在の絶対座標 | responseを元Document座標空間へ返す互換契約 | 全カードがlegacy `Cards:` 節に残る | 機能上必須・保持 |
| 正規化相対座標 | IR spec §2.2.1で唯一「要求」 | 200/300 | 必須・欠落あり |
| card relation | ADR-0069 Stage 4「edgesも渡す」 | 199/300 | 必須・欠落あり |
| 島membership | Stage 4の島構造 | final promptでは30/30完全membership | 必須・保持 |
| `parentIslandId` / placard / review state | ADR-0069 D3=A | 代表fixtureで階層・placardを十分に測れていない | 必須・未測定 |
| derived island relation | Stage 4 / AC-7 | 代表規模の個別coverage件数は未測定 | 必須・未測定 |
| evidence link全件 | 現行Stage 4 ACに要求なし | evidence scenarioでは0/30 | 必須とは認定しない |

### 現時点の判断

全カード本文やraw coordinateが300/300で見えていても、正規化相対座標が200/300、card relationが199/300なら、Stage 4で追加した「位置から独立した構造」を全カードには提供できていない。

したがって `suggest-layout` は、現在の代表規模だけでもtask-required semantic coverage lossが成立している。

## 7. route横断の整理

| route | 現時点で確定しているscale欠落 | 代表規模で未測定の必要意味 |
| --- | --- | --- |
| `detect-contradiction` | focus cardが切り詰められるとAC-1のhuman adjudicationが消え得る | focus pairを固定したevidence/contradictionState coverage |
| `suggest-card-groups` | candidate card 200/300、完全島membership 20/30、relation 199/300 | holdState、parentIslandId |
| `generate-narrative` | 一般relationは199/300だが、AC-3の核心型を直接測れていない | causal、negate |
| `suggest-layout` | normalized coordinates 200/300、relation 199/300 | island hierarchy、placard/review state、derived island relation |

## 8. 次の実装順序

1. **`AI-IR-FOCUS-PRESERVATION-01`**
   - human adjudicationの再提案防止という明示ACを守るため、token戦略全体より先に直す価値がある。
2. **代表規模fixtureの必要意味化**
   - `generate-narrative` に `causal` / `negate` を混在させる。
   - groupsに `holdState` とparent hierarchyを加える。
   - layoutのhierarchy / derived island relationを数える。
3. **named provider token観測**
   - ここまでの意味coverageを壊さず、どの方式がtoken予算へ収まるかを判断する。
4. **scale投影戦略の決定**
   - global cap、task-specific projection、batch/hierarchicalを比較する。
5. **Stage 5**
   - 上記を踏まえて残る7 routeを個別に移行する。

## 9. 境界

- R15のevidence `20→0` を再び一般的なrenderer bugへ戻さない。
- exact token数を推定しない。
- 300枚全量を無条件に各promptへ送ることを目標にしない。
- focus保持は「AIが重要度を決める」仕組みにしない。route契約が明示した対象だけを保護する。
- Case 001〜003や第三者価値実証の代替証拠として扱わない。
