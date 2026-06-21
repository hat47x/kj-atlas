# Issue Draft: UI-QUALITY-A11Y-01 アクセシビリティテストの体系化と拡充

- Type: Documentation quality
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Claude Code（a11y test steward; per ADR-0045）
- Scope: `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/canvas/`
- Related Backlog: `UI-QUALITY-A11Y-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Expected verification level: `unit`

## Requirement meta I/F

- RequirementID: UI-QUALITY-A11Y-01
- RequirementStatement: ADR-0044 UQ-2（アクセシビリティ）が「薄い」と判定された課題に対し、主要対話要素にrole/aria/ラベルが付きスクリーンリーダで意味が取れることをユニットテストで検証できるようにする。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario: 前提=新規UIコンポーネントが追加される / 操作=accessibility testファイルを実行する / 期待結果=aria-label/role/titleの欠落が検出される / 除外=WCAG適合認証、E2Eレベルのスクリーンリーダ実機テスト
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: N/A
- VerificationLevel: unit
- DecisionStatus: Fixed

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
- [ ] CardView.accessibility.test.ts — claimType badge aria-labels, critique indicator, holdState badge
- [ ] 既存コンポーネント（SharePanel, NarrativesPanel, StartPanel 等）のa11y baseline

## 5) タスク分解

- [x] T1 DomainStateSummary a11y test
- [x] T2 ShelfPanel a11y test
- [ ] T3 CardView domain badge a11y test
- [ ] T4 Existing component a11y baseline scan

## Commits
- e0db0d79 test(UQ-2): add accessibility tests for DomainStateSummary + ShelfPanel (8 tests)
