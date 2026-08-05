# Issue: QA-MONKEY-16 未レビュー標識のaria-labelが禁止属性で、カード名に状態が混入する

- Type: Bug
- Status: Done
- Source Issue: `MVP-EXIT-01`（人間受入項目の機械代替検証後に実施したモンキーテストで発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/CardView.tsx`
- Related Backlog: `QA-MONKEY-16`
- Related ADR/Spec: `04_Documentation/acceptance_check.md`, `01_Plans/issues/issue-QA-MONKEY-14-island-editor-fields-unlabeled-axe-critical.md`
- Expected verification level: `e2e`

## 課題

カード右上の未レビュー標識（琥珀色の点）は、role を持たない `<span>` に `aria-label` を付けて状態を伝えている。

```tsx
// src/canvas/CardView.tsx
<span
  aria-label={t("card_view.unreviewed")}
  title={t("card_view.unreviewed")}
  style={{ position: "absolute", top: 6, right: 6, width: 7, height: 7, ... }}
/>
```

ARIAでは、暗黙のroleが `generic` の要素に対する `aria-label` は禁止されている。これにより2つの症状が出る。

**症状1: カード本文の編集中にaxe違反となる。** インライン編集中はこの `<span>` が name-from-content を持つ祖先（カードの `button`）の外に出るため、axe が `aria-prohibited-attr`（impact `serious`）として検出する。

```
[1440px] カード選択なし: violations=0
[1440px] カード本文インライン編集中: violations=1
    [serious] aria-prohibited-attr x1 :: <span aria-label="カード本文は未レビューです" title="カード本文は未レビューです" ...>
[1440px] カードのコンテキストメニュー表示中: violations=0
```

**症状2: 通常表示ではカードのaccessible nameに状態が混入する。** 標識が `button` の内側にあるため、`aria-label` が name-from-content の一部として取り込まれ、カードの名前が状態＋本文の連結になる。

```
role=button name="カード本文は未レビューです 未レビューのカード"   ← 未レビューのカード
role=button name="レビュー済みのカード"                          ← レビュー済みのカード
```

つまり「カードの名前」がレビュー状態によって変わる。読み上げ上は状態が先に来るため状態自体は伝わるが、名前は対象の同一性を表すものであり、状態は `aria-describedby` などで別に伝えるのが本来の形である。名前で要素を指す操作（読み上げ後の呼び出し、名前指定のセレクタ）はレビュー状態の変化で不安定になる。

利用者への影響: 支援技術での聞こえ方が状態変化で揺れる。編集中は標識の情報が仕様上無効な経路に載っている。

## 再現手順

1. `?locale=ja` でアプリを開き、未レビューのカード（`textReviewed` を持たないカード）を含む文書を開く。
2. accessibility tree でそのカードの `button` の name を確認する → 状態文言が本文の前に連結されている。
3. そのカードをダブルクリックしてインライン編集に入り、axe（`wcag2a, wcag2aa, wcag21a, wcag21aa`）を実行する → `aria-prohibited-attr` が1件。

## 対応方針

- 実施すること: 状態を name ではなく説明として伝える形へ変える。たとえば標識に `role="img"` を与えて `aria-label` を正当化するか、標識を `aria-hidden="true"` にしてカード側から `aria-describedby` で状態テキストを参照する。どちらでも、状態が音声で伝わることは維持する。
- 実施しないこと: 未レビュー標識の見た目・位置の変更。レビュー状態そのものの仕様変更。

同じファイル内の `card_view.protected` バッジは `<span aria-hidden="true">` + テキストで構成されており、そちらは問題がない。方式をどちらかへ揃える。

## 予算申告

- 複雑性予算（`ADR-0043`）: N/A（表示変更なし）
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [x] インライン編集中のaxeで `aria-prohibited-attr` が0件になる。
- [x] 未レビューのカードの accessible name が本文のみになる。
- [x] 未レビュー状態が支援技術に伝わり続ける（name以外の経路で確認する）。
- [x] 既存E2Eのカード名指定（`getByRole("button", { name: ... })`）が退行しない。

## 検証計画

- 実行する確認: accessibility treeでのname確認、インライン編集中のaxe、`playwright test e2e/a11y_axe_smoke.spec.ts` と カード操作系E2E。
- 期待結果: 違反0件。nameは本文のみ。状態は説明として取得できる。

## 補足

- 既存E2Eがこの混入で落ちていないのは、Playwright の `name` オプションが既定で部分一致のため。`exact: true` を使う箇所が増えると顕在化する。
- `QA-MONKEY-14` と同じく、`a11y_axe_smoke.spec.ts` がインライン編集中の状態を走査していれば検出できた。走査状態の追加は `QA-MONKEY-14` 側で扱う。
- 調査記録: `03_Implement/frontend/docs/mvp_exit_monkey_test_log_2026-07-29.md`

## 実施結果（2026-08-02）

- 未レビュー状態をカード名から分離し、`aria-describedby` が参照する非表示テキストとして公開した。視覚的な琥珀色の点は `aria-hidden="true"` とし、見た目と位置は変更していない。
- 通常カードとインライン編集欄の双方で、名前は操作対象、説明は未レビュー状態という役割分担にした。遠距離マーカー表示では存在しない説明IDを参照しない。
- 実ブラウザでカード名 `unreviewed card body`、説明 `Card text is unreviewed`、編集欄名 `Edit card text` を確認した。
- 検証: `CardView.accessibility.test.ts` 11/11、専用E2E 1/1、axe smoke 10/10、full Vitest 228 files / 1329 tests、full Playwright 195/195、typecheck、本番build。
- 実装候補: `52860060c0ce3b1ed900c888e0a77263177df580`
