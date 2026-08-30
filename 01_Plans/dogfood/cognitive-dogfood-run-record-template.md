# Cognitive Dogfood Run Record Template

> `COGNITIVE-EVAL-01` の4arm比較を、別セッション・別モデル・Case 001〜003でも同じ粒度で記録するためのテンプレート。
> この文書は評価方法であり、各ケースの答えを含めない。

## 0. Run metadata

- Case ID:
- Round: 1 / 2 / revisit
- Arm: A / B / C / D
- Blind alias: pending / <alias>
- Run ID:
- Run validity: valid / partial / invalid / pending
- Date:
- Execution order position:
- Operator:
- Model/provider:
- Model/version if known:
- Temperature/reasoning setting if configurable:
- KJ Atlas version/commit:
- cultural-substrate-weaving version/commit: N/A or SHA
- Source manifest ID:
- Operator pack/version:
- Context started fresh: yes / no
- Known contamination: none / <description>
- Operator/setup friction log: <UI locator exploration, environment/file preparation, experiment administration; exclude from M9/T9 unless separately triaged as a product finding>

## 1. Fixed question

対象ケースのlaunch packetからそのまま転記する。armごとに言い換えない。

> <question>

## 2. Input verification

### Common domain sources

- [ ] 全arm共通のfrozen repository snapshotから作成したsanitized evidence bundleだけを使用した。
- [ ] 今回の問いへの既存回答・仮説・experimenter-only評価情報を入力へ混ぜていない。
- [ ] source path / snapshot SHA / bundle IDを保存した。

### Arm-specific method

- [ ] A/C: cultural-substrate-weavingを使用していない。
- [ ] B/D: 指定commitのcanonical cultural-substrate-weaving bundleだけを方法として使用した。
- [ ] C/D: KJ Atlas外部表象を分析中に使用した。
- [ ] A/B: KJ Atlasキャンバスを分析用の外部表象として使用していない。

該当しないチェックは `N/A` と注記してよい。該当する条件が満たされない場合はrunを `valid` にしない。

### Deviations

- <none or explicit deviations>

## 3. Pre-analysis state

分析開始前に、operatorが知っている結論ではなく、実験上の状態だけを書く。

- 事前に固定された制約:
- 今回決めないこと:
- 追加資料が必要になった場合の扱い:
- stopping condition:

## 4. Raw analysis artifacts

### A/B

- Raw conversation/document artifact:
- Intermediate notes:

### C/D

- KJ Atlas document ID/file:
- InquiryJourney/bundle reference:
- Raw card count:
- Islands/groups:
- Isolated cards:
- Explicit conflicts:
- Explicit gaps:
- Narrative/export artifact:

> カード枚数、島数、操作回数は成果指標ではない。再現・監査のためだけに記録する。

## 5. AI proposal ledger

重要なAI提案について、最終成果に入ったものだけでなく、棄却・保留も残す。

| Proposal ID | Proposal | Evidence cited | Human action | Reason | Later verdict |
|---|---|---|---|---|---|
| P-001 |  |  | accept / modify / reject / defer |  | pending |

AI proposalを一件も利用しなかった場合は `none used` と明記する。空欄のままにしない。

### Calibration notes

- AIが正しかったが棄却した提案:
- AIが誤っていたが採用しかけた提案:
- 根拠を確認したため判断が変わった提案:
- AI出力の流暢さ/断定の強さが判断へ影響した兆候:

## 6. Required output

実行前に、そのcase/armのlaunch packetにある `Required output` の各項目を**順序・意味を変えず** `### 6.1` 以降の見出しへ転記する。Case 001の製品価値項目をCase 002/003へ流用したり、逆にCase 002/003の問いをCase 001へ混ぜない。

例ではなく、実runでは次のplaceholderをcase固有項目へ置換する。

### 6.1 <required output item 1>

- Result:
- Evidence:
- Counterevidence:
- Uncertainty:

### 6.2 <required output item 2>

- Result:
- Evidence:
- Counterevidence:
- Uncertainty:

### 6.n <continue until every preregistered required output item is represented>

必要に応じて表・文章を使ってよい。重要なのはlaunch packetの全要求を落とさず、主要主張からsourceへ戻れることである。

## 7. Conflict-bearing source check

対象ケース文書で事前登録されたtest IDだけを判定する。arm実行中には「正解」やtestの説明を教えない。

- <case test ID> detected: yes / no / partial
  - temporal/contract interpretation:

Case 001は `T1`〜`T3`、Case 002は `C2-T1`〜`C2-T4`、Case 003は `C3-T1`〜`C3-T5` を使用する。評価者は、単にキーワードへ言及したかではなく、**古い状態・訂正済み状態・条件付き設計・未実装契約を現在状態へ誤採用しなかったか**を見る。

## 8. M1–M9 evidence

数値化できない項目を0にしない。`not measurable` と具体的理由を記録する。

### M1 生存所見

- New candidate findings:
- After dedup/removal:
- Surviving against target evidence:
- High-impact finding(s):

### M2 根拠接地

- Major claims with resolvable provenance:
- Major claims without sufficient provenance:
- Temporal/provenance failures:

### M3 異論・残差保持

- Dissent preserved:
- Isolated/residual material preserved:
- Dissent collapsed or omitted:

### M4 早期収束耐性

- Initial hypothesis/structure:
- Evidence that changed it:
- Structure/decision after revision:
- Anchoring failures:

### M5 AI依存校正

- Useful AI proposals accepted:
- Erroneous/irrelevant proposals rejected:
- Erroneous proposals accepted or insufficiently checked:
- Useful proposals wrongly rejected:

