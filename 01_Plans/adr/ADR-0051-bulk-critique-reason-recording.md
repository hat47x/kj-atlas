# ADR-0051: Bulk Critique Reason Recording

- Status: Proposed
- Date: 2026-07-10
- Deciders: Maintainer and product-design review
- Scope: `03_Implement/frontend/src/ui/BulkOperationsBar.tsx`, `03_Implement/frontend/src/App.tsx`, `01_Plans/issues/issue-UX-WORKFLOW-01-hold-critique-action-continuity.md`

## Context

The bulk operation bar can already hold several selected cards and mark them with a quick critique flag. A user who wants to preserve the reason for that decision still has to leave the bulk workflow, select one card, and edit its note. That breaks the hold -> reason -> review loop and makes it easy to retain uncertainty without retaining its context.

The product model treats critique as human-authored context. It must remain available when AI is disabled, and an existing human note must never be silently replaced by a bulk action.

## Decision

Add an explicit `Add reason` action to the bulk operation bar for selections of two or more cards.

- The user enters one shared reason and explicitly saves it.
- The trimmed reason is appended to every selected card's existing critique note, separated by a blank line.
- Existing notes and authored wording are preserved; the action never replaces them.
- The update is recorded as one document/history operation.
- The action does not call an AI provider and remains available when `KJ_ATLAS_LLM_PROVIDER=none`.
- Escape/cancel closes the editor without changing the document. `Ctrl+Enter` or `Cmd+Enter` saves the entered reason.
- The quick critique flag remains a separate operation for users who only need a marker.

## Alternatives Considered

1. Require one-card-at-a-time editing. Rejected because it interrupts a valid bulk hold workflow.
2. Replace every selected card's note. Rejected because it would destroy authored context.
3. Store a separate group-level note. Deferred because the current data model has no group-note field and the selected cards are the visible targets of the action.
4. Generate a reason with AI. Rejected because recording human context must not depend on an optional provider.

## Consequences

Positive:

- Hold and reason recording are reachable from one selection context.
- The operation is reversible through the existing history mechanism.
- The UI makes the AI-independent persistence boundary explicit.

Trade-offs:

- A shared reason may be too broad for cards that need different explanations; users can refine individual notes afterward.
- Repeated use appends notes and can make a card's critique longer. The UI does not deduplicate authored text.

## Verification

- `src/ui/ux_operability_regression.test.ts` checks the reason editor contract and handler wiring.
- `src/i18n/catalog_integrity.test.ts` and `src/i18n/untranslated_key_inventory.test.ts` cover both catalogs.
- `e2e/bulk_hold_reason_flow.spec.ts` covers mouse selection, bulk hold, `Ctrl+Enter` reason save, and saved-state verification.

## Traceability

- Related issue: `01_Plans/issues/issue-UX-WORKFLOW-01-hold-critique-action-continuity.md`
- Related ADR: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`
