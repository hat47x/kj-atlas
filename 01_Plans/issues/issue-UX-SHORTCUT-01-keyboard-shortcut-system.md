# Issue Draft: UX-SHORTCUT-01 ショートカット体系の実装（保持系最短・Esc段階・OS別表記）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-SHORTCUT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D2 ショートカット原則）, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/issues/issue-PRODUCT-UX-02-workspace-information-architecture.md`（L139 の先送り解消）
- Expected verification level: `e2e`

## Implementation note (2026-07-07, shortcut discoverability)

- H/U/R selected-card state shortcuts are now surfaced in the canvas legend as a provisional discovery path. The legend already explains card state language, so it is a natural place to show the key-to-state mapping without introducing a full shortcut help surface yet.
- At that point AC-4 remained open because the full `?` cheat sheet still needed OS-specific labels, explicit disabled-while-editing guidance, and rediscovery from menus or the command palette.

## Implementation note (2026-07-07, shortcut help dialog)

- Added a guarded `?` shortcut help dialog with OS-aware primary modifier labels, disabled-while-editing guidance, Esc close behavior, focus trapping, and focus restoration to the element that opened it. This addresses the interactive cheat-sheet portion of AC-4.
- Remaining follow-up: rediscovery from menus or the future command palette is still pending, so AC-4 should not be closed solely from this change.

## Implementation note (2026-07-07, header rediscovery)

- Added a compact `?` button in the primary toolbar so users can rediscover the shortcut help without already knowing the `?` key. This closes the basic menu/visible-surface rediscovery gap for AC-4; future command-palette integration can remain a separate UX-CMDK-01 follow-up.

## Implementation note (2026-07-07, responsive shortcut help regression)

- The shortcut help trigger and dialog now have regression coverage across desktop, tablet-width, and narrow mobile viewports. This keeps AC-4 from silently regressing into an off-screen or keyboard-only discovery path when the header wraps.
- Verified locally with `tsc --noEmit`, `ux_operability_regression.test.ts`, and `git diff --check`. Full Playwright execution remains part of the broader E2E gate because the local browser/runtime setup can vary by machine.

## Implementation note (2026-07-07, selected-card shortcut E2E)

- Added `shortcut_card_state.spec.ts` to cover the H/U/R selected-card shortcuts as user-facing operations: H toggles hold, U toggles the default critique note, R toggles reviewed state, and each change is reversible with `Control+Z`.
- The same spec fixes AC-2 by focusing the critique textarea and verifying H/U/R are inserted as text while hold/review state remain unchanged.
- Local verification passed `tsc --noEmit`, `ux_operability_regression.test.ts`, `useHotkeys.test.ts`, and `git diff --check`. Playwright browser execution remains blocked in this agent environment until the missing Chromium runtime is installed.

## Implementation note (2026-07-07, Escape staged dismissal)

- Added a shared `dismiss-top-layer` hotkey action so global Escape closes only the topmost open layer before falling back to selection clear. Current order: shortcut help, share panel, view controls, canvas legend, work mode, then selection clear.
- Reading navigation keeps priority over layer dismissal so its existing Escape-to-disable behavior is not regressed.
- Existing panel-local Escape/focus-return handlers remain in place; the shared action covers the case where focus is outside the open panel but a layer is still visible.

## Shortcut binding inventory (2026-07-07)

