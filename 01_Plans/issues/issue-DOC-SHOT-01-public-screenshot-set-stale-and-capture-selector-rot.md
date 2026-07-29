# Issue: DOC-SHOT-01 公開画像セットのstaleとcapture scriptのselector腐り

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Documentation
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `MVP-EXIT-01`
- Priority: P1
- Owner: Maintainer
- Scope: `04_Documentation/assets/screenshots/`, `03_Implement/frontend/scripts/`
- Related ADR/Spec: `04_Documentation/assets/screenshots/README.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
- Expected verification level: `docs-check`

## 課題

- 現在の問題:
  - **(A) 公開画像がstale。** ヘッダーに「サポート診断バンドル」ボタンが追加されたが、公開中のスクリーンショットに反映されていない。再撮影で比較した `app-canvas-overview` / `selection-context-card` / `share-export-safe-mode` / `start-document-entry` / `mobile-toolbar-smoke-390` / `product-value-first-island` のすべてで再現。ヘッダーを含む `ui-*.png` も同じ理由でstaleと推定する。390pxではヘッダーの折り返しが2行から3行へ変わるため、レイアウトの説明も影響を受ける。provenance記録上の対象revisionは `1367740d...`（2026-07-11）。
  - **(B) 再撮影手段が壊れていた。** `capture_release_screenshots.mjs` / `capture_ui_catalog.mjs` / `capture_product_value_screenshots.mjs` がキャンバス上のカードを `getByRole("option")` で選択していたが、現行実装のカードは `aria-pressed` を持つ `button`（`ADR-0052` のcanvas card移行後）。3本とも実行途中で停止していた。
- 利用者または開発への影響: 公開文書の画面説明が実画面と一致しない。`PRODUCT-QA-01` G5 の No-Go条件「古いUIを公開する」に該当し、`MVP-EXIT-01` の出荷判断を止めている。(B) により、staleに気づいても直せない状態が続いていた。

## 対応方針

- 実施すること:
  - (B) を修正する（対応済み: 3本のselectorを `button` へ変更。release 5/5、product-value 6/6の生成成功を確認）。
  - (A) を、S2修正（`UI-QUALITY-A11Y-07`）をcommitしたうえで正本環境から再撮影し、README のprovenance行を更新する。
  - 再撮影後に、画像の秘密情報・表示ラベル・SafeMode境界を目視確認する。
- 実施しないこと:
  - 未commitのUI変更から撮影すること（README の撮影provenance規定に反する）。
  - ヘッダーのボタン構成そのものの変更（`DOC-IA-01` で扱う）。

## 予算申告

- 複雑性予算（`ADR-0043`）: N/A
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [x] capture script 3本が現行UIに対して最後まで実行できる。
- [ ] 公開画像23件が候補commitのUIと一致する。
- [ ] `04_Documentation/assets/screenshots/README.md` のprovenance行（対象revision、撮影日、browser、生成結果）が更新されている。
- [ ] 再撮影した画像に秘密情報が含まれないことを目視確認する。

## 検証計画

- 実行する確認:

```bash
cd 03_Implement/frontend
node ./scripts/capture_release_screenshots.mjs
node ./scripts/capture_product_value_screenshots.mjs
node ./scripts/capture_ui_catalog.mjs
```

- 期待結果: 5/5、6/6、12/12の生成成功。生成物とヘッダー構成が現行UIと一致する。

## 補足

- selector腐りは、公開画像の生成をCIから外していると検出できない。「文書に載る画像を生成するscriptが動くこと」だけでも定期実行の対象にするか検討する。
- 詳細な調査記録は `03_Implement/frontend/docs/mvp_exit_human_acceptance_log_2026-07-29.md` §3。
