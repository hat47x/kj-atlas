# Issue Draft: QA-MONKEY-05 Island accessibility duplicate controls

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/canvas`
- Related Backlog: `QA-MONKEY-05`
- Related ADR/Spec: `02_Architecture/architecture.md`, `04_Documentation/e2e_testing.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-05
- RequirementStatement: Island canvas controls must expose unique, purposeful accessible controls without duplicate select targets or nested button names.
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=document with one selected card / 操作=Create Island, inspect DOM/accessibility tree / 期待結果=one select/focus target per island and no compound button name containing child controls / 除外=visual-only island labels that are not interactive.
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A

## 1) 課題 / Problem statement

- Monkey test created an island from a selected card.
- DOM snapshot exposed multiple duplicate controls named like `Select island <uuid>`.
- A compound island button also included nested control text such as focus/collapse actions in its accessible name.

## 2) 背景 / Context

- Canvas islands contain multiple visual and interactive layers.
- The current DOM appears to expose repeated island selection affordances to keyboard/screen-reader users.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Canvas manipulation should remain understandable outside pointer-only use.
- 安全（THREAT_MODEL / SafeMode）: No direct safety impact.
- 企業・行政要件（enterprise_architecture）: Accessibility is important for enterprise/public operation.
- 後方互換（schemas）: UI DOM/accessibility change only.

## 4) 提案する解決策 / Proposed solution

- 変更対象: Frontend canvas/island components.
- 変更の最小単位: Audit `IslandView` interactive elements, mark decorative layers `aria-hidden`, and keep one keyboard target for island selection plus separate named controls for focus/collapse.
- 非目標: Redesigning island visual appearance or changing island data model.

## 5) 受入条件 / Acceptance criteria

- [x] One island creates one primary accessible select target.
- [x] Focus/collapse controls have separate concise accessible names.
- [x] No button accessible name contains unrelated child control labels.
- [x] Browser e2e or DOM snapshot regression verifies the accessibility tree after island creation.
- [x] No SafeMode/share-export behavior changes.

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Inspect `IslandView` and related canvas layer roles.
- [x] T2 Remove duplicate interactive roles from decorative layers.
- [x] T3 Add accessibility regression coverage.
- [x] T4 Re-run frontend tests and browser island creation smoke.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- <new-or-updated-island-a11y-test>`
  - Browser smoke: create island and inspect DOM snapshot.
- 期待結果:
  - Duplicate `Select island <uuid>` controls are eliminated.
- 完了時の検証:
  - Unit DOM snapshot coverage and browser smoke both confirm one select target plus separate focus/collapse controls.

## 8) 代替案 / Alternatives considered

- 代替案A: Hide all island controls from assistive tech. Rejected because keyboard users still need island operations.
- 代替案B: Leave duplicate controls as-is. Rejected because it creates confusing navigation.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: Removing the wrong role could make an operation inaccessible.
- 影響範囲: Canvas island interaction.
- ロールバック手順: Revert component role/ARIA changes and keep visual behavior unchanged.

## 10) Additional context

- ADR化が必要になる条件: Keyboard interaction model for the entire canvas is redesigned.

## 11) Closeout

- Implementation: polygon island hit targets now use a native transparent `button` with the decorative SVG marked `aria-hidden`; keyboard-triggered selection bypasses pointer coordinate hit-testing. Rectangular decorative layers are explicitly `aria-hidden`.
- Regression coverage: `IslandView.accessibility.test.ts` verifies rectangular, polygon, and collapsed island control naming.
- Browser smoke: on `http://127.0.0.1:4173/`, created an island from one selected card and inspected the DOM/accessibility snapshot. Result: `Select island` count=1, `Focus island` count=1, `Collapse island` count=1, and compound select names=false.
- Validation:
  - `npm run test -- src/canvas/IslandView.accessibility.test.ts` -> 3 tests passed
  - `npm run typecheck` -> passed

---
