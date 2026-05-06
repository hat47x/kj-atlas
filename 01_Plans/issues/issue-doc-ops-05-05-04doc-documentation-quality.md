# Issue Draft: DOC-OPS-05-05 01_Plans/documentation_quality.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream F (Doc-Ops Draft)
- Scope: `01_Plans/documentation_quality.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: `01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`, `01_Plans/issues/issue-doc-ops-05-07-04doc-e2e-verification-log-2026-03-03.md`
- Dependency status: `未確定（DOC-OPS-05 Open gate 判定待ち）`

## Requirement meta I/F
- RequirementID: `DOC-OPS-05-05`
- RequirementStatement: 内部品質基準文書としての扱いを固定し、Open化審査に必要な判断情報を揃える。
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Classification（Fixed）
- Decision: **Move internal**
- Basis: 内部審査用の品質統制基準であり、対外公開本文ではない。

## Phase Run（Plan→Execute→Verify→Proceed）
### Phase 1: Read（Draft理由・不足情報確認）
- Draft理由を「依存確定証跡不足」に一本化。
- 不足情報を `Approval Record`（日時/承認者/対象/判断/evidence）として明示。

### Phase 2: AC/DoD補完提案→合意（提案整備）
- AC提案:
  - AC-1: 本Issue単体で Classification / Gate / Validation / Proceed が再読可能。
  - AC-2: docs-check pass + self-correction `<=3` を記録。
  - AC-3: `Approval Record` の5項目を記録。
- DoD提案:
  - DoD-1: 3Issueで品質ゲート定義（docs-check必須、他は期待レベル定義のみ）一致。
  - DoD-2: 依存未確定時は Proceed を **Hold**、self-correction 4回目相当は **Stop**。

### Phase 3: Open化に必要な前提・証跡定義
- 前提:
  1. DOC-OPS-05 依存確定。
  2. Approval Record 記録完了。
  3. docs-only 制約維持（実装変更なし）。
- 証跡:
  - `git diff --check -- 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`

### Phase 4: 相互リンク・用語統一・完了条件整備
- 相互リンク対象を05/06/07で固定。
- 用語を `Proceed/Hold/Stop`、`Go/NoGo`、`docs-check` に統一。
- 完了条件を「AC/DoD充足 + 依存確定証跡あり」に統一。

### Phase 5: Verify（Draft脱却判定、非競合確認）
- Draft脱却判定: **Hold**（依存未確定のため Open不可）。
- 非競合確認: 05/06/07 の分類・ゲート・停止条件に矛盾なし。
- Self-correction: `1/3`（上限内）。

## Validation
- docs-check: **必須**
- unit/integration/e2e: **期待レベル定義のみ（非目標）**

## Non-goals
- `03_Implement/**` の実装変更
- `04_Documentation/**` 本文改稿
- unit/integration/e2e 実行結果の新規作成

## Proceed tri-state
- ProceedDecision: **Hold**
- Reason: `DOC-OPS-05` 依存確定証跡待ち。


## Stream F draft整備 pass（2026-05-06 / DOC-OPS-05-05）

### Phase 1 Read同期
- 対象限定を確認: 本対応は当該Issueメモのみを更新し、`01_Plans/documentation_quality.md` 本文や実装コードは変更しない。
- 依存状態を確認: `DOC-OPS-05` のOpen gate証跡が未確定のため、Proceedは `Hold` 維持。

### Phase 2 ADR要素（C/D/C）
- Context: 内部品質基準文書の公開境界を誤ると、内部統制の運用情報が外部公開されるリスクがある。
- Decision: Classificationを `Move internal` 固定とし、Open化判定に必要な承認証跡を `Approval Record` 5項目で管理する。
- Consequences: 公開可否判断が再現可能になり、依存未確定時の誤Proceedを抑止できる。

### Phase 3 Plan→Execute
- Plan: AC/DoDの不足を「証跡項目」「停止条件」「語彙統一」の3点で補完する。
- Execute: docs-only範囲で文言と判定導線を整備し、実装・公開判定の確定は行わない。

### Phase 4 Verify→Proceed
- Verify: docs-check前提の整合（Classification/Gate/Validation/Proceed）を確認。
- Proceed: 依存証跡未確定のため `ProceedDecision: Hold` を継続。
- Self-correction: `2/3`（上限内、4回目相当はStop）。
