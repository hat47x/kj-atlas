# Issue Draft: UX-SHORTCUT-01 ショートカット体系の実装（保持系最短・Esc段階・OS別表記）

- Type: Feature request
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Claude Code
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-SHORTCUT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D2 ショートカット原則）, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/issues/issue-PRODUCT-UX-02-workspace-information-architecture.md`（L139 の先送り解消）
- Expected verification level: `e2e`

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

- [x] AC-1: H/U/R が選択時のみ機能し、⌘Z で可逆であることが e2e で固定される（`e2e/retention_keyboard_shortcuts.spec.ts`）。
- [x] AC-2: テキスト編集中に単一キーが発火しない（本文に文字が入る）ことが e2e で固定される。
- [x] AC-3: Esc 段階処理を検証（`e2e/esc_staged_closing.spec.ts`）。**設計判断の記録**: 既存の「各オーバーレイが自身の Escape で `preventDefault()` を呼び、`useHotkeys.ts` の window レベル listener が `event.defaultPrevented` で bail-out する」という規約が、フォーカスのあるサーフェスのみ閉じる段階処理を**既に実現**しているため、新規の中央集権的スタックは実装しない（非回帰・低リスクを優先）。UX-OPERABILITY-04 契約は不変。
- [x] AC-4: **Deferred（follow-up PR）**。? チートシートは別PRで実装する（本PRはH/U/R・入力ガード・Esc検証・棚卸しに限定）。
- [x] AC-5: 既存バインド（Cmd/Ctrl+1/2/3、Alt+Shift+1/2/3、Cmd/Ctrl+Z/Y/G、Enter/Space）が非回帰。T1 棚卸し結果は下記完了記録に記載。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 既存バインド棚卸し（衝突表を本メモに追記）。
- [ ] T2 キーディスパッチャ（選択ガード・入力中ガード・OS 判定）。
- [ ] T3 保持系/作成/型/整理キーの接続（既存ハンドラへ委譲）。
- [ ] T4 Esc 段階スタックの一元化。
- [ ] T5 チートシート UI＋メニュー併記＋i18n。
- [ ] T6 e2e 一式。

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

## 完了記録（1/2）2026-07-07（Claude Code）— H/U/R・入力ガード・Esc検証・棚卸し

### T1 既存バインド棚卸し（衝突表）

| キー | 既存 | 新規 | 判定 |
|---|---|---|---|
| Cmd/Ctrl+1/2/3 | viewMode 切替 | — | 非該当（修飾あり） |
| Alt+Shift+1/2/3 | 構造レベル切替 | — | 非該当（修飾あり） |
| Cmd/Ctrl+Z / Y | Undo/Redo | — | 非該当（修飾あり） |
| Cmd/Ctrl+G | 島を作成 | — | 非該当（修飾あり） |
| Cmd/Ctrl+K | コマンドパレット（UX-CMDK-01） | — | 非該当（修飾あり） |
| 平文 `n`/`p`/`r`（`useHotkeys.ts`） | 読み順ナビ（`readingNavEnabled` 時のみ） | `r`=レビュー済み切替 | **衝突を検出**。新規ハンドラを `!readingNavEnabled` でゲートし、読み順ナビ有効時は新旧どちらも同時に発火しない（相互排他）よう解消 |
| Delete/Backspace（`useHotkeys.ts`） | 選択削除（常時） | — | 非該当（対象キー差異） |
| 平文 `h`/`u` | なし | 保留切替／違和感クイックフラグ | 新規・衝突なし |

### 実装

- 新規 `window` keydown effect（`selectedCard` 定義直後）: 修飾キーなし・`isEditableHotkeyTarget`（Cmd+1/2/3 等と共用）で入力中を除外・`readingNavEnabled` で読み順ナビ中を除外・`selectedCard`（単一選択）が無ければ何もしない。
- **H**: `handleCardHoldStateChange(id, holdState==="held" ? "active" : "held")`（既存ハンドラ、CMDK と同一ロジック）。
- **U**: `handleCardCritiqueChange` を安全なトグルとして利用 — **既存の自由記述テキストは破壊しない**。空→クイックフラグ用の定型マーカー文言をセット、マーカー文言と一致→クリア、それ以外（ユーザーが自分で書いた文章）→**無変更（no-op）**。KJ法憲章「一枚一志」（原文の声を勝手に扱わない）に整合。
- **R**: `handleCardTextReviewedChange(id, !textReviewed)`。
- Esc 段階処理: 新規スタックは実装せず、既存の `preventDefault()` → `defaultPrevented` bail-out 規約が正しく機能することを e2e で確認・固定（設計判断は AC-3 参照）。

### 検証

- typecheck 0 / vitest **895 passed**（182 files。回帰アンカー1件追加）
- e2e 新規7件 passed: `retention_keyboard_shortcuts.spec.ts`（H可逆・U安全トグル・R切替・編集中無効化）／`esc_staged_closing.spec.ts`（パレット/凡例のEscでは選択が残る・無オーバーレイ時のEscは選択解除という既存挙動が非回帰）
- 既存の広範な e2e（`command_palette`・`canvas_legend`・`canvas_protection`・`card_meta_row`・`domain_expression_keyboard_access`・`keyboard_release_candidate_flow`）**14件で非回帰確認**
- 実機スクショで H→U→R 実行後のカード表示（メタ行「主張/保留/●」）・選択コンテキスト（保留:保留／違和感:違和感あり／レビュー状態:レビュー済み）を確認

### 残作業（follow-up PR）

- **AC-4: ? チートシート**（OS別表記・Esc閉じ・単一キー節「編集中無効」脚注）。Round 5 レッドライン確定済み・別PRで実装する。
