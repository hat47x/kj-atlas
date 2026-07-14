# ADR-0053: Work-mode navigation semantics

- Status: Proposed
- Date: 2026-07-15
- Deciders: Productization Program Owner / UX Lead / Project Maintainers
- Scope: `02_Architecture/design/`, `03_Implement/frontend/src/ui/WorkModePanel.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/e2e/`

## Context

The design request for the work-mode surface describes five advanced-function tabs and asks for `role="tablist"` semantics. The current implementation has a single full-surface `role="dialog"` with one scrollable region. Narrative, HIL workflow, merge/patch workspace, critique, and diff content are rendered as stacked sections inside that region.

The current implementation therefore does not expose a tablist. Adding `role="tablist"` without changing the interaction model would misrepresent the UI to keyboard and screen-reader users. Conversely, changing to tabs would hide some advanced functions, introduce a selected-tab state, and require a new keyboard contract. `ADR-0052` intentionally does not decide this work-mode question.

## Decision

This ADR proposes the following recommendation for acceptance:

1. Keep the current work-mode surface as one modal dialog with clearly named, stacked advanced sections for the MVP-to-productization transition.
2. Do not add `role="tablist"`, `role="tab"`, or `aria-selected` unless the UI actually changes to a single-panel tab interaction.
3. Treat the work-mode title as the dialog name. Give each advanced function a visible heading and a stable region boundary where the component owns a distinct workflow.
4. Update the design source to describe the five-function grouping as an information architecture reference, not as a literal tab contract.
5. Add an E2E contract for mouse and keyboard traversal of the stacked sections, Escape close, focus return, and the absence of false tab semantics.

The alternative of a literal tab interface remains valid for a later product decision. It must be evaluated as a separate interaction change with explicit behavior for Left/Right arrow navigation, Home/End, selected-tab announcements, hidden-panel focus management, and mobile layout.

This ADR does not change the canvas/menu ARIA decision in `ADR-0052`.

## Consequences

- The existing dialog and focus-trap implementation can remain stable while the decision is reviewed.
- Keyboard users can traverse all visible advanced workflows with ordinary Tab navigation; no hidden tab panel is introduced.
- The design request and the implementation will have an explicit documented relationship instead of an implicit drift.
- A future tab redesign will require a new or superseding ADR and a new E2E contract; it must not be introduced as an ARIA-only patch.
- Until this ADR is accepted, `UI-QUALITY-A11Y-02` remains open for the work-mode semantics decision.

## Non-goals

- This ADR does not implement the work-mode UI.
- This ADR does not decide the visual order or detailed layout of each advanced workflow.
- This ADR does not add or remove AI capabilities, change provider behavior, or alter SafeMode/export boundaries.

## Traceability

- Related: `01_Plans/issues/issue-UI-QUALITY-A11Y-02-per-surface-aria-focus-spec.md`
- Related: `01_Plans/issues/issue-UI-QUALITY-A11Y-04-work-mode-navigation-semantics.md`
- Related: `01_Plans/issues/issue-UX-NAV-01-work-mode-surface-navigation-hierarchy.md`
- Related: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Related: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`
- Related: `01_Plans/adr/ADR-0052-canvas-and-menu-aria-semantics.md`
- Source: `02_Architecture/design/design-request-2026-07-round3.md`
- Source: `02_Architecture/design/design-qa-checklist.md`

---

## Authoring Checklist

- [x] Status, date, deciders, and scope are recorded.
- [x] Context, proposed decision, consequences, non-goals, and traceability are recorded.
- [x] The proposed interaction model is distinguishable from the literal-tab alternative.
- [ ] Productization Program Owner and UX Lead accept the proposed decision.
- [ ] The linked issue records the final decision and verification evidence.
