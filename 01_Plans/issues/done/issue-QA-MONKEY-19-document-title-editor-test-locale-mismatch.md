# Issue: QA-MONKEY-19 document-title-editor.spec.tsが`?locale=en`でも日本語プレースホルダーを期待し失敗する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `MVP-EXIT-01`（アドホック・モンキーテストで発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/e2e/document-title-editor.spec.ts`
- Related Backlog: `QA-MONKEY-19`
- Related ADR/Spec: `01_Plans/issues/done/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`（G3 日本語UI / G7 ビルドと回帰）
- Expected verification level: `e2e`

## 課題

`e2e/document-title-editor.spec.ts` の `"displays the document title and enters edit mode on click"` は `page.goto("/?locale=en")` で英語ロケールを指定しているにもかかわらず、新規文書のタイトルプレースホルダーが日本語 `"無題"` になることを期待している。

```ts
await page.goto("/?locale=en");
await page.getByRole("button", { name: "Create new document" }).click();
await expect(page.getByTestId("document-title-display")).toBeVisible();
await expect(page.getByTestId("document-title-display")).toHaveText("無題"); // ← 期待値が日本語
```

実際に実行すると、**製品側は正しく英語の `"Untitled"` を表示しており、テストの期待値だけが誤って日本語のまま**になっている。

```
Error: expect(locator).toHaveText(expected) failed
Locator:  getByTestId('document-title-display')
Expected: "無題"
Received: "Untitled"
  9 × locator resolved to <h1 title="Click to edit title" data-testid="document-title-display">Untitled</h1>
```

`DocumentTitleEditor.tsx` は `t("document_title.untitled")` を正しく使っており、`ja.json` は `"無題"`、`en.json` は `"Untitled"` で、両ロケールとも正しく定義されている。**製品コードに問題はなく、テストの期待値が古いか、当初から誤っていた**と判断する。

## 影響

- このテストは現状 **失敗する**。3件中1件が赤い状態でこのファイルは緑扱いになっていない。`PRODUCT-QA-01` G7（ビルドと回帰）の「変更リスクに対応するE2Eが成功する」を判定する際、このファイルが対象範囲に含まれる候補は正しく判定できない。
- 赤いテストが放置されると、今後このテストに触れる開発者が「英語ロケールなのに日本語を期待する」という誤った前提を踏襲しかねない。

## 対応方針

- 実施すること: 該当行の期待値を `t("document_title.untitled")` の英語値である `"Untitled"` に修正する。
- 実施しないこと: `DocumentTitleEditor.tsx` 側の変更（製品コードは正しいため不要）。

## 予算申告

- 複雑性予算（`ADR-0043`）: N/A
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [x] `document-title-editor.spec.ts` の3件すべてが成功する。
- [x] 同ファイル内の他の期待値（ロケールと表示文言の対応）に同種の不一致がないか確認する。

## 検証計画

- 実行する確認: `playwright test e2e/document-title-editor.spec.ts`。
- 期待結果: 3/3成功。

## 対応

`"無題"` を `"Untitled"` に修正した（`document_title.untitled` の `en.json` 値と一致）。同ファイルの他2テストは `?locale=en` を使っておらず、ロケールと文言の対応に同種の不一致は無いことを確認した。

## 検証結果（2026-08-13）

- `playwright test e2e/document-title-editor.spec.ts`: 3/3成功（修正前は1件失敗）。

## 補足

- `test defect` に分類する（`PRODUCT-QA-01` の重大度分類：製品欠陥ではなくテスト欠陥）。`DocumentTitleEditor.tsx` 側の実装は修正前から正しく、変更していない。
