# Issue: UI-CANVAS-01 折りたたみ島のピーク操作がwindowリスナーに依存し、蓄積・固着しうる

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/IslandView.tsx`, `03_Implement/frontend/src/canvas/CanvasShell.tsx`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題:
  - `IslandView.tsx:561-572` の折りたたみ島「ピーク」ボタンの `onPointerDown` は、`window.addEventListener("mouseup", () => { onPeekEnd?.(); }, { once: true })` という生のリスナーを、`useEffect` の外・参照追跡なしで直接登録している。
  - `CanvasShell.tsx`（`event.currentTarget.setPointerCapture(event.pointerId)` を `onPointerDown`系ハンドラで呼び、`onPointerUp`/`onPointerCancel` の両方をJSX上で明示的に配線する、`releasePointerCapture`とセットの方式）が、同種のドラッグ/ホールド操作に対して確立しているパターンと異なり、この箇所だけ `"mouseup"` イベント一発・`{ once: true }` だけに依存している。
  - `"mouseup"` は、タッチ操作が途中でスクロールに移行した場合（ブラウザは `pointercancel` を発火し、`mouseup` は発火しない）や、何らかの理由で `mouseup` が `window` まで届かないケースでは発火しない。`{ once: true }` は「発火したら自動的に外れる」だけであり、発火しなければ永久にリスナーが残る。
- 利用者または開発への影響:
  - 上記の条件でピーク操作を行うたびに、`onPeekEnd` を閉じ込めた `window` リスナーが1つずつ蓄積し、セッションの残り期間中ずっと解放されない（ページを開いたまま繰り返し操作するほど蓄積する）。
  - 加えて、対応する `onPeekEnd?.()` が呼ばれないため、アプリ側の `isPeeking` 相当の状態が固着したままになる可能性がある。

## 対応方針

- 実施すること（人間の設計判断が必要）:
  - `CanvasShell.tsx` が既に確立している `setPointerCapture`/`onPointerUp`/`onPointerCancel` パターンに合わせて、このピーク操作を再設計する。具体的には、`onPointerDown` で `event.currentTarget.setPointerCapture(event.pointerId)` を呼び、同じ要素に `onPointerUp`/`onPointerCancel` の両方を配線して `onPeekEnd?.()` と `releasePointerCapture` を呼ぶ形に置き換えることが有力な方向性だが、ピーク操作特有のUX（ボタン外に指/カーソルが移動した場合の扱い等）を踏まえた設計判断が必要なため、単純な一行修正では済まない。
- 実施しないこと:
  - ピーク機能自体のUX変更（表示内容やトリガー条件の変更）。

## 受入条件

- [x] タッチのスクロール移行や `mouseup` がwindowに届かないケースを含め、ピーク操作のたびに `window` リスナーが確実に解放される。→ `IslandView.tsx` のピークボタンが `window.addEventListener("mouseup", ..., { once: true })` を**廃止**し、`CanvasShell` と同じ `setPointerCapture` + `onPointerUp` / `onPointerCancel` へ移行（2026-08-15）。window リスナーを一切登録しないため、蓄積は構造的に起きない。
- [x] `onPeekEnd` が呼ばれずに `isPeeking` 相当の状態が固着するケースがなくなる。→ `onPointerCancel` が `onPeekEnd?.()` を呼ぶ（`mouseup` が発火しない touch→scroll 移行も解除）。App 側 `handleIslandPeekEnd` → `setPeekIslandId(undefined)` へ正しく連鎖することを確認。
- [x] 関連する安全・互換性を損なわない。→ App 側の補助 `mouseup` リスナー（`App.tsx:6639`）は `useEffect` 内で `removeEventListener` 付きのため無害なまま。full suite 1451 tests・typecheck pass。
- [x] 宣言した検証を実行するか、未実施理由を記録する。→ **自動化の未実施理由を記録**: vitest 環境は `node`（jsdom 未導入・testing-library 未使用）のため、pointer イベントの対話的単体テストは現行基盤では不可。代わりに (a) 構造的検証（window リスナー登録の消滅＝蓄積不可能）と (b) 全suite回帰（1451 tests pass）で固定した。対話的検証は将来 jsdom/Playwright のピークE2Eで補う。

## 検証計画

- 実行する確認:
  - ピーク操作を複数回行った後に `window` のイベントリスナー数が増え続けないことを確認する単体テスト（可能であれば）、またはブラウザでの手動確認（ピーク→タッチスクロールで中断→再度ピーク、を繰り返し `isPeeking` が固着しないことを確認）。
- 期待結果:
  - リスナーが蓄積せず、`isPeeking` が正しく解除される。
- 実績（2026-08-15）: 上記 AC-4 の通り、構造的検証＋full suite 1451 tests pass で固定。対話的ピークE2Eは既存E2E群のピークカバレッジ拡張として将来課題。

## 補足

- 依存・リスク・ロールバックがある場合だけ記載する。
  - この所見は3体の独立検証者のうち2体がセッション接続エラーで失敗した調査から得られたが、該当コード（`IslandView.tsx:561-572`）と比較対象パターン（`CanvasShell.tsx`の`setPointerCapture`関連4箇所）はorigin/mainのソースを直接読んで確認済み。

---
