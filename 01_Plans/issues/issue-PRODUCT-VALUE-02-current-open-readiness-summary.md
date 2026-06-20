# Issue Draft: PRODUCT-VALUE-02 current open-readiness summary

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-PRODUCT-VALUE-02-ambiguity-evidence-workflow.md`（Open 2026-06-20）
- Priority: P1
- Owner: Codex (Product Value evidence steward; accountable owner remains Productization Program Owner / QA Lead)
- Scope: `01_Plans/issues/issue-PRODUCT-VALUE-02-ambiguity-evidence-workflow.md`, `02_Architecture/value_traceability.md`, `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `03_Implement/frontend/e2e/`
- Related Backlog: `PRODUCT-VALUE-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `docs-check`

## Draft→Open 2026-06-20
PV-02 parent issue Open化（ADR-0040で循環デッドロック解消済み）に伴いsummaryもOpen。

## Current Open-Readiness Summary 2026-06-17

### Product Value Intent

`PRODUCT-VALUE-02` is the ambiguity and evidence workflow gate. It exists to prove that kj-atlas can keep unresolved material useful instead of turning it into accidental certainty. A user should be able to preserve holds, critiques, evidence gaps, contradictions, and counter-opinions as work states that remain visible, filterable, reviewable, and safe to include or exclude before sharing.

This is not a request for automatic truth scoring, automatic resolution, ranking, or AI-driven removal of uncertainty. The value is that the product lets people keep ambiguous material in a disciplined shape until a human decides what to do with it.

### Current Mainline Status

- `ADR-0032` is accepted and keeps V1/V2/V3 active: externalization, structuring, and human review are product-value loops, not optional polish.
- `ADR-0040` resolves the earlier circular blocker between `ADR-0032` and `PRODUCT-VALUE-02`. Existing schema concepts such as `claimType`, `critiqueInputs`, `evidenceLinks`, `reviewState`, and review attribution can be surfaced first without forcing a broad schema migration.
- The phase boundary is clear: Phase 1 should expose existing reversible state as readable UI and evidence; later phases may add optional hold/shelf fields only after a separate issue or ADR confirms the data contract.
- The recent mainline convergence through PR #2418 records that manual authoring and first-value readiness are improving, but it does not yet prove the ambiguity workflow.
- Current fixture manifest: PR #2428 names `buildDomainExpressionDocument()` in `03_Implement/frontend/e2e/helpers/product_value_fixtures.ts` as the PV02 reusable fixture, with document ID `doc_domain_expression_keyboard_access` and representative E2E `03_Implement/frontend/e2e/domain_expression_keyboard_access.spec.ts`.

### Open-Readiness Gaps

- The source issue remains `Draft` because the product has not completed the owner-reviewed Go/No-Go rule for the ambiguity evidence workflow. The Phase 1 fixture identity is now fixed, but hold/pending evidence, share/export proof, AI-boundary proof, and UX acceptance of findability remain open.
- Current documentation names the concepts, but the representative user journey still needs to show exactly how a person notices, preserves, filters, reviews, and shares unresolved material.
- The UI must distinguish "unresolved", "needs review", "evidence missing", and "counter-opinion present" from final answers. These states must not be silently collapsed into a normal card, island, or final narrative.
- SafeMode and share/export behavior must prove that unresolved or unreviewed material is handled deliberately. The product should show what will be included, excluded, or masked before the user shares a package.
- `human_reviewed` remains a human-only state. No worker, AI assist path, import path, or API convenience behavior may set it automatically.

### Next Implementation Slice

1. Review `doc_domain_expression_keyboard_access` as the Phase 1 ambiguity/evidence fixture and decide whether split-first evidence is acceptable for standard users.
2. Add or cite share/export preflight evidence showing that the ambiguous target claim, unreviewed contradiction, critique note, and evidence links remain visible or safely excluded before sharing.
3. Add or cite AI-boundary proof showing that ambiguity/evidence/contradiction is carried as a constraint and cannot be converted into `human_reviewed` by a worker, AI assist path, import path, or API shortcut.
4. Decide whether read-only reachability is enough for Phase 1 findability, or whether dedicated unresolved-state filters must be added before Open.
5. Record the result in `PRODUCT-QA-01` before changing the source issue from `Draft` to `Open`.

### ADR Boundary

No new ADR is needed for the Phase 1 summary. A new ADR is required if implementation introduces new persistent schema fields for hold/shelf membership, changes the meaning of `human_reviewed`, adds automatic resolution or scoring, changes SafeMode/share-export policy, or makes LLM assistance mandatory for ambiguity handling.

## Current-Main Evidence Rerun 2026-06-17: PV02 ambiguity/evidence fixture

- Candidate mainline: `origin/main@659c3097b90078dc7aa559fe7239cf7068678524`.
- Fixture: `buildDomainExpressionDocument()` / `doc_domain_expression_keyboard_access`.
- Representative E2E: `03_Implement/frontend/e2e/domain_expression_keyboard_access.spec.ts`.
- Execution note: Playwright config could not start its `npm run dev` webServer on this Codex host because `npm` is not on the normal PATH. Vite was started directly with bundled Node.js, then Playwright was run against `http://127.0.0.1:4173`.
- Verification command:
  - `node .\node_modules\playwright\cli.js test e2e/first_meaningful_map_mouse_flow.spec.ts e2e/domain_expression_keyboard_access.spec.ts e2e/review_pack_trace_export.spec.ts --reporter=line`
- Result: **pass, 3 tests total; PV02 representative E2E passed**.

### Evidence packet impact

