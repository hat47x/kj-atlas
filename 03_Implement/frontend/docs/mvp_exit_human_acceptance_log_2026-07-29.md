# MVP-EXIT-01 人間受入項目の検証ログ（2026-07-29）

対象読者: maintainer / QA contributor。本文書は開発者向け検証記録であり、公開文書ではない。

`01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md` の「現在の判断」に残っていた4件の人間確認について、実施した検証、得られた証跡、機械代替の限界、残る人間判断を記録する。

## 候補の固定

| 項目 | 値 |
| --- | --- |
| 候補commit | `94120c7c8117d9292a2c13761317e446e60883b5`（検証開始時点でworking treeはclean） |
| 検証中に加えた変更 | `src/canvas/CardView.tsx`、`src/i18n/locales/{ja,en}.json`、`scripts/capture_{release_screenshots,ui_catalog,product_value_screenshots}.mjs`（下記S2・D2） |
| locale | `ja` |
| viewport | 1440×900（390×720はmobile確認のみ） |
| LLM provider | 未接続（fixtureはPlaywright routeで固定） |
| 実行環境 | Linux sandbox / Chrome for Testing 145.0.7632.6 / Playwright 1.58.2 |

検証中の変更は候補commitに含まれていない。最終判断は「これらをcommitした候補」に対して再確認する必要がある。

## 検証方法と、その限界

3件の人間確認は、いずれも「人間の感覚器で確認する」ことが受入条件に書かれている。ここで行ったのは**機械代替**であり、等価ではない。

| 元の人間確認 | 機械代替 | 代替できたこと | 代替できないこと |
| --- | --- | --- | --- |
| 物理キーボードでの主要操作 | 実キーイベントのみで操作するPlaywrightスクリプト（マウス入力を一切使わない） | 到達可能性、Enter/Space起動、Escape復帰、入力確定・取消の成立 | 実キーボードのIME、OS側ショートカット競合、押しやすさ・迷いといった主観 |
| スクリーンリーダーでの開始・編集・保存・共有前確認 | Chromium accessibility treeとlive region配線の検査 | role / accessible name / aria-live / tab semantics / focus復帰といった、支援技術に渡る情報の有無 | NVDA・JAWS・VoiceOverが実際に読み上げる語順、冗長さ、無音区間 |
| 公開文書のリリース候補画面 | capture scriptによる再撮影と、既存公開画像との目視比較 | 画像と現行UIの一致・不一致の判定 | 公開文書全体の読みやすさ、掲載順の妥当性 |

したがって本ログは、残る人間確認を**消滅させるものではなく、確認すべき範囲を狭めるもの**である。

## 1. 物理キーボード受入（機械代替）

スクリプト: `keyboard_acceptance.mjs`（本ログに添付。`04_Documentation/acceptance_check.md`「キーボードで確認すること」1〜5に対応）

結果: **10/10 pass**

| ID | 確認内容 | 結果 | 証跡 |
| --- | --- | --- | --- |
| K0 / K0b | 開始パネルの「サンプルを開く」へTabで到達し、Enterで実行できる | pass | 3回のTabで到達、パネルが閉じ文書が開く |
| K1 | Tabでヘッダー・キャンバス上のカード・右側パネルへ移動できる | pass | 到達領域 `header` / `main` / `aside`、カード到達あり |
| K2a | フォーカス中のボタンをEnterで実行できる | pass | 「新規カード」がEnterで作動 |
| K2b | フォーカス中のトグルをSpaceで実行できる | pass | 「詳細」の `aria-pressed` が `false` → `true` |
| K3a | 「表示」を開いた後、次の項目へ移動できる | pass | パネル可視、フォーカスがパネル内へ進む |
| K3b | 「共有と再現」を開いた後、パネル内の項目へ移動できる | pass | `data-panel="share-replay"` 内へTabで到達 |
| K5 | Escapeで閉じ、元のボタンへフォーカスが戻る | pass | 閉じたうえで「共有と再現」ボタンへ復帰 |
| K4 | 入力欄で入力・削除・確定が完結する | pass | 作成直後に入力欄へフォーカス、Backspace反映、Enterで確定 |
| K4b | Escapeで編集を取り消して元の作業へ戻れる | pass | 取消後に本文が残らない |

残る人間確認: 実キーボード（特にIME変換中のEnter/Escape）と、OS/ブラウザのショートカット競合。

## 2. スクリーンリーダー受入（機械代替）

スクリプト: `screenreader_acceptance.mjs`（`04_Documentation/acceptance_check.md`「スクリーンリーダーで確認すること」1〜6に対応）

初回結果: **5/6 pass、1 fail**。fail は実装欠陥だったため修正し、再実行して 6/6 pass。

| ID | 確認内容 | 結果 | 証跡 |
| --- | --- | --- | --- |
| S1 | 見出しジャンプでプロダクト名の `h1` へ到達できる | pass | `h1 = "kj-atlas Canvas"`（文書内の `h1` は1件） |
| S2 | カード追加直後の本文入力欄が読み上げられる | **初回fail → 修正後pass** | 下記参照 |
| S3 | 選択時に「現在の選択」が自動的に読み上げられる | pass | `aria-live="polite"` / `aria-label="現在の選択"`、読み上げ順は「カードを選択中 → 対象 → レビュー状態」 |
| S4 | 作業モードがtabとして認識され矢印/Home/Endで移動する | pass | `tablist` 1件・`tab` 7件、ArrowRight/Home/Endが機能、`aria-selected` は常に1件 |
| S5 | 「出典参照を含める」ON時に警告文が説明として結び付く | pass | ON時に `aria-describedby` が付与され、参照先が解決し警告文が存在する |
| S6 | 凡例がdialogとして名前付きで、Escape後にトリガーへ戻る | pass | `role=dialog` / name `状態の凡例`、Escapeで閉じフォーカス復帰 |

