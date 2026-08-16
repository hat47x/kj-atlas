# kj-atlas アドホック・モンキーテスト記録（2026-08-16）

対象読者: maintainer / QA contributor。開発者向けの再現・回帰記録であり、公開文書ではない。

8月13日以後に追加されたモンキーハーネスの実操作性を再点検し、狭幅・日英locale・長時間seed・キーボードfocus・島のfocus/camera同期を重点探索した。疑わしい事象は固定プローブへ縮小し、製品欠陥とハーネス誤検知を分離した。

## 環境

| 項目 | 値 |
| --- | --- |
| 候補 | `b235a024`付近のmain + 本記録のQA-MONKEY-27〜30修正 |
| 実行環境 | Windows Edge / Playwright 1.58.2 / axe-core 4.12.1。ViteはWSL上のNode 20で配信 |
| locale | `ja` / `en` |
| viewport | 320 / 390 / 768 / 1440 |
| fixture | Playwright routeで固定した6カード・1島、個別プローブ用fixture、および隔離SQLite + DeepSeek実API |

## 方法

1. `monkey_ui_sweep.mjs`で、キーボード、カード選択・編集、コンテキストメニュー、header、checkbox、drag、rubber-band、wheelをseed固定で反復した。
2. focus脱落は操作前が非bodyで、操作後にbodyへ遷移した場合だけ報告した。console errorはReact stackを含む長さまで保持し、直近最大200操作を記録した。
3. `monkey_adversarial_probes.mjs`へ、コンテキストメニュー、選択解除focus、島focus/camera同期、通常zoom永続化、inline編集取消・確定、カード削除、サンプル開始後のfocusを固定回帰として追加した。
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
| `QA-MONKEY-27` | Accessibility / P1 | inline本文編集をEnter確定するとtextarea消滅後にfocusがbodyへ落ちた | Escape経路と共通のfocus復帰処理へ修正、A16へ固定 |
| `QA-MONKEY-28` | QA / P2 | focus脱落判定がEnter/Space/Delete/Backspaceと非同期完了を扱わなかった | 対象キーを拡張し、RAF・短い非同期待ち後の安定状態を判定 |
| `QA-MONKEY-29` | Accessibility / P1 | focus中の選択カードをDeleteするとfocusがbodyへ落ちた | 文書順の近傍カードへfocusを移すよう修正、A17へ固定 |
| `QA-MONKEY-30` | Accessibility / P1 | 「サンプルを開く」をEnter実行すると開始パネル消滅後にfocusがbodyへ落ちた | 読込完了後に先頭カードへfocusを移すよう修正、A18へ固定 |
| `AI-DEEPSEEK-STATUS-01` | Contract / P1 | DeepSeekはruntimeで受理されるがprovider status型が拒否し500になる | backend/frontend/診断bundle/日英表示/仕様を同期し、API・実Edge回帰へ固定 |
| `MCP-DOGFOOD-12` | QA / P2 | MCP監査E2Eがnpm不在とWSLのWindows TEMPで起動不能 | package-local tsxとLinux一時領域を使うよう修正 |
| `QA-MONKEY-31` | Accessibility / P1 | ミニマップを折りたたむと置換されたtoggleからfocusがbodyへ落ちた | 置換後toggleへfocusを引き継ぐよう修正、A19へ固定 |
| `AI-DEEPSEEK-MODEL-01` | Contract / P1 | DeepSeek既定modelが送信層でだけ解決され、統制層で`default`として403拒否された | provider既定modelを統制前に解決し、実API回帰で確認 |
| `AI-TITLE-SAFEMODE-01` | Security / UX / P1 | タイトル提案がレビュー証明を欠き422、島タイトルのreview filterも欠落 | レビュー済み島タイトル・カードだけに限定して証明を付与 |
| `OPS-LLM-COST-03` | Operations / UX / P2 | 生成後もView panelが起動時のcall count/token usageを表示した | panel open時に最新snapshotを再取得 |

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

QA-MONKEY-27〜30では各500 loopへ拡張した。修正前はseed 505（ja/320）でサンプル開始後、606（en/390）で共有パネルEscape後、8080（en/1440）で編集Enter後のfocus脱落候補を検出した。固定再現の結果、共有パネルと編集Enterは次frame復帰前の過渡状態であり、ハーネスを安定状態判定へ修正した。seed 606と8080は修正後finding 0、seed 505の実欠陥はA18で修正前false・修正後trueを確認した。

管理CLI・MCP・DeepSeek連動を加えた継続探索では、管理API 12/12、CLI→CE-4監査15/15、修正後MCP→CE-4監査8/8、MCP package 61/61を確認した。seed 9091（en/320、500 loop）はfinding 0。seed 10001（ja/1440、500 loop）はミニマップtoggleのfocus脱落1件を検出しA19へ固定した。

その後、Git管理外のlocal credentialを環境変数へ一時注入し、隔離SQLiteでDeepSeek実APIを検証した。資格情報の値は出力・記録・コミットしていない。初回は既定modelの統制不整合でカード改善・島要約がともに403となり、`AI-DEEPSEEK-MODEL-01`を修正後、両方200、島内grounding ID、call count 2、入力626／出力122トークンを確認した。実Edgeのタイトル提案ではSafeMode契約不整合と利用量表示のstale snapshotを順に検出・修正し、候補3件、採用前タイトル不変、`deepseek: 1`、入力118／出力47トークンを再読込なしで確認した。

## 固定回帰と自動検査

- adversarial A1〜A19: A15はja/enの双方で取消後focus復帰、A16はEnter確定後focus復帰、A17は削除後の近傍カードfocus、A18はサンプル開始後の先頭カードfocus、A19はミニマップ切替後のtoggle focusを確認。
- axe smoke: start、選択context、島editor、inline editor、凡例、共有、作業mode、agent export/import、menuの10/10成功。
- header responsive/keyboard: 390〜1440pxのlayout、panel範囲、Escape focus復帰、shortcutの9/9成功。
- seed 404修正後: finding 0。未捕捉例外、console error、白画面、SafeMode消失、無名dialog/button/field、横overflow、NaN座標は検出なし。
- DeepSeek実API: カード改善1/1、島要約1/1、タイトル候補1/1。すべて`deepseek-chat`のprimary pathでfallbackなし。
- proposal-only: タイトル候補3件の表示後も現在タイトルは不変。候補選択前の自動適用なし。
- 利用量表示: 実生成後にView panelを開き、call count/token usageの最新snapshotを表示。

## 再現コマンド

```bash
cd 03_Implement/frontend
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4173

KJ_ATLAS_MONKEY_SEED=404 \
KJ_ATLAS_MONKEY_ACTIONS=400 \
KJ_ATLAS_MONKEY_VIEWPORT=1440 \
KJ_ATLAS_BASE_URL='http://127.0.0.1:4173/?locale=en' \
node ./scripts/monkey_ui_sweep.mjs

KJ_ATLAS_MONKEY_ONLY=A1,A2,A15,A16,A17,A18,A19 node ./scripts/monkey_adversarial_probes.mjs
```

Windows側のEdgeを明示して実行する環境では、`KJ_ATLAS_SCREENSHOT_BROWSER_PATH`に実行ファイルを設定する。`SUSPECT`やfindingは自動的に製品欠陥とはみなさず、固定プローブまたは同seed再実行で再現してから課題化する。
