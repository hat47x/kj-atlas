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
