# Issue Draft: DOC-OPS-05-06 04_Documentation/e2e_testing.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream F (Doc-Ops Draft)
- Scope: `04_Documentation/e2e_testing.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/e2e_testing.md`, `01_Plans/documentation_quality.md`
- Dependencies: `01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`, `01_Plans/issues/issue-doc-ops-05-07-04doc-e2e-verification-log-2026-03-03.md`
- Dependency status: `未確定（DOC-OPS-05 Open gate 判定待ち）`

## Requirement meta I/F
- RequirementID: `DOC-OPS-05-06`
- RequirementStatement: E2E運用文書の公開改善方針を維持しつつ、Open化判定情報を固定する。
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Classification（Fixed）
- Decision: **Improve external**
- Basis: E2E検証導線を利用者に提示する公開導線文書である。

## Phase Run（Plan→Execute→Verify→Proceed）
### Phase 1: Read（Draft理由・不足情報確認）
- Draft理由を「依存確定証跡不足」に統一。
- 不足情報は Approval Record 5項目に整理。

### Phase 2: AC/DoD補完提案→合意（提案整備）
- AC提案:
  - AC-1: Improve external の根拠と公開境界を単体再読可能化。
  - AC-2: docs-check pass + self-correction `<=3` 記録。
  - AC-3: Approval Record（日時/承認者/対象/判断/evidence）記録。
- DoD提案:
  - DoD-1: 3Issueで Gate/Validation/Proceed の語彙・構造一致。
  - DoD-2: 依存未確定は **Hold**、4回目相当は **Stop**。

### Phase 3: Open化に必要な前提・証跡定義
- 前提:
  1. ADR-0019との整合維持。
  2. DOC-OPS-05 依存確定。
  3. docs-only 制約維持。
- 証跡:
  - `git diff --check -- 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`

### Phase 4: 相互リンク・用語統一・完了条件整備
- 05/05/07との相互リンクを固定。
- 判定語彙を `Go/NoGo`, `Proceed/Hold/Stop` に統一。
- 完了条件は「依存確定 + AC/DoD充足 + docs-check pass」。

### Phase 5: Verify（Draft脱却判定、非競合確認）
- Draft脱却判定: **Hold**（依存未確定）。
- 非競合確認: 3Issue間で Gate定義・Stop条件の競合なし。
- Self-correction: `1/3`。

## Validation
- docs-check: **必須**
- unit/integration/e2e: **期待レベル定義のみ（非目標）**

## Non-goals
- `03_Implement/**` の実装変更
- `04_Documentation/e2e_testing.md` 本文改稿
- unit/integration/e2e 実行結果の新規作成

## Proceed tri-state
- ProceedDecision: **Hold**
- Reason: `DOC-OPS-05` 依存確定証跡待ち。


## Stream F draft整備 pass（2026-05-06 / DOC-OPS-05-06）

### Phase 1 Read同期
- 対象限定を確認: 本対応はIssueメモ整備のみ。`04_Documentation/e2e_testing.md` 本文改稿は非実施。
- 依存状態を確認: DOC-OPS-05 Open gate証跡未確定のため、Open化判定は保留。

### Phase 2 ADR要素（C/D/C）
- Context: E2E運用導線は公開対象だが、判定証跡が不足した状態でOpen化すると運用境界が曖昧になる。
- Decision: Classificationを `Improve external` 固定、判定要件を `Approval Record` 5項目で明文化する。
- Consequences: 公開文書としての改善方針を維持しつつ、依存未確定時は安全側（Hold）で停止できる。

### Phase 3 Plan→Execute
- Plan: AC/DoDに「再読可能性」「self-correction上限」「依存未確定時停止」を保持する。
- Execute: 用語を `Go/NoGo` と `Proceed/Hold/Stop` に統一し、3Issue横断整合を維持する。

### Phase 4 Verify→Proceed
- Verify: docs-check基準の整合確認を実施。
- Proceed: 依存証跡未確定のため `Hold` 継続。
- Self-correction: `2/3`（上限内）。


## Stream F unblock criteria update（2026-05-06 / execution readiness）

### Read
- 停止要因は `DOC-OPS-05依存証跡未確定` と `3Issue横断の語彙整合未確認`。

### AC/DoD解除条件（Open化条件）
- [ ] U1: `Classification: Improve external` の根拠段落に公開境界（含む/含まない）を1段落で追記。
- [ ] U2: 05/05/07との相互リンクが存在し、各Issueの Proceed 判定日時が記録されている。
- [ ] U3: `Dependency status` が更新され、Hold解除の根拠を明記。

### Validation plan（コマンド）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `rg -n "Classification|Dependency status|ProceedDecision|Related Backlog" 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `git diff --check -- 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`

### Proceed
- 判定: **Hold維持**。
- Open化条件: U1〜U3完了時に Draft解除可。
