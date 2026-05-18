# Issue: UX-OPERABILITY-04 パネル閉じる操作とフォーカス復帰境界（仕様）

- Type: Planning
- Status: Open
- Priority: P1
- Owner: Stream C
- DecisionStatus: Fixed
- Execution: Ready
- Scope: `01_Plans/issues/`, `01_Plans/adr/`, `03_Implement/frontend/docs/e2e_testing.md`
- Related Backlog: `UX-OPERABILITY-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

`表示` / `共有と再現` パネルの `Escape` 閉じると起点フォーカス復帰を I/F 境界として固定する。

## I/F Contract (Mock-first)

- DOM expectation:
  - 一時パネルは `data-panel="view"` / `data-panel="share-replay"` で識別できる。
  - 開始ボタンは `data-focus-return-id` を保持し、閉じる後の復帰先を識別できる。
- Event contract:
  - パネル open 中の `Escape` で `PanelDismissed(panelId, reason="escape")` を発火する。
  - `PanelDismissed` 後に `FocusReturned(triggerId)` を発火する。
  - `FocusReturned` は対応する起点ボタンへフォーカスされることで観測可能。

## AC (Acceptance Criteria)

- [ ] `表示` / `共有と再現` の両パネルで `Escape` 閉じる要件を明記する。
- [ ] 閉じる後のフォーカス復帰先（起点）を明記する。
- [ ] 「開始→選択→表示→閉じる→復帰」の E2E 観点へ接続できる。
- [ ] share/export 文脈の安全確認導線を失わない回帰条件を含める。

## DoD

- [ ] `UX-OPERABILITY-01`〜`03` と用語・契約が一致している。
- [ ] 仕様のみで実装手順やコード差分を含まない。
- [ ] 未確定アクセシビリティ要件があれば `Execution: Hold` と解除条件を明示する。

## Validation plan

- `rg -n "Escape|PanelDismissed|FocusReturned|focus-return|表示|共有と再現" 01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md 03_Implement/frontend/docs/e2e_testing.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md 03_Implement/frontend/docs/e2e_testing.md`

## Dependencies

- Depends on: `UX-OPERABILITY-03`
