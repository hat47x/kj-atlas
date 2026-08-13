# kj-atlas アドホック・モンキーテスト記録（2026-08-13）

対象読者: maintainer / QA contributor。開発者向け検証記録であり、公開文書ではない。

前回（`mvp_exit_monkey_test_log_2026-07-29.md`）で見つかった `QA-MONKEY-14`〜`17` はすべて実装側で修正・Done済みだったため、本回は未踏領域（コマンドパレット、undo/redo、ドラッグ、ズーム、島への参加、文書タイトル編集）を中心にアドホック操作と拡張モンキースイープを実施した。

## 環境

| 項目 | 値 |
| --- | --- |
| 候補 | working tree HEAD（`git status` clean、`7dd39539` 相当） |
| 実行環境 | Linux sandbox / Chrome for Testing 145.0.7632.6 / Playwright 1.58.2 / axe-core 4.12.1 |
| locale | `ja`（一部 `en` で対照） |
| viewport | 390 / 960 / 1440 |
| 備考 | サンドボックスがpnpmシンボリックリンクをI/Oエラーで読めなかったため、`03_Implement/frontend` を除外コピーした scratch ディレクトリへ `npm install` して検証した。`04_Documentation` / `02_Architecture` への相対パス参照を持つテスト（`external_agent_workflow_doc.test.ts` 等）はscratch単体では偽陽性で失敗したため、リポジトリ階層を再現した第二のscratchで再確認し、偽陽性であることを確認した。 |

## 方法

1. **手動アドホック探索**: コマンドパレット、undo/redo（多段、undo枯渇、undo後の新規操作によるredo破棄）、島への参加（ドラッグ&ドロップ、1回のundoでの復元）、ズーム（wheelでの拡大縮小、クランプ境界、リセット/全体に合わせるメニュー）、ヘッダーの「表示」ラベル重複、文書タイトル編集。
2. **拡張モンキースイープ**: 既存 `monkey_ui_sweep.mjs` にカードドラッグ、ラバーバンド選択、wheelズームのアクションを追加し、seed 21〜24で実行（各80〜120アクション、1440/960px）。
3. 疑わしい事象は個別スクリプトで最小再現に切り分けた。

## 検出した課題（起票・修正済み）

| ID | 概要 | 重大度 | 対応 |
| --- | --- | --- | --- |
| `QA-MONKEY-18` | キャンバスのwheelズームハンドラがReactの既定passiveリスナー上で`preventDefault()`を呼んでおり、ホイール操作のたびにconsole errorが出て`preventDefault`が無効化されていた | P1 | `useEffect` + `addEventListener(..., {passive:false})`へ変更し修正・検証済み |
| `QA-MONKEY-19` | `document-title-editor.spec.ts`が`?locale=en`で日本語プレースホルダー`"無題"`を期待しており、テストが赤いまま放置されていた（製品側は正しく`"Untitled"`を表示） | P2（test defect） | 期待値を`"Untitled"`へ修正・検証済み |
| `DX-TYPECHECK-01` | `tsc --noEmit`が`AppErrorBoundary.test.ts`のTypeScriptオーバーロード解決エラーで失敗する | P2 | 直近（2026-08-12/13）の無関係な進行中実装のため、起票のみで修正は見送った |

## 確認して問題が無かった項目

| 確認 | 結果 |
| --- | --- |
| コマンドパレット（`Ctrl+K`）: 開閉、ja localeでの表示（`コマンドを検索`）、絞り込み、Escapeで閉じる | ok |
| undo: カード作成→undo→redoで件数が正しく往復する | ok |
| undo枯渇（履歴の先頭を超えて連打）で例外や不正状態にならない | ok |
| undo後に新規操作を行うとredoスタックが正しく破棄される | ok |
| ズームのclamp（`MIN_ZOOM=0.2` / `MAX_ZOOM=4`）、大量ホイール操作後も一貫 | ok |
| メニューバーの「全体に合わせる」「ズームリセット」 | ok（メニュー経由で正しく動作。トップレベルのトリガーはヘッダーの「表示」ボタン(`role=button`)とメニューバーの「表示」カテゴリ(`role=menuitem`)がラベル重複するが、roleが異なり機能上の破綻はない） |
| カードを島の領域までドラッグ&ドロップして参加、1回のundoで位置・membership双方が復元される（`acceptance_check.md`手順6） | ok（初回誤検知あり。ヘッダー分のスクリーンオフセットを無視した自分の座標計算ミスで、正しい座標変換で再検証し正常動作を確認） |
| 文書タイトル編集（表示・編集モード切替） | ok |

## 拡張モンキースイープの結果

| seed | viewport | actions | findings |
| --- | --- | --- | --- |
| 21 | 1440 | 91 | `action-blocked`（無効ボタンへのクリックタイムアウト、製品欠陥ではない）×4、`focus-lost-to-body`×1（文書を開いた直後、何も選択・展開していない状態でのEscape。既存の"Escape with no overlay open"仕様と整合し、実害の薄い端点と判断） |
| 22 | 1440 | 105（打ち切り） | `console.error :: Unable to preventDefault...`（`QA-MONKEY-18`の元検出）、他は`action-blocked`のみ |
| 23 | 1440 | 81 | `action-blocked`×2のみ |
| 24 | 960 | 88 | `action-blocked`×4のみ |

`action-blocked`はいずれも、条件を満たさず無効化されたボタン（削除・保存・やり直す等）やモーダル表示中のキャンバス操作へのクリックタイムアウトで、harnessの制約であり製品の欠陥ではない。

## 修正の検証

### QA-MONKEY-18

- 修正前: 実際のマウスホイール操作のたびに `Unable to preventDefault inside passive event listener invocation.` がconsoleへ出力され、documentのbubbleフェーズで観測した実イベントの `defaultPrevented` は `false` のままだった。
- 修正後: console error 0件、`defaultPrevented === true`。ズームクランプ（0.2倍〜4倍）は修正前後で同一の挙動。
- 回帰確認: `tsc --noEmit`（新規エラーなし）、`vitest run` 239 files / 1430 tests成功、Playwright 38 tests成功（キャンバス・キーボード・ヘッダー・a11y・レスポンシブ関連）。

### QA-MONKEY-19

- 修正前: `document-title-editor.spec.ts` 3件中1件が失敗（`?locale=en`で`"無題"`を期待、実際は`"Untitled"`）。
- 修正後: 3/3成功。

## 再現に使ったスクリプト

拡張済みの `03_Implement/frontend/scripts/monkey_ui_sweep.mjs`（drag-card / rubber-band-select / wheel-zoomアクションを追加）をそのまま使用した。

```bash
cd 03_Implement/frontend
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4173 &
KJ_ATLAS_MONKEY_SEED=21 KJ_ATLAS_MONKEY_ACTIONS=120 node ./scripts/monkey_ui_sweep.mjs
```