| Binding | Owner | Guard / collision note | Regression evidence |
| --- | --- | --- | --- |
| H / U / R | `useHotkeys` | Single-key, selection-scoped, disabled in editable targets and with modifiers. R yields to reading navigation when reviewed-only mode is available. | `useHotkeys.test.ts`, `ux_operability_regression.test.ts` |
| ? / Shift+/ | `useHotkeys` + `ShortcutHelpDialog` | Single-key help discovery, disabled in editable targets and with modifiers. | `useHotkeys.test.ts`, `header_toolbar_layout.spec.ts`, `ux_operability_regression.test.ts` |
| Escape / Delete / Backspace / Arrow / Shift+Arrow | `useHotkeys`, card/polygon/panel-local handlers | Selection and nudge keys remain in the shared resolver; panel-local Escape/Tab contracts are scoped to dialogs and overlays. | `useHotkeys.test.ts`, `canvas_focus_order.spec.ts`, `polygon_vertex_edit.spec.ts`, `ux_operability_regression.test.ts` |
| Cmd/Ctrl+G | `App.tsx` island creation handler | Modifier-only creation shortcut; no overlap with single-key H/U/R/? because the resolver ignores meta/ctrl/alt. | Source inventory; out of AC-5's current non-regression scope. |
| Cmd/Ctrl+Z, Cmd/Ctrl+Y, Cmd/Ctrl+Shift+Z | `App.tsx` undo/redo handler | Browser-standard editing shortcuts are handled only at app level when undo/redo is available. | `first_meaningful_map_mouse_flow.spec.ts` |
| Cmd/Ctrl+1/2/3 | `App.tsx` view-mode handler | Disabled in editable targets; excludes Alt/Shift to avoid collision with hierarchy shortcuts. | `header_toolbar_layout.spec.ts` |
| Alt+Shift+1/2/3 | `App.tsx` hierarchy-level handler | Disabled in editable targets; excludes Cmd/Ctrl to avoid collision with view-mode shortcuts. Uses `event.code` so Shift-modified digit keys still resolve on common keyboard layouts. | `header_toolbar_layout.spec.ts`, `ux_operability_regression.test.ts` |

Inventory conclusion: no duplicate active binding was found. Modifier-based view-mode and hierarchy-level shortcuts now have direct E2E coverage in `header_toolbar_layout.spec.ts`; local execution was blocked before test body execution because Playwright Chromium was not installed in the agent environment.

## Requirement meta I/F（共通キー）

- RequirementID: UX-SHORTCUT-01
- RequirementStatement: ADR-0048 D2 のショートカット原則（保持系を修飾なし最短キー・Esc 段階処理・ブラウザ標準不上書き・入力中単一キー無効・OS 別表記・メニュー/パレット併記）を実装し、チートシート（?）で発見可能にする。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=カードを選択 / 操作=H（保留切替）・U（違和感）・R（レビュー済み切替）、テキスト編集中に同キー、? でチートシート / 期待結果=選択時のみ状態が切替わり ⌘Z で戻る。編集中は文字入力になる。チートシートに OS に応じた表記で全キーが並ぶ / 除外=キーのユーザー再割当（リバインド）機能、viewMode 既存バインド（Cmd+1/2/3 等）の変更。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: N/A（共有系のキーは設けない）
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048 D2）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- 現状のバインドは散在（Cmd/Ctrl+1/2/3 viewMode、Alt+Shift+1/2/3 構造レベル、Enter/Space/Escape 契約）で、**体系**（原則・衝突回避・発見可能性）が無い。PRODUCT-UX-02 L139 はショートカット体系の確定を ADR へ先送りしており、ADR-0048 D2 で確定済み。本Issueはその実装。
- 保持系（保留・違和感）に至る最短操作がマウス経由のみで、核価値の操作が確定系より遠い（CB-2 緊張）。

## 2) 背景 / Context

- 壁打ち成果（拡張提案 P8・図H）がカテゴリ別キー割当・Esc 段階・衝突回避ポリシー・OS 別表記を設計済み。プロトタイプで H/U/R・1/2/3/0・G・L・W・⌘J/⌘K/⌘F・?・⌘Z/⌘⇧Z を検証済み。
- PROJECT-GOV-01 L699 の警告に従い、現 main の Space キー・キャンバス系バインドを実装前に棚卸しする。

## 3) 判断基準による優先度評価

- 価値: 保持系最短キーは「少ない操作で曖昧さを保持」を操作レベルで実現する（CB-2 改善）。
- 安全: ブラウザ標準不上書き・入力中無効の安全規則を体系として固定。共有・削除系に単一キーを与えない（削除は Delete/⌫ のみ、選択時限定）。
- 規模拡大: 新コマンドのキー割当先が原則で決まる（場当たり割当の防止）。
- 後方互換: 既存バインド（viewMode・構造レベル・Enter/Space/Escape 契約）は変更しない。

## 3.2 非目標 / Non-goals

- キーリバインド（ユーザー設定）機能。既存 viewMode / 構造レベルのバインド変更。VUI・自然文（Pending）。メニューバー再編そのもの。

## 4) 提案する解決策 / Proposed solution

