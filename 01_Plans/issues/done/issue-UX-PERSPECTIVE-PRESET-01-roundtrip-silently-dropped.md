# Issue: UX-PERSPECTIVE-PRESET-01 perspectivePresetsのimport後data lossを防ぐ

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/domain/view/perspective.ts`
- Related ADR/Spec: `03_Implement/frontend/src/export/view_metadata.ts`, `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- Expected verification level: `unit`

## 課題

`view.json`の`viewState.perspectivePresets`はexport・validation・旧mode文字列の互換往復まで契約済みだったが、`App.tsx`のimport適用処理がfieldをruntime stateへ保持していなかった。そのため、import後に通常view exportまたはbundle exportを行うとfieldが静かに失われた。

## 対応

- `perspectivePresets`専用runtime stateを追加した。
- import fieldが存在する場合は順序・値・旧mode文字列を変更せずdeep copyして保持する。空配列も空配列のまま保持する。
- fieldがない旧`view.json`だけは既存のdefault presetsへフォールバックする。
- 通常のview metadata exportとbundle exportの双方へ保持値を渡すよう配線した。
- 専用のpreset管理UIは追加していない。今回の契約は既存`view.json`のdata preservationであり、常時表示UIや新しい操作面を増やさない。

## Acceptance

- [x] import済み`perspectivePresets`をruntime stateへ保持する方針を確定した。
- [x] import→通常exportとimport→bundle exportの双方でfieldを再出力する。
- [x] field欠落・空配列・旧mode文字列の互換境界を回帰テストで固定した。

## Validation

- `vitest run src/domain/view/perspective.test.ts src/export/view_metadata.test.ts src/import/view_import.test.ts src/ui/ux_operability_regression.test.ts`: 79 passed
- `vitest run`: 1,271 passed（220 files）
- `tsc --noEmit`: passed
- `python 01_Plans/docs_check.py --root .`: passed（35 active memos）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`: passed（35 active memos）
