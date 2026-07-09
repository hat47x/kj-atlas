# Issue: DX-E2E-02 Canvas Legend Heading Assertion Drift

- Type: Bug / E2E maintenance
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: UX-LABEL-01 validation
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/e2e/canvas_legend.spec.ts`, `03_Implement/frontend/src/ui/CanvasLegend.tsx`
- Expected verification level: E2E

## Problem

The canvas legend renders the translation key `legend.group.shortcuts` as `Shortcuts`, while the E2E assertion still expected the removed label `Selected-card keys`. The implementation and translation catalog were already aligned; only the assertion had drifted.

## Resolution

Updated the E2E assertion to follow the rendered `Shortcuts` heading. No runtime behavior changed.

## Verification

- The focused canvas legend E2E passes together with the retention and shortcut E2E set.

## ADR Impact

No ADR is needed. This is a test expectation correction.
