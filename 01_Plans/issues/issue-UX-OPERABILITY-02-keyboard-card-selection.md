# Issue: UX-OPERABILITY-02 キーボードによるカード選択境界（仕様）

- Type: Planning
- Status: Open
- Priority: P1
- Owner: Stream C
- DecisionStatus: Fixed
- Execution: Ready
- Scope: `01_Plans/issues/`, `01_Plans/adr/`, `03_Implement/frontend/docs/e2e_testing.md`
- Related Backlog: `UX-OPERABILITY-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

カード選択におけるキーボード到達性を、実装方式に依存しない I/F 契約として固定する。

## I/F Contract (Mock-first)

- DOM expectation:
  - カード要素は `role="option"` 相当の選択可能要素として観測できる。
  - フォーカス中カードは `data-focus="card"`、選択済みカードは `aria-selected="true"` で観測できる。
- Event contract:
  - `Tab/Shift+Tab` でカードへ到達できる。
  - `Enter` または `Space` により `SelectionChanged(cardId)` が発火する。
  - `SelectionChanged(cardId)` 後に `ContextPanelRequested(cardId)` が発火し、UX-03 に引き渡される。

## AC (Acceptance Criteria)

- [ ] カードがキーボードフォーカス対象であることを仕様化している。
- [ ] `Enter/Space` による選択と、選択結果の確認可能性を仕様化している。
- [ ] 選択後の文脈導線を `UX-OPERABILITY-03` へ接続している。
- [ ] ポインタ操作との同等性（同一イベント契約）を回帰条件に含める。

## DoD

- [ ] AC が E2E で観測可能な事実として記述されている。
- [ ] 実装コードファイルは Scope に含まれない。
- [ ] 未確定アクセシビリティ項目がある場合は `Execution: Hold` と解除条件を記載する。

## Validation plan

- `rg -n "Tab|Shift\+Tab|Enter|Space|aria-selected|SelectionChanged|ContextPanelRequested" 01_Plans/issues/issue-UX-OPERABILITY-02-keyboard-card-selection.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-02-keyboard-card-selection.md`

## Dependencies

- Depends on: `UX-OPERABILITY-01`
- Blocks: `UX-OPERABILITY-03`
