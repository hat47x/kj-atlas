# Issue: UX-OPERABILITY-05 主要ツールバーの推奨導線優先化（契約同期）

- Type: Planning
- Status: Done
- Priority: P1
- Owner: Stream C
- Execution: Ready
- Scope: `01_Plans/issues/issue-UX-OPERABILITY-01..05*.md`（docs + frontend ui）
- Related Backlog: `UX-OPERABILITY-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

主要ツールバーの推奨導線（表示 / 共有と再現 / 安全確認）を、UX-OPERABILITY-01〜04 で固定した統一契約に整合させ、実装前提を文書上で確定する。

## Operation Flow Contract（Unified / Mock-first）

- Pointer contract:
  - 推奨導線トリガー操作は pointer/keyboard いずれでも同一のパネル契約に接続する。
- Keyboard contract:
  - `Enter/Space` による選択契約、`Escape` によるパネル閉鎖契約を維持する。
- Focus contract:
  - 推奨導線トリガーは `data-focus-return-id="view-controls-trigger"` / `data-focus-return-id="share-panel-trigger"` を保持する。
- Panel contract:
  - 一時パネルは `data-panel="view"` / `data-panel="share-replay"` で識別できる。
  - 選択文脈領域は `data-ui-region="selection-context"` を維持する。

## AC (Acceptance Criteria)

- [x] AC/DoDをUX-OPERABILITY-01〜04と同じフォーマットで統一する。
- [x] 主要ツールバーの推奨導線を壊さず、legacy導線の補助的位置づけを維持する。
- [x] キーボード操作（Enter/Space/Escape）とフォーカス復帰契約が回帰しない。
- [x] `selection-context` / `advanced` / `view` / `share-replay` の契約属性を維持する。

## DoD

- [x] UX Operabilityの契約項目を docs-check で検証し、再現コマンドを提示できる。
- [x] 変更は許可スコープ（issue-UX-OPERABILITY-01..05*.md）内に限定される。
- [x] SafeMode既定ON・share/export安全導線を弱める変更を含まない。

## Phase Plan（Read → Contract → Execute/Verify）

- Phase 1 Read:
  - UX-01〜04 の契約を参照し、主要ツールバー導線との対応表を確認。
- Phase 2 Contract unify:
  - pointer/keyboard/focus/panel の4契約を推奨導線へ写像して整合。
- Phase 3 Plan→Execute→Verify（max 3 self-heal）:
  - `docs-check-1`: トリガー属性（focus-return-id）の整合確認。
  - `docs-check-2`: `Enter/Space/Escape` のイベント契約整合確認。
  - `docs-check-3`: `selection-context` / `view` / `share-replay` の属性整合確認。
- Phase 4 Stopper:
  - 契約不一致、前提崩れ（UX-01〜04との矛盾）、未定義依存がある場合は `Execution: Hold`。

## Validation plan

- `rg -n "Operation Flow Contract|Enter|Space|Escape|data-focus-return-id|selection-context|view|share-replay|Execution: Hold" 01_Plans/issues/issue-UX-OPERABILITY-0{1,2,3,4,5}*.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-05-primary-toolbar-task-prioritization.md`

## Dependencies

- Depends on: `UX-OPERABILITY-04`
- Completes: `UX-OPERABILITY-05`

## Hold trigger

- `Execution: Hold` は、キーボード導線（Enter/Space/Escape）またはフォーカス復帰契約が docs-check で観測不能になった場合に適用する。
- 解除条件は、契約属性とイベント導線を再観測できること。


## Implementation Notes

- `03_Implement/frontend/src/canvas/CardView.tsx` における keyboard 選択契約（`Enter/Space`, `aria-selected`, `data-focus="card"`）を回帰対象として固定。
- `03_Implement/frontend/src/ui/SidePanel.tsx` で `selection-context` / `advanced` の段階開示契約（`data-panel`, `data-panel-group`, `aria-expanded`）を実装・検証。
- `03_Implement/frontend/src/ui/SharePanel.tsx` と `03_Implement/frontend/src/App.tsx` の `Escape` 閉鎖 + フォーカス復帰契約を回帰対象として維持。
