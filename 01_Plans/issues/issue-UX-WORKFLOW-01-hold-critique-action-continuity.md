# Issue: UX-WORKFLOW-01 Hold And Critique Action Continuity

- Type: Feature request / UX
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: VALUE-DOGFOOD-01
- Priority: P1
- Owner: Codex
- Scope: `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-WORKFLOW-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`
- Expected verification level: `e2e`

## Problem

The hold operation is available from the bulk operation bar, but critique is reached from the selection context panel. In the 2026-07-08 dogfood run, this made two closely related actions feel disconnected:

- Hold: preserve the unresolved item.
- Critique: record why the unresolved item remains ambiguous or needs reproposal.

For standard users, these are likely to be one continuous workflow rather than separate feature areas.

## Why It Matters

KJ Atlas should help users keep uncertainty visible without losing the reason for that uncertainty. If hold and critique are separated too strongly, users may preserve items without recording the reasoning that makes later review valuable.

## Expected Behavior

- When selected cards can be held, the UI should also make the next critique/reason-recording step discoverable.
- The user should not need to understand the internal difference between the bulk bar and the side panel to complete the hold -> reason -> review loop.
- The label should use product language that is natural in Japanese and English. Avoid exposing internal terms where a user-facing phrase is clearer.

## Acceptance Criteria

- [ ] A selected-card workflow offers a visible path from hold to critique/reason recording.
- [ ] The action names are consistent between the bulk bar, side panel, and keyboard flow.
- [ ] The UI explains or implies that critique notes remain saved even when AI reproposal is unavailable.
- [ ] E2E covers selected cards -> hold -> add critique reason -> verify saved state.

## Validation Plan

- `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test e2e/domain_expression_keyboard_access.spec.ts --reporter=line`
- Add or update an E2E for the mouse-first bulk operation path.
- Verify Japanese and English labels through catalog integrity tests.

## Dogfood Evidence

- `01_Plans/dogfood-log-2026-07-08.md`

## ADR Impact

No ADR is needed if this only changes action placement and copy. Revisit ADR-0040 only if the definition of hold, critique, or reproposal authority changes.
