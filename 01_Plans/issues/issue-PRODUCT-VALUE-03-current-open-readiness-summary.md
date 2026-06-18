# Issue Draft: PRODUCT-VALUE-03 current open-readiness summary

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-PRODUCT-VALUE-03-reviewable-outcome-package.md`
- Priority: P1
- Owner: Codex (Product Value evidence steward; accountable owner remains Productization Program Owner / QA Lead)
- Scope: `01_Plans/issues/issue-PRODUCT-VALUE-03-reviewable-outcome-package.md`, `02_Architecture/value_traceability.md`, `04_Documentation/narratives.md`, `04_Documentation/data_handling.md`, `03_Implement/frontend/e2e/`
- Related Backlog: `PRODUCT-VALUE-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `02_Architecture/review_attribution.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `docs-check`

## Current Open-Readiness Summary 2026-06-17

### Product Value Intent

`PRODUCT-VALUE-03` is the reviewable outcome package gate. It exists to prove that kj-atlas can produce an output that another person can inspect without losing the path back to the source material, unresolved points, SafeMode choices, and review status.

The output package is not just a polished narrative or export file. It must carry enough context for a reader to understand what is settled, what is still uncertain, what evidence was used, and what was intentionally withheld or masked.

### Current Mainline Status

- `ADR-0032` defines V4 as sharing and learning: narrative, review pack, SafeMode, review attribution, and source trace must connect to a pre-share confirmation flow.
- `ADR-0031` and the current documentation already emphasize screen information architecture, SafeMode visibility, and share/export confirmation.
- `data_handling.md` describes the user's responsibility to confirm what is shared and what is excluded. It also anchors the expectation that unreviewed material and sensitive content must not be exposed accidentally.
- Recent mainline PRs improved evidence governance and project baseline records, but no current PR proves that an exported outcome can be reviewed end to end as a product artifact.
- Current fixture manifest: PR #2428 names `buildReviewPackTraceDocument()` in `03_Implement/frontend/e2e/helpers/product_value_fixtures.ts` as the PV03 reusable fixture, with document ID `doc_review_pack_trace_export` and representative E2E `03_Implement/frontend/e2e/review_pack_trace_export.spec.ts`.

### Open-Readiness Gaps

- The source issue remains `Draft` because the minimum reviewable package has not yet been accepted as a Go/No-Go evidence packet. The fixture identity and trace-export E2E are fixed, but SafeMode/readability evidence, read-only reviewer inspection, screenshot or trace bundle location, and final Product QA / MVP-EXIT decision linkage remain open.
- The reviewable package must identify at least: summary, settled claims, unresolved points, evidence links or source references, review status, SafeMode/share-export result, and trace-back path to the source map.
- The reader must be able to return from the outcome package to the originating card, island, relation, or review state. A final-looking text export without trace-back is not enough.
- SafeMode ON must demonstrate masking or exclusion of unreviewed raw content, sensitive details, and unnecessary identity information.
- The package must avoid implying formal approval, signature, or organizational authorization unless a separate review workflow explicitly provides it.

### Next Implementation Slice

1. Review `doc_review_pack_trace_export` and decide whether it represents the promised reviewable outcome package for a standard reviewer.
2. Capture or cite screenshots of package preview, SafeMode/share-export confirmation, reviewed/unreviewed status, and trace-back from output to source material.
3. Add or cite read-only reviewer inspection evidence that a package recipient can inspect the outcome without mutating source data.
4. Add an evidence record to `PRODUCT-QA-01` and cross-reference it from `MVP-EXIT-01` only after the package can be regenerated.
5. Keep organizational approval, signatures, automatic publication, and multi-reviewer workflow outside this issue unless a new ADR expands the authority model.

### ADR Boundary

No new ADR is needed to define the minimum package evidence. A new ADR is required if the package format becomes a stable public contract, if electronic signature or formal approval semantics are introduced, if review attribution authority changes, if SafeMode/share-export policy changes, or if the product starts publishing packages automatically.

## Current-Main Evidence Rerun 2026-06-17: PV03 reviewable package fixture

- Candidate mainline: `origin/main@659c3097b90078dc7aa559fe7239cf7068678524`.
- Fixture: `buildReviewPackTraceDocument()` / `doc_review_pack_trace_export`.
- Representative E2E: `03_Implement/frontend/e2e/review_pack_trace_export.spec.ts`.
- Execution note: Playwright config could not start its `npm run dev` webServer on this Codex host because `npm` is not on the normal PATH. Vite was started directly with bundled Node.js, then Playwright was run against `http://127.0.0.1:4173`.
- Verification command:
  - `node .\node_modules\playwright\cli.js test e2e/first_meaningful_map_mouse_flow.spec.ts e2e/domain_expression_keyboard_access.spec.ts e2e/review_pack_trace_export.spec.ts --reporter=line`