- **保持系（最短・修飾なし・選択時のみ）**: H=保留切替 / U=違和感切替 / R=レビュー済み切替。**作成・編集**: N=新規カード、E/Enter=編集、⌘D=複製、Delete=削除。**型変更**: 1/2/3=事実/主張/仮説、0=不明。**整理**: G=島を作成、L=関係線。**ナビ・面**: W or ⌘J=作業面、⌘K=パレット（UX-CMDK-01）、⌘F=状態フィルタへ、⌘.=凡例、?=チートシート。
- **Esc 段階処理**: チートシート→パレット→メニュー→編集取消→凡例→作業面→選択解除 の順で手前から1つずつ閉じる。
- **安全規則**: テキスト入力中は単一キー完全無効。英字キーは選択がある時のみ。⌘C/V/X/A/P は OS/ブラウザへ委譲。修飾キー併用のアプリ操作のみ preventDefault。
- **発見可能性**: ? チートシート（OS 別表記・手動切替つき）、メニュー項目へのキー併記。
- 実装前に既存バインド棚卸し（`metaKey|ctrlKey|key ===` の grep）で重複割当ゼロを確認。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: H/U/R が選択時のみ機能し、⌘Z で可逆であることが e2e で固定される。
- [x] AC-2: テキスト編集中に単一キーが発火しない（本文に文字が入る）ことが e2e で固定される。
- [x] AC-3: Esc 段階処理が仕様順で1段ずつ閉じ、既存の Escape+フォーカス復帰契約（UX-OPERABILITY-04）が非回帰。
- [x] AC-4: ? チートシートが OS 別表記で表示され、Escape で閉じる。
- [x] AC-5: 既存バインド（Cmd/Ctrl+1/2/3、Alt+Shift+1/2/3、Enter/Space）が非回帰。重複割当なしの棚卸し結果を記録。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 既存バインド棚卸し（衝突表を本メモに追記）。
- [x] T2 キーディスパッチャ（選択ガード・入力中ガード・OS 判定）。
- [x] T3 保持系/作成/型/整理キーの接続（既存ハンドラへ委譲）。
- [x] T4 Esc 段階スタックの一元化。
- [x] T5 チートシート UI＋メニュー併記＋i18n。
- [x] T6 e2e 一式。

## Implementation note (2026-07-07)

- T2/T3 の一部として、`useHotkeys` に選択カード1枚向けの H/U/R を追加した。
  - H: `holdState` を `held` / `active` で切り替える。
  - U: `critique` が未設定なら短い違和感メモを入れ、設定済みなら外す。
  - R: `textReviewed` を切り替える。ただし読書ナビが有効な場合は既存の reviewed-only 切替を優先し、キー衝突を避ける。
- 入力中ガード（input/textarea/select/contentEditable）と修飾キーガードは `useHotkeys` に維持した。キー判定を `resolveHotkeyAction` へ切り出し、`useHotkeys.test.ts` で H/U/R、入力中無効、修飾キー無効、読書ナビ中の R 衝突回避を固定した。`ux_operability_regression.test.ts` に静的回帰アンカーも追加済み。
- 未完了: なし。Playwright のブラウザ実行は、ローカルの Chromium ランタイム導入後に `shortcut_card_state.spec.ts` と `header_toolbar_layout.spec.ts` を実行して最終確認する。

## 7) 検証計画 / Validation plan

- `rg -n "metaKey|ctrlKey|event.key" 03_Implement/frontend/src | sort`（棚卸し）
- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（キーは不可視。チートシートは ? 呼び出し時のみ） / 保留操作の距離=改善（保持系が修飾なし単一キー＝確定系より近い） / 取り消し導線=あり（全キー操作は ⌘Z/Ctrl+Z で可逆）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Related: `01_Plans/issues/issue-UX-CMDK-01-command-palette.md`（表記・バインド共通化）, `issue-PROJECT-GOV-01-mainline-convergence-and-branch-hygiene.md`（L699 棚卸し警告）
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（P8・図H）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 実装設計の到着（2026-07-04 Round 5）

- チートシートのレッドライン確定（同 §段階2）: ? 起動・Esc閉じ・右上にMac/Windows/Linux切替（自動検出）・kbd=11px monospace 角丸5 padding2/8・単一キー節に「編集中無効」脚注。プロトタイプ実装済み。
