# Issue: UI-QUALITY-A11Y-06 差分/診断/バンドル出力の進行状況がスクリーンリーダーへ未通知

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Feature
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/ReviewDiffPanel.tsx`, `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/ui/SidePanel.tsx`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: 差分計算（`ReviewDiffPanel.tsx`）・診断実行（`SidePanel.tsx`の`isDiagnosticsRunning`）・バンドル書き出し（`SharePanel.tsx`の`isBundleExportRunning`）はいずれも、App.tsxが所有する`computeProgressMessage`（workerの`onProgress`コールバックから毎秒複数回更新されうる）をそのまま`<div>`に表示するが、3箇所とも`aria-live`/`role="status"`を持たない。`onProgress`の中間更新は`setStatusMessage`（アプリ全体のトースト）へは一切渡らず、処理完了/キャンセル時の最終メッセージだけがトーストで一度通知される。そのため、晴眼者には進行状況がリアルタイムで見えるが、スクリーンリーダー利用者には処理中ずっと何も読み上げられず、完了時に最終結果を1回聞くだけになる。
- 判断が必要な理由: `BulkOperationsBar.tsx:144`の`role="status" aria-live="polite"`パターンをそのまま適用すれば技術的には直せるが、`onProgress`は1秒間に複数回発火しうるため、`aria-live="polite"`をそのまま使うと一部のスクリーンリーダーで読み上げが過剰になる可能性がある。中間更新をスロットル/デバウンスするか、ステージ遷移時のみ通知するか、現状のまま許容するかは、UX判断が必要。
- 利用者または開発への影響: 実害はアクセシビリティ体験の欠落（処理中の進行状況が伝わらない）であり、機能的な誤動作ではない。

## 対応方針

- 実施すること: 中間進行状況の通知方針（都度通知/間引いて通知/ステージ変化のみ通知/対応しない）をMaintainerが決定する。
- 実施しないこと: `role="status" aria-live="polite"`の機械的な追加。読み上げ頻度に関する判断を経ずに追加すると、過剰な読み上げによる別の体験劣化を招く可能性がある。

## 受入条件

- [ ] 進行状況の通知方針が決定される。
- [ ] 決定した方針に沿って3箇所（`ReviewDiffPanel.tsx`/`SharePanel.tsx`/`SidePanel.tsx`）に実装される。

## 検証計画

- 実行する確認: 実装後、スクリーンリーダーでの手動確認、または既存のaxe/a11yスモークテストの拡張。
- 期待結果: 処理中の進行状況が過不足なくスクリーンリーダーへ伝わる。

## 補足

- 発見経緯: 第14ラウンドの棚卸し（aria-live観点）で発見。同じ観点で見つかった以下3件は、既存の同種パターン（`TenantSessionControl.tsx`/同一ファイル内の`role="status"`スパン/隣接する`trustBoundaryErrorMessage`の`aria-live`）をそのまま複製するだけの機械的な修正だったため、本ラウンドで直接対応済み。
  - `DiagnosticsBundlePanel.tsx`のコピー結果通知
  - `SidePanel.tsx`の関係説明コピー結果通知
  - `MergeSuggestionsPanel.tsx`のエラー表示（隣接する`trustBoundaryErrorMessage`との不整合）
