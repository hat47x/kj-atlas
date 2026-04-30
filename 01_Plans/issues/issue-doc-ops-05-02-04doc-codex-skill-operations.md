# Issue Draft: DOC-OPS-05-02 04_Documentation/codex_skill_operations.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream E
- Scope: `04_Documentation/codex_skill_operations.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `00_Prompt/codex_gsd_skill_ops.md`, `01_Plans/documentation_quality.md`, `04_Documentation/codex_skill_operations.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `DOC-OPS-05-02`
- RequirementStatement: 対象文書の公開境界を明示し、Open化判定に必要な判断情報を不足なく揃える。
- PriorityClass: Must
- AcceptanceScenario: 前提=DOC-OPS-05前半はIssue品質固定; 操作=公開/内部分類根拠と検証手順を記載; 期待結果=Ready/Hold/Needs-decision判定可能; 除外=本体文書改稿
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## Proposed classification
- Decision: **Move internal（維持）**
- Rationale: 内部運用手順・権限運用の性格が強く、公開境界を越えると誤公開リスクがある。

## Acceptance criteria / DoD（補完合意済み）
- [ ] AC1 分類方針（Move internal）と根拠（Audience/Goal/Public boundary）を単一箇所で参照可能。
- [ ] AC2 GoNoGoGate=Required の No-Go 条件（内部運用手順・非公開導線を含む場合）を明記。
- [ ] AC3 Validation plan は `docs-check` と一致。
- [ ] AC4 Proceed を `Ready/Hold/Needs-decision` 三値で記録。
- [ ] DoD1 Verifyは `git diff --check` と memo validator の成功を必須化。
- [ ] DoD2 Self-correction は最大3回、4回目相当は停止して Hold。

## Mini Phase（single cycle）
### 1) Read
- 本Issueを再読し、docs-only・当該ファイル限定編集を確認。

### 2) Plan
- 重複ログを除去し、分類/AC/DoD/Proceed を1系統に正規化する計画を確定。

### 3) Execute
- 本Issueメモ内のみ更新。AC/DoD補完提案を採用済みとして本文へ固定。

### 4) Verify
- `git diff --check`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-correction: 0/3

### 5) Proceed
- 判定: **Hold**
- 根拠: internal運用責務が主で public-exposure のGo条件を満たさない。
- Blocker: なし（分類は確定、公開化のみ保留）。
