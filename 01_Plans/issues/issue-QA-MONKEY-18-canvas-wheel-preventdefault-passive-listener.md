# Issue: QA-MONKEY-18 キャンバスのwheelズームがpassiveリスナー上でpreventDefaultを呼び、無効化される

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `MVP-EXIT-01`（アドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/CanvasShell.tsx`
- Related Backlog: `QA-MONKEY-18`
- Related ADR/Spec: `04_Documentation/acceptance_check.md`（マウスで確認すること）, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`（G2 主要操作）
- Expected verification level: `e2e`

## 課題

キャンバス上でマウスホイール／トラックパッドを操作するたびに、コンソールへ次のエラーが出る。

```
Unable to preventDefault inside passive event listener invocation.
```

`CanvasShell.tsx` のズームハンドラは JSX の `onWheel={handleWheel}` で登録されており、React は `wheel` イベントを既定で **passive** リスナーとして登録する。`handleWheel` の先頭で呼んでいる `event.preventDefault()` は、passiveリスナー内では黙って無効化される。

```tsx
// src/canvas/CanvasShell.tsx
const handleWheel = (event: WheelEvent<HTMLDivElement>) => {
  event.preventDefault(); // passiveリスナー内では効果を持たない
  ...
};
...
<div
  ...
  onWheel={handleWheel}
```

合成 `WheelEvent` を直接dispatchして確認したところ、`cancelable: true` であるにもかかわらず `defaultPrevented: false` のまま終わる。

```
dispatchEvent 後の状態: {"cancelable":true,"defaultPrevented":false}
```

利用者への影響: `acceptance_check.md` はマウスホイールでのズームを主要操作として明記していない（明示的な確認手順は無い）が、ズームはキャンバス操作の主要な入口の一つである。`preventDefault()` が効かないことで、ブラウザ既定のwheel挙動（トラックパッドでの2本指スクロールに伴うページスクロール、`Ctrl`+ホイールでのブラウザ全体のページズーム等）がアプリのズームと同時に発生しうる。今回のfixtureでは可視のページスクロールは確認できなかった（`body`がスクロール不可のため）が、コンソールエラー自体は主要操作のたびに確実に発生しており、診断ログや将来の厳格化（unhandled error監視等）に不要なノイズを残す。

## 再現手順

1. `?locale=ja` でアプリを開き、サンプル文書を開く。
2. キャンバス上へマウスを移動し、ホイールを1回動かす（`page.mouse.wheel(0, 200)` 相当）。
3. コンソールエラーを確認する。

観測結果: 単発のホイール操作で毎回上記エラーが出る。ズームの最小・最大クランプ自体（`MIN_ZOOM=0.2` / `MAX_ZOOM=4`）は正しく機能しており、ズーム量そのものは壊れていない。

## 対応方針

- 実施すること: `handleWheel` をJSXの `onWheel` から外し、`viewportRef` に対して `useEffect` 内で `addEventListener("wheel", handleWheel, { passive: false })` を使ってネイティブに登録する。クリーンアップで `removeEventListener` する。
- 実施しないこと: ズームの計算ロジック（`clamp`、`applyZoomAtScreenPoint`、感度）の変更。

## 予算申告

- 複雑性予算（`ADR-0043`）: N/A（表示・操作の変更なし、内部実装のみ）
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [x] キャンバス上でのホイール操作で `Unable to preventDefault inside passive event listener invocation.` が出ない。
- [x] 合成 `WheelEvent`（`cancelable: true`）をdispatchしたとき `defaultPrevented === true` になる。
- [x] 既存のズーム関連E2E（`responsiveness_performance_budget.spec.ts` 等、wheelを使うもの）に退行がない。
- [x] `MIN_ZOOM` / `MAX_ZOOM` のクランプが従来どおり機能する。

## 検証計画

- 実行する確認: 上記再現手順の再実行（console errorが出ないことを確認）、合成イベントでの `defaultPrevented` 確認、`vitest run`、対象E2E、typecheck。
- 期待結果: console error 0件、`defaultPrevented === true`、既存テストに退行なし。

## 対応

`03_Implement/frontend/src/canvas/CanvasShell.tsx` の `onWheel={handleWheel}`（JSX、React既定でpassive）を撤去し、`viewportRef` に対する `useEffect` 内で `addEventListener("wheel", handleWheelNative, { passive: false })` をネイティブ登録する形に変更した。クリーンアップで `removeEventListener` する。計算ロジック（`clamp`、`applyZoomAtScreenPoint`、`ZOOM_SENSITIVITY`）は変更していない。

## 検証結果（2026-08-13）

- 実際のマウスホイール操作（`page.mouse.wheel`）後のconsole error: 0件（修正前は毎回 `Unable to preventDefault inside passive event listener invocation.` が発生）。
- documentのbubbleフェーズで観測した実イベントの `defaultPrevented`: `true`（修正前 `false`）。`cancelable: true` は変わらず。
- ズームクランプの再確認: 初期カード幅比で ズームアウト後 `0.20`（`MIN_ZOOM`）、ズームイン後 `4.00`（`MAX_ZOOM`）と、修正前と同じ結果。
- `tsc --noEmit`: 新規エラーなし（既存の無関係な1件 `AppErrorBoundary.test.ts` は`DX-TYPECHECK-01`で別途起票、本変更とは無関係）。
- `vitest run`: 239 files / 1430 tests 成功（`src/canvas/` 8 files / 40 tests を含む）。
- `playwright test`: キャンバス・キーボード・ヘッダー・a11y系38 tests成功（`canvas_focus_order`, `canvas_protection`, `card_single_save_creation`, `first_meaningful_map_mouse_flow`, `island_tidy`, `minimap`, `a11y_axe_smoke`(10件), `large_document_operability`, `responsiveness_performance_budget`, `header_toolbar_layout`(9件), `hierarchy_level_persistence`, `keyboard_release_candidate_flow`, `retention_keyboard_shortcuts`(4件)）。

## 補足

- 発見はキャンバス操作を含む拡張モンキースイープ（drag / wheel-zoom / rubber-band select を追加したseed）で、`wheel-zoom` アクションの直後にのみ再現した。
- 同じ調査中に「カードを島の領域までドラッグして離すと1回のundoで元に戻る」（`acceptance_check.md` 手順6）を疑ったが、これは誤検知だった。ヘッダー分のスクリーン座標オフセットを考慮せずにドロップ座標を計算していたための計測ミスで、正しい座標で再検証したところ `moveCardToIsland` によるisland参加と1回のundoでの復元は正しく機能している。
