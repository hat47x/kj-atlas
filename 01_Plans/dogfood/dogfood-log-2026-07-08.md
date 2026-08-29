# Dogfood Log - 2026-07-08

> VALUE-DOGFOOD-01 follow-up. This run was performed by Codex as a surrogate operator using the local browser surface. It is useful as product evidence, but it does not replace a maintainer's own real-topic dogfood run required by ADR-0042.

## Run Context

- App URL: `http://127.0.0.1:4173/?locale=en`
- Browser: in-app Chromium surface
- Backend state: unavailable for `doc_phase1_canvas`; the app showed a 500 load error and then recovered through the built-in sample flow.
- Data used: built-in sample document with three Japanese cards.
- SafeMode: ON throughout the share/export preflight check.
- External sharing: not performed. The run opened the share/export panel and inspected the preflight content only.

## Steps Performed

1. Opened the app and observed the initial backend load failure for `doc_phase1_canvas`.
2. Used the start panel's built-in sample action. The app loaded three sample cards and displayed SafeMode ON.
3. Selected two cards by mouse-style interaction and created one island from the bulk operation bar.
4. Applied hold state to the two selected cards, then opened the critique workflow from the selection context panel.
5. Opened the Share & Reproduce panel and inspected the export preflight while SafeMode was ON.

## Observations

- The built-in sample fallback works and gives the user a path forward when the backend is unavailable. This is valuable for first-run evaluation.
- After creating an island from two selected cards, the canvas showed an island containing `2 card(s) in island`, but the right-side context and header status could be read as competing states: the header still said `2 cards selected`, while the side panel said `Island selected`. This is a value-harming ambiguity because the user may not know whether the next action will apply to the cards or the island.
- The hold operation is discoverable from the bulk operation bar. Critique is not available in the same bulk operation bar after the same selection; it is available from the side panel as `critique`. The split location makes the intended "leave ambiguity and retain a reason" workflow harder to learn.
- The Share & Reproduce preflight correctly showed SafeMode ON and explained that unreviewed drafts are excluded. It also displayed `View visibility: Restricted` and `Pack visibility: Public` at the same time. The information is technically useful, but a standard user may not immediately understand the difference between the view and the review pack.
- The preflight listed unresolved review signals before export. This supports product value because it turns sharing into a final check rather than a blind export.

## Friction Classification

### High Priority / Value-Harming

1. Selection state becomes ambiguous after creating an island from a multi-card selection.
   - User risk: the next operation target is unclear.
   - Product value impact: weakens trust in the core thinking loop of grouping, holding, and reviewing.
   - Tracking: `01_Plans/issues/done/issue-UX-STATE-01-selection-target-consistency-after-bulk-island.md`.

2. Hold and critique are split across different action surfaces for the same selected cards.
   - User risk: users can preserve a card but may miss the action that records why it remains unresolved.
   - Product value impact: weakens the domain concept that ambiguity should remain visible and explainable.
   - Tracking: `01_Plans/issues/done/issue-UX-WORKFLOW-01-hold-critique-action-continuity.md`.

### Lower Priority / Usability

1. Backend failure recovery is possible but the first visible state is still an error.
   - Existing fallback helps. A future first-run polish pass should make the "continue with sample" path more prominent when the server is unavailable.

2. Share preflight visibility terms need plainer guidance.
   - The current terms are precise, but users need a short explanation of why the view and pack can have different visibility.
   - Tracking: `01_Plans/issues/done/issue-UX-SHARE-02-visibility-scope-plain-language.md`.

## SafeMode And Share Preflight

- SafeMode ON was visible in the global header and in the Share & Reproduce panel.
- The preflight stated that unreviewed drafts are excluded while SafeMode is ON.
- The fixed redaction contexts were shown as locked for Share / Review Pack.
- No export or external sharing was executed during this run.

## NOTICE Stage Judgment

- No README NOTICE stage change is recommended from this run.
- Reason: this was a surrogate Codex run against a built-in sample with the backend unavailable. ADR-0042 requires maintainer use on a real topic before moving the project out of the current notice posture.

## Follow-Up

- Create or keep issues for the three observed UX frictions above.
- Run the same five-step flow on a maintainer-owned real topic before re-evaluating the README NOTICE stage.
