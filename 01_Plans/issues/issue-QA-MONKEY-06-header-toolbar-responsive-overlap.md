# Issue Draft: QA-MONKEY-06 Header toolbar responsive overlap

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui`
- Related Backlog: `QA-MONKEY-06`
- Related ADR/Spec: `04_Documentation/e2e_testing.md`, `02_Architecture/architecture.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-06
- RequirementStatement: Header toolbar controls must remain readable and non-overlapping at the default desktop browser viewport.
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=1280x720 browser viewport / 操作=open app and open view/share controls / 期待結果=toolbar buttons do not wrap into vertical unreadable labels or occlude canvas/right panels / 除外=very narrow mobile layout, which should be handled by its own breakpoint spec.
- GoNoGoGate（Required / Optional / N/A）: N/A
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export labels must remain visible.
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- Monkey testing at the default browser size showed the header toolbar crowding.
- Some buttons wrapped into stacked vertical text and dropdown panels overlapped canvas/right-panel content.
- SafeMode/share labels became harder to read during ordinary exploration.

## 2) 背景 / Context

- The app has accumulated many header controls for view modes, search, share/export, and CE workflows.
- Current layout appears to rely on available horizontal space without a stable overflow strategy.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Repeated analysis work needs a scannable, low-friction control surface.
- 安全（THREAT_MODEL / SafeMode）: SafeMode and share/export status should not be visually obscured.
- 企業・行政要件（enterprise_architecture）: Operator workflows require predictable navigation.
- 後方互換（schemas）: UI layout only; no data contract change.

## 4) 提案する解決策 / Proposed solution

- 変更対象: Frontend header/layout components.
- 変更の最小単位: Introduce stable toolbar wrapping/overflow groups or responsive breakpoints that preserve readable labels and panel placement.
- 非目標: Redesigning the full product navigation IA.

## 5) 受入条件 / Acceptance criteria

- [x] At 1280x720, toolbar labels are horizontal/readable and do not overlap adjacent controls.
- [x] Open panels are positioned without covering essential status controls incoherently.
- [x] SafeMode/share/export status remains visible and readable.
- [x] Browser screenshot/e2e regression covers at least 1280x720 and one narrower breakpoint.
- [x] No behavior changes to document data, SafeMode rules, or export output.

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Identify the header/control containers causing wrap and overlap.
- [x] T2 Add responsive grouping or overflow behavior.
- [x] T3 Verify screenshots at 1280x720 and a narrower breakpoint.
- [x] T4 Re-run frontend tests and browser smoke.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run typecheck`
  - `npm run test`
  - Browser screenshot checks at 1280x720 and narrow breakpoint.
- 期待結果:
  - No vertical button text, no incoherent overlap, SafeMode/share labels readable.
- 未実施時の理由・代替検証:
  - `npm run typecheck` passed.
  - `npm run test` passed: 159 files / 721 tests.
  - `npm run test -- src/ui/i18n_equivalence.integration.test.ts` passed: 9 tests.
  - Edge + Playwright browser metrics passed at 1280x720 and 920x720: offscreen toolbar buttons=0, vertical-ish labels=0, View/share panel header overlap=false, share panel viewport overflow=false.
  - Added `e2e/header_toolbar_layout.spec.ts` to keep the 1280x720 and 920x720 layout regression under Playwright E2E.

## 8) 代替案 / Alternatives considered

- 代替案A: Shorten labels only. Rejected as insufficient for accumulated controls.
- 代替案B: Hide lower-priority controls entirely. Rejected unless paired with an explicit overflow/menu design.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: Moving controls can disrupt existing keyboard/muscle-memory workflows.
- 影響範囲: Header toolbar and dropdown positioning.
- ロールバック手順: Revert layout grouping/overflow changes.

## 10) Additional context

- Closeout: ADR is not required for this repair because the change preserves the existing product navigation and only stabilizes responsive layout, panel placement, and legacy label presentation.

## Evidence Refresh 2026-06-06: current-main header and panel rerun

- Candidate: `origin/main@f9c042f595aa96754b6da83e0e62ca946f48ac27`.
- Reviewer: Codex.
- Scope: current-main Playwright rerun of the fixed header toolbar responsive-overlap path. This is an evidence refresh only; it does not change layout code, navigation information architecture, SafeMode/share-export behavior, issue status, or release authority.
- Local execution:
  - Bundled Node.js started Vite directly on `127.0.0.1:4173` because this Codex host did not expose `npm` on PATH.
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/first_run_document_entry.spec.ts e2e/header_toolbar_layout.spec.ts --reporter=line` -> pass, 11 tests.
- Covered user operations:
  - Toolbar button bounds and horizontal readability at 1440x900, 1280x720, 920x720, 768x720, and 390x720.
  - View panel and Share & Reproduce panel opening without crossing the header or viewport edge.
  - Keyboard focus into View / Share & Reproduce panels and `Escape` return to the originating button at 1440x900 and 768x720.
- Human follow-ups:
  - Confirm real Chrome visual screenshot approval remains required before release because Playwright geometry checks do not judge visual polish or Japanese copy quality.
  - Keep ADR escalation unnecessary unless the product changes the primary toolbar task model or global responsive-navigation strategy.

- ADR化が必要になる条件: Product-level navigation or responsive strategy is redefined.

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
