# Issue: DX-E2E-07 Current UI Contract Drift Batch

- Type: Bug / Test infrastructure
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `PRODUCT-QA-01`
- Priority: P1
- Owner: Codex
- Scope: `03_Implement/frontend/e2e/`, `03_Implement/frontend/e2e/helpers/`
- Related Backlog: `DX-E2E-07`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`, `01_Plans/issues/issue-UX-STATE-01-selection-target-consistency-after-bulk-island.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
- Expected verification level: `e2e`

## Requirement meta I/F

- RequirementID: DX-E2E-07
- RequirementStatement: Current-main E2E expectations must follow the accepted command addresses, work-mode disclosure, single-primary-selection model, and share/export flow without restoring obsolete UI solely for stale tests.
- PriorityClass: Must
- AcceptanceScenario: 前提=current main のUIと145件のPlaywright suite / 操作=全件を実ブラウザで実行 / 期待結果=現行契約に対する実不具合だけが失敗し、旧UI住所や文言による偽陰性がない / 除外=timeout引き上げだけでの緑化、ADR-0054、外部接続実装。
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export / import-sanitize
- VerificationLevel: e2e
- DecisionStatus: Fixed（既存ADR/Done issueの現行UI契約へテストを追随する）
- DecisionQueueRef: N/A

## Problem

The 2026-07-13 current-main release-gate run collected all 145 tests after DX-E2E-05 was fixed, but 26 failed under six workers. A final isolation run with one worker and a 60-second ceiling recovered 9 and left 17 deterministic failures.

The remaining failures cluster around UI addresses changed by already-accepted work:

- Header/shortcut surfaces: 4 (`header_toolbar_layout`).
- Work-mode / advanced disclosure: 5 (`i18n_locale_functional_equivalence`, four `ops_recovery_guidance`).
- Share/export completion: 3 (`large_document_operability`, `pre_share_summary_gate`, `review_pack_trace_export`).
- Legacy JSON address: 4 (two polygon autofit and two polygon vertex-edit cases).
- Public-pack visibility: 1.

Restoring obsolete buttons or old panel placement only to satisfy these assertions would violate ADR-0048's command-address structure and recent workspace IA decisions.

## Decision

Treat this as one bounded E2E contract-reconciliation batch. For each failure, compare the test against the current accepted UI address first; update stale setup/locators when runtime behavior is correct, and split any real product regression into its own issue before changing production code.

## Acceptance criteria

- [ ] All 17 failures are classified as test defect, product defect, or environment limitation with a referenced current contract.
- [ ] Shortcut help, work-mode, legacy JSON, and share/export tests open the current owning surface before acting.
- [ ] No removed UI is reintroduced solely for test compatibility.
- [ ] SafeMode, proposal-only, single-primary-selection, and share/export redaction remain non-regressed.
- [ ] The full 145-test suite passes in the standard Playwright environment; any system-Chrome fallback is recorded separately.
- [ ] Test timeouts are not increased without evidence that the operation itself legitimately exceeds the existing budget.

## Task breakdown

- [ ] T1 Reconcile header shortcut and modifier-key expectations with the current shortcut cheat sheet and mode controls.
- [ ] T2 Reconcile work-mode/Advanced setup for comparison and recovery flows.
- [ ] T3 Reconcile legacy JSON and share/export ownership after menu/workspace IA changes.
- [ ] T4 Split genuine runtime regressions, if any, into dedicated issues.
- [ ] T5 Run focused specs, then the complete 145-test suite.

## Validation plan

- Focused: `cd 03_Implement/frontend && npm run e2e -- e2e/header_toolbar_layout.spec.ts e2e/i18n_locale_functional_equivalence.spec.ts e2e/ops_recovery_guidance.spec.ts e2e/polygon_autofit_qa_boundary.spec.ts e2e/polygon_vertex_edit.spec.ts e2e/large_document_operability.spec.ts e2e/pre_share_summary_gate.spec.ts e2e/public_pack_visibility_compat.spec.ts e2e/review_pack_trace_export.spec.ts --reporter=line`.
- Full: `cd 03_Implement/frontend && npm run e2e -- --reporter=line`.
- Required result: focused and full suites pass without weakening timeout or safety assertions.

## Risks and rollback

- Risk: adapting tests to implementation bugs instead of accepted behavior.
- Control: cite the owning ADR/Done issue for every changed expectation; create a product issue where no accepted contract supports the runtime behavior.
- Rollback: revert only the affected spec/helper change; do not change application state or persisted data.

## Completion boundary

This issue is Open. It is a release-gate blocker for G2/G4/G7, but it does not authorize final shipment, ADR-0054 work, or changes to SafeMode/share policy.
