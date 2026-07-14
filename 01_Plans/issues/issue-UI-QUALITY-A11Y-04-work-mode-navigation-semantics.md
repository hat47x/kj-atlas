# Issue Draft: UI-QUALITY-A11Y-04 Work-mode navigation semantics

- Type: Architecture / Accessibility
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: TBD (Productization Program Owner / UX Lead)
- Scope: `02_Architecture/design/`, `01_Plans/adr/ADR-0053-work-mode-navigation-semantics.md`, `03_Implement/frontend/src/ui/WorkModePanel.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/e2e/`
- Related Backlog: `UI-QUALITY-A11Y-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0053-work-mode-navigation-semantics.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/issues/issue-UX-NAV-01-work-mode-surface-navigation-hierarchy.md`
- Expected verification level: `e2e`

## Requirement meta I/F

- RequirementID: UI-QUALITY-A11Y-04
- RequirementStatement: The work-mode navigation semantics must match the actual interaction model and must not expose a false tablist to keyboard or screen-reader users.
- PriorityClass: Should
- AcceptanceScenario: Given the work-mode surface is opened, when a user uses mouse or keyboard input, then the visible advanced workflows are reachable in a predictable order, Escape closes the surface, focus returns to the trigger, and the DOM uses dialog/heading/region semantics appropriate to the chosen model.
- GoNoGoGate: Optional
- SecurityGateImpact: N/A
- VerificationLevel: e2e
- DecisionStatus: Pending
- DecisionQueueRef: `ADR-0053`

## 1) Problem statement

The design request describes five work-mode tabs with `role="tablist"`, while the implementation currently renders one modal dialog containing stacked sections. The accessibility issue `UI-QUALITY-A11Y-02` correctly leaves this as an unresolved decision because the implemented UI has no literal tabs. Without an explicit decision, future changes may add ARIA tab roles without implementing tab behavior or may update the design source without recording the interaction consequences.

## 2) Context

- `WorkModePanel.tsx` owns a full-surface dialog, focus containment, Escape close, and focus return.
- `App.tsx` passes the advanced workflows as one `advancedWorkModeContent` tree.
- `design-request-2026-07-round3.md` asks for a five-function tab layout, while `design-qa-checklist.md` records the current stacked-region design judgment.
- `ADR-0052` is limited to canvas selection and menu semantics and must not be used to decide this issue.

## 3) Proposed resolution

Use `ADR-0053` to select one of these explicit models:

1. Stacked sections: keep one dialog, expose visible headings/regions, and verify ordinary Tab traversal across all visible workflows.
2. Literal tabs: implement a real tablist with selected state, arrow-key navigation, hidden-panel focus rules, and responsive behavior before adding tab roles.

The current recommendation is option 1 because it matches the implementation and keeps all advanced workflows visible during the productization transition. This recommendation is not final until the ADR deciders accept it.

### Baseline evidence before the decision

- The current source-level UI contract test `src/ui/ux_operability_regression.test.ts` passed **32/32** on 2026-07-15.
- The baseline confirms one `role="dialog"`, `aria-modal="true"`, a focusable panel root, Tab containment, Escape handling, and that Narratives/HIL/diff content is owned by `WorkModePanel` rather than `SidePanel`.
- This is baseline evidence only. It does not satisfy AC-1, AC-2, or AC-5 because the interaction model has not yet been accepted and the pointer/keyboard contract still needs a focused Playwright scenario.

## 4) Acceptance criteria

- [ ] AC-1: `ADR-0053` records an accepted decision and names the chosen interaction model.
- [ ] AC-2: The design source, `UX-NAV-01`, and `UI-QUALITY-A11Y-02` use the same model and terminology.
- [ ] AC-3: If stacked sections are accepted, the dialog has visible headings or named regions for each distinct workflow, and no false tab roles are present.
- [ ] AC-4: If literal tabs are accepted, the implementation provides selected-tab state, arrow-key navigation, hidden-panel focus handling, and responsive behavior before `role="tab"` is added.
- [ ] AC-5: Playwright covers mouse opening, keyboard traversal, Escape close, focus return, and the selected model's screen-reader-relevant DOM contract.
- [ ] AC-6: `validate_active_issue_memos.py` and the issue memo unit tests pass after the status transition.

## 5) Task breakdown

- [ ] T1: Review and accept or revise `ADR-0053` with the Productization Program Owner and UX Lead.
- [ ] T2: Synchronize the design source, `UX-NAV-01`, and `UI-QUALITY-A11Y-02` with the accepted model.
- [ ] T3: Implement only the semantics required by the accepted model.
- [ ] T4: Add or update focused Playwright coverage for pointer and keyboard actions.
- [ ] T5: Run typecheck, focused E2E, accessibility smoke, and issue memo validation.

## 6) Validation plan

- Before implementation: inspect the DOM and design source; confirm that the proposed roles describe the actual interaction model.
- After implementation:
  - `node node_modules/@playwright/test/cli.js test e2e/a11y_axe_smoke.spec.ts e2e/<work-mode-spec>.spec.ts --reporter=line`
  - `node node_modules/typescript/bin/tsc --noEmit`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- Expected result: no false tab semantics, predictable pointer/keyboard behavior, and no regression in Escape/focus-return behavior.

## 7) Alternatives considered

- Add `role="tablist"` to the current stacked content: rejected because ARIA roles would not match the interaction model.
- Close `UI-QUALITY-A11Y-02` without a decision: rejected because the design source and implementation would remain ambiguous.
- Redesign the entire work-mode surface immediately: deferred because it would mix a semantics decision with a larger product UX change.

## 8) Risks and rollback

- Risk: a tab decision can hide workflows and increase keyboard steps. Mitigation: require explicit arrow-key and focus behavior in AC-4.
- Risk: a documentation-only change can become stale. Mitigation: keep the design source, ADR, issue, and E2E contract in one traceability chain.
- Rollback: if the accepted model causes usability or accessibility regressions, restore the last verified interaction model and supersede `ADR-0053` with a new decision; do not leave partial ARIA roles in place.

## 9) Additional context

- This issue is intentionally Draft until the design/ownership decision is available.
- It is a derived task from the remaining item in `UI-QUALITY-A11Y-02`, not a request to change the existing `ADR-0052` scope.
