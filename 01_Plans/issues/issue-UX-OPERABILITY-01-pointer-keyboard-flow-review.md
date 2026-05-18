# Issue: UX-OPERABILITY-01 マウス/キーボード操作動線レビュー（仕様固定）

- Type: Planning
- Status: Open
- Priority: P1
- Owner: Stream C
- DecisionStatus: Fixed
- Execution: Ready
- Scope: `01_Plans/adr/`, `01_Plans/issues/`, `03_Implement/frontend/docs/e2e_testing.md`
- Related Backlog: `UX-OPERABILITY-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

UI 操作モデルを 4 分類（到達性 / フォーカススコープ / 段階的開示 / 閉じる・復帰）で仕様固定し、後続 Issue（02→03→04）の契約前提を統一する。

## I/F Contract (Mock-first)

- DOM expectation:
  - `data-ui-region="primary-flow"` が初期表示で存在する。
  - `data-ui-region="selection-context"` は選択前は空または placeholder、選択後に更新される。
- Event contract:
  - `PointerSelect(targetId)` と `KeyboardSelect(targetId)` は同一の `SelectionChanged(targetId)` を発火する。
  - `SelectionChanged` は `ContextPanelRequested(targetId)` を後続へ通知する。

## AC (Acceptance Criteria)

- [x] 4分類の用語が ADR-0030 と一致している。
- [x] `01 → 02 → 03 → 04` の固定順が明記されている。
- [x] 後続 Issue が参照する I/F 契約（DOM / Event）を先行定義している。
- [x] 本 Issue は仕様のみで、実装コード変更を含まない。

## DoD

- [x] 後続 Issue 参照が有効で重複・矛盾がない。
- [x] 受入境界は E2E 観測可能な事実で記述されている。
- [x] 曖昧なアクセシビリティ要件が残る場合は `Execution: Hold` 条件を明示する。

## Validation plan

- `rg -n "到達性|フォーカススコープ|段階的開示|閉じる|復帰|SelectionChanged" 01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md 01_Plans/issues/issue-UX-OPERABILITY-0{1,2,3,4}*.md`
- `git diff -- 01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md 01_Plans/issues/issue-UX-OPERABILITY-01-pointer-keyboard-flow-review.md`

## Dependencies

- Blocks: `UX-OPERABILITY-02`
- Blocked by: `ADR-0030` Accepted


## Hold trigger

- `Execution: Hold` は、フォーカス可視性・読み上げ可能名・キーボード到達性のいずれかが未確定で E2E 観測条件へ落とせない場合に適用する。
- 解除条件は、未確定項目が ADR-0030 と整合した観測可能文（DOM属性またはイベント契約）として AC/DoD に反映されること。
