# Issue Draft: DOC-OPS-05-06 04_Documentation/e2e_testing.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream E
- Scope: `04_Documentation/e2e_testing.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/e2e_testing.md`, `04_Documentation/operations.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `DOC-OPS-05-06`
- RequirementStatement: E2E運用文書の公開改善方針を維持しつつ、Open化判定に必要な情報を固定する。
- PriorityClass: Must
- AcceptanceScenario: 前提=ADR-0019を正本維持; 操作=Improve external方針と検証/Proceedを明記; 期待結果=Open化着手可否が判断可能; 除外=本文改稿
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## Proposed classification
- Decision: **Improve external（維持）**
- Rationale: 対外導線の主要文書であり、公開品質改善の価値が高い。

## Acceptance criteria / DoD（補完合意済み）
- [ ] AC1 Improve external 判定と根拠を明記。
- [ ] AC2 GoNoGoGate=Required（ADR-0019整合、公開境界）を明文化。
- [ ] AC3 Validation plan は `docs-check` と一致。
- [ ] AC4 Proceed 三値を記録。
- [ ] DoD1 Verify結果併記。
- [ ] DoD2 Self-correction 最大3回、超過時は Hold。

## Mini Phase（single cycle）
### 1) Read
- 本Issueを再読し、docs-only・単一ファイル編集制約を確認。

### 2) Plan
- 重複実行記録を整理し、分類/条件/Proceedを1セット化する計画を確定。

### 3) Execute
- 本Issueメモのみ更新。AC/DoD不足補完を本文に反映。

### 4) Verify
- `git diff --check`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-correction: 0/3

### 5) Proceed
- 判定: **Ready**
- 根拠: Improve external 方針、GoNoGo条件、Verify手順が再現可能。
- Blocker: なし。


## Stream H DOC-OPS-05 serial update（2026-04-30）

### Phase 1 Read同期
- Read Order（00→02）と本Issue、対象Docを再読し、docs-only制約を確認。

### Phase 2 章ごとのAC定義
- AC固定: Audience / Goal / Non-goal / Public boundary / Related / GoNoGoGate / VerificationLevel(docs-check)。

### Phase 3 章単位更新（直列）
- 本Issueに対応する章のみを更新対象として直列処理し、未承認事項の確定化は行わない。

### Phase 4 docs-check / link-check
- `git diff --check` と `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md` を実行対象とする。
- 自己修復回数: 0/3（4回目相当はHold停止）。

### Phase 5 issue更新
- 判定: **Ready**（停止条件非該当、docs-only維持）。
