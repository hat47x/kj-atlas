# Issue Draft: QA-MONKEY-13 Alt+Shift+2（構造レベル「中間」）ショートカットが「概要」を適用してしまう

- Type: Bug
- Status: Done
- Source Issue: `DX-E2E-07`（e2e契約再照合バッチの検証中に発見。テスト側のドリフトではなく実挙動のバグと判定しT4に基づき分離）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/App.tsx`（Alt+Shift+1/2/3 構造レベルショートカットのkeydownハンドラ、`handleHierarchyLevelChange`）
- Related Backlog: `QA-MONKEY-13`
- Related ADR/Spec: `01_Plans/issues/issue-DX-E2E-07-current-ui-contract-drift-batch.md`
- Expected verification level: `e2e`

## 背景

`DX-E2E-07`（e2e契約再照合バッチ）の一環として `e2e/header_toolbar_layout.spec.ts` の "modifier shortcuts update visible view and hierarchy state" を実ブラウザ（Docker Playwright）で再検証したところ、構造レベルショートカット（Alt+Shift+1/2/3 → 概要/中間/詳細）のうち **Alt+Shift+2（「中間」への切替）だけが一貫して失敗する**ことを発見した。他の2つのdrift（`aria-pressed`欠落、メニュー移動）を修正した後もこの1点だけが再現し続けたため、テスト側のドリフトではなく製品コード側の実バグと判断した。

## 再現手順と証拠

サンプル文書を開き（`page.goto("/")`のみ、Advanced UI等は不要）、「表示」パネルを開いて構造レベルのselect（`view_controls.hierarchy.*`）の値を監視しながら:

1. `Alt+Shift+1` → select値が `overview` になる（正しい）。
2. `Alt+Shift+2` → select値が **`overview`のまま変化しない**（期待値は `mid`）。
3. `Alt+Shift+3` → select値が `detail` になる（正しい）。
4. 続けて再度 `Alt+Shift+2` を押す（現在値は`detail`）→ select値が **`overview`になる**（期待値は`mid`）。

`window`にcapture段階でkeydownロガーを仕込んで確認したところ、いずれの押下でも `event.key`・`event.altKey`・`event.shiftKey`・`event.defaultPrevented` は正しく観測される（例: `key=2 alt=true shift=true defaultPrevented=false`）。つまりキーイベント自体は正しく発火・到達しているが、`App.tsx`側の該当分岐（`event.key === "2"` → `handleHierarchyLevelChange("mid")`）を経由した結果が、**常に`handleHierarchyLevelChange("overview")`を呼んだ場合と同じ状態**に帰着する。

## 除外した仮説（再現検証で否定済み）

- `maxDepthForHierarchyLevel("mid")` / `resolveHierarchyLevel` の純粋関数バグ → 否定（`hierarchy_level.test.ts`で`maxDepthForHierarchyLevel("mid") === 1`をユニットテスト済み、かつ実装を目視確認済み・正しい）。
- `<option value="mid">` がDOMに存在しない → 否定（`ViewControlsPanel.tsx`に存在確認済み）。
- キーイベント自体が発火しない、または`defaultPrevented`により早期returnしている → 否定（captureフェーズでの直接ロギングにより、正しい属性で確実に発火していることを確認済み）。
- select要素へのフォーカスにより`isEditableHotkeyTarget`が早期returnしている → 否定（select要素にフォーカスを当てる操作は行っていない）。
- 「2回目以降のショートカット呼び出しは一般的に失敗する」という一般化 → 否定（`Alt+Shift+3`は`Alt+Shift+1`の直後でも正しく`detail`になる。問題は**特定の`Alt+Shift+2`のみ**で再現する）。

## 未解明の点（次の一手）

- `App.tsx`の`handleKeyDown`（構造レベル用、~9419-9438行）の`event.key === "2"`分岐自体は目視で正しく見えるため、**別の箇所に"2"を`"overview"`相当の効果にマッピングしてしまう重複ハンドラ、または`handleHierarchyLevelChange`呼び出し経路の分岐ミスが存在する可能性**が高い。React DevTools（またはReactの状態更新に対する一時的な計装）で、`Alt+Shift+2`押下時に`handleHierarchyLevelChange`へ実際に渡される引数値を直接ログ出力し、`"mid"`が渡されているのに結果が`"overview"`になるのか、それとも呼び出し自体で`"overview"`が渡されてしまっているのかを切り分けること。
- 同ファイル内の他のCtrl/Meta系ショートカット（`handleApplyViewMode`、~9385-9391行）との干渉可能性も完全には排除できていない（条件チェック上は干渉しないと判定したが、実装調査時に再確認のこと）。

## 受け入れ条件（案）

- [x] AC-1: 根本原因を特定する（下記「対応記録」参照）。
- [x] AC-2: `Alt+Shift+2`が構造レベルを`mid`へ正しく切り替えるよう修正する。
- [x] AC-3: `Alt+Shift+1`/`Alt+Shift+3`の既存の正しい挙動が回帰しないことを確認する（フルe2eスイート 165/165 で確認済み）。
- [x] AC-4: `e2e/header_toolbar_layout.spec.ts`の "modifier shortcuts update visible view and hierarchy state" が実ブラウザで完走する（テスト自体は変更していない -- 元のアサーションがそのまま正しい仕様を反映していた）。

## 対応記録（2026-07-15）

**根本原因**: `App.tsx`に3箇所の`setHierarchyLevel`呼び出しがあり、うち2つが競合していた。

1. `handleHierarchyLevelChange(level)`（ユーザー操作の唯一の入口 -- ショートカット・ドロップダウン・ボタン群すべてがこれを呼ぶ）は `setHierarchyLevel(level)` と `setMaxDepth(maxDepthForHierarchyLevel(level))` を同時に呼ぶ。`mid` の場合 `maxDepth = 1`。
2. 別の `useEffect`（依存配列 `[maxAvailableDepth, maxDepth]`）が「`maxDepth` が `maxAvailableDepth`（文書内の島の最大ネスト深さ）を超えていたら切り詰める」処理を行う。検証に使ったテスト文書は島が0件（`islands: []`）のため `maxAvailableDepth = 0`。`maxDepth = 1 > 0` が真となり、`setMaxDepth(0)` が発火してしまう。
3. さらに別の `useEffect`（依存配列 `[maxDepth]`）が「`maxDepth` が変化するたびに `hierarchyLevel` を `resolveHierarchyLevel(maxDepth)` で再導出する」処理を行う。上記2.の`setMaxDepth(0)`により再度この effect が発火し、`resolveHierarchyLevel(0)` = `"overview"` として `hierarchyLevel` を上書きしてしまう。

結果として、ユーザーが明示的に選んだ `"mid"` が、文書に深い島が1つも無い場合に限り、2段階のeffect連鎖によって静かに `"overview"` へ書き換えられていた。`"overview"`（`maxDepth=0`）と `"detail"`（`maxDepth="all"`、切り詰めeffectが早期returnする）は、この切り詰め条件に該当しないため正しく動作していた。

事象の再現手順（`console.log`によるライブ計装で確認）:
- `handleHierarchyLevelChange("mid")` は正しく呼ばれ、`setHierarchyLevel("mid")` / `setMaxDepth(1)` を実行 -- ここまでは正常。
- 直後に切り詰めeffectが `setMaxDepth(0)` を発火。
- その`maxDepth`変化を受けて同期effectが `setHierarchyLevel("overview")` を発火 -- ここでユーザー選択が上書きされる。

**修正**: `03_Implement/frontend/src/App.tsx` の切り詰めeffectの条件に `&& maxAvailableDepth > 0` を追加した。`maxAvailableDepth === 0` は「深さ1以上にネストした島が1つも無い（島が0件、または全島が最上位のみ）」ことを意味し、この場合 `maxDepth=1` と `maxDepth=0` は表示結果に違いを生まない（切り詰める対象の内容が実在しない）ため、切り詰め自体が不要かつ有害（ユーザーの明示的な選択を無言で覆す）と判断した。`hierarchyLevel`をmaxDepthから再導出する同期effect自体は温存した（数値の深さセレクタを直接操作した場合に3段階の簡易表示を追従させる、別の意図された挙動のため）。

**検証**: `tsc --noEmit` クリーン。Vitest 190/190ファイル・1034/1034テスト green（`hierarchy_level.test.ts`含む既存の純粋関数テストは無変更で通過）。フルPlaywrightスイート再実行: **165/165 全件 green**（今セッション初のフルスイート完全green）。`e2e/header_toolbar_layout.spec.ts`の対象テストを含む9件すべて再確認済み。

## Traceability

- Derived-from: `01_Plans/issues/issue-DX-E2E-07-current-ui-contract-drift-batch.md`（e2e契約再照合バッチの検証中に発見、T4に基づき分離）
- Related: `03_Implement/frontend/e2e/header_toolbar_layout.spec.ts`（"modifier shortcuts update visible view and hierarchy state"）
- Related: `03_Implement/frontend/src/domain/view/hierarchy_level.ts`, `03_Implement/frontend/src/domain/view/hierarchy_level.test.ts`
