# Issue Draft: UX-OPERABILITY-01 マウス/キーボード操作動線レビュー（仕様固定）

- Type: Planning
- Status: Draft
- Priority: P1
- Owner: Stream D
- Scope: `01_Plans/adr/`, `01_Plans/issues/`, `04_Documentation/acceptance_check.md`, `03_Implement/frontend/docs/e2e_testing.md`
- Related Backlog: `UX-OPERABILITY-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

UI操作モデルの観点を仕様として固定し、後続実装Issue（02→03→04）の前提を統一する。

## AC (Acceptance Criteria)

- [ ] 到達性/フォーカススコープ/段階的開示/閉じる・復帰の4分類で課題を整理できる。
- [ ] `UX-OPERABILITY-02`〜`04` への依存順序（01→02→03→04）が明記されている。
- [ ] `acceptance_check.md` と `e2e_testing.md` に、実装前計画として同一の検証観点を反映できる。
- [ ] 本Issueは「仕様のみ、コード変更なし」を維持する。

## DoD

- [ ] ADR-0030 と語彙が一致している。
- [ ] 後続Issue参照が有効で、重複/矛盾がない。
- [ ] 実装手順ではなく、受入境界（I/Fレベル）で止めている。

## Validation plan

- `rg "到達性|フォーカス|段階的開示|Escape|復帰" 01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md 01_Plans/issues/issue-UX-OPERABILITY-0{1,2,3,4}*.md`
- `git diff -- 01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md 01_Plans/issues/issue-UX-OPERABILITY-01-pointer-keyboard-flow-review.md`

## Dependencies

- Blocks: `UX-OPERABILITY-02`
- Blocked by: `ADR-0030` 文言確定