- Result: **pass, 3 tests total; PV03 representative E2E passed**.

### Evidence packet impact

- The PV03 review-pack trace fixture remains executable on current `main` after the post-2430 baseline/governance sync.
- Review-pack export evidence is refreshed for importing the fixture, selecting the target claim, verifying Overview trace exclusion, verifying Detail trace inclusion, and confirming ZIP contents for evidence, contradiction, and trace analytics files.
- This rerun does not satisfy Productization Program Owner / QA Lead package acceptance, SafeMode/readability screenshot evidence, read-only reviewer inspection, release-suitable screenshot or trace bundle approval, approval/signature authority, or shipment approval.
- Status impact: **Draft remains**. This is execution freshness evidence only.

## Screenshot Evidence Refresh 2026-06-17: PV03 traceable review package

- Candidate mainline: `origin/main@e92710bfcbb4`.
- Capture script: `03_Implement/frontend/scripts/capture_product_value_screenshots.mjs`.
- Screenshot: `04_Documentation/assets/screenshots/product-value-review-pack-trace.png`.
- Fixture state: `doc_review_pack_trace_export`, Japanese UI locale, selected reviewed claim, Share & Reproduce panel open, selected-card traces enabled, detail granularity selected.
- Regeneration command:
  - `node .\scripts\capture_product_value_screenshots.mjs`
- Evidence packet impact:
  - Adds a visual proof that the current sharing surface can expose SafeMode context, reviewed/unreviewed state, trace inclusion, and detail export granularity together.
  - Does not satisfy Productization Program Owner / QA Lead package acceptance, read-only reviewer inspection, ZIP content acceptance, approval/signature authority, or shipment approval.
  - Status impact: **Draft remains**.

## Read-only Reviewer Evidence 2026-06-18

- Candidate mainline: `origin/main@d2b5f8cfab8d5ac49388f0f130dae1eeb2315049`.
- Representative E2E: `03_Implement/frontend/e2e/review_pack_trace_export.spec.ts`.
- Screenshot: `04_Documentation/assets/screenshots/product-value-review-pack-readonly.png`.
- Evidence:
  - A reviewer can open the PV03 fixture in read-only mode, select the reviewed target claim, and inspect supporting and contradicting evidence.
  - Primary editing actions and card-level claim/review/evidence/critique controls are disabled before interaction rather than failing only after activation.
  - Share & Reproduce remains available for inspection and continues to show the fixed SafeMode redaction context.
- Verification:
  - Targeted Playwright: 2 passed.
  - Frontend typecheck: pass.
  - UX operability regression: 6 passed.
- Evidence packet impact:
  - The automated read-only reviewer inspection requirement is now replayable and has a Japanese UI screenshot.
  - Productization Program Owner / QA Lead package acceptance, physical keyboard acceptance, screen-reader acceptance, and final shipment approval remain open.
  - Status impact: **Draft remains**.

## Acceptance Criteria

- [ ] AC-01: The source issue has a reader-facing current summary or clearly links to this summary.
- [x] AC-02: The reviewable-package fixture is named, stored, and reusable before implementation starts. Current fixture: `buildReviewPackTraceDocument()` / `doc_review_pack_trace_export`.
- [ ] AC-03: The package includes summary, settled claims, unresolved points, evidence/source references, review status, SafeMode/share-export result, and trace-back path.
- [ ] AC-04: SafeMode ON evidence shows that unreviewed raw content, sensitive details, and unnecessary identity information are masked or excluded.
- [ ] AC-05: The package does not imply formal approval, signature, or organizational authorization outside the accepted review model.

## Validation Plan

- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py`
- `git diff --check -- 01_Plans/issues/issue-PRODUCT-VALUE-03-current-open-readiness-summary.md`

## Authoring Checklist

- [x] `Source Issue` is aligned with the current work.
- [x] `Related ADR/Spec` contains the minimum references.
- [x] Acceptance criteria include safety, exchange, and verification.
- [x] `Validation plan` contains concrete commands.
- [x] Non-goals prevent scope creep.
