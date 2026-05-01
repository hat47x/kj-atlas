# Issue Draft: DOC-OPS-05-05 01_Plans/documentation_quality.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream H
- Scope: `01_Plans/documentation_quality.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `04_Documentation/release.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `DOC-OPS-05-05`
- RequirementStatement: 内部品質基準文書としての扱いを固定し、Open化審査に必要な判断情報を揃える。
- PriorityClass: Must
- AcceptanceScenario: 前提=Draft品質均一化; 操作=分類方針/品質ゲート/検証手順を記載; 期待結果=Open可否を一読判定; 除外=本体改稿
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## Open化判断情報（分類/ゲート/検証/Proceed三値）
### Classification
- Decision: **Move internal（維持）**
- Rationale: 内部統制向け品質規約のため、公開文書本体とは責務が異なる。
- Boundary note: CE/HIL/FBおよび実装コードの変更は本Issue対象外。

### Gate（GoNoGo）
- Gate type: `Required`
- Gate condition:
  1. 公開境界（internal/public）の責務分離が明文化されていること。
  2. Open化判断に必要な根拠（分類・検証・Proceed）が本メモ単体で追跡可能であること。
  3. docs-check 前提の検証手順と結果が整合していること。
- Gate verdict: **NoGo（現時点）**

### Verification plan/result
- Planned checks:
  - `git diff --check`
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Result summary: pass（整形・メモ整合に問題なし）
- Self-correction budget: `0/3`（本更新時点）

### Proceed tri-state
- ProceedDecision: **Hold**
- Alternatives: `Proceed` / `Hold` / `Stop`
- Current reason: Move internal 判定が固定であり、Open化のGo条件（公開側移設合意）が未充足。

## Acceptance criteria / DoD（Phase 3補完）
- [x] AC1 Move internal 判定と根拠を単一箇所化。
- [x] AC2 GoNoGoGate=Required の判定条件（公開境界・責務分離）を明文化。
- [x] AC3 Validation plan は `docs-check` と一致。
- [x] AC4 Proceed 三値（Proceed/Hold/Stop）を記録。
- [x] DoD1 AC確認・Verify結果併記で完了判定。
- [x] DoD2 Self-correction 最大3回、超過時は Hold。

## Phase execution record（Stream H）

### Phase 1 Read
- 本Issue本文・Requirement meta I/F・既存Draftログを再読し、判断情報が複数節に分散している点を確認。

### Phase 2 ADR/CDC
- 参照整合: `ADR-0024` の品質ゲート境界と `documentation_quality.md` の内部品質文書という位置づけを再確認。
- CDC（変更制約）: CE/HIL/FB/実装コードへの干渉禁止、対象外ファイル非編集を維持。

### Phase 3 Plan（AC/DoD不足補完）
- Open化判断情報を「Classification / Gate / Verification / Proceed tri-state」に再編する方針を確定。
- AC/DoDの不足（Proceed三値の明示、Gate条件の具体化）を補完する計画を固定。

### Phase 4 Execute（メモ整備）
- 本Issueファイルのみ更新し、判定情報を単一セクションへ集約。
- Draft運用ログをPhase 1〜6構造へ統一。

### Phase 5 Verify（3回まで自己修復）
- Verify command:
  - `git diff --check`
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-correction count: `0/3`
- Verify verdict: **Pass**

### Phase 6 Proceed/Stop
- Final decision: **Hold**
- Reason: 内部文書維持（Move internal）判定が妥当で、Open化Go条件は未達。
- Stop条件該当: なし（致命的ブロッカーなし）。