### M6 再訪・訂正可能性

- Can decision be reconstructed from evidence now?:
- Revisit scheduled/possible?:
- Missing state needed for future correction:

### M7 注意・探索制御

- Low-salience evidence surfaced:
- Gap/conflict/time transition discovered:
- Attention captured by verbose/salient but low-value material:

### M8 決定への変換品質

- Concrete issue/research/defer/reject output:
- Evidence needed to execute it:
- Later implementation/review status:

### M9 認知摩擦

M9は分析方法・外部表象・意味保持のために利用者/分析者が負担した摩擦だけを扱う。UI locator探索、実験用ファイル配置、connector/browser/local環境準備、run record管理などの **operator/setup frictionはM9へ算入しない**。それらが一般利用者にも再現する製品課題だと疑われる場合は、M9へ後付けせずF0〜F2 findingとして別にtriageする。

#### Useful friction

- <pause/check/revisit that changed judgment>

#### Waste friction

- <operation burden that produced no observed cognitive value>

#### Excluded operator/setup friction

- <environment/UI-locator/experiment-administration burden excluded from M9>

## 9. Retention audit (especially C/D)

最終成果を元材料へ戻す。

- [ ] 孤立カードを不当に消していない。
- [ ] 対立を一般論へ溶かしていない。
- [ ] 不確実な材料を確定事実へ昇格していない。
- [ ] 主要主張から出所へ戻れる。
- [ ] 途中で「守る」とした材料が最終成果でも守られている。
- [ ] 後段の訂正を無視して初期記述へ回帰していない。

Detected losses:

- <none or list>

## 10. InquiryJourney actual-use record (C/D only)

この節は `DOMAIN-W-ITERATION-01` Phase 2手動中核の**実使用証拠**を残し、T9（Phase 3 proposal-only AI支援を別issue化するか）の判断材料へ接続する。

実験用の独自履歴方式は作らず、製品の `InquiryJourneyV1` / `RoundSnapshotV1` / handoff / lineage / compare / resume を使用した範囲だけ記録する。実験Round番号をW型stageへ機械対応させない。

A/Bではこの節を削除するか `N/A` とする。

### 10.1 Product journey references

- InquiryJourney ID / bundle reference:
- Working document ID/file:
- Snapshot IDs used:
- W-type stage(s) actually chosen by human:
- Iteration(s):
- Parent/branch relation used:
- Handoff created: yes / no
- Resume brief used: yes / no
- Round comparison used: yes / no
- Card lineage consulted: yes / no

### 10.2 Did the manual core change the work?

- Snapshot/handoff prevented loss of a meaningful state: yes / no / not exercised
  - evidence:
- Resume brief reduced reconstruction burden: yes / no / not exercised
  - evidence:
- Comparison changed or corrected a judgment: yes / no / not exercised
  - evidence:
- Lineage/provenance helped resolve a stale or conflicting claim: yes / no / not exercised
  - evidence:
- Branching allowed exploration without overwriting a valuable prior state: yes / no / not exercised
  - evidence:
- Product journey mechanics added waste friction without observed cognitive value:

### 10.3 T9 manual-friction observations

AI支援候補を思いついた回数ではなく、**手動中核で現実に繰り返し発生した摩擦**だけを書く。operator/setup frictionはここへ入れない。

| Observation ID | Operation | Manual burden | Cognitive risk | Non-AI workaround | Proposal-only AI help | Automation risk | Run verdict |
|---|---|---|---|---|---|---|---|
| JF-001 | 問い / 引継ぎ / 差分 / 反証 / 再開 / その他 |  | omission / anchoring / stale evidence / loss of dissent / other |  |  |  | needed / manual sufficient / conditional / unresolved |

### 10.4 T9 run-level verdict

- Repeated friction class(es) observed in this run:
- Manual core sufficient for this run: yes / no / mixed
- Candidate Phase 3 support worth cross-case review:
- Functional/manual-core defect discovered instead of AI need:
- Notes for cross-case synthesis:

> **単一runではT9を完了させず、Phase 3 issueも原則起票しない。** Case portfolioで事前登録した横断ゲートに従う。操作そのものを完了できない欠陥は、AI支援で迂回せず手動中核のbug/feature gapとして扱う。

## 11. Candidate source requests

run中に不足を発見した資料はここへ置く。このrunだけへ追加して結論を強化しない。

| Candidate source | Why needed | Which claim could change | Next common round? |
|---|---|---|---|
|  |  |  | yes / no |

## 12. cultural-substrate-weaving execution record (B/D only)

B/Dでは必須。A/Cではこの節を削除するか `N/A` とする。

- Activation verdict: activate / limited / no increment / stop
- Activation reason:
- Framework candidates considered:
- Selected framework(s) and reason:
- Rejected framework(s) and reason:
- New semantic units/relations/questions attributed to framework exploration:
- Target-side evidence used to validate them:
- Removal test — framework terminology removed:
- Substitution test — alternative framework/baseline could produce same finding:
- Skill-specific surviving findings after removal/substitution:
- Framework-capture or duplication signs:
- Stop condition reached:

「体系を使った」こと自体を増分と数えない。対象へ戻って生存し、体系語を除いても成立する差だけを記録する。

## 13. Static intake validation

raw artifact保存後、blind package作成前にrun-record validatorを実行し、その結果を保存する。

- Validator command:
- Validator result: pass / fail / warnings
- Validation output artifact/log:
- Remaining manual checks:

validatorは方法の優劣を採点しない。比較条件・記録完全性・明らかなcontamination/placeholderだけを検査する。