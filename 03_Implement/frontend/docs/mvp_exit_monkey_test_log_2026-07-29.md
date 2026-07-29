# MVP-EXIT-01 関連部分のモンキーテスト記録（2026-07-29）

対象読者: maintainer / QA contributor。開発者向け検証記録であり、公開文書ではない。

`03_Implement/frontend/docs/mvp_exit_human_acceptance_log_2026-07-29.md` で機械代替検証した範囲（キーボード操作、accessibility semantics、カード編集、ヘッダー、表示・共有パネル、作業モードタブ、凡例、選択コンテキスト）に対して、ランダム操作と敵対的操作を実施した記録。

## 環境と候補

| 項目 | 値 |
| --- | --- |
| 候補 | `94120c7c` + `UI-QUALITY-A11Y-07` / `DOC-SHOT-01`(B) の未commit修正 |
| 実行環境 | Linux sandbox / Chrome for Testing 145.0.7632.6 / Playwright 1.58.2 / axe-core（`@axe-core/playwright` 4.12.1） |
| locale | `ja` |
| viewport | 390 / 768 / 960 / 1440 |
| fixture | Playwright routeで固定した決定論的文書（LLM未接続） |

## 方法

2種類を併用した。

**(1) 種付きランダム操作（monkey）**: mulberry32 の疑似乱数で、Tab / Shift+Tab / Enter / Space / Escape / 矢印 / Home / End / Delete / Backspace、ヘッダーボタンのクリック、カードのクリック・Shiftクリック・ダブルクリック・右クリック、メニュー項目のクリック、チェックボックス操作、文字入力を混ぜて流す。各操作の後に不変条件を検査し、違反を直近12操作のトレース付きで記録する。

検査した不変条件:

- 未捕捉例外（`pageerror`）とconsole error
- アプリのアンマウント（白画面）
- 画面テキストへの `undefined` / `NaN` / `[object Object]` の露出
- SafeMode表示の消失
- `aria-pressed` の不正値
- 名前のない `role="dialog"`
- accessible nameのない可視ボタン・可視入力欄
- viewport幅を超える横オーバーフロー
- Tab / Shift+Tab / Escape 後の `<body>` へのフォーカス脱落

**(2) 敵対的な狙い撃ち（adversarial）**: 文書化された期待に対して、壊れやすい組み合わせを個別に確認する。

実行したseedと幅: seed 1/2/7（1440）、seed 3/4（390）、seed 5（768）、seed 11（960）。1回あたり19〜70操作。sandboxの実行時間上限により、一部のrunは途中で打ち切られている（打ち切り自体は製品の事象ではない）。

## 検出した課題（起票済み）

| ID | 概要 | 重大度の見立て |
| --- | --- | --- |
| `QA-MONKEY-14` | 島エディタの `ID` / `タイトル` 欄が未ラベルで、axe `label` **critical** ×2。axe smokeに島選択状態が無い | Major |
| `QA-MONKEY-15` | ja localeで島の既定名が `Island N`（英語）。文書へ保存され共有物にも載る | Major |
| `QA-MONKEY-16` | 未レビュー標識の `<span aria-label>` が禁止属性（axe `aria-prohibited-attr` serious）。通常表示ではカード名に状態が混入 | Minor〜Major |
| `QA-MONKEY-17` | 390pxでヘッダー検索行が左に26px切れ、スクロールでも到達できない | Minor〜Major |

`QA-MONKEY-14` と `QA-MONKEY-16` は、いずれも `e2e/a11y_axe_smoke.spec.ts` が走査していない状態で起きている。先に修正した `UI-QUALITY-A11Y-07` も同じ理由だった。**個別の欠陥3件ではなく、axe走査状態のカバレッジ不足が共通の原因**であり、走査状態の追加を `QA-MONKEY-14` の受入条件に含めた。

## 確認して問題が無かった項目（起票しない）

| 確認 | 結果 |
| --- | --- |
| 既存カードの編集を `Esc` で取り消すと元の本文へ戻る | ok（本文が復元、書き換えは残らない） |
| 入力欄の外をクリックすると編集が確定する | ok |
| カードのコンテキストメニューが `Escape` で閉じる | ok（残存6件は常設メニューバーで、harness側の誤検知だった） |
| ヘッダーのメニューバーのARIA構造 | ok（`role="menubar"` > `role="menuitem"`、`aria-haspopup` / `aria-expanded` あり） |
| 検索欄での `Delete` / `Backspace` が選択カードを削除しない | ok |
| 島の作成を「元に戻す」で取り消せる | ok（島 1 → 0） |
| 作業モードtabの roving tabindex | ok（tab 7件中 `tabindex=0` は1件） |
| 「島を作成」の連打で島が二重生成されない | ok（島は1件） |
| `エージェント応答を取り込む` / `エージェントへ依頼` / `サポート診断バンドル` のモーダル挙動 | ok（`role="dialog"` + `aria-modal="true"`、開いた直後に「閉じる」へフォーカス、`Escape` で閉じる） |
| ランダム操作中の未捕捉例外・console error・白画面・SafeMode表示の消失・`undefined` 等の露出 | 検出なし |
| Tab / Escape 後のフォーカス脱落 | 検出なし |

### 途中で否定した仮説

- 「960pxで `エージェント応答を取り込む` を開くとヘッダーが操作不能になり、Escapeで閉じられない」
  → **否定**。当該パネルは `role="dialog"` `aria-modal="true"` の全面モーダルで、ヘッダーを覆うのは仕様どおり。Escapeでも閉じる。最初の観測は、パネル本体ではなくヘッダーのトリガーボタンのテキストを可視判定に使っていた計測ミスだった。
- 「ヘッダーの `menuitem` が `menu` / `menubar` の外にある（axe `aria-required-parent`）」
  → **否定**。親は `role="menubar"`。

## harness側の既知の限界

- 無効化されたボタン（`削除` / `保存` / `やり直す` など、条件を満たさないと disabled）へのクリックがタイムアウトし、`action-blocked` として記録される。製品の事象ではない。
- モーダルが開いている間はキャンバスのカードがクリックできず、同様に `action-blocked` になる。
- 1回のbash呼び出しの時間上限により、runが途中で終了することがある。その場合は `harness-exception` が記録される。

## 再現に使ったスクリプト

`03_Implement/frontend/scripts/` に配置した。

```bash
cd 03_Implement/frontend
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4173 &

SEED=1 ACTIONS=150 VIEWPORT=1440 node ./scripts/monkey_ui_sweep.mjs
ONLY=A1,A2,A3,A4 node ./scripts/monkey_adversarial_probes.mjs
```

`monkey_ui_sweep.mjs` は違反を、`monkey_adversarial_probes.mjs` は各確認の ok / SUSPECT をJSONで出力する。SUSPECT はそのまま欠陥を意味しない。上記のとおり、確定させる前に個別の再現で切り分ける必要がある。
