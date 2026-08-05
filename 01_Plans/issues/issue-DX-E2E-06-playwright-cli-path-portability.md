# Issue: DX-E2E-06 Playwright CLI Path Portability

- Type: Documentation quality / Test infrastructure
- Status: Done
- Source Issue: `PRODUCT-QA-01`
- Priority: P2
- Owner: Codex
- Scope: `00_Prompt/agent_collaboration.md`, `03_Implement/frontend/docs/e2e_testing.md`
- Related Backlog: `DX-E2E-06`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `03_Implement/frontend/package.json`
- Expected verification level: `docs-check`

## Problem

The current dependency layout exposes the direct Playwright CLI at `node_modules/@playwright/test/cli.js`, while two authoritative execution examples still referenced `node_modules/playwright/cli.js`. On a clean pnpm-style install the old path does not exist, so the documented fallback command fails before Playwright starts.

## Decision

Keep `npm run e2e` as the primary command and update only current authoritative direct-execution examples to `@playwright/test/cli.js`. Historical issue evidence is not rewritten.

## Acceptance criteria

- [x] Current agent and E2E runbooks reference an installed CLI path.
- [x] Package scripts and product runtime behavior remain unchanged.
- [x] Historical command evidence remains an audit record rather than being silently rewritten.

## Validation

- `Test-Path 03_Implement/frontend/node_modules/@playwright/test/cli.js` -> true.
- `rg -n "node_modules/playwright/cli.js" 00_Prompt/agent_collaboration.md 03_Implement/frontend/docs/e2e_testing.md` -> 0 current authoritative matches.

## Non-goals

- Dependency upgrades, Playwright browser installation policy, or bulk rewriting historical issue logs.

## Completion record

- Completed: 2026-07-13
- Classification: documentation/test-command portability drift.
