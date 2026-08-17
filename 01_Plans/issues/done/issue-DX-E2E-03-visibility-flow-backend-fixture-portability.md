# Issue: DX-E2E-03 Visibility Flow Backend Fixture Portability

- Type: DX / Test infrastructure
- Status: Done
- Source Issue: `UX-SHARE-02`
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/e2e/pub_visibility_i18n_readonly_flow.spec.ts`, `03_Implement/frontend/docs/e2e_testing.md`
- Related Backlog: `DX-E2E-03`
- Related ADR/Spec: `01_Plans/issues/issue-UX-SHARE-02-visibility-scope-plain-language.md`, `01_Plans/issues/issue-DX-E2E-02-canvas-legend-heading-drift.md`
- Expected verification level: `e2e`

## Problem

`pub_visibility_i18n_readonly_flow.spec.ts` contains visibility persistence, replacement, and read-only checks that call `/docs/doc_phase1_canvas` and `/ai/provider-status`. Without route fixtures, running the frontend E2E suite without the backend waits for the 30-second test timeout, even when the UI assertion itself is unrelated to backend behavior.

The `UX-SHARE-02` scope explanation scenario already used an explicit fixture, while the remaining tests had an implicit backend prerequisite. This made local reproduction slow and obscured whether a failure was a UI regression or an unavailable service.

## Expected behavior

- The file provides a deterministic route fixture for each scenario; it does not claim backend integration coverage.
- A frontend-only run completes without an unexplained backend timeout.
- The visibility persistence scenario explicitly verifies browser-side visibility state after reload; backend document persistence remains outside this fixture-backed file.

## Acceptance criteria

- [x] The visibility explanation scenario remains independently runnable with its fixture.
- [x] Persistence/replacement/read-only scenarios have a deterministic fixture boundary.
- [x] Running the file without a backend does not produce unexplained 30-second locator timeouts.
- [x] The test names and issue documentation distinguish fixture-backed UI coverage from backend integration coverage.

## Validation plan

- `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test e2e/pub_visibility_i18n_readonly_flow.spec.ts --reporter=line` -> 4 passed without a backend process.
- `vitest run src/ui/SharePanel.test.ts src/i18n/catalog_integrity.test.ts src/i18n/untranslated_key_inventory.test.ts` -> 18 passed.
- `python 01_Plans/issues/validate_active_issue_memos.py` -> `ok: validated 0 active issue memos`.

## Coverage classification

| Scenario | Coverage boundary |
| --- | --- |
| Visibility edits after reload | Fixture-backed UI plus browser storage persistence |
| Differing view and pack visibility explanation | Fixture-backed UI |
| English visibility and document replacement flow | Fixture-backed UI |
| Read-only and SafeMode restrictions | Fixture-backed UI |

Backend API persistence and provider implementation contracts remain covered by backend tests and are intentionally not represented as passing in this file.

## Completion record

- Completed: 2026-07-10
- Result: All four scenarios run independently with explicit `/packs/index.json`, `/docs/doc_phase1_canvas`, and `/ai/provider-status` fixtures.
- Product impact: No visibility semantics, SafeMode policy, persistence behavior, or share/export output changed.

## Non-goals

- No change to visibility semantics, SafeMode policy, persistence behavior, or share/export output.
- No masking of failed backend integration as a passing UI test.
