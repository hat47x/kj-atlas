# Issue Draft: PRODUCT-VALUE-01 current open-readiness summary

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-PRODUCT-VALUE-01-first-meaningful-map-activation.md`（Open 2026-06-20）
- Priority: P1
- Owner: Codex (Product Value evidence steward; accountable owner remains Productization Program Owner / QA Lead)
- Scope: `01_Plans/issues/issue-PRODUCT-VALUE-01-first-meaningful-map-activation.md`, `03_Implement/frontend/e2e/`, `04_Documentation/`
- Related Backlog: `PRODUCT-VALUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `docs-check`

## Draft→Open 2026-06-20
PV-01 parent issue Open化に伴いsummaryもOpen。ADR-0032 Accepted (ADR-0040)。

## Status Update 2026-06-24

Parent issue In Progress. All implementation (T1-T5) complete:
- **StartPanel**: value proposition messaging (en/ja)
- **DomainStateSummary**: card state counts + progress hints
- **CardView**: claimType/critique/reviewState badges (DOMAIN-EXPR-01)
- **SidePanel**: domain state display in card detail
- **T3 Keyboard accessibility**: keyboard_release_candidate_flow E2E covers Tab/Enter/Space. acceptance_check.md covers keyboard checks.
- **T4 E2E first-meaningful-map**: first_meaningful_map_mouse_flow, keyboard_release_candidate_flow, first_run_document_entry, first_value_share_preflight E2E all exist and passed (mainline evidence).
- **T5 Docs sync**: installation.md, operations.md, public_index.md, acceptance_check.md reference first-run path with StartPanel + SafeMode.

Remaining: Human product-value acceptance (H-PV1/H-PV2/H-PV3). No implementation blockers.
Full unit test suite: 173 files, 826 tests passed (2026-06-24).

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

## Current-Main Evidence Rerun 2026-06-17: PV01 first meaningful map fixture

- Candidate mainline: `origin/main@659c3097b90078dc7aa559fe7239cf7068678524`.
- Fixture: `buildFirstMeaningfulMapDocument()` / `doc_first_meaningful_map_mouse`.
- Representative E2E: `03_Implement/frontend/e2e/first_meaningful_map_mouse_flow.spec.ts`.
- Execution note: Playwright config could not start its `npm run dev` webServer on this Codex host because `npm` is not on the normal PATH. Vite was started directly with bundled Node.js, then Playwright was run against `http://127.0.0.1:4173`.
- Verification command:
  - `node .\node_modules\playwright\cli.js test e2e/first_meaningful_map_mouse_flow.spec.ts e2e/domain_expression_keyboard_access.spec.ts e2e/review_pack_trace_export.spec.ts --reporter=line`
- Result: **pass, 3 tests total; PV01 representative E2E passed**.

### Evidence packet impact

- The PV01 fixture remains executable on current `main` after the post-2430 baseline/governance sync.
- Mouse-operation evidence is refreshed for sample opening, two-card selection, `Create Island`, visible `Island 1`, and selection-context confirmation.
- This rerun does not satisfy Productization Program Owner / QA Lead acceptance, release-suitable screenshot or trace bundle approval, SafeMode/import/sample-entry screenshot evidence, physical keyboard acceptance, screen-reader acceptance, or shipment approval.
- Status impact: **Draft remains**. This is execution freshness evidence only.

## Screenshot Evidence Refresh 2026-06-17: PV01 first meaningful island

- Candidate mainline: `origin/main@e92710bfcbb4`.
- Capture script: `03_Implement/frontend/scripts/capture_product_value_screenshots.mjs`.
- Screenshot: `04_Documentation/assets/screenshots/product-value-first-island.png`.
- Fixture state: `doc_first_meaningful_map_mouse`, Japanese UI locale, two cards selected and grouped into `Island 1`.
- Regeneration command:
  - `node .\scripts\capture_product_value_screenshots.mjs`
- Evidence packet impact:
  - Adds a release-documentation-suitable visual proof for sample opening, card selection, first island creation, SafeMode visibility, and selection-context confirmation.
  - Does not satisfy Productization Program Owner / QA Lead acceptance, keyboard acceptance, screen-reader acceptance, full share preflight approval, or shipment approval.
  - Status impact: **Draft remains**.

## First-Value Share Preflight Evidence 2026-06-19

- Candidate mainline: `origin/main@bd7e7ee35275b25f0f17defe02cbde619dbaa0a8`.
- Representative E2E: `03_Implement/frontend/e2e/first_value_share_preflight.spec.ts`.
- Screenshot: `04_Documentation/assets/screenshots/product-value-first-island-share-preflight.png`.
- Evidence:
  - SafeMode ON is visible in the start panel before sample loading.
  - The same deterministic fixture proceeds through two-card selection, first-island creation, and Share & Reproduce.
  - SafeMode ON excludes unreviewed drafts at preflight and reports 5 remaining review signals.
- Verification: targeted Playwright **1 passed**; screenshot capture regenerated six Product Value images.
- Evidence packet impact:
  - Automated SafeMode/sample-entry/first-island/share-preflight evidence is now connected by one fixture.
  - Productization Program Owner / QA Lead fixture acceptance, mouse/keyboard naturalness, keyboard-fixture sufficiency, physical keyboard acceptance, screen-reader acceptance, and shipment approval remain open.
  - Status impact: **Draft remains**.

## Delegated Human Approval 2026-06-29: H-PV1

- 委任元: 利用者指示「人間承認（PRODUCT-VALUE-01/02/03 H-PV1/H-PV2/H-PV3）を代行」。
- 扱い: Codex が Productization Program Owner / QA Lead / UX reviewer の確認観点を代理レビューする。これは製品出荷承認、物理キーボード実機受入、スクリーンリーダー受入、Compose-backed release rehearsal の代替ではない。
- 参照E2E:
  - `first_meaningful_map_mouse_flow.spec.ts`
  - `first_value_share_preflight.spec.ts`
  - `domain_expression_keyboard_access.spec.ts`（keyboard route sufficiency）
- 参照スクリーンショット:
  - `04_Documentation/assets/screenshots/product-value-first-island.png`
  - `04_Documentation/assets/screenshots/product-value-first-island-share-preflight.png`
- 実行結果: 2026-06-29 対象Playwrightセット **10 passed**。

### H-PV1 decision

| Decision | Proxy outcome | Rationale |
| --- | --- | --- |
| Fixture represents first value moment | Go | `doc_first_meaningful_map_mouse` は3カードから2カードを束ね、`Island 1` と未レビュー状態を同時に見せる。標準利用者が「置いたもの」と「まだ決めていないこと」を理解できる最小シナリオとして妥当。 |
| Mouse path naturalness | Go | サンプルを開く、2カードを選択する、`Create Island` を押す、共有前確認へ進む経路が画面上の主要操作だけで完結する。 |
| Keyboard evidence sufficiency | Conditional Go | 既存 keyboard route はサンプル、検索、カード選択、違和感入力、共有前確認、フォーカス復帰を確認している。PV01専用fixtureの完全なkeyboard再演は将来強化でよい。 |
| Evidence bundle location | Go | 既存スクリーンショットとE2E名で再実行・参照できる。 |

- Status impact: H-PV1の「fixture意味」「操作自然性」「証跡場所」ブロッカーは代理レビュー済みとして扱う。Shipment No-Go要素（実機アクセシビリティ、release screenshot approval、Compose startup、最終program approval）は残す。
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
