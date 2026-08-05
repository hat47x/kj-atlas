# Issue: UI-QUALITY-A11Y-08 一部のポップアップ系パネルにTabフォーカストラップが無い

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Feature
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/ui/CanvasLegend.tsx`, `03_Implement/frontend/src/ui/CommandPalette.tsx`, `03_Implement/frontend/src/ui/ShortcutCheatsheet.tsx`, `03_Implement/frontend/src/App.tsx`（`ViewControlsPanel`のインラインdialog）
- Related ADR/Spec: `02_Architecture/design/ui_design_handoff.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: 次の5箇所のポップアップ/ダイアログは、Escape閉鎖とトリガへのfocus復帰は実装済みだが、Tabキーによるフォーカストラップ（`getFocusableElements`/`focusableSelector`ベースのTab循環）を持たない。`TenantChangeConfirmationDialog.tsx`・`DiagnosticsBundlePanel.tsx`・`WorkModePanel.tsx`等は同じ3点セット（Escape・Tabトラップ・focus復帰）をすべて実装している。
  1. `SharePanel.tsx`（メイン`role="dialog"`パネルと`role="alertdialog"`の共有前確認ゲート、両方）
  2. `CanvasLegend.tsx`
  3. `CommandPalette.tsx`
  4. `ShortcutCheatsheet.tsx`
  5. `App.tsx`内`ViewControlsPanel`のインラインdialog
- 判断が必要な理由: 同一の欠落パターンが独立した5コンポーネントに存在することは、単純な実装漏れというより「背景をbackdropで覆うポップアップにはTabトラップが不要」という暗黙の設計方針が一部に存在する可能性を示唆する。特に`SharePanel.tsx`は`position: fixed`かつ`width: min(340px, ...)`でビューポート全体を覆わないため、背景のキャンバス操作がTabで到達可能なままになり、他の4件（backdrop covered）とは実害の性質が異なる。全5件に同一のTabトラップを一律追加すべきか、backdrop有無で扱いを分けるべきかはUX判断が必要。
- 利用者または開発への影響: キーボードユーザーがダイアログ内でTabを押し続けた場合、`SharePanel.tsx`では背景のキャンバス操作へフォーカスが漏れる可能性がある。他の4件はbackdropで背景が視覚的に隠れているため、実害はより限定的。

## 対応方針

- 実施すること: 「backdropで覆われないポップアップ（SharePanel等）には既存の`focusableSelector`/`getFocusableElements`パターンをそのまま追加する」「backdropで覆われるポップアップは現状を許容する」といった扱いの区分をMaintainerが決定する。
- 実施しないこと: 5箇所全てへの一律のTabトラップ追加。設計方針の確認前に一律追加すると、意図的な設計判断を上書きする可能性がある。

## 受入条件

- [ ] backdrop有無によるTabトラップの要否方針が決定される。
- [ ] 決定した方針に沿って該当箇所に実装される。

## 検証計画

- 実行する確認: 実装後、`npm run test`（frontend、該当パネルのa11y関連テスト）。
- 期待結果: 方針に沿ったTabトラップの有無が一貫する。

## 補足

- 発見経緯: 第15ラウンドの棚卸し（ダイアログのfocus-trap/Escape観点）で発見。
