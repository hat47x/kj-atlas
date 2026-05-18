# Issue: UX-OPERABILITY-03 選択文脈優先パネル境界（仕様）

- Type: Planning
- Status: Open
- Priority: P1
- Owner: Stream C
- DecisionStatus: Fixed
- Execution: Ready
- Scope: `01_Plans/issues/`, `01_Plans/adr/`, `03_Implement/frontend/docs/e2e_testing.md`
- Related Backlog: `UX-OPERABILITY-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

選択直後に必要情報を先頭提示し、高度機能は明示操作で開示する文脈優先モデルを固定する。

## I/F Contract (Mock-first)

- DOM expectation:
  - `data-panel="selection-context"` が選択後に先頭表示される。
  - `data-panel-group="advanced"` は初期状態 `aria-expanded="false"`。
  - `data-panel-group="advanced"` は明示操作（button press）で `aria-expanded="true"` に遷移する。
- Event contract:
  - `ContextPanelRequested(targetId)` 受信時に `ContextPanelRendered(targetId)` を返す。
  - `Tab` 順序は `selection-context` 内の主要導線を先に巡回し、その後に `advanced` 開示導線へ進む。

## AC (Acceptance Criteria)

- [x] 選択直後の必須表示（確認・基本編集・レビュー導線）を明記する。
- [x] 高度機能群の初期非表示と段階開示条件を明記する。
- [x] Tab 順序が文脈優先であることを観測可能条件で示す。
- [x] `UX-OPERABILITY-04` の閉じる/復帰仕様と矛盾しない。

## DoD

- [x] `UX-OPERABILITY-02`（入力）と `UX-OPERABILITY-04`（終了動作）の接続点を明示する。
- [x] 実装詳細・コンポーネント分割の指定に踏み込まない。
- [x] 曖昧要件が残る場合は `Execution: Hold` 条件を明示する。

## Validation plan

- `rg -n "selection-context|advanced|aria-expanded|ContextPanelRequested|ContextPanelRendered|Tab" 01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`

## Dependencies

- Depends on: `UX-OPERABILITY-02`
- Blocks: `UX-OPERABILITY-04`


## Hold trigger

- `Execution: Hold` は、フォーカス可視性・読み上げ可能名・キーボード到達性のいずれかが未確定で E2E 観測条件へ落とせない場合に適用する。
- 解除条件は、未確定項目が ADR-0030 と整合した観測可能文（DOM属性またはイベント契約）として AC/DoD に反映されること。
