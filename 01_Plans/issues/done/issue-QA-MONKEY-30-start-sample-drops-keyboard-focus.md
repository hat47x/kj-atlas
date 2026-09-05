# Issue: QA-MONKEY-30 サンプル開始後にキーボードfocusが失われる

- Type: Bug / Accessibility
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`
- Related Backlog: `QA-MONKEY-30`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）
- Expected verification level: `e2e`

## 課題

開始パネルの「サンプルを開く」をEnterで実行すると、サンプルは開くが、focus中のボタンを含む開始パネルが消滅してfocusが`body`へ落ちる。キーボード利用者は読み込まれたキャンバスの先頭から操作を再開できない。

## 対応方針

- サンプル読込処理の完了後、次frameで先頭カードへfocusを移す。
- 公開pack、API文書、内蔵サンプルのいずれの読込経路にも同じ完了処理を適用する。
- 読込対象にカードがない場合はfocus移動を行わず、例外にしない。

三要素牽制: 業務上はサンプル開始後すぐ整理操作へ進める。データモデルと読込優先順位は不変。機能上は画面遷移後のfocusだけを補完するためADR不要。

## 受入条件

- [x] 「サンプルを開く」をEnterで実行するとサンプルが開く。
- [x] 読込後、先頭カードへfocusが移る。
- [x] 公開pack/API/内蔵fallbackの読込分岐を変更しない。
- [x] カード0件でも例外を発生させない。

## 対応結果（2026-08-16）

- 共通finallyで読込完了後の先頭カードへfocusを移し、全読込分岐を維持した。
- A18は修正前false・修正後true。全18固定プローブ、typecheckを通過した。

## 検証計画

- `monkey_adversarial_probes.mjs` A18を実画面確認する。
- RAF後に判定するランダムseed 505を再実行する。
- frontend typecheck、UX operability test、docs-check、active issue validatorを実行する。


## 配置の整理（2026-09-05）

- 本Issueは、モンキーテストで見つかった直接のUI／キーボード操作不具合を修正し、個別の回帰確認まで終えて `Done` となっていた。一方、R18時点のlegacy集合に含まれたため、完了済みのまま作業中Issueと同じルートへ残っていた。
- 2026-09-05の残存39件参照グラフ監査で、本Issueは他のlegacy Doneとの系列内ID参照を持たない孤立成分であり、旧rootパスの外部引用もないことを確認した。
- 既存のライフサイクル契約に従い、本変更ではこの条件を満たすQA-MONKEY完了Issue 5件を `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を39から34へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
