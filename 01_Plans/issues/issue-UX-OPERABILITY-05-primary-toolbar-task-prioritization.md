# Issue: UX-OPERABILITY-05 主要ツールバーの推奨導線優先化（実装）

- Type: Execution
- Status: In Progress
- Priority: P1
- Owner: Stream C
- DecisionStatus: Fixed
- Execution: Ready
- Scope: `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/domain/`, `03_Implement/frontend/tests/`, `01_Plans/issues/`
- Related Backlog: `UX-OPERABILITY-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `unit`

## Goal

主要ツールバーで推奨導線（表示 / 共有と再現 / 安全確認）を優先し、legacy操作は補助導線として区別する。UX-OPERABILITY-01〜04で固定した契約を壊さずに操作導線を実装整合する。

## I/F Contract (Mock-first)

- DOM expectation:
  - 推奨導線トリガーは `data-focus-return-id="view-controls-trigger"` / `data-focus-return-id="share-panel-trigger"` を保持する。
  - 一時パネルは `data-panel="view"` / `data-panel="share-replay"` で識別できる。
  - 選択文脈領域は `data-ui-region="selection-context"` を維持する。
- Event contract:
  - `Escape` で `PanelDismissed` 相当の閉鎖導線が発火し、起点へフォーカス復帰する。
  - カード選択は `Enter/Space` で `SelectionChanged` 相当の導線を維持する。

## AC (Acceptance Criteria)

- [x] AC/DoDをUX-OPERABILITY-01〜04と同じフォーマットで統一する。
- [x] 主要ツールバーの推奨導線を壊さず、legacy導線の補助的位置づけを維持する。
- [x] キーボード操作（Enter/Space/Escape）とフォーカス復帰契約が回帰しない。
- [x] `selection-context` / `advanced` / `view` / `share-replay` の契約属性を維持する。

## DoD

- [x] UX Operabilityの契約項目を回帰テストで検証し、再現コマンドを提示できる。
- [x] 変更は許可スコープ（frontend/ui|canvas|domain|tests + issue同期）内に限定される。
- [x] SafeMode既定ON・share/export安全導線を弱める変更を含まない。

## Validation plan

- `cd 03_Implement/frontend && node ./node_modules/vitest/vitest.mjs run tests/ux_operability_regression.test.ts`
- `cd 03_Implement/frontend && node ./node_modules/vitest/vitest.mjs run src/ui/SharePanel.test.ts`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-05-primary-toolbar-task-prioritization.md 03_Implement/frontend/tests/ux_operability_regression.test.ts`

## Dependencies

- Depends on: `UX-OPERABILITY-04`
- Completes: `UX-OPERABILITY-05`

## Hold trigger

- `Execution: Hold` は、キーボード導線（Enter/Space/Escape）またはフォーカス復帰契約がE2E/単体確認で観測不能になった場合に適用する。
- 解除条件は、契約属性とイベント導線をテストで再観測できること。
