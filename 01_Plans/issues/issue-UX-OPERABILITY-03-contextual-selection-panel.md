# Issue: UX-OPERABILITY-03 選択文脈優先パネル境界（仕様）

- Type: Planning
- Status: Done
- Priority: P1
- Owner: Stream C
- DecisionStatus: Fixed
- Execution: Ready
- Scope: `01_Plans/issues/issue-UX-OPERABILITY-01..05*.md`（docs + frontend ui）
- Related Backlog: `UX-OPERABILITY-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

選択直後に必要情報を先頭提示し、高度機能は明示操作で開示する文脈優先モデルを固定する。

## Operation Flow Contract（Unified / Mock-first）

- Pointer contract:
  - pointer 起点の選択でも `ContextPanelRequested(targetId)` を受信可能である。
- Keyboard contract:
  - keyboard 起点の選択でも同一に `ContextPanelRequested(targetId)` を受信可能である。
- Focus contract:
  - `Tab` 順序は `selection-context` 内の主要導線を先に巡回し、その後 `advanced` 開示導線へ進む。
- Panel contract:
  - `data-panel="selection-context"` が選択後に先頭表示される。
  - `data-panel-group="advanced"` は初期 `aria-expanded="false"`、明示操作で `aria-expanded="true"`。
  - `ContextPanelRequested(targetId)` 受信時に `ContextPanelRendered(targetId)` を返す。

## AC (Acceptance Criteria)

- [x] 選択直後の必須表示（確認・基本編集・レビュー導線）を明記する。
- [x] 高度機能群の初期非表示と段階開示条件を明記する。
- [x] Tab 順序が文脈優先であることを観測可能条件で示す。
- [x] `UX-OPERABILITY-04` の閉じる/復帰仕様と矛盾しない。

## DoD

- [x] `UX-OPERABILITY-02`（入力）と `UX-OPERABILITY-04`（終了動作）の接続点を明示する。
- [x] 実装詳細・コンポーネント分割の指定に踏み込まない。
- [x] 曖昧要件が残る場合は `Execution: Hold` 条件を明示する。

## Phase Plan（Read → Contract → Execute/Verify）

- Phase 1 Read:
  - UX-02 の `SelectionChanged → ContextPanelRequested` 契約を入力として確認。
- Phase 2 Contract unify:
  - `selection-context` 先頭表示 + `advanced` 段階開示を panel 契約として固定。
- Phase 3 Plan→Execute→Verify（max 3 self-heal）:
  - `docs-check-1`: `selection-context` の先頭提示条件を検証。
  - `docs-check-2`: `advanced` の `aria-expanded` 遷移条件を検証。
  - `docs-check-3`: `ContextPanelRendered` 応答契約を検証。
- Phase 4 Stopper:
  - Tab順序の競合、段階開示条件の未定義、または UX-04 との矛盾検知時は `Execution: Hold`。

## Validation plan

- `rg -n "Operation Flow Contract|selection-context|advanced|aria-expanded|ContextPanelRequested|ContextPanelRendered|Tab" 01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`

## Dependencies

- Depends on: `UX-OPERABILITY-02`
- Blocks: `UX-OPERABILITY-04`

## Hold trigger

- `Execution: Hold` は、フォーカス可視性・読み上げ可能名・キーボード到達性のいずれかが未確定で E2E 観測条件へ落とせない場合に適用する。
- 解除条件は、未確定項目が ADR-0030 と整合した観測可能文（DOM属性またはイベント契約）として AC/DoD に反映されること。


## Implementation Notes

- `03_Implement/frontend/src/canvas/CardView.tsx` における keyboard 選択契約（`Enter/Space`, `aria-selected`, `data-focus="card"`）を回帰対象として固定。
- `03_Implement/frontend/src/ui/SidePanel.tsx` で `selection-context` / `advanced` の段階開示契約（`data-panel`, `data-panel-group`, `aria-expanded`）を実装・検証。
- `03_Implement/frontend/src/ui/SharePanel.tsx` と `03_Implement/frontend/src/App.tsx` の `Escape` 閉鎖 + フォーカス復帰契約を回帰対象として維持。

## E2E追認 2026-06-29

- `UX-NAV-01 AC-2` として利用者から指定された「高度機能パネル抽出」は、本issueの `advanced` 段階開示契約と `UX-COMPLEXITY-01` AC-2 の組み合わせとして扱う。
- 追加E2E `selection context keeps advanced panel extracted behind explicit disclosure` により、選択文脈の基本情報と高度パネルの分離、初期 `aria-expanded=false`、明示開閉の可逆性を実ブラウザで確認した。
- 結果: 2026-06-29 の対象Playwrightセットで **10 passed**。
