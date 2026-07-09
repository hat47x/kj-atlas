# Issue: DX-E2E-01 Keep Playwright Runner And Test API On One Version

- Type: Bug / Developer experience
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: UX-STATE-01 validation
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/package.json`, local E2E setup
- Expected verification level: E2E

## Problem

The package lock resolves Playwright 1.58.2, but the caret range for `@playwright/test` allowed a local install of 1.61.1. Running the 1.58.2 Playwright CLI with 1.61.1 test definitions fails before tests are discovered.

## Expected Behavior

- The Playwright CLI and `@playwright/test` resolve to the same version in local development and CI.
- A direct E2E invocation starts the configured web server and discovers the requested test file.

## Acceptance Criteria

- [ ] `@playwright/test` is pinned to the lockfile's Playwright version.
- [ ] A clean dependency install resolves matching `playwright` and `@playwright/test` versions.
- [ ] A targeted E2E can run from the project command line.

## Implementation Notes

- 2026-07-10: pinned `@playwright/test` to `1.58.2`, matching the committed lockfile. A dependency reinstall resolves both `@playwright/test` and `playwright` to 1.58.2.
- 2026-07-10: `node_modules/.bin/playwright test e2e/selection_target_after_island_creation.spec.ts --reporter=line` passed. Use the project binary rather than calling the `playwright` package CLI file directly so pnpm's dependency resolution path is preserved.

## ADR Impact

No ADR is needed. This is dependency determinism within the existing E2E verification policy.
