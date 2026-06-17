# Issue Draft: PRODUCT-VALUE-01 current open-readiness summary

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-PRODUCT-VALUE-01-first-meaningful-map-activation.md`
- Priority: P1
- Owner: Codex (Product Value evidence steward; accountable owner remains Productization Program Owner / QA Lead)
- Scope: `01_Plans/issues/issue-PRODUCT-VALUE-01-first-meaningful-map-activation.md`, `03_Implement/frontend/e2e/`, `04_Documentation/`
- Related Backlog: `PRODUCT-VALUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `docs-check`

## Current Open-Readiness Summary 2026-06-17

### Product Value Intent

`PRODUCT-VALUE-01` is the first-value gate for kj-atlas. The user must be able to start from a sample or a short memo, create at least a few cards, form a first meaningful grouping or focus point, and understand what remains undecided before saving or sharing. This issue is not about proving every downstream data structure. It is about proving that a first-time user can reach a useful, inspectable map without depending on an LLM.

### Current Mainline Status

- `mvp-manual-authoring-ui` is already canonical on `main`. It added manual card authoring, canvas right-click editing, first-run Docker hardening, MVP verification documentation, and the Advanced UI toggle.
- PR #2411 refreshed the representative realistic journey after Advanced UI moved non-essential controls out of the default first-run surface.
- PR #2412 through #2417 synchronized QA-E2E, Product QA, MVP-EXIT, Project baseline, and Project governance records around the same interpretation: manual authoring and Advanced UI improve productization evidence but do not approve shipment.
- Latest governance checkpoint: `PROJECT-GOV-01` post-2416 checkpoint records `origin/main@59bf94493651f734755c473122e835eff2ce59c8`, CI success through #2417, and `unmerged_count=0` for observed 2026-06-06-or-later `codex/*` branches.
- Current fixture manifest: PR #2428 names `buildFirstMeaningfulMapDocument()` in `03_Implement/frontend/e2e/helpers/product_value_fixtures.ts` as the PV01 reusable fixture, with document ID `doc_first_meaningful_map_mouse` and representative E2E `03_Implement/frontend/e2e/first_meaningful_map_mouse_flow.spec.ts`.

### Open-Readiness Gaps

- The source issue remains `Draft` because the first meaningful map gate has not yet been accepted as a value-bearing evidence packet by the Productization Program Owner / QA Lead. The fixture identity is now fixed, but human acceptance, screenshot or trace bundle location, and release decision linkage remain open.
- Manual card authoring lowers the risk of LLM dependency, but the product still needs evidence that the user can complete the first-value path with mouse and keyboard in a natural flow.
- The minimum evidence packet should include: input text or sample name, resulting cards, first grouping or focus point, visible undecided or pending state, SafeMode/import validation visibility, and the save/share preflight boundary.
- Human acceptance remains outside the automated evidence. Physical keyboard review, screen-reader acceptance, and release screenshots must be recorded in `PRODUCT-QA-01` / `MVP-EXIT-01` before this can support shipment.

### Next Implementation Slice

1. Review `doc_first_meaningful_map_mouse` and decide whether the three default cards and `Island 1` grouping represent the promised first value moment for a standard user.
2. Capture or cite a release evidence bundle that shows sample/import entry, first island creation, SafeMode visibility, and the save/share preflight boundary for this fixture.
3. Decide whether the existing keyboard release-candidate route can stand beside the PV01 mouse fixture, or whether PV01 needs its own fixture-specific keyboard trace.
4. Keep `PRODUCT-VALUE-01` in `Draft` until Productization Program Owner / QA Lead acceptance and `PRODUCT-QA-01` / `MVP-EXIT-01` decision linkage are recorded.

### ADR Boundary

No new ADR is needed for this summary. An ADR is required only if the project changes the definition of "first meaningful map", introduces persistent user profiles or cloud history, changes SafeMode/import policy, changes public sharing authority, or makes LLM assistance mandatory for the first-value path.

## Acceptance Criteria

- [ ] AC-01: The source issue has a reader-facing current summary or clearly links to this summary.
- [x] AC-02: A deterministic first-value fixture is defined before implementation work starts. Current fixture: `buildFirstMeaningfulMapDocument()` / `doc_first_meaningful_map_mouse`.
- [ ] AC-03: The evidence packet requirements are mapped to `PRODUCT-QA-01` and `MVP-EXIT-01`.
- [ ] AC-04: Any change to the meaning of "first meaningful map" is routed through ADR.

## Validation Plan

- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py`
- `git diff --check -- 01_Plans/issues/issue-PRODUCT-VALUE-01-current-open-readiness-summary.md`

## Authoring Checklist

- [x] `Source Issue` is aligned with the current work.
- [x] `Related ADR/Spec` contains the minimum references.
- [x] Acceptance criteria include safety, exchange, and verification.
- [x] `Validation plan` contains concrete commands.
- [x] Non-goals prevent scope creep.