### S2で見つかった実装欠陥（修正済み）

カード本文のインライン編集 `<textarea>`（`src/canvas/CardView.tsx`）に、`aria-label`、`aria-labelledby`、`<label>`、`placeholder`、`title` のいずれもなかった。accessible nameが空のため、支援技術は「編集」＋入力値しか伝えられず、`acceptance_check.md` の「本文入力欄にフォーカスがあることが読み上げられ」を満たさない。

自動axe検査がこれを検出していなかったのは、既存のaxe smokeがインライン編集中の状態を通っていないためと考えられる。

修正: `aria-label={t("card_view.edit_textarea_label")}` を付与し、`ja` / `en` の両カタログにキーを追加した。修正後 `AXrole=textbox` / `AXname="カード本文を編集"` を確認。

回帰確認: frontend typecheck 成功、`src/i18n/` 61件 pass、`src/ui/ux_operability_regression.test.ts` と `src/canvas/` 計73件 pass、`e2e/card_single_save_creation.spec.ts` pass。

残る人間確認: 実際のNVDA/JAWS/VoiceOverでの読み上げ語順と冗長さ。特にS3の読み上げ順は、保留・違和感・根拠が存在するカードで検証していない（今回のfixtureに該当状態がない）。

## 3. 公開文書のリリース候補画面

結果: **不一致あり（公開Go条件を満たさない）**

### D1: 公開画像セットがstale

`04_Documentation/assets/screenshots/README.md` の stale 判定（「参照するUIラベル、レイアウト、表示状態」の変化）に該当する。

現行UIのヘッダーには **「サポート診断バンドル」** ボタンが存在するが、公開中の画像には存在しない。再撮影して比較した5件すべてで再現した。

| 画像 | 差分 |
| --- | --- |
| `app-canvas-overview.png` | ヘッダーに「サポート診断バンドル」なし |
| `selection-context-card.png` | 同上 |
| `share-export-safe-mode.png` | 同上 |
| `start-document-entry.png` | 同上 |
| `mobile-toolbar-smoke-390.png` | 同上。390pxではヘッダーの折り返しが2行→3行に変わる |
| `product-value-*.png` | 同上（`product-value-first-island.png` で確認） |
| `ui-*.png` | ヘッダーを含むものは同じ理由でstaleと推定（未撮影） |

provenance記録上の対象revisionは `1367740d...`（2026-07-11撮影）であり、以後のヘッダー変更が反映されていない。

### D2: capture scriptのselectorが腐っていた（修正済み）

再撮影を試みた時点で、公開画像を生成する3本のscriptがいずれも失敗した。キャンバス上のカードを `getByRole("option")` で選択していたが、現行実装のカードは `aria-pressed` を持つ `button` である（`ADR-0052` のcanvas card移行後の実装と、`e2e/first_meaningful_map_mouse_flow.spec.ts` の記述が一致している）。

つまり **公開画像を再生成する手段自体が壊れていた**。`capture_release_screenshots.mjs` / `capture_ui_catalog.mjs` / `capture_product_value_screenshots.mjs` の該当selectorを `button` へ修正し、release 5/5・product-value 6/6の生成成功を確認した（ui-catalogは本環境の実行時間上限により2/12までで打ち切り。selector修正の効果は確認済み）。

### 本環境で公開画像を差し替えなかった理由

`04_Documentation/assets/screenshots/README.md` は「対象revision（commit SHA。未commitのUI変更から撮らない）」を要求している。本検証のworking treeにはS2の修正が未commitで含まれるため、この規定に従い公開画像は差し替えていない。再撮影は、S2・D2の修正をcommitしたうえで正本環境から実施する。

### D3: 判断が必要な表示（product defectとは断定しない）

`acceptance_check.md` は「AIによる提案、差分確認、パッチ、診断などは『詳細』を選ぶまで表示されません」と説明しているが、「サポート診断バンドル」ボタンは `isAdvancedUiEnabled` で囲われておらず通常表示に常設されている（隣接する `agent_task_export` / `agent_response_import` は囲われている）。右側パネルの「診断を実行」も通常表示に出ており、これは以前の公開画像でも同様であるため、文書の記述と実装の境界が以前からずれている可能性がある。

意図的な設計（サポート用途は基本操作、AI高度機能のみ詳細）であれば文書側を直し、意図せぬ露出であれば実装側を直す。いずれも設計判断であるため、ここでは変更していない。

## 4. 最終出荷判断

`PRODUCT-QA-01` のGate Recordを `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md` に記録した。結論は **No-Go**（G5 公開文書が「古いUIを公開する」No-Go条件に該当）。

製品そのものの主要操作・安全境界・accessibility基盤に、出荷を止める欠陥は見つかっていない。残るのは、修正のcommitと公開画像の再撮影という機械的な工程である。

## 再現手順

```bash
cd 03_Implement/frontend
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4173 &
node ./scripts/keyboard_acceptance.mjs        # 本ログ添付のスクリプトを配置した場合
node ./scripts/screenreader_acceptance.mjs
node ./scripts/capture_release_screenshots.mjs
```

検証スクリプトは本コミットではrepoへ取り込んでいない。継続的に回すなら `e2e/` 配下のspecとして取り込み、CIのaccessibilityレーンへ接続する（`UI-QUALITY-A11Y-*` 系issueの対象）。
