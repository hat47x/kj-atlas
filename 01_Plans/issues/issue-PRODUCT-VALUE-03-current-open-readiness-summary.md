# Issue Draft: PRODUCT-VALUE-03 current open-readiness summary

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-PRODUCT-VALUE-03-reviewable-outcome-package.md`（Open 2026-06-20）
- Priority: P1
- Owner: Codex (Product Value evidence steward; accountable owner remains Productization Program Owner / QA Lead)
- Scope: `01_Plans/issues/issue-PRODUCT-VALUE-03-reviewable-outcome-package.md`, `02_Architecture/value_traceability.md`, `04_Documentation/narratives.md`, `04_Documentation/data_handling.md`, `03_Implement/frontend/e2e/`
- Related Backlog: `PRODUCT-VALUE-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `02_Architecture/review_attribution.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `docs-check`

## Draft→Open 2026-06-20
PV-03 parent issue Open化に伴いsummaryもOpen。ADR-0032 Accepted。

## Status Update 2026-06-24

PV-03 In Progress. Implementation status:
- **Narrative grounding**: claimType + reviewState annotations in both markdown/HTML export AND in-app NarrativesPanel grounding display
- **Evidence/Contradiction Links**: narrative export now includes Evidence/Contradiction Links section (DOMAIN-EXPR-04)
- **Share preflight domain summary**: SharePanel already includes comprehensive domainExpressionSummary (unreviewed cards/islands, hold/unknown claims, critique targets, evidence/contradiction links, evidence gaps) with SafeMode masking
- **Read-only reviewer**: E2E verifies reviewer can inspect evidence without mutating source data
- **Review-pack trace export**: E2E verifies trace files (evidence, contradiction, analytics) in Detail export
- Full unit test suite: 173 files, 826 tests passed (2026-06-24).

Remaining: H-PV3 acceptance of the current reviewable package fixture, trace-back proof, SafeMode readability, and read-only reviewer journey is proxy-approved (2026-06-29, carried forward 2026-07-02). Formal package public contract, signature/approval workflow, physical keyboard acceptance, screen-reader acceptance, and final program approval remain outside this approval. No implementation blockers.

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

- The source issue is In Progress. The minimum reviewable package evidence packet is proxy-approved for the current fixture, including trace-export E2E, SafeMode/readability evidence, read-only reviewer inspection, screenshot or trace bundle location, and Product QA / MVP-EXIT decision linkage.
- The reviewable package must identify at least: summary, settled claims, unresolved points, evidence links or source references, review status, SafeMode/share-export result, and trace-back path to the source map.
- The reader must be able to return from the outcome package to the originating card, island, relation, or review state. A final-looking text export without trace-back is not enough.
- SafeMode ON must demonstrate masking or exclusion of unreviewed raw content, sensitive details, and unnecessary identity information.
- The package must avoid implying formal approval, signature, or organizational authorization unless a separate review workflow explicitly provides it.

### Next Implementation Slice

1. Keep `doc_review_pack_trace_export` replayable as the reviewable outcome package fixture.
2. Refresh screenshots of package preview, SafeMode/share-export confirmation, reviewed/unreviewed status, and trace-back paths when release-candidate evidence is regenerated.
3. Preserve read-only reviewer inspection as a non-mutating path for package recipients.
4. Keep `PRODUCT-QA-01` and `MVP-EXIT-01` cross-references current whenever the package evidence bundle changes.
5. Keep organizational approval, signatures, automatic publication, package public contract, and multi-reviewer workflow outside this issue unless a new ADR expands the authority model.

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
- Historical status impact at the time: **Draft remained**. Current H-PV carry-forward is recorded below.

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
  - Historical status impact at the time: **Draft remained**. Current H-PV carry-forward is recorded below.

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
  - Historical status impact at the time: **Draft remained**. Current H-PV carry-forward is recorded below.

## Delegated Human Approval 2026-06-29: H-PV3

- 委任元: 利用者指示「人間承認（PRODUCT-VALUE-01/02/03 H-PV1/H-PV2/H-PV3）を代行」。
- 扱い: Codex が Productization Program Owner / QA Lead / UX reviewer の確認観点を代理レビューする。これは正式な組織承認、電子署名、公開配布契約、最終出荷承認の代替ではない。
- 参照E2E:
  - `review_pack_trace_export.spec.ts`
  - `domain_expression_keyboard_access.spec.ts`
  - `first_value_share_preflight.spec.ts`
- 参照スクリーンショット:
  - `04_Documentation/assets/screenshots/product-value-review-pack-trace.png`
  - `04_Documentation/assets/screenshots/product-value-review-pack-readonly.png`
  - `04_Documentation/assets/screenshots/product-value-ambiguity-share-preflight.png`
- 実行結果: 2026-06-29 対象Playwrightセット **10 passed**。

### H-PV3 decision

| Decision | Proxy outcome | Rationale |
| --- | --- | --- |
| H-PV3-1 package fixture | Go | `doc_review_pack_trace_export` は reviewed target、support、contradiction、unreviewed counter-signal、reviewable island、trace files を含み、レビュー可能成果物の最小説明に足る。 |
| H-PV3-2 trace-back proof | Go | ZIP file-name proofに加え、read-only reviewer E2Eが元カード・根拠・矛盾の画面検査を確認している。現段階では追加のreader-facing backlink UIをOpen前必須にはしない。 |
| H-PV3-3 Overview/Detail trace controls | Go | Overviewではselected-card traceが無効化され、Detailでは有効化される。文言もexport結果と一致しており、標準レビュアーに対して誤解を招きにくい。 |
| SafeMode/read-only authority | Go | Share/Review Packの固定マスク文言とread-only編集無効化をE2Eで再確認した。 |

- Status impact: H-PV3のfixture/package acceptance、trace-back sufficiency、Overview/Detail UX acceptanceは代理レビュー済みとして扱う。正式なpackage public contract、署名/承認workflow、物理キーボード/スクリーンリーダー受入、最終出荷承認は残す。

## Acceptance Criteria

- [x] AC-01: The source issue has a reader-facing current summary or clearly links to this summary.
- [x] AC-02: The reviewable-package fixture is named, stored, and reusable before implementation starts. Current fixture: `buildReviewPackTraceDocument()` / `doc_review_pack_trace_export`.
- [x] AC-03: The package includes summary, settled claims, unresolved points, evidence/source references, review status, SafeMode/share-export result, and trace-back path.
- [x] AC-04: SafeMode ON evidence shows that unreviewed raw content, sensitive details, and unnecessary identity information are masked or excluded.
- [x] AC-05: The package does not imply formal approval, signature, or organizational authorization outside the accepted review model.

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
