# Issue: UX-SHARE-02 Plain Language For View And Pack Visibility

- Type: UX / Documentation alignment
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: VALUE-DOGFOOD-01
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/i18n/`, `04_Documentation/`
- Related Backlog: `UX-SHARE-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-PRODUCT-UX-03-safe-share-export-flow.md`
- Expected verification level: `unit + e2e`

## Problem

The share/export preflight can display different visibility values for the view and the review pack. In the 2026-07-08 dogfood run, the preflight showed:

- `View visibility: Restricted`
- `Pack visibility: Public`

The distinction is technically useful, but a standard user may not understand why one artifact is restricted while another is public or what practical effect that has before export.

## Why It Matters

The share/export flow is a safety boundary. Users should understand who can see each artifact before they create files intended for sharing or review.

## Expected Behavior

- The preflight should explain, in plain language, that view visibility and pack visibility refer to different artifacts.
- When the values differ, the UI should highlight that difference as something to confirm, not as a hidden detail.
- Japanese copy should use standard user-facing terms for sharing and visibility scope; avoid awkward literal expressions.

## Acceptance Criteria

- [ ] Preflight copy distinguishes the view from the review pack in one short user-facing explanation.
- [ ] Differing visibility values are easy to notice before export.
- [ ] Japanese and English catalogs contain matching entries.
- [ ] A SharePanel unit test covers the differing-visibility explanation.
- [ ] A Playwright or integration check confirms the explanation is visible in the share/export panel.

## Validation Plan

- `cd 03_Implement/frontend && node ./node_modules/vitest/vitest.mjs run src/ui/SharePanel.test.ts src/i18n/catalog_integrity.test.ts`
- `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`

## Dogfood Evidence

- `01_Plans/dogfood-log-2026-07-08.md`

## ADR Impact

No ADR is required unless visibility semantics or SafeMode/export policy changes. This issue should stay at copy and preflight presentation level.

## Implementation Evidence 2026-07-08

- Added preflight copy that distinguishes view visibility from pack visibility before export.
- The hint is visually emphasized when the view and pack visibility values differ.
- Added Japanese and English i18n catalog entries.
- Added a SharePanel unit test for the differing-visibility explanation.
- Verification:
  - `node .\node_modules\vitest\vitest.mjs run src/ui/SharePanel.test.ts src/i18n/catalog_integrity.test.ts src/i18n/untranslated_key_inventory.test.ts` -> 3 files / 18 tests passed.
  - `node .\node_modules\typescript\bin\tsc --noEmit` -> passed.
- Remaining: run a browser/Playwright check against the visible share/export panel before closing the issue.
