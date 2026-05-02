# Issue Draft: DOC-OPS-05-05 01_Plans/documentation_quality.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream G
- Scope: `01_Plans/documentation_quality.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `04_Documentation/release.md`
- Dependencies: `DOC-OPS-05`
- Dependency status: `未確定（DOC-OPS-05 の Open gate 判定待ち）`
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

## Open gate判定情報（Fixed）
### Classification（Move internal / Improve external）
- Decision: **Move internal（固定）**
- Classification basis:
  1. Audience: 文書執筆者・レビュアー向け内部品質統制。
  2. Goal: 公開文書の品質担保ルールを内部で運用すること。
  3. Public boundary: 対外説明本文ではなく、内部審査の基準書。
- Boundary note: CE/HIL/FBおよび実装コード変更は対象外。

### GoNoGoGate=Required（判定条件）
- Gate type: `Required`
- Go条件（全件必須）:
  1. internal/public の責務分離（上記Classification basis）が明文化済み。
  2. Open判定に必要な4要素（Classification / Gate / Verification / Proceed）が本メモ単体で追跡可能。
  3. `docs-check` 手順・実行結果・自己修復回数（<=3）が併記されている。
  4. 依存 `DOC-OPS-05` のOpen gateが確定済み。
- NoGo/Hold条件（いずれかで不成立）:
  - Go条件の欠落。
  - 依存 gate 未確定。
- Gate verdict: **NoGo（現時点）**

### Verification（docs-check）
- Planned checks:
  - `git diff --check -- 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- Result summary: pass
- Self-correction budget: `0/3`

### Proceed tri-state
- ProceedDecision: **Hold**
- Alternatives: `Proceed` / `Hold` / `Stop`
- Reason: Move internal 判定は固定済みだが、依存 `DOC-OPS-05` gate が未確定。

## Acceptance criteria / DoD
- [x] AC1 Move internal 判定と分類根拠（Audience/Goal/Public boundary）を単一箇所化。
- [x] AC2 GoNoGoGate=Required のGo/NoGo条件を明文化。
- [x] AC3 Validation plan が `docs-check` と一致。
- [x] AC4 Proceed 三値（Proceed/Hold/Stop）を記録。
- [x] DoD1 Verify結果とSelf-correction回数を併記。
- [x] DoD2 Self-correction 最大3回、超過時は Hold。

## Phase execution record（Stream G）
### Phase 1: Read
- 本Issue・`ADR-0024`・`documentation_quality.md` の参照関係を再確認。

### Phase 2: ADR/CDC
- ADR整合: 品質ゲート境界（ADR-0024）に従い internal文書扱いを固定。
- CDC: 対象外ファイル非編集、docs-only制約を維持。

### Phase 3: Plan
- Open gate情報を `Classification / Gate / Verification / Proceed` に再編。
- Required gateのGo/NoGo条件を明示する計画を固定。

### Phase 4: Execute
- 本Issueメモのみ更新し、分類根拠と判定条件を統合。

### Phase 5: Verify
- `git diff --check -- 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- Self-correction count: `0/3`
- Verify verdict: **Pass**

### Phase 6: Proceed
- Final decision: **Hold**
- Reason: 依存 `DOC-OPS-05` Open gate未確定のため。
