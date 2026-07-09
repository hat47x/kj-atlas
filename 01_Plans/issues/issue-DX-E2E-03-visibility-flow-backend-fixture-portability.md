# Issue: DX-E2E-03 Visibility Flow Backend Fixture Portability

- Type: DX / Test infrastructure
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `UX-SHARE-02`
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/e2e/pub_visibility_i18n_readonly_flow.spec.ts`, `03_Implement/frontend/playwright.config.ts`, `03_Implement/frontend/README.md`
- Related Backlog: `DX-E2E-03`
- Related ADR/Spec: `01_Plans/issues/issue-UX-SHARE-02-visibility-scope-plain-language.md`, `01_Plans/issues/issue-DX-E2E-02-canvas-legend-heading-drift.md`
- Expected verification level: `e2e`

## Problem

`pub_visibility_i18n_readonly_flow.spec.ts` contains visibility persistence and read-only checks that call `/docs/doc_phase1_canvas` and `/ai/provider-status` without defining Playwright route fixtures. Running the frontend E2E suite without the backend therefore waits for the 30-second test timeout, even when the UI assertion itself is unrelated to backend behavior.

The newly added `UX-SHARE-02` scope explanation scenario uses an explicit fixture and passes independently. The remaining tests still have an implicit backend prerequisite, which makes local reproduction slow and obscures whether a failure is a UI regression or an unavailable service.

## Expected behavior

- The file either provides a deterministic route fixture for each test that does not verify backend integration, or explicitly documents and enforces a backend webServer prerequisite.
- A frontend-only run fails fast with a clear setup error when backend integration is intentionally required.
- Visibility persistence tests retain their current API behavior checks; the fixture must not silently turn an integration test into a render-only test.

## Acceptance criteria

- [ ] The visibility explanation scenario remains independently runnable with its fixture.
- [ ] Persistence/replacement/read-only scenarios have an explicit backend dependency or deterministic fixture boundary.
- [ ] Running the file without a backend does not produce unexplained 30-second locator timeouts.
- [ ] The test names and issue documentation distinguish UI-only, frontend fixture, and backend integration coverage.

## Validation plan

- `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test e2e/pub_visibility_i18n_readonly_flow.spec.ts -g "share preflight explains" --reporter=line`
- Run the complete file once with the backend process available and once in the documented frontend-only mode.
- Record whether each scenario is UI-only, fixture-backed, or backend-integrated.

## Non-goals

- No change to visibility semantics, SafeMode policy, persistence behavior, or share/export output.
- No masking of failed backend integration as a passing UI test.
