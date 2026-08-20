# Issue Draft: UI-QUALITY-A11Y-01 アクセシビリティテストの体系化と拡充

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Claude Code（a11y test steward; per ADR-0045）
- Scope: `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/canvas/`
- Related Backlog: `UI-QUALITY-A11Y-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Expected verification level: `unit`
- Progress: T1-T4 complete (10 components / 46 tests).

## Requirement meta I/F

- RequirementID: UI-QUALITY-A11Y-01
- RequirementStatement: ADR-0044 UQ-2（アクセシビリティ）が「薄い」と判定された課題に対し、主要対話要素にrole/aria/ラベルが付きスクリーンリーダで意味が取れることをユニットテストで検証できるようにする。
- AcceptanceScenario: 前提=新規UIコンポーネントが追加される / 操作=accessibility testファイルを実行する / 期待結果=aria-label/role/titleの欠落が検出される / 除外=WCAG適合認証、E2Eレベルのスクリーンリーダ実機テスト
- SecurityGateImpact: N/A

## 1) 課題

ADR-0044 は UQ-2（a11y）を「現状薄い → 拡充対象」と判定した。既存の `IslandView.accessibility.test.ts` は1ファイルのみで体系化されていない。

## 2) 背景

- `IslandView.accessibility.test.ts` が a11y テストの先行例（aria-label一致数検証）
- DOMAIN-EXPR-01/02 で CardView, DomainStateSummary, ShelfPanel が追加された
- テストパターン: `createElement` + `renderToStaticMarkup` + aria-label/role 検証

## 3) 提案

新規コンポーネントごとに accessiblity test を追加し、CIで実行可能にする。

## 4) 受入条件

- [x] DomainStateSummary.accessibility.test.ts (4 tests) — aria-label, label visibility, empty state
- [x] ShelfPanel.accessibility.test.ts (4 tests) — aria-label, restore button, empty state, reason text
- [x] CardView.accessibility.test.ts (7 tests) — role, aria-selected, claimType/critique/holdState/unreviewed aria-labels, tabIndex
- [x] StartPanel.accessibility.test.ts (6 tests) — dialog role, aria-modal, SafeMode, button labels
- [x] SearchBar.accessibility.test.ts (5 tests) — text input, prev/next, match counter, checkbox
- [x] ImportPanel.accessibility.test.ts (4 tests) — title, file input, drop zone, button
- [x] DomainStateFilterBar.test.ts (4 tests) — filter chips, highlight, clear button
- [x] 既存コンポーネント（SharePanel, NarrativesPanel 等）のa11y baseline

## 5) タスク分解

- [x] T1 DomainStateSummary a11y test
- [x] T2 ShelfPanel a11y test
- [x] T3 CardView domain badge a11y test
- [x] T3.5 StartPanel a11y test
- [x] T3.6 SearchBar a11y test
- [x] T3.7 ImportPanel a11y test
- [x] T3.8 DomainStateFilterBar a11y test
- [x] T4 Existing component a11y baseline scan

## Commits
- e0db0d79 DomainStateSummary + ShelfPanel (8)
- 46ee3189 CardView (7) + UI-QUALITY-A11Y-01 issue
- 3276c90b StartPanel (6)
- d9d8cd1b SearchBar (5)
- 8eee93f4 ImportPanel (4)
- 549b72fa DomainStateFilterBar (4)
- SharePanel baseline (2): trigger/dialog relationship, expanded state, accessible dialog and close labels
- NarrativesPanel baseline (3): labelled region/input, selected and expanded states, alert announcements
- **Total: 10 components, 46 a11y tests**
