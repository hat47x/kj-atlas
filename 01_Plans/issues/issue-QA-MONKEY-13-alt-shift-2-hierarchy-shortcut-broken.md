# Issue Draft: QA-MONKEY-13 Alt+Shift+2（構造レベル「中間」）ショートカットが「概要」を適用してしまう

- Type: Bug
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
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

- [ ] AC-1: 根本原因を特定する。
- [ ] AC-2: `Alt+Shift+2`が構造レベルを`mid`へ正しく切り替えるよう修正する。
- [ ] AC-3: `Alt+Shift+1`/`Alt+Shift+3`の既存の正しい挙動が回帰しないことを確認する。
- [ ] AC-4: `e2e/header_toolbar_layout.spec.ts`の "modifier shortcuts update visible view and hierarchy state" が実ブラウザで完走する（テスト自体の変更は不要 -- 現状のアサーションは正しい仕様を反映している）。

## Traceability

- Derived-from: `01_Plans/issues/issue-DX-E2E-07-current-ui-contract-drift-batch.md`（e2e契約再照合バッチの検証中に発見、T4に基づき分離）
- Related: `03_Implement/frontend/e2e/header_toolbar_layout.spec.ts`（"modifier shortcuts update visible view and hierarchy state"）
- Related: `03_Implement/frontend/src/domain/view/hierarchy_level.ts`, `03_Implement/frontend/src/domain/view/hierarchy_level.test.ts`
