# Issue: UI-QUALITY-A11Y-05 読み順並び替えのキーボード到達性を確認する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Quality
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/src/canvas/ReadingOrderLayer.tsx`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- Expected verification level: `unit`

## 課題

発見時はcanvas上の読み順バッジがpointer dragでしか並び替えられず、代替操作がないと判断していた。しかし現行コードを再監査すると、SidePanelの読み順一覧にnative `button`による「上へ」「下へ」が既にあり、`handleMoveReadingOrderItem(index, -1 | 1)`へ配線されていた。

## 対応

- SidePanelの上/下ボタンがキーボードで到達できるnative buttonであることを確認した。
- 先頭の上ボタンと末尾の下ボタンが無効になり、範囲外移動を提示しないことを確認した。
- 並び替えが既存の単一history stepへ接続されることを確認した。
- canvas上のpointer drag操作は変更せず維持した。
- 上記の実装境界が失われた場合に検出する回帰テストを追加した。

## Acceptance

- [x] キーボードのみで1項目ずつ上/下へ並び替えられる操作方式が存在する。
- [x] 既存のpointer drag操作を維持している。
- [x] 両操作が同じDocumentの読み順更新契約へ接続される。

## Validation

- `vitest run src/ui/ux_operability_regression.test.ts src/canvas/ReadingOrderLayer.test.ts src/domain/reading_order_ops.test.ts`: 40 passed
- `tsc --noEmit`: passed
- `python 01_Plans/docs_check.py --root .`: passed（34 active memos）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`: passed（34 active memos）
