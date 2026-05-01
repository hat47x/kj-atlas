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
- Dependency status: `未確定（DOC-OPS-05 の Open gate 判定待ち）`
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
- 判定: **Conditional**（分類方針の固定は完了）
- 根拠: Move internal 判定と移管先候補、Verify手順が明文化済み。
- Blocker: 依存 `DOC-OPS-05` の gate未確定（実体移設は後続タスク）。

## Stream E execution log（2026-05-01 / DOC-OPS-05-07 Draft解消）

### Phase 1: Draft issueのAC/DoD明文化
- Assumption: 日付付き検証ログは運用証跡であり、公開主文書ではなく移設判断を優先する。
- AC補強: `Move internal` 判定根拠（Audience/Goal/Public boundary）と移設先候補の同時記録を必須化。

### Phase 2: Plan（不足メタ提案）
- 提案1: Move internal の最終配置先を `候補` から `確定` へ遷移させる判定者を固定。
- 提案2: 移設後リンク方針（旧パスからの参照維持方法）を明記。
- 提案3: `DOC-OPS-05` gate未確定時の既定判定を `Hold` に固定。

### Phase 3: 用語・役割・導線・固定値(D1-D4)整合チェック
- 本IssueはAUTH固定値の再定義を行わず、関連章（operations/security/e2e_testing）への導線維持のみを実施。
- 判定: 用語・責務・導線の差分なし（D1-D4新規定義なし）。

### Phase 4: issueステータス更新案（Draft→Open条件）
- 提案: **Draft維持（移設先確定まで）**。
- Open条件案:
  1. `Move internal` の受け皿ディレクトリとリンク方針が確定。
  2. 参照導線（04_Documentation -> 01_Plans/issues）が切断されていない。
  3. docs-checkの再現コマンドが記録済み。

### Phase 5: AC/DoD判定
- 判定: **Conditional**（分類固定は完了、実体移設計画の確定待ち）。
- Self-correction: 0/3。

## Stream E Proceed判定（2026-05-01）
- Open化可否: **Hold**
- Stopper:
  1. 依存 `DOC-OPS-05` の gate確定待ち。
  2. Move internal の受け皿確定と責務者固定が未完了。
