# Issue: QA-MONKEY-23 選択コンテキストのボタン上でEscapeするとキーボードfocusが失われる

- Type: Bug / Accessibility
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`
- Related Backlog: `QA-MONKEY-23`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）
- Expected verification level: `e2e`

## 課題

カードを選択し、右側の「選択中のカードを表示」ボタンへキーボードfocusを移してEscapeを押すと、グローバルショートカットが選択を解除する。選択専用ボタンはその再描画で消えるため、focusが`body`へ落ち、その後のTab操作の開始位置と作業文脈が失われる。島選択の同等ボタンも同じ構造を持つ。

## 対応方針

- 選択コンテキスト領域をプログラムによるfocusが可能な安定要素にする。
- 選択解除で消えるカード・島の表示ボタン上でEscapeを受けた場合、グローバル選択解除より先にfocusを選択コンテキストへ戻す。
- Escapeによる選択解除、SafeMode、データ更新、通常のTab順は変更しない。

三要素牽制: 業務上はキーボード利用者が選択解除後も操作を継続できる。データ設計・保存境界は不変。機能上は既存Escape選択解除の直前にfocus復帰先だけを安定化し、選択・権限・SafeMode判定は変更しない。新しい製品判断ではないためADR不要。

## 受入条件

- [x] 「選択中のカードを表示」上のEscapeでカード選択が解除される。
- [x] 選択専用ボタンが消えた後もfocusが`body`へ落ちず、選択コンテキストに残る。
- [x] 島の同等ボタンにも同じfocus継続契約を適用する。
- [x] 選択コンテキストは通常のTab順へ新たなstopを追加しない。

## 検証計画

- `monkey_adversarial_probes.mjs` A12でカード選択からのEscapeを実画面確認する。
- frontend typecheck、対象unit test、docs-check、active issue validatorを実行する。

## 対応結果（2026-08-16）

- 選択コンテキストを`tabIndex=-1`のプログラムfocus先にし、Escape選択解除で同領域内の操作要素が消えてbody focusになった場合だけ、同領域へfocusを復帰するようにした。
- 通常のTab順にはstopを追加せず、別の処理がfocusを移した場合は上書きしない。
- A12で選択解除=true、context focus=trueを確認し、全14プローブでも再発0件だった。


## 配置の整理（2026-09-05）

- 本Issue群は、2026-08-16のモンキーテストで見つかった誤検知・検出漏れ・キーボードfocus継続性・再現記録のdriftを、QAハーネスと既存UI挙動の境界を崩さず解消した完了系列として `Done` となっていた。
- `QA-MONKEY-20/22/28` は正常な操作遮断や操作前からのbody focusを欠陥扱いしない一方、Enter / Space / Delete / Backspaceを含む実際のfocus脱落は検出できるよう、観測契約を精密化した。
- `QA-MONKEY-23/25/27/29` は選択解除・本文編集の取消/確定・カード削除でDOM要素が消える場合にも、作業文脈へfocusを戻してキーボード操作を継続できる境界を固定した。
- `QA-MONKEY-26` は現行ハーネスに合う再現CLIと実施記録を固定し、観測結果の再現可能性を回復した。
- これらは新しい製品仕様の追加ではなく、既存のアクセシビリティ基準・QA判定・再現性を実装と検証へ反映した完了記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は8から0へ縮小する。R18 identity manifestは不変の歴史境界として維持し、今後 `Status: Done` のmemoがactive rootへ残ることを許容しない。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
