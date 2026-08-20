# Issue: DX-E2E-04 Critique Label Assertion Drift

- Type: DX / Test infrastructure
- Status: Done
- Source Issue: `PERF-BUDGET-01`
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/e2e/complexity_budget_foregrounding.spec.ts`
- Related Backlog: `DX-E2E-04`
- Related ADR/Spec: `01_Plans/issues/issue-UX-LABEL-01-retention-vocabulary-consistency.md`, `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Expected verification level: `e2e`

## Problem

The complexity-budget E2E expected `Critique:` in the selection context. The current user-facing vocabulary is `Critique note:`, as defined by UX-LABEL-01 and the `side_panel.context.critique` translation key. The stale assertion caused an unrelated regression run to fail even though the UI matched the accepted vocabulary.

## Decision

Update the E2E expectation to the accepted `Critique note:` label. Do not change the UI copy or introduce an alias solely for a stale test.

## Acceptance criteria

- [x] The E2E expectation matches the canonical `Critique note` vocabulary.
- [x] The UI and i18n catalog remain unchanged.
- [x] The related complexity, domain-expression, review-pack, and performance E2E files pass together.
- [x] The issue records that the failure was test-contract drift, not a product regression.

## Validation

- `node ./node_modules/@playwright/test/cli.js test e2e/complexity_budget_foregrounding.spec.ts e2e/domain_expression_keyboard_access.spec.ts e2e/review_pack_trace_export.spec.ts e2e/responsiveness_performance_budget.spec.ts --reporter=line` -> 11 passed.
- `node ./node_modules/typescript/bin/tsc --noEmit` -> passed.
- `python 01_Plans/issues/validate_active_issue_memos.py` -> passed.

## Non-goals

- No runtime, i18n catalog, data model, or accessibility semantics changes.
- No renaming of the domain concept `Critique`.

## Completion record

- Completed: 2026-07-10
- Root cause: stale English E2E assertion (`Critique:`) after UX-LABEL-01 standardized the surface label.