- The PV02 Phase 1 fixture remains executable on current `main` after the post-2430 baseline/governance sync.
- Keyboard evidence is refreshed for selecting the ambiguous target claim, reading `Review state: Unreviewed`, reaching claim type, evidence/contradiction text, critique note, review checkbox, and critique tag controls.
- This rerun does not satisfy hold/pending split acceptance, share/export preflight evidence for unresolved or unreviewed ambiguity state, AI-boundary proof, UX acceptance of findability, physical keyboard acceptance, screen-reader acceptance, or shipment approval.
- Status impact: **Draft remains**. This is execution freshness evidence only.

## Screenshot Evidence Refresh 2026-06-17: PV02 ambiguity state

- Candidate mainline: `origin/main@e92710bfcbb4`.
- Capture script: `03_Implement/frontend/scripts/capture_product_value_screenshots.mjs`.
- Screenshot: `04_Documentation/assets/screenshots/product-value-ambiguity-state.png`.
- Fixture state: `doc_domain_expression_keyboard_access`, Japanese UI locale, ambiguous target claim selected inside a review cluster with review state visible.
- Regeneration command:
  - `node .\scripts\capture_product_value_screenshots.mjs`
- Evidence packet impact:
  - Adds a visual proof that an unresolved claim, supporting note, counter-opinion, grouped context, SafeMode visibility, and side-panel review state can be inspected in the current UI.
  - Does not satisfy hold/pending split acceptance, share/export preflight evidence for unresolved material, AI-boundary proof, UX acceptance of findability, physical keyboard acceptance, screen-reader acceptance, or shipment approval.
  - Status impact: **Draft remains**.

## Share Preflight Evidence 2026-06-18

- Candidate mainline: `origin/main@2e1f0edd38a089005269da91b213914500ec3af5`.
- Representative E2E: `03_Implement/frontend/e2e/domain_expression_keyboard_access.spec.ts`.
- Screenshot: `04_Documentation/assets/screenshots/product-value-ambiguity-share-preflight.png`.
- Evidence:
  - Share & Reproduce keeps unresolved-domain counts visible before export.
  - The deterministic fixture reports 2 unreviewed cards, 1 Hold/unknown claim, 1 critique target, 2 evidence links, 1 contradiction, and 0 evidence gaps.
  - SafeMode ON states that unreviewed drafts are excluded and does not expose the include-drafts control.
- Verification: targeted Playwright **2 passed**.
- Evidence packet impact:
  - The Phase 1 share/export proof requirement is now replayable and has a Japanese UI screenshot.
  - Hold/Pending schema work, AI-boundary proof, human findability acceptance, keyboard/screen-reader acceptance, and umbrella Product Value approval remain open.
  - Status impact: **Draft remains**.

## AI Review-Boundary Evidence 2026-06-19

- Candidate mainline: `origin/main@219eec7ed1e9e36c87905bae04cd917b1b98efa5`.
- Implementation evidence:
  - `03_Implement/backend/src/kj_atlas_api/models_ai.py`
  - `03_Implement/frontend/src/domain/hil_rs_contract.ts`
  - `03_Implement/frontend/src/domain/hil_rs_apply.ts`
- Result:
  - AI proposal responses are limited to `unreviewed`.
  - HIL rediff validation and application reject direct or nested review-state injection.
  - Valid human review attribution remains an import/persistence responsibility rather than an AI-generated state.
- Verification: backend 6 passed; frontend targeted 23 passed; typecheck passed.
- Evidence packet impact:
  - The AI/worker automatic `human_reviewed` promotion blocker is addressed with defense in depth.
  - ContextBundle constraint-preservation proof, Hold/Pending work, human findability/accessibility acceptance, and umbrella Product Value approval remain open.
  - Status impact: **Draft remains**.

## ContextBundle Constraint Evidence 2026-06-19

- Candidate mainline: `origin/main@8f81e5d70112d9570bf5c940a206a216cd468293`.
- Fixed profile: `A2-minimal-v1`.
- Evidence:
  - The reviewed selected item remains a hypothesis rather than becoming a fact.
  - Selected items, relations, evidence, counter-opinions, and contradictions are explicitly unresolved, constraint-only, and not eligible for automatic resolution.
  - Strict SafeMode excludes unreviewed counter-opinion text while preserving non-textual evidence and contradiction signals for downstream review.
  - The route-level test verifies the semantics through `/context/bundle`, in addition to the existing deterministic hash and preview-gate checks.
- Evidence packet impact:
  - The fixed-profile ContextBundle constraint-preservation blocker is addressed.
  - Real data-source projection parity remains held by the existing CE1 integration boundary.
  - Hold/Pending, human findability/accessibility acceptance, and umbrella Product Value approval remain open.
  - Status impact: **Draft remains**.

## Acceptance Criteria

- [ ] AC-01: The source issue has a reader-facing current summary or clearly links to this summary.
- [x] AC-02: The deterministic ambiguity fixture is named, stored, and reusable before implementation starts. Current fixture: `buildDomainExpressionDocument()` / `doc_domain_expression_keyboard_access`.
- [ ] AC-03: The UI/E2E evidence distinguishes unresolved, unreviewed, evidence-missing, and counter-opinion states from final conclusions.
- [ ] AC-04: Share/export preflight evidence shows how unresolved and unreviewed material is handled under SafeMode.
- [ ] AC-05: Any schema expansion or review-authority change is routed through issue/ADR before code changes.

## Validation Plan

- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py`
- `git diff --check -- 01_Plans/issues/issue-PRODUCT-VALUE-02-current-open-readiness-summary.md`

## Authoring Checklist

- [x] `Source Issue` is aligned with the current work.
- [x] `Related ADR/Spec` contains the minimum references.
- [x] Acceptance criteria include safety, exchange, and verification.
- [x] `Validation plan` contains concrete commands.
- [x] Non-goals prevent scope creep.
