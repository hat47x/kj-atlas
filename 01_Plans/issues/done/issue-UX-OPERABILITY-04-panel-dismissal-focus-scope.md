# Issue: UX-OPERABILITY-04 パネル閉じる操作とフォーカス復帰境界（仕様）

- Type: Planning
- Status: Done
- Priority: P1
- Owner: Stream C
- Execution: Ready
- Scope: `01_Plans/issues/issue-UX-OPERABILITY-01..05*.md`（docs + frontend ui）
- Related Backlog: `UX-OPERABILITY-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

`表示` / `共有と再現` パネルの `Escape` 閉じると起点フォーカス復帰を I/F 境界として固定する。

## Operation Flow Contract（Unified / Mock-first）

- Pointer contract:
  - pointer 起点で開いたパネルでも `Escape` 閉じる契約を適用する。
- Keyboard contract:
  - keyboard 起点で開いたパネルでも `Escape` で閉じる。
- Focus contract:
  - 開始ボタンは `data-focus-return-id` を保持し、`FocusReturned(triggerId)` 後に同一起点へ復帰する。
- Panel contract:
  - 一時パネルは `data-panel="view"` / `data-panel="share-replay"` で識別できる。
  - open 中の `Escape` で `PanelDismissed(panelId, reason="escape")` を発火する。
  - `PanelDismissed` 後に `FocusReturned(triggerId)` を発火する。

## AC (Acceptance Criteria)

- [x] `表示` / `共有と再現` の両パネルで `Escape` 閉じる要件を明記する。
- [x] 閉じる後のフォーカス復帰先（起点）を明記する。
- [x] 「開始→選択→表示→閉じる→復帰」の E2E 観点へ接続できる。
- [x] share/export 文脈の安全確認導線を失わない回帰条件を含める。

## DoD

- [x] `UX-OPERABILITY-01`〜`03` と用語・契約が一致している。
- [x] 仕様のみで実装手順やコード差分を含まない。
- [x] 未確定アクセシビリティ要件があれば `Execution: Hold` と解除条件を明示する。

## Phase Plan（Read → Contract → Execute/Verify）

- Phase 1 Read:
  - UX-03 までの `selection-context` 契約と終了動作境界の接続点を確認。
- Phase 2 Contract unify:
  - `PanelDismissed` / `FocusReturned` を終了時の正準イベントとして固定。
- Phase 3 Plan→Execute→Verify（max 3 self-heal）:
  - `docs-check-1`: `view` / `share-replay` の識別属性検証。
  - `docs-check-2`: `Escape → PanelDismissed` の順序検証。
  - `docs-check-3`: `FocusReturned` の起点一致検証。
- Phase 4 Stopper:
  - 閉鎖イベント欠落、復帰先未定義、または安全導線欠落を検知した場合は `Execution: Hold`。

## Validation plan

- `rg -n "Operation Flow Contract|Escape|PanelDismissed|FocusReturned|data-focus-return-id|data-panel=\"view\"|data-panel=\"share-replay\"" 01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md`

## Dependencies

- Depends on: `UX-OPERABILITY-03`
- Blocks: `UX-OPERABILITY-05`

## Hold trigger

- `Execution: Hold` は、フォーカス可視性・読み上げ可能名・キーボード到達性のいずれかが未確定で E2E 観測条件へ落とせない場合に適用する。
- 解除条件は、未確定項目が ADR-0030 と整合した観測可能文（DOM属性またはイベント契約）として AC/DoD に反映されること。


## Implementation Notes

- `03_Implement/frontend/src/canvas/CardView.tsx` における keyboard 選択契約（`Enter/Space`, `aria-selected`, `data-focus="card"`）を回帰対象として固定。
- `03_Implement/frontend/src/ui/SidePanel.tsx` で `selection-context` / `advanced` の段階開示契約（`data-panel`, `data-panel-group`, `aria-expanded`）を実装・検証。
- `03_Implement/frontend/src/ui/SharePanel.tsx` と `03_Implement/frontend/src/App.tsx` の `Escape` 閉鎖 + フォーカス復帰契約を回帰対象として維持。
