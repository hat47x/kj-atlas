# CE1 Stream B Approval Log (Query Preview/UI boundary)

## Context
- CE1 contract (`CE1-PREVIEW-GATE-IF`, `CE0-SAFEMODE-IF`, `CE1-HASH-DET-IF`) requires Query Preview confirmation, safeMode strict guard, and deterministic same-input handling before submit.

## Decision
- Frontend Query Preview validation adds a strict blocker for `safeModePolicy=strict && reviewFilter=includeUnreviewed`.
- Frontend domain adds a canonical query key function for client-side deterministic checks with semantically equal inputs.
- UI tests keep submit-gate behavior visible and verify the new strict blocker rendering.

## Consequences
- Unreviewed text mixing is blocked at UI boundary before request dispatch in strict mode.
- Client can assert same-input determinism through canonical query key comparison.
- CE1 mock flow remains proposal-only and contract-compliant while backend integration is still stubbed.

## 2026-05-01 Stream B Phase Log (A2/A3 verify-only sync)

### Phase 1: Read Sync
- Reconfirmed fixed dependency order `A1 -> A2 -> A3` and Stream B scope constraints from the project dashboard prompt block.
- Reconfirmed A2 handoff ID and tie-break contract lock in `tests/fixtures/fb_p2c_01/polygon_autofit_cases.json` and `src/domain/p2c_polygon_handoff.ts`.
- No contract drift detected; no `02_Architecture/*` or backend edits required.

### Phase 2: A2 Mock Integration
- Verified fixture/stub path remains active by executing Stream B mock validation tests (`stream_d_p2c_mock_validation`, `p2a/validation`).
- Confirmed tests still consume frozen contract IDs and handoff IDs without interface expansion.

### Phase 3: A3 Frontend Implementation
- Verified readiness panel/UI contract output remains stable via render test (`P2AReadinessPanel.render.test.ts`).
- No additional API fields, no contract redefinition, and no backend dependency introduction.

### Phase 4: Verify & Handoff
- Regression commands passed (see terminal log in this commit).
- Handoff status for Stream D: **No unresolved frontend-side contract mismatch**; proceed with integration/doc sync using existing A1 fixed values.
