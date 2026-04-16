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
