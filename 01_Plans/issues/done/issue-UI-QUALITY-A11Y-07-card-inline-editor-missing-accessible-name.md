# Issue: UI-QUALITY-A11Y-07 カード本文インライン編集欄にaccessible nameがない

- Type: Bug
- Status: Done
- Source Issue: `MVP-EXIT-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/src/i18n/locales/`
- Related ADR/Spec: `04_Documentation/acceptance_check.md`, `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`
- Expected verification level: `integration`

## 課題

- 現在の問題: カード本文のインライン編集 `<textarea>` に `aria-label` / `aria-labelledby` / `<label>` / `placeholder` / `title` のいずれもなく、accessible nameが空だった。
- 利用者または開発への影響: スクリーンリーダー利用者は「新規カード」実行後にフォーカスが本文入力欄へ移ったことを音声で判別できない。`04_Documentation/acceptance_check.md`「スクリーンリーダーで確認すること」2 を満たさない。自動axe検査は、インライン編集中の状態を通っていないため検出していなかった。

再現手順:

1. `?locale=ja` でアプリを開き、サンプル文書を開く。
2. ヘッダーの「新規カード」を実行する。
3. `document.activeElement` の accessible name を確認する（修正前は空）。

## 対応方針

- 実施すること: `card_view.edit_textarea_label` を `ja` / `en` に追加し、編集用 `<textarea>` に `aria-label` として与える。
- 実施しないこと: 編集欄のfocus管理やcommit挙動の変更。カード表示側のaria設計の見直し。

## 予算申告

- 複雑性予算（`ADR-0043`）: N/A（初期表示への純増なし）
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [x] 編集欄のAXノードが `role=textbox` かつ accessible name を持つ。
- [x] 関連する安全・互換性を損なわない（表示・commit挙動は不変）。
- [x] 宣言した検証を実行する。

## 検証計画

- 実行する確認: accessibility treeでのrole/name確認、frontend typecheck、`src/i18n/`、`src/canvas/`、`src/ui/ux_operability_regression.test.ts`、`e2e/card_single_save_creation.spec.ts`。
- 期待結果: `AXrole=textbox` / `AXname="カード本文を編集"`。既存テストに退行なし。

実施結果（2026-07-29）: 上記すべて成功。詳細は `03_Implement/frontend/docs/mvp_exit_human_acceptance_log_2026-07-29.md` §2。

## 補足

- インライン編集中の状態を自動axe検査の対象に加えるかは別issueとする。今回の欠陥は、編集中という一時状態が自動検査の経路から外れていたために残っていた。
