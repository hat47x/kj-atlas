# Issue: UX-STATE-01 Selection Target Consistency After Bulk Island Creation

- Type: Bug / UX
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: VALUE-DOGFOOD-01
- Priority: P1
- Owner: Codex
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-STATE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`
- Expected verification level: `e2e`

## Problem

When a user selects multiple cards and creates an island from the bulk operation bar, the UI can present competing target states. In the 2026-07-08 dogfood run, the header still reported `2 cards selected` while the right-side context panel reported `Island selected`.

This makes it unclear whether the next action applies to the selected cards, the island, or both.

## Why It Matters

Grouping cards is part of the core product value. If the action target is ambiguous immediately after a grouping operation, users may hesitate to continue or may apply hold, critique, delete, or review actions to the wrong object.

## Expected Behavior

- After bulk island creation, the primary selection target should be clear and consistent across the header, bulk bar, canvas, and side panel.
- If both the new island and the original cards remain selected, the UI should explicitly describe that combined state.
- If the island becomes the primary target, the bulk bar should no longer present card-only language without context.
- Keyboard focus and screen reader text should expose the same target model as the visual UI.

## Acceptance Criteria

- [x] Creating an island from two selected cards yields one unambiguous selection summary.
- [x] The side panel title, header status, and bulk operation surface describe the same primary target.
- [x] Card-only actions and island actions are visually and semantically separated when both are available.
- [x] A Playwright E2E covers mouse selection -> create island -> inspect target summary -> apply one safe operation.

## Validation Plan

- `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test e2e/*selection*.spec.ts --reporter=line`
- Add or update a targeted E2E if no existing spec covers this exact transition.
- Manually verify the same flow with a mouse and with keyboard selection.

## Implementation Notes

- 2026-07-10: Island creation now clears the source-card selection before selecting the new island. This removes the card-only bulk bar and leaves the island inspector as the single primary target.
- A targeted operability regression contract verifies that the transition preserves this ordering. `e2e/selection_target_after_island_creation.spec.ts` verifies both the rendered mouse flow and keyboard flow (`Enter` / `Shift+Space` selection followed by keyboard island creation).

## Dogfood Evidence

- `01_Plans/dogfood-log-2026-07-08.md`

## Verification update (2026-07-10)

- The existing mouse scenario selects two cards with a pointer, creates an island, and verifies that the island is the only primary target.
- The added keyboard scenario focuses each card, uses `Enter` and `Shift+Space` to select them, then focuses and activates `Create Island` with `Enter`.
- Both scenarios assert the same side-panel summary and that the card-only bulk bar is hidden after creation. No simultaneous card/island selection model is introduced.

## Completion record (2026-07-10)

- `e2e/selection_target_after_island_creation.spec.ts`: 2 passed.
- Pointer scenario: two-card selection -> island creation -> island summary -> island collapse operation.
- Keyboard scenario: `Enter` / `Shift+Space` selection -> keyboard island creation -> island summary -> keyboard island collapse operation.
- No ADR was added because the existing single-primary-target model was clarified; the product model was not changed.

## ADR Impact

No ADR is needed if the work only clarifies existing target semantics. Create an ADR only if the product model changes to allow simultaneous island and card primary selections.
