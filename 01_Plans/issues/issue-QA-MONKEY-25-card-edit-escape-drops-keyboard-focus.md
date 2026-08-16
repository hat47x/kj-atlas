# Issue: QA-MONKEY-25 カード本文編集をEscape取消するとキーボードfocusが失われる

- Type: Bug / Accessibility
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`
- Related Backlog: `QA-MONKEY-25`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）, `01_Plans/issues/issue-QA-MONKEY-23-selection-clear-drops-keyboard-focus.md`
- Expected verification level: `e2e`

## 課題

英語UI・1440px・seed 404のランダム操作で、カード本文のinline textarea上からEscapeで編集を取り消すと、元本文は復元される一方、textareaの消滅に伴ってfocusが`body`へ落ちることを確認した。キーボード利用者は編集前のカード位置を失い、次のTab操作がページ先頭から再開される。

## 対応方針

- CardViewの安定したroot要素をrefで保持する。
- Escapeで既存の取消処理を実行した次の描画frameに、同じカードrootへfocusを戻す。
- Enter確定、blur確定、本文・選択・SafeMode・保存データの契約は変更しない。

三要素牽制: 業務上はカード本文の確認・取消後も同じカードから作業を継続できる。データ設計と保存境界は不変。機能上は既存Escape取消後のfocus遷移だけを補完し、編集確定・取消内容・権限判定は変更しない。新しい製品判断ではないためADR不要。

## 受入条件

- [x] Escapeで編集内容を破棄し、元本文へ戻る。
- [x] textarea消滅後、同じカードrootへfocusが戻る。
- [x] Enter確定と外側click確定の既存挙動が回帰しない。
- [x] 日本語・英語UIのどちらでもfocus復帰する。

## 検証計画

- `monkey_adversarial_probes.mjs` A1/A2/A15で取消・確定・focus復帰を実画面確認する。
- 発見seed 404・1440px・英語UIを再実行する。
- frontend typecheck、CardView accessibility test、docs-check、active issue validatorを実行する。

## 対応結果（2026-08-16）

- CardView rootをrefで保持し、Escape取消後の次frameで同じカードへfocusを戻すよう修正した。
- A1/A2/A15で元本文復元、外側click確定、ja/en双方のfocus復帰を確認した。
- 発見seed 404・英語UI・1440px・400 loopを再実行し、finding 0件を確認した。
- frontend typecheck成功、CardView/操作性47 tests成功、全15 adversarial probes成功、axe 10 testsとheader 9 tests成功。
