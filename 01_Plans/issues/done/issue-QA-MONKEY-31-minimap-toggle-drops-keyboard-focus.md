# Issue: QA-MONKEY-31 ミニマップ切替後にキーボードfocusが失われる

- Type: Bug / Accessibility
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のseed 10001アドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/Minimap.tsx`, `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`
- Related Backlog: `QA-MONKEY-31`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）, `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D2）
- Expected verification level: `e2e`

## 課題

展開中ミニマップの「折りたたむ」をSpace/Enterで実行すると、focus中の小ボタンを含むミニマップDOMが置換され、focusが`body`へ落ちる。逆方向の展開でも同じ構造を持ち、キーボード利用者が切替後に操作位置を失う。

## 対応方針

- 展開・折りたたみボタンで同じrefを共有する。
- 状態保存後の次frameで置換後ボタンへfocusを移す。
- 自動非表示、pointer pan、tenant別折りたたみ状態の契約は変更しない。

三要素牽制: 業務上は補助ナビゲーションの表示密度を変えた後も操作を継続できる。データ上は既存のtenant-scoped collapse設定だけを保存する。機能上は置換後のfocus遷移だけを補完し、カメラや選択状態は変更しない。ADR不要。

## 受入条件

- [x] Space/Enterで折りたたむと展開ボタンへfocusが移る。
- [x] 再展開すると折りたたみボタンへfocusが移る。
- [x] pointer操作とtenant別永続化が回帰しない。
- [x] 320pxの自動非表示で例外を発生させない。

## 対応結果（2026-08-16）

- 展開・折りたたみtoggleでrefを共有し、置換後の次frameにfocusを引き継ぐようにした。
- A19、全19固定プローブ、seed 10001修正後finding 0、frontend近接112件、typecheckを通過した。

## 検証計画

- `monkey_adversarial_probes.mjs` A19を実Edgeで確認する。
- seed 10001を再実行し、frontend typecheck、Minimap近接テスト、docs-check、active issue validatorを実行する。


## 配置の整理（2026-09-05）

- 本Issueは、モンキーテストで見つかった直接のUI／キーボード操作不具合を修正し、個別の回帰確認まで終えて `Done` となっていた。一方、R18時点のlegacy集合に含まれたため、完了済みのまま作業中Issueと同じルートへ残っていた。
- 2026-09-05の残存39件参照グラフ監査で、本Issueは他のlegacy Doneとの系列内ID参照を持たない孤立成分であり、旧rootパスの外部引用もないことを確認した。
- 既存のライフサイクル契約に従い、本変更ではこの条件を満たすQA-MONKEY完了Issue 5件を `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を39から34へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
