# Issue Draft: DOC-OPS-05-06 04_Documentation/e2e_testing.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream L
- Scope: `04_Documentation/e2e_testing.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/e2e_testing.md`, `01_Plans/documentation_quality.md`
- Dependencies: `DOC-OPS-05`, `DOC-OPS-05-05`, `DOC-OPS-05-07`
- Dependency status: `未確定（DOC-OPS-05 の Open gate 判定待ち）`
- Expected verification level: `docs-check / unit / integration / e2e（期待レベル固定。実行義務はdocs-checkのみ）`

## Requirement meta I/F（共通キー / Stream L統一）
- RequirementID: `DOC-OPS-05-06`
- RequirementStatement: E2E運用文書の公開改善方針を維持しつつ、Open化判定情報を固定する。
- PriorityClass: Must
- AcceptanceScenario: 前提=ADR-0019整合; 操作=Improve external方針/品質ゲート/検証計画を明示; 期待結果=Open可否を単体判定; 除外=実装改修
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## ADR-style 明文化
### Context
- E2E方針は `ADR-0019` が正本だが、Draftメモ間で検証期待レベルと停止条件の書式が揺れている。

### Decision
- 本Issueは **Improve external** を維持し、3Issue共通の品質ゲート定義を採用する。
- docs-onlyタスクとして `docs-check` のみ実行し、unit/integration/e2e は「期待レベル定義のみ」と固定する。

### Consequences
- E2E公開文書のOpen判断で、ADR正本との整合を崩さずに判定可能。
- 実装未着手でも、Open化判断に必要な運用メタを先行確定できる。

## Open gate判定情報（Fixed）
### Classification（Move internal / Improve external）
- Decision: **Improve external（固定）**
- Classification basis:
  1. Audience: 導入・運用担当者（外部利用者を含む）。
  2. Goal: E2E検証導線の再現可能提示。
  3. Public boundary: 対外公開導線の主文書。

### GoNoGoGate=Required（判定条件）
- Go条件（全件必須）:
  1. 3Issueで共通メタ項目（Context/Decision/Consequences, AC, Validation, Non-goals）が一致。
  2. docs-check の実行結果が記録され、self-correction が `<=3`。
  3. `DOC-OPS-05` 依存確定証跡（日時・承認者・対象・判断）が追跡可能。
- NoGo/Hold条件:
  - 上記いずれか未達。
- Stop条件:
  - self-correction が `4回目` 相当に到達。
- Gate verdict: **NoGo（現時点）**

## Validation（共通定義）
- docs-check: **必須**
- unit: **期待レベル定義のみ（非目標）**
- integration: **期待レベル定義のみ（非目標）**
- e2e: **期待レベル定義のみ（非目標）**
- Planned checks:
  - `git diff --check -- 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- Result summary: pass
- Self-correction budget: `0/3`

## Non-goals（共通定義）
- `03_Implement/**` の実装変更
- `04_Documentation/e2e_testing.md` 本文改稿
- unit/integration/e2e 実行結果の新規作成

## Proceed tri-state
- ProceedDecision: **Hold**
- Alternatives: `Proceed` / `Hold` / `Stop`
- Reason: `DOC-OPS-05` 依存未確定。

## Open化 AC / DoD（統一）
- [ ] AC-Open-1: Classification / Gate / Validation / Proceed が本Issue単体で再読可能。
- [ ] AC-Open-2: docs-check pass と self-correction `<=3` を記録。
- [ ] AC-Open-3: 依存確定証跡（日時・承認者・対象・判断）を記録。
- [ ] AC-Open-4: docs-only制約を維持。
- [ ] DoD-Open-1: 3Issue横断で品質ゲート定義が一致。
- [ ] DoD-Open-2: 未解消項目がある場合は Hold/Stop へ遷移。
- [ ] DoD-Open-3: 次工程への引継ぎに「実装禁止解除条件」を1文で含む。

## Stream L execution log（2026-05-04）
### Phase 1: 共通テンプレ適合チェック
- 05/06/07 のメタ項目・AC・Validation・Non-goals の整合を比較。

### Phase 2: ADR-style 明文化
- Context/Decision/Consequences を本Issueへ明示。
- docs-check/unit/integration/e2e の期待レベルを固定。

### Phase 3: 依存・競合整理
- 参照整合: `ADR-0019`, `e2e_testing.md`, `documentation_quality.md`。
- 実装依存なし検証項目: docs-check + メタ整合確認。

### Phase 4: 実行
- Open昇格可能粒度へ AC/DoD と停止条件を再編。

### Phase 5: Verify/Stop
- 3Issue横断の品質ゲート一致を確認。
- 未解消: 依存確定証跡不足のため **Hold** 維持。


## Stream E preparation addendum（2026-05-04 / Draft→Open昇格準備）

### Phase 1: Read
- `ADR-0019` と DOC-OPS-05-05/06/07 の整合を再確認し、Improve external分類と共通品質ゲート定義を維持。

### Phase 2: Plan（AC/DoD不足補完）
- AC補完: Open判定前の依存確定証跡 + Approval Record を必須化。
- DoD補完: docs-only制約維持、self-correction `<=3`、超過時Stopを明示。

### Phase 3: Execute（proposal-only）
- 文章整備のみ。`04_Documentation/e2e_testing.md` 本文改稿・実装変更は非実施。

### Phase 4: Verify
- Gate条件（3Issue共通メタ一致 / docs-check記録 / 依存証跡）を再照合。

### Phase 5: Proceed
- 判定: **Hold**（依存未確定）。
- Open昇格提案条件: 依存確定 + docs-check pass + tri-state再判定可能。
- 未定義競合/4回目相当修復は **Stop**。
