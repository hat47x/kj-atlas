# Cognitive Dogfood Blind Review Template

> arm/method identityを見ず、成果物そのものをsourceへ戻して評価する。
> 単一総合点や「好み」で順位付けしない。

## 0. Review metadata

- Case ID:
- Round:
- Blind alias:
- Review stage: BR1 / BR2
- Reviewer/run ID:
- Date:
- Reviewer context started fresh: yes / no
- Other packages seen before this review: none / <aliases>
- Arm mapping known: no / yes
- Common source snapshot:
- Package digest:
- Blind status: blind / partial blind / unblinded
- Known limitation:

## 1. Review object

### BR1

- Package artifact:
- Common source bundle/reference:

### BR2

- Packages compared:
- BR1 artifacts compared:
- Package presentation order:

## 2. Evidence correctness

主要主張をsourceへ戻して確認する。

| Claim / finding | Source used | Source supports it? | Temporal state handled? | Counterevidence handled? | Review |
|---|---|---|---|---|---|
|  |  | yes / partial / no | yes / partial / no | yes / partial / no |  |

- Unsupported leap(s):
- Source misread(s):
- Stale-state adoption(s):
- Important evidence used correctly:

## 3. Primary job / product boundary

- Primary job candidate as understood from package:
- Is it stated as a user job rather than a feature list?:
- Evidence that supports it:
- Evidence that weakens it:
- Existing approaches that package correctly says are sufficient:
- Existing approaches that package may have unfairly understated:
- Product boundary still unclear:

## 4. Falsification quality

- Strongest counter-hypothesis in package:
- Could this evidence actually overturn/revise the conclusion?:
- Conditions under which KJ Atlas would be unnecessary:
- Counterargument that is only ceremonial/weak:
- Missing disconfirming evidence:

## 5. Uncertainty / dissent / residuals

- Important uncertainty preserved:
- Important defer preserved:
- Dissent/counterevidence preserved:
- Low-salience or isolated material that remained visible:
- Material flattened into a generic compromise:
- Material promoted from uncertain/inference to fact:

## 6. Temporal correction check

事前登録された自然発生の時間差を、packageがどの程度扱えているかを見る。テストの「正解語」を探すのではなく、古い記述と現在状態の関係を評価する。

| Check | Detected relationship | Earlier state misused as current? | Review |
|---|---|---|---|
| temporal case 1 |  | yes / no / unclear |  |
| temporal case 2 |  | yes / no / unclear |  |
| temporal case 3 |  | yes / no / unclear |  |

## 7. Decision usefulness

- Concrete next validation / issue / defer / reject action:
- Does action match the missing evidence?:
- Would a maintainer know what evidence changes the decision?:
- Does package prematurely request a new ADR?:
- Does package turn every observation into a feature request?:
- What should remain F0 rather than issue/ADR?:

## 8. Revisitability from the package

この節は成果物だけを見る。どのmethodを使ったかは推測しない。

- Can major claims be reconstructed from cited evidence?:
- Can a later reviewer identify what was uncertain?:
- Can a later reviewer see why a counter-hypothesis was rejected/deferred?:
- What would be difficult to revisit?:

## 9. Important omissions

- High-impact evidence omitted:
- Important contradiction omitted:
- Important existing-tool sufficiency omitted:
- Important unproven assumption omitted:
- Candidate finding absent from package but supported by source:

## 10. BR1 verdict

BR1では他packageとの順位付けをしない。

- Evidence-grounded strengths:
- Evidence-grounded weaknesses:
- High-impact surviving findings:
- High-impact unsupported findings:
- Main correction required:
- Overall evidence status: robust / usable-with-corrections / weak / invalid
- Confidence in this review: high / medium / low
- Blind limitation affecting confidence:

---

## 11. BR2 cross-package synthesis only

BR2でのみ記入する。arm mappingを見ないまま行う。

### 11.1 Semantic deduplication

表現差だけのものを別findingとして数えない。

| Semantic finding | Packages containing it | Survives source check? | Material difference between packages |
|---|---|---|---|
|  |  | yes / partial / no |  |

### 11.2 Package-specific surviving findings

| Finding | Only/stronger in alias | Source survival | Decision impact | Missing elsewhere or merely phrased differently? |
|---|---|---|---|---|
|  |  |  |  |  |

### 11.3 Package-specific failure modes

| Failure | Alias | Evidence | Severity | Could change conclusion? |
|---|---|---|---|---|
|  |  |  |  |  |

### 11.4 Comparison without a winner score

- Findings common to all packages:
- Findings present in only some packages and source-grounded:
- Unsupported/overclaimed findings present in only some packages:
- Best temporal correction behavior and why:
- Best dissent/uncertainty preservation and why:
- Best falsification behavior and why:
- Best decision/revisit support and why:
- Packages that appear semantically equivalent after deduplication:
- Cases where additional method/process seems to have produced no visible output increment:
- Cases where output appears worse despite being more elaborate:

### 11.5 Frozen pre-unblind verdict

- Differences that look real enough to carry into unblinding:
- Differences that are likely style/verbosity only:
- Evidence gaps preventing comparison:
- Invalid/partial-blind package(s):
- What should be checked after arm mapping is opened:
- Verdict frozen at:

> この節を保存した後にarm mappingを開示する。unblind後の解釈でここを書き換えない。

## 12. Post-unblind synthesis — separate pass

blind verdict凍結後にのみ記入する。

- Alias → Arm mapping:
- Apparent KJ Atlas increment candidate:
- Apparent cultural-substrate-weaving increment candidate:
- Apparent D interaction candidate:
- Method-induced harm candidate:
- M1〜M9 run-record evidenceとの一致/不一致:
- M9/T9とのtrade-off:
- F0/F1/F2/F3 triage candidates:
- Cross-case evidence still required:

単一Case 001だけでproduct/skillの恒久判断を確定しない。