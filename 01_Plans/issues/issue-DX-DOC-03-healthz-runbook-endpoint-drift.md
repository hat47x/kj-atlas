# Issue: DX-DOC-03 Health Check Endpoint Drift

- Type: Documentation quality
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `PRODUCT-QA-01`
- Priority: P3
- Owner: Codex
- Scope: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Related Backlog: `DX-DOC-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `03_Implement/frontend/docs/e2e_testing.md`
- Expected verification level: `docs-check`

## Problem

ADR-0019 still showed the Compose health probe as `/api/health`, while the implemented and operationally verified endpoint is `/api/healthz`. The parenthetical "or equivalent" avoided a functional contradiction but left a copy-paste failure in the canonical acceptance example.

## Decision

Update the ADR example to the implemented `/api/healthz` endpoint. No API contract or runtime route changes.

## Acceptance criteria

- [x] ADR-0019 and the E2E runbook use `/api/healthz` for the Compose probe.
- [x] Backend-local checks continue to use `/healthz`.
- [x] No runtime, SafeMode, or deployment behavior changes.

## Validation

- `rg -n "localhost:8080/api/healthz" 01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md 03_Implement/frontend/docs/e2e_testing.md` -> both references present.
- `git diff --check` -> pass.

## Non-goals

- Route aliases, Compose startup changes, or health payload changes.

## Completion record

- Completed: 2026-07-13
- Classification: current-runbook copy/paste drift.
