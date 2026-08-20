# Issue: DX-E2E-05 First-run Start Panel Contract Drift

- Type: Bug / Test infrastructure
- Status: Done
- Source Issue: `PRODUCT-QA-01`
- Priority: P1
- Owner: Codex
- Scope: `03_Implement/frontend/e2e/first_run_start_panel.spec.ts`, `03_Implement/frontend/e2e/helpers/i18n.ts`
- Related Backlog: `DX-E2E-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
- Expected verification level: `e2e`

## Problem

The full Playwright suite could not collect any tests because `first_run_start_panel.spec.ts` imported five start-panel locator constants that were no longer exported. After collection was restored, the same spec still targeted a nonexistent `data-ui-region` value and asserted SafeMode as one text node even though the UI uses a `dt`/`dd` pair.

## Decision

Restore locale-neutral start-panel locators in the shared helper and align the spec with the current `data-panel="start-document-entry"`, accessible dialog name, and split safety-status structure. Runtime UI, SafeMode policy, and schema remain unchanged.

## Acceptance criteria

- [x] Playwright collects the full E2E suite without an import error.
- [x] The start panel is located through its current stable panel contract.
- [x] Japanese/English action names and SafeMode ON remain verified without coupling to hint text layout.
- [x] The 960px and 390px scenarios pass in a real browser.

## Validation

- System Chrome fallback: `playwright test e2e/first_run_start_panel.spec.ts --config=playwright.system-chrome.config.ts --reporter=line` -> 2 passed.
- Full-suite collection after the fix: 145 tests collected.

## Non-goals

- No application behavior, translation catalog, SafeMode, share/export, or accessibility-role redesign.
- No ADR-0054 or external-connection work.

## Completion record

- Completed: 2026-07-13
- Classification: test-contract drift that previously made the release E2E gate false-red before test execution.
