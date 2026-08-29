# Cognitive Dogfood Run Record Template

> `COGNITIVE-EVAL-01` の4arm比較を、別セッション・別モデルでも同じ粒度で記録するためのテンプレート。
> この文書は評価方法であり、各ケースの答えを含めない。

## 0. Run metadata

- Case ID:
- Round: 1 / 2 / revisit
- Arm: A / B / C / D / blinded alias
- Run ID:
- Date:
- Operator:
- Model/provider:
- Model/version if known:
- Temperature/reasoning setting if configurable:
- KJ Atlas version/commit:
- cultural-substrate-weaving version/commit: N/A or SHA
- Source manifest ID:
- Context started fresh: yes / no
- Known contamination:

## 1. Fixed question

ケース文書からそのまま転記する。armごとに言い換えない。

> <question>

## 2. Input verification

### Common domain sources

- [ ] 全arm共通のrepository snapshotだけを使用した。
- [ ] 今回の問いへの既存回答・仮説を入力へ混ぜていない。
- [ ] source path / snapshot SHAを保存した。

### Arm-specific method

- [ ] A/C: cultural-substrate-weavingを使用していない。
- [ ] B/D: 指定commitのcultural-substrate-weavingだけを方法として使用した。
- [ ] C/D: KJ Atlas外部表象を使用した。
- [ ] A/B: KJ Atlasキャンバスを使用していない。

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

### Calibration notes

- AIが正しかったが棄却した提案:
- AIが誤っていたが採用しかけた提案:
- 根拠を確認したため判断が変わった提案:
- AI出力の流暢さ/断定の強さが判断へ影響した兆候:

## 6. Required output

### 6.1 利用者の仕事

- Primary job candidate:
- Adjacent jobs:
- Evidence:
- Uncertainty:

### 6.2 既存手段との境界

- Existing approaches sufficient when:
- Existing approaches become insufficient when:
- Evidence:

### 6.3 現在実現している価値

| Claim | Evidence | Evidence time | Confidence | Counterevidence |
|---|---|---|---|---|
|  |  |  |  |  |

### 6.4 未実証の価値仮説

| Hypothesis | Why plausible | What is still missing | Falsification route |
|---|---|---|---|
|  |  |  |  |

### 6.5 KJ Atlasが不要かもしれない条件

- <counter-hypothesis>

### 6.6 次の検証/issue

- Action:
- Why now:
- Expected evidence:
- ADR trigger involved: yes / no

### 6.7 訂正・矛盾・旧情報

| Source | Earlier/visible claim | Later/current evidence | Run judgment |
|---|---|---|---|
|  |  |  |  |

### 6.8 保留

| Deferred point | Missing evidence | Why not infer now |
|---|---|---|
|  |  |  |

## 7. Conflict-bearing source check

ケースで事前登録された項目だけを判定する。arm実行中には「正解」を教えない。

- T1 detected: yes / no / partial
  - temporal interpretation:
- T2 detected: yes / no / partial
  - temporal interpretation:
- T3 detected: yes / no / partial
  - temporal interpretation:

評価者は、単にキーワードへ言及したかではなく、**古い状態を現在の状態として誤採用しなかったか**を見る。

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

#### Useful friction

- <pause/check/revisit that changed judgment>

#### Waste friction

- <operation burden that produced no observed cognitive value>

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

## 10. Candidate source requests

run中に不足を発見した資料はここへ置く。このrunだけへ追加して結論を強化しない。

| Candidate source | Why needed | Which claim could change | Next common round? |
|---|---|---|---|
|  |  |  | yes / no |

## 11. Blind-review package

評価者へ渡す際にはArm/方法名を除去し、次だけを渡す。

- 固定問い
- source manifest
- required output
- claim/evidence table
- contradictions/deferred points
- proposal ledger（method-identifying文言は必要に応じ匿名化）
- C/Dのカード構造は、方法推定を避けるblind reviewでは文章化した等価表現も併用する

### Reviewer questions

1. 重要な主張は証拠に接地しているか。
2. 時点の異なる主張を正しく更新しているか。
3. 反証・不要条件・保留を保持しているか。
4. 重要で新しい生存所見はあるか。
5. もっともらしいが対象資料にない一般論を混ぜていないか。
6. 次の行動は具体的で、その必要性を証拠から説明できるか。
7. 後から訂正可能な形で理由が残っているか。

## 12. Attribution after comparison

arm単独では帰属しない。比較後に記入する。

- KJ Atlas product:
- cultural-substrate-weaving:
- caller/domain context:
- model behavior:
- experiment design:
- unresolved attribution:

## 13. Revisit

- Revisit date:
- New evidence:
- Findings retained:
- Findings modified:
- Findings rejected:
- Previously deferred points resolved:
- Product/skill changes caused by this run:
- Regression/overfitting check result:
