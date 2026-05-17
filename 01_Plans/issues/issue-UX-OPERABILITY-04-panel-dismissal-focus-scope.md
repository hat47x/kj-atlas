# Issue Draft: UX-OPERABILITY-04 パネル閉じる操作とフォーカス復帰境界（仕様）

- Type: Planning
- Status: Draft
- Priority: P1
- Owner: Stream D
- Scope: `01_Plans/issues/`, `01_Plans/adr/`, `04_Documentation/acceptance_check.md`, `03_Implement/frontend/docs/e2e_testing.md`
- Related Backlog: `UX-OPERABILITY-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

`表示` / `共有と再現` パネルにおける「Escapeで閉じる + 起点フォーカス復帰」の仕様を固定する。

## AC (Acceptance Criteria)

- [ ] `表示` / `共有と再現` の両パネルで `Escape` 閉じる要件を明記する。
- [ ] 閉じた後のフォーカス復帰先（起点）を明記する。
- [ ] 開始→選択→表示→閉じる→復帰 のE2E観点に接続できる記述になっている。
- [ ] share/export 文脈での安全確認導線が失われないことを回帰条件に含める。

## DoD

- [ ] `acceptance_check.md` / `e2e_testing.md` に同一語彙で計画観点が反映されている。
- [ ] `UX-OPERABILITY-01`〜`03` と定義衝突がない。
- [ ] 仕様のみで、実装手順やコード差分を含まない。

## Validation plan

- `rg "Escape|閉じる|復帰|起点|表示|共有と再現" 01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md 04_Documentation/acceptance_check.md 03_Implement/frontend/docs/e2e_testing.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md 04_Documentation/acceptance_check.md 03_Implement/frontend/docs/e2e_testing.md`

## Dependencies

- Depends on: `UX-OPERABILITY-03`
