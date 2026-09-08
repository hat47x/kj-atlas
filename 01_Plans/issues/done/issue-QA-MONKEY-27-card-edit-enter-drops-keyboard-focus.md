# Issue: QA-MONKEY-27 カード本文編集をEnter確定するとキーボードfocusが失われる

- Type: Bug / Accessibility
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`
- Related Backlog: `QA-MONKEY-27`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）, `01_Plans/issues/done/issue-QA-MONKEY-25-card-edit-escape-drops-keyboard-focus.md`
- Expected verification level: `e2e`

## 課題

カード本文のinline textareaで本文を変更しEnterを押すと、本文は正しく確定するが、textarea消滅後にfocusが`body`へ落ちる。Escape取消経路はQA-MONKEY-25で同じカードへ戻すよう修正済みだが、確定経路には同じ継続契約が適用されていなかった。

## 対応方針

- CardView内の「次frameで同じカードrootへfocusする」処理を共通化する。
- Enter確定後とEscape取消後の双方から共通処理を呼ぶ。
- Shift+Enter改行、外側click確定、本文保存、選択、SafeModeの契約は変更しない。

三要素牽制: 業務上は本文確定後も同じカードからレビューを継続できる。データ設計・保存境界は不変。機能上は確定後のfocus遷移だけを補完し、本文値と履歴単位は変更しない。新しい製品判断ではないためADR不要。

## 受入条件

- [x] Enterで変更本文が確定する。
- [x] textarea消滅後、同じカードrootへfocusが戻る。
- [x] Escape取消の元本文復元・focus復帰が回帰しない。
- [x] Shift+Enterと外側clickの既存挙動が回帰しない。

## 対応結果（2026-08-16）

- Enter/Escapeの双方を共通の次frame focus復帰処理へ統合した。
- A1/A2/A15/A16、近接47 tests、typecheckを通過した。

## 検証計画

- `monkey_adversarial_probes.mjs` A1/A2/A15/A16を実画面確認する。
- Enter/Spaceをfocus脱落検査へ加えたランダムseedを再実行する。
- frontend typecheck、CardView accessibility test、docs-check、active issue validatorを実行する。


## 配置の整理（2026-09-05）

- 本Issue群は、2026-08-16のモンキーテストで見つかった誤検知・検出漏れ・キーボードfocus継続性・再現記録のdriftを、QAハーネスと既存UI挙動の境界を崩さず解消した完了系列として `Done` となっていた。
- `QA-MONKEY-20/22/28` は正常な操作遮断や操作前からのbody focusを欠陥扱いしない一方、Enter / Space / Delete / Backspaceを含む実際のfocus脱落は検出できるよう、観測契約を精密化した。
- `QA-MONKEY-23/25/27/29` は選択解除・本文編集の取消/確定・カード削除でDOM要素が消える場合にも、作業文脈へfocusを戻してキーボード操作を継続できる境界を固定した。
- `QA-MONKEY-26` は現行ハーネスに合う再現CLIと実施記録を固定し、観測結果の再現可能性を回復した。
- これらは新しい製品仕様の追加ではなく、既存のアクセシビリティ基準・QA判定・再現性を実装と検証へ反映した完了記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は8から0へ縮小する。R18 identity manifestは不変の歴史境界として維持し、今後 `Status: Done` のmemoがactive rootへ残ることを許容しない。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
