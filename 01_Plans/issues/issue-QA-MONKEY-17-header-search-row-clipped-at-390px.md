# Issue: QA-MONKEY-17 390pxでヘッダーの検索行が左右に切れ、スクロールもできない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `MVP-EXIT-01`（人間受入項目の機械代替検証後に実施したモンキーテストで発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`（ヘッダーの検索・状態フィルタ行）
- Related Backlog: `QA-MONKEY-17`
- Related ADR/Spec: `04_Documentation/acceptance_check.md`（表示幅を変えて確認する / 確認結果の判定）, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`（G4 画面耐性）
- Expected verification level: `e2e`

## 課題

390px幅で、ヘッダーの検索行が **左に26px はみ出して恒久的に切れる**。横スクロールバーは出ず、スクロールで到達することもできない。

- 検索欄（placeholder「カードを検索」）: `left = -26px` → 画面上は「ドを検索」と読める。
- 「状態フィルタ」ラベル: `left = -26px` → 「ルタ」と読める。
- 「非一致を非表示」ラベル: `right = 416px`（viewport 390px）→ 右端が切れる。

`acceptance_check.md`「確認結果の判定」は「主要操作が画面外に見切れる」を **停止** に分類しており、検索は同文書「大きな文書で確認する」の手順1で使う主要操作である。

## 原因

検索行の祖先に `overflow-x: hidden` かつ `justify-content: center` のコンテナがあり、その中に幅442pxの子が入っている。

```
input   : left=-26  width=147  overflow-x=clip
div     : left=-26  width=442                      ← 中身
div     : left=-26  width=442
div     : left= 16  clientW=358  scrollW=404  overflow-x=hidden  justify-content=center   ← ここで切れる
header  : left=  0  width=390   flex-wrap=wrap
```

`justify-content: center` のため、はみ出しが左右へ均等に配分される。`overflow-x: hidden` はスクロールを許さないので、**左側にはみ出した26pxは操作でも復帰できない**。`document.documentElement` 側のオーバーフローは0のため、ページ全体の横スクロールも発生しない。

`overflow-x: auto` であれば少なくとも右方向へはスクロールできるが、`justify-content: center` と併用すると左側は依然として到達不能である（`scrollLeft` は負値を取れない）。

## 再現手順

1. viewport 390×720 で `?locale=ja` を開き、サンプル文書を開く。
2. ヘッダーの検索欄と「状態フィルタ」の左端を見る。

観測結果:

```
viewportWidth: 390 / docOverflowX: 0 / headerOverflowX: 0
clipped:
  input  "カードを検索"    left=-26  right=121
  span   "状態フィルタ"    left=-26  right= 40
  label  "非一致を非表示"  left=306  right=416
```

この事象は今回のヘッダー変更で生じたものではない。2026-07-11撮影の公開画像 `04_Documentation/assets/screenshots/mobile-toolbar-smoke-390.png` にも同じ切れ方が写っており、以前から存在する。

## 対応方針

- 実施すること: 390pxで検索欄と状態フィルタの左端が画面内に収まるようにする。`justify-content` を `flex-start` にする、行を折り返す、狭幅では検索欄を別行に落とす、などのうち複雑性予算に見合う方法を選ぶ。
- 実施しないこと: 検索・状態フィルタの機能変更。1440px時のレイアウト変更。

### 採用判断

中央コンテナを左揃え・`min-width: 0`にし、検索行自身を狭幅時だけ自然に折り返す。要素や操作を増やさず、390pxでは到達不能な左右クリップをなくし、十分な幅では従来の一行配置を保つ。

## 予算申告

- 複雑性予算（`ADR-0043` CB-1）: 狭幅で行が増える案を選ぶ場合、初期表示の縦方向が増える。表示要素そのものは増やさない。
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [x] 390pxで、検索欄・「状態フィルタ」・「非一致を非表示」がいずれも viewport 内に収まる（`left >= 0` かつ `right <= viewport幅`）。
- [x] 768px / 960px / 1440px のレイアウトが退行しない。
- [x] 切れが残る要素がある場合は、スクロールなど到達手段がある。
- [x] 公開画像 `mobile-toolbar-smoke-390.png` を `DOC-SHOT-01` の再撮影に合わせて更新する。

## 検証計画

- 実行する確認: 代表4幅（390 / 768 / 960 / 1440）で、ヘッダー内の可視要素の矩形が viewport に収まることを確認するE2E。既存の `header_toolbar_layout.spec.ts` / viewport系E2E。
- 期待結果: 4幅すべてで見切れ0件。既存E2Eに退行なし。

## 検証結果

- `header_toolbar_layout.spec.ts` を含む近接E2E 19件成功。390 / 768 / 920 / 1280 / 1440pxでヘッダー検索行の可視要素がviewport内に収まることを矩形で確認した。
- `ui-responsive-768.png` / `ui-responsive-960.png` / `mobile-toolbar-smoke-390.png` を再生成し、目視で退行と見切れがないことを確認した。
- frontend全体のVitest 1324件、typecheck、build、docs-checkが成功した。

## 補足

- `header` 自身は `flex-wrap: wrap` で折り返しているが、切れているのは内側の `overflow-x: hidden` + `justify-content: center` のコンテナであり、折り返しの対象になっていない。
- 調査記録: `03_Implement/frontend/docs/mvp_exit_monkey_test_log_2026-07-29.md`
