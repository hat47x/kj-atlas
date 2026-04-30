# Issue Draft: DOC-OPS-05-07 04_Documentation/e2e_verification_log_2026-03-03.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream E
- Scope: `04_Documentation/e2e_verification_log_2026-03-03.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/e2e_verification_log_2026-03-03.md`, `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `DOC-OPS-05-07`
- RequirementStatement: 対象検証ログを「内部移管」または「対外改善」で分類し、次の実行計画を固定する。
- PriorityClass: Must
- AcceptanceScenario: 前提=04_Documentation分類棚卸し済; 操作=読者/目的/配置先を判定; 期待結果=分類結果と次アクションを記録; 除外=本文全面改稿
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## Proposed classification
- Decision: **Move internal（維持）**
- Rationale: 日付付き検証ログは運用証跡であり、対外説明主文書ではない。

## Acceptance criteria / DoD（補完合意済み）
- [ ] AC1 分類結果（Move internal）と根拠（Audience/Goal/Public boundary）を明記。
- [ ] AC2 変更先候補（`01_Plans/issues/e2e_verification_logs/` など）を記録。
- [ ] AC3 Validation plan は `docs-check` と一致。
- [ ] AC4 GoNoGoGate 判定条件と Proceed 三値を記録。
- [ ] DoD1 Verify結果併記。
- [ ] DoD2 Self-correction 最大3回、超過時は Hold。

## Mini Phase（single cycle）
### 1) Read
- 本Issue再読で分類未整理点を確認し、対象外ファイル非接触制約を確認。

### 2) Plan
- 分類根拠・移管先候補・Proceed記録を1セットに集約する計画を確定。

### 3) Execute
- 本Issueメモのみ更新。重複ストリーム記録を整理。

### 4) Verify
- `git diff --check`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-correction: 0/3

### 5) Proceed
- 判定: **Ready**（分類方針の固定は完了）
- 根拠: Move internal 判定と移管先候補、Verify手順が明文化済み。
- Blocker: なし（実体移設は後続タスク）。
