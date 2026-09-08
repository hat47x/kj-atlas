# Issue: QA-MONKEY-29 focus中のカードをDelete削除するとキーボードfocusが失われる

- Type: Bug / Accessibility
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`
- Related Backlog: `QA-MONKEY-29`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）
- Expected verification level: `e2e`

## 課題

focus中のカードを選択してDeleteまたはBackspaceで削除すると、active element自体がDOMから消滅し、focusが`body`へ落ちる。削除自体は成功するが、キーボード利用者は残存カードから操作を継続できない。

## 対応方針

- CardView rootへカードIDを表すdata属性を付け、削除時にfocus中のカードを識別する。
- focus中のカードが削除対象だった場合のみ、文書順で同位置（末尾削除時は直前）の残存カードへ次frameでfocusを移す。
- pointer操作、focus外の一括削除、全カード削除では不要なfocus移動を行わない。

三要素牽制: 業務上は削除後も残存カードの整理を継続できる。データモデル、削除対象、履歴単位は不変。機能上は削除後のfocus遷移だけを補完し、新しい製品判断ではないためADR不要。

## 受入条件

- [x] focus中の選択カードをDelete削除すると、そのカードが削除される。
- [x] 残存カードがある場合、文書順の近傍カードへfocusが移る。
- [x] 全カード削除時とfocus外の削除時に例外や意図しないfocus移動がない。
- [x] Enter確定・Escape取消のfocus復帰が回帰しない。

## 対応結果（2026-08-16）

- 削除対象がactive cardの場合だけ、同位置または直前の残存カードへfocusを引き継ぐようにした。
- A15/A16/A17、近接47 tests、typecheckを通過した。

## 検証計画

- `monkey_adversarial_probes.mjs` A15/A16/A17を実画面確認する。
- Delete/Backspaceをfocus脱落検査へ加えたランダムseedを再実行する。
- frontend typecheck、CardView accessibility test、UX operability test、docs-check、active issue validatorを実行する。


## 配置の整理（2026-09-05）

- 本Issue群は、2026-08-16のモンキーテストで見つかった誤検知・検出漏れ・キーボードfocus継続性・再現記録のdriftを、QAハーネスと既存UI挙動の境界を崩さず解消した完了系列として `Done` となっていた。
- `QA-MONKEY-20/22/28` は正常な操作遮断や操作前からのbody focusを欠陥扱いしない一方、Enter / Space / Delete / Backspaceを含む実際のfocus脱落は検出できるよう、観測契約を精密化した。
- `QA-MONKEY-23/25/27/29` は選択解除・本文編集の取消/確定・カード削除でDOM要素が消える場合にも、作業文脈へfocusを戻してキーボード操作を継続できる境界を固定した。
- `QA-MONKEY-26` は現行ハーネスに合う再現CLIと実施記録を固定し、観測結果の再現可能性を回復した。
- これらは新しい製品仕様の追加ではなく、既存のアクセシビリティ基準・QA判定・再現性を実装と検証へ反映した完了記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は8から0へ縮小する。R18 identity manifestは不変の歴史境界として維持し、今後 `Status: Done` のmemoがactive rootへ残ることを許容しない。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
