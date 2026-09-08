# Issue: QA-MONKEY-25 カード本文編集をEscape取消するとキーボードfocusが失われる

- Type: Bug / Accessibility
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`
- Related Backlog: `QA-MONKEY-25`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）, `01_Plans/issues/done/issue-QA-MONKEY-23-selection-clear-drops-keyboard-focus.md`
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


## 配置の整理（2026-09-05）

- 本Issue群は、2026-08-16のモンキーテストで見つかった誤検知・検出漏れ・キーボードfocus継続性・再現記録のdriftを、QAハーネスと既存UI挙動の境界を崩さず解消した完了系列として `Done` となっていた。
- `QA-MONKEY-20/22/28` は正常な操作遮断や操作前からのbody focusを欠陥扱いしない一方、Enter / Space / Delete / Backspaceを含む実際のfocus脱落は検出できるよう、観測契約を精密化した。
- `QA-MONKEY-23/25/27/29` は選択解除・本文編集の取消/確定・カード削除でDOM要素が消える場合にも、作業文脈へfocusを戻してキーボード操作を継続できる境界を固定した。
- `QA-MONKEY-26` は現行ハーネスに合う再現CLIと実施記録を固定し、観測結果の再現可能性を回復した。
- これらは新しい製品仕様の追加ではなく、既存のアクセシビリティ基準・QA判定・再現性を実装と検証へ反映した完了記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は8から0へ縮小する。R18 identity manifestは不変の歴史境界として維持し、今後 `Status: Done` のmemoがactive rootへ残ることを許容しない。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
