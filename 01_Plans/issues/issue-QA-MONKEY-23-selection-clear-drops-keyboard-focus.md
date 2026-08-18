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
