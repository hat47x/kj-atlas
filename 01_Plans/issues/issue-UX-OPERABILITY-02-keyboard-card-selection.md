# Issue Draft: UX-OPERABILITY-02 キーボードによるカード選択境界（仕様）

- Type: Planning
- Status: Draft
- Priority: P1
- Owner: Stream D
- Scope: `01_Plans/issues/`, `01_Plans/adr/`
- Related Backlog: `UX-OPERABILITY-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

カード選択におけるキーボード到達性の受入境界を定義する（実装方式は決めない）。

## AC (Acceptance Criteria)

- [ ] 「カードがフォーカス対象であること」を仕様要件として明記する。
- [ ] 「選択操作（Enter/Space等）」と「選択結果の確認可能性」を仕様要件として明記する。
- [ ] 選択後、次の文脈導線が `UX-OPERABILITY-03` に引き渡されることを明記する。
- [ ] マウス操作互換を壊さないことを回帰条件に含める。

## DoD

- [ ] `DecisionStatus` が `Fixed` になり、未確定論点があれば明示できている。
- [ ] AC がテスト観点（E2Eでの観測可能な事実）で書かれている。
- [ ] 実装コードファイルをScopeに含めない。

## Validation plan

- `rg "カード|キーボード|選択|Enter|Space|回帰" 01_Plans/issues/issue-UX-OPERABILITY-02-keyboard-card-selection.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-02-keyboard-card-selection.md`

## Dependencies

- Depends on: `UX-OPERABILITY-01`
- Blocks: `UX-OPERABILITY-03`
