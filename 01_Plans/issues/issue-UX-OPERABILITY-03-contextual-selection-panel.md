# Issue Draft: UX-OPERABILITY-03 選択文脈優先パネル境界（仕様）

- Type: Planning
- Status: Draft
- Priority: P1
- Owner: Stream D
- Scope: `01_Plans/issues/`, `01_Plans/adr/`
- Related Backlog: `UX-OPERABILITY-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

選択直後に必要情報を提示し、高度機能は段階開示するUI情報境界を固定する。

## AC (Acceptance Criteria)

- [ ] 選択直後に表示されるべき情報（選択対象確認・基本編集・レビュー導線）を明記する。
- [ ] 初期非表示/段階開示の対象（高度機能群）を明記する。
- [ ] Tab順序が「文脈優先」であることを要件化する。
- [ ] `UX-OPERABILITY-04` の閉じる/復帰要件と矛盾しない。

## DoD

- [ ] 文脈優先の定義が曖昧語ではなく観測可能条件で書かれている。
- [ ] `UX-OPERABILITY-02` と `UX-OPERABILITY-04` の接続点が明示されている。
- [ ] 実装詳細（具体コンポーネント設計）へ踏み込んでいない。

## Validation plan

- `rg "文脈|段階的開示|Tab|選択直後|高度機能" 01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`

## Dependencies

- Depends on: `UX-OPERABILITY-02`
- Blocks: `UX-OPERABILITY-04`
