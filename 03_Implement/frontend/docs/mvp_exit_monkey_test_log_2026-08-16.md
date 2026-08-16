# kj-atlas アドホック・モンキーテスト記録（2026-08-16）

対象読者: maintainer / QA contributor。開発者向けの再現・回帰記録であり、公開文書ではない。

8月13日以後に追加されたモンキーハーネスの実操作性を再点検し、狭幅・日英locale・長時間seed・キーボードfocus・島のfocus/camera同期を重点探索した。疑わしい事象は固定プローブへ縮小し、製品欠陥とハーネス誤検知を分離した。

## 環境

| 項目 | 値 |
| --- | --- |
| 候補 | `d2ea5778`付近のmain + 本記録のQA-MONKEY-25修正 |
| 実行環境 | Windows Edge / Playwright 1.58.2 / axe-core 4.12.1。ViteはWSL上のNode 20で配信 |
| locale | `ja` / `en` |
| viewport | 320 / 390 / 768 / 1440 |
| fixture | Playwright routeで固定した6カード・1島、および個別プローブ用fixture。backend/LLM未接続 |

## 方法

1. `monkey_ui_sweep.mjs`で、キーボード、カード選択・編集、コンテキストメニュー、header、checkbox、drag、rubber-band、wheelをseed固定で反復した。
2. focus脱落は操作前が非bodyで、操作後にbodyへ遷移した場合だけ報告した。console errorはReact stackを含む長さまで保持し、直近最大200操作を記録した。
3. `monkey_adversarial_probes.mjs`へ、コンテキストメニュー、選択解除focus、島focus/camera同期、通常zoom永続化、inline編集取消focusを固定回帰として追加した。
4. axe smoke 10状態とheader responsive/keyboard 9検査を別途実行した。

## 検出・起票した課題

| ID | 種別・優先度 | 概要 | 対応 |
| --- | --- | --- | --- |
| `QA-MONKEY-20` | QA / P2 | 常設menuitemと正常な操作遮断を製品findingとしていた | baseline差分とactionable事前判定へ修正済み |
| `QA-MONKEY-21` | Accessibility / P1 | canvas context menuに名前・初期focus・矢印移動・Escape focus復帰がなかった | 修正済み、A10へ固定 |
| `QA-MONKEY-22` | QA / P2 | focus脱落判定が操作前状態を比較していなかった | 修正済み |
| `QA-MONKEY-23` | Accessibility / P1 | 選択専用ボタン上のEscapeでfocusがbodyへ落ちた | 選択contextへ復帰するよう修正済み、A12へ固定 |
| `QA-MONKEY-24` | Reliability / P1 | focus中の折りたたみ島を展開するとcamera transform同期が更新loopになった | callbackを安定化して修正済み、A13/A14へ固定 |
| `QA-MONKEY-25` | Accessibility / P1 | inline本文編集をEscape取消するとtextarea消滅後にfocusがbodyへ落ちた | 同じカードへ復帰するよう修正、A15へ固定 |
| `QA-MONKEY-26` | Documentation / P2 | 8月13日以後の実施結果と現行CLIが恒久記録に反映されていなかった | 本記録を追加し、7月29日の旧環境変数名を更新 |

## ランダムスイープ結果

すべて指定loop数は400。`actions`は実際にtraceへ追加された操作数で、対象要素が存在せず空操作になったloopを除く。

| seed | locale | viewport | actions | 結果 |
| --- | --- | --- | --- | --- |
| 101 | ja | 320 | 311 | finding 0 |
| 202 | en | 390 | 379 | finding 0 |
| 303 | ja | 768 | 325 | finding 0 |
| 404 修正前 | en | 1440 | 338 | `Escape@Edit card text`後のfocus脱落1件（QA-MONKEY-25） |
| 404 修正後 | en | 1440 | 337 | finding 0 |

前段のQA-MONKEY-22〜24修正時には、seed 808・390pxとseed 909・1440pxを各300 loopで実行し、いずれもfinding 0を確認した。

## 固定回帰と自動検査

- adversarial A1〜A14: 14/14 ok。A15はja/enの双方で元本文復元=true、同じカードへのfocus復帰=true。
- axe smoke: start、選択context、島editor、inline editor、凡例、共有、作業mode、agent export/import、menuの10/10成功。
- header responsive/keyboard: 390〜1440pxのlayout、panel範囲、Escape focus復帰、shortcutの9/9成功。
- seed 404修正後: finding 0。未捕捉例外、console error、白画面、SafeMode消失、無名dialog/button/field、横overflow、NaN座標は検出なし。

## 再現コマンド

```bash
cd 03_Implement/frontend
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4173

KJ_ATLAS_MONKEY_SEED=404 \
KJ_ATLAS_MONKEY_ACTIONS=400 \
KJ_ATLAS_MONKEY_VIEWPORT=1440 \
KJ_ATLAS_BASE_URL='http://127.0.0.1:4173/?locale=en' \
node ./scripts/monkey_ui_sweep.mjs

KJ_ATLAS_MONKEY_ONLY=A1,A2,A15 node ./scripts/monkey_adversarial_probes.mjs
```

Windows側のEdgeを明示して実行する環境では、`KJ_ATLAS_SCREENSHOT_BROWSER_PATH`に実行ファイルを設定する。`SUSPECT`やfindingは自動的に製品欠陥とはみなさず、固定プローブまたは同seed再実行で再現してから課題化する。
