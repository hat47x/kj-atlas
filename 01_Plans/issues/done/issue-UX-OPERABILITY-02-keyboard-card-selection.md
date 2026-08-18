# Issue: UX-OPERABILITY-02 キーボードによるカード選択境界（仕様）

- Type: Planning
- Status: Done
- Priority: P1
- Owner: Stream C
- Execution: Ready
- Scope: `01_Plans/issues/issue-UX-OPERABILITY-01..05*.md`（docs + frontend ui）
- Related Backlog: `UX-OPERABILITY-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

カード選択におけるキーボード到達性を、実装方式に依存しない I/F 契約として固定する。

## Operation Flow Contract（Unified / Mock-first）

- Pointer contract:
  - pointer 選択時は `SelectionChanged(cardId)` を発火し、keyboard 契約と同一の結果を返す。
- Keyboard contract:
  - `Tab/Shift+Tab` でカードへ到達できる。
  - `Enter` または `Space` により `SelectionChanged(cardId)` が発火する。
- Focus contract:
  - フォーカス中カードは `data-focus="card"` で観測できる。
  - 選択済みカードは `aria-selected="true"` で観測できる。
- Panel contract:
  - `SelectionChanged(cardId)` 後に `ContextPanelRequested(cardId)` が発火し、UX-03 に引き渡される。

## AC (Acceptance Criteria)

- [x] カードがキーボードフォーカス対象であることを仕様化している。
- [x] `Enter/Space` による選択と、選択結果の確認可能性を仕様化している。
- [x] 選択後の文脈導線を `UX-OPERABILITY-03` へ接続している。
- [x] ポインタ操作との同等性（同一イベント契約）を回帰条件に含める。

## DoD

- [x] AC が E2E で観測可能な事実として記述されている。
- [x] 実装コードファイルは Scope に含まれない。
- [x] 未確定アクセシビリティ項目がある場合は `Execution: Hold` と解除条件を記載する。

## Phase Plan（Read → Contract → Execute/Verify）

- Phase 1 Read:
  - UX-01 基底契約（pointer/keyboard/focus/panel）を読み込み、カード選択境界へマップ。
- Phase 2 Contract unify:
  - `SelectionChanged(cardId)` を pointer/keyboard 共通の正準イベントとして固定。
- Phase 3 Plan→Execute→Verify（max 3 self-heal）:
  - `docs-check-1`: Tab 到達性と Enter/Space 契約記述の確認。
  - `docs-check-2`: `data-focus` / `aria-selected` の観測属性確認。
  - `docs-check-3`: `ContextPanelRequested` 接続確認。
- Phase 4 Stopper:
  - キー割当競合、フォーカス観測不能、または UX-03 への依存未定義を検知したら `Execution: Hold`。

## Validation plan

- `rg -n "Operation Flow Contract|Tab|Shift\+Tab|Enter|Space|aria-selected|data-focus|SelectionChanged|ContextPanelRequested" 01_Plans/issues/issue-UX-OPERABILITY-02-keyboard-card-selection.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-02-keyboard-card-selection.md`

## Dependencies

- Depends on: `UX-OPERABILITY-01`
- Blocks: `UX-OPERABILITY-03`

## Hold trigger

- `Execution: Hold` は、フォーカス可視性・読み上げ可能名・キーボード到達性のいずれかが未確定で E2E 観測条件へ落とせない場合に適用する。
- 解除条件は、未確定項目が ADR-0030 と整合した観測可能文（DOM属性またはイベント契約）として AC/DoD に反映されること。


## Implementation Notes

- `03_Implement/frontend/src/canvas/CardView.tsx` における keyboard 選択契約（`Enter/Space`, `aria-selected`, `data-focus="card"`）を回帰対象として固定。
- `03_Implement/frontend/src/ui/SidePanel.tsx` で `selection-context` / `advanced` の段階開示契約（`data-panel`, `data-panel-group`, `aria-expanded`）を実装・検証。
- `03_Implement/frontend/src/ui/SharePanel.tsx` と `03_Implement/frontend/src/App.tsx` の `Escape` 閉鎖 + フォーカス復帰契約を回帰対象として維持。
