# Issue Draft: UX-CMDK-01 コマンドパレット（⌘K / Ctrl+K）

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Claude Code
- Scope: `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-CMDK-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D2 収納5層・第5層）, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-CMDK-01
- RequirementStatement: 全コマンドを検索・実行できるコマンドパレット（⌘K/Ctrl+K）を導入し、収納5層（ADR-0048 D2）の第5層＝「新機能の既定の住所」を実体化する。常時表示ゼロで到達可能量を増やす。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=文書を開いた状態 / 操作=⌘K→コマンド名を入力→Enter / 期待結果=該当コマンドが実行され、Esc で閉じるとトリガ元へフォーカス復帰。入力欄フォーカス中に開いてもテキストを破壊しない / 除外=自然文/AI 解釈（Pending・ADR-0048）、文書内容の全文検索（既存検索の領分）。
- SecurityGateImpact: SafeMode（共有系コマンドは既存の共有前確認フローを経由し、パレットから直接出力しない）

## 1) 課題 / Problem statement

- コマンドパレットは現状ゼロ実装（コード・issue・ADR に該当なし）。機能追加のたびにツールバー/パネルへ常設要素が増える圧力があり、CB-1/CB-3 を構造的に守る「オーバーフロー弁」が無い。
- キーボード中心の熟練利用で、任意コマンドへの最短到達手段が無い。

## 2) 背景 / Context

- ADR-0048 D2 が収納5層を確定。第5層（パレット）は「新機能はまずパレットに登録し、恒久配置は利用実績で判断」という追加規律の前提。
- 壁打ち成果（改善提案 3-3、拡張提案 P8）が UI・キーボード仕様を設計済み。プロトタイプに実装例あり。

## 3) 判断基準による優先度評価

- 価値: 常時表示を増やさず到達可能量を増やす＝CB-1 と機能成長の両立装置。
- 安全: 共有・書き出し系は既存確認フロー経由（パレットが安全境界を短絡しない）。
- 規模拡大: 将来機能の既定の住所として恒久的に効く。
- 後方互換: スキーマ変更なし。⌘K は既存機能と重複割当なし（要確認は Validation に含む）。

## 3.2 非目標 / Non-goals

- 自然文・音声（VUI）による操作解釈（ADR-0048 Pending。別Issueで dogfood 後に判断）。
- 文書内テキスト検索の代替。メニューバー再編（UX-NAV-01/ヘッダ系の領分）。

## 4) 提案する解決策 / Proposed solution

- ダイアログ型パレット: ⌘K/Ctrl+K で開き検索入力へフォーカス、↑↓で候補移動・Enter 実行・Esc で閉じてフォーカス復帰（ADR-0030 契約、`data-focus-return-id` 使用）。`aria-activedescendant` で読み上げ対応。
- コマンドレジストリ: 既存操作（新規カード・島を作成・削除・保存・表示モード・作業ドロワー・共有と再現・凡例 等）を id+ラベル+ショートカット表記で登録。**保持系（保留/違和感）を上位固定**（CB-2）。
- 実行結果は既存ハンドラへ委譲（新ロジックを持たない）。共有系はパネルを開くまで（出力はしない）。
- OS 別ショートカット表記（UX-SHORTCUT-01 と共通のフォーマッタ）。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: ⌘K/Ctrl+K で開閉し、Esc でトリガ元へフォーカス復帰することが e2e で固定される（`e2e/command_palette.spec.ts`）。
- [x] AC-2: 検索→Enter で代表コマンド（新規カード・島を作成・保留切替・共有と再現を開く）が実行される。全11コマンドとも既存ハンドラへの委譲のみで新規ロジックを持たない。
- [x] AC-3: テキスト編集中に誤発火しない（`isEditableHotkeyTarget` を既存ロジックから再利用。入力欄では OS 既定を優先することを e2e で固定）。
- [x] AC-4: 保持系（`toggle-hold`）コマンドが候補上位に固定表示される（安定ソートで category="hold" を先頭に）。
- [x] AC-5: 初期表示アンカー非回帰（`data-ui-core-action`×7 不変）。トリガは View パネル内の非インタラクティブなヒント文言のみ（ボタン等は追加しない）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 コマンドレジストリ（既存ハンドラの列挙・保持系上位固定）。
- [x] T2 パレット UI（ダイアログ・検索・キーボードナビ・aria）。
- [x] T3 グローバルキーバインド（入力中ガード・重複割当チェック）。
- [x] T4 i18n＋OS 別表記。
- [x] T5 e2e（開閉・実行・フォーカス復帰・誤発火なし）。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`
- `rg -n "metaKey|ctrlKey" src/App.tsx src/canvas src/ui`（既存バインドとの衝突棚卸し）

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（パレットは呼び出し時のみ。常設トリガは追加しない） / 保留操作の距離=改善（保持系を候補上位に固定） / 取り消し導線=あり（Esc で閉じ復帰。実行コマンドは既存の元に戻すに乗る）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Related: `01_Plans/issues/issue-UX-SHORTCUT-01-keyboard-shortcut-system.md`（表記・バインド共通化）
- Related: `02_Architecture/design/kj-atlas UI改善提案.dc.html`（3-3）, `02_Architecture/design/kj-atlas プロトタイプ.dc.html`
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 実装設計の到着（2026-07-04 Round 5）

- レッドライン確定（`02_Architecture/design/kj-atlas 拡張提案.dc.html` §段階2）: 中央モーダル 幅min(560,92vw)・角丸12、検索入力44h/13px、候補行36h（アイコン16＋ラベル13＋右にOS別キー表記）、保持系コマンド上位固定、空クエリ=最近/推奨・0件=該当なし、`aria-activedescendant`。プロトタイプ実装済み。

## 完了記録 2026-07-06（Claude Code）

- **コマンドレジストリ**（`App.tsx` の `paletteCommands` useMemo）: 11コマンド（新規カード・島を作成・保留を切り替え・作業モード・共有と再現・表示・状態の凡例を切り替え・元に戻す・やり直す・保存・空キャンバスのヒントを再表示）すべてが既存ハンドラ（`handleAddCard`/`handleCreateIsland`/`handleCardHoldStateChange`/`handleUndo`/`handleRedo`/`handleSave`/`handleResetEmptyCanvasHint`/既存 state setter）への参照委譲のみ。既存の enabled 条件（`canEditDocument`・`selectedCardIds.length>0`・`canUndo`/`canRedo`・`isDirty`・`emptyCanvasHintCompleted`）に基づき、無効なコマンドは一覧から**除外**（グレーアウトではない）。
- **UI**（新規 `src/ui/CommandPalette.tsx`）: 中央モーダル（幅 `min(560px,92vw)`・角丸12）・検索入力（44h/13px）・候補行（36h・カテゴリ別グリフ・OS別ショートカット右寄せ）。`role="dialog"`/`role="listbox"`/`role="option"`/`aria-activedescendant` の combobox パターン。↑↓移動・Enter実行・Esc閉じ。
- **保持系上位固定**: `Array.prototype.sort`（安定ソート）で `category==="hold"` を先頭に。
- **フォーカス復帰**: `handleCloseCanvasLegend`（UX-VISUAL-01）と同型の「unmount前に同期 focus」パターンを再利用。開いた時点の `document.activeElement` を ref に保持し、Escape/背景クリック（キャンセル経路）でのみ復帰。**コマンド実行時は復帰を強制しない**（例: 新規カード実行時にカードの編集用テキストエリアが自身の `autoFocus` でフォーカスを持つため、これを奪わない）。
- **誤発火防止**（AC-3）: App.tsx 既存の `isEditableHotkeyTarget`（Cmd+1/2/3 等と共用）をそのまま再利用し、テキスト入力欄にフォーカスがある間は ⌘K を無視して OS/ブラウザ既定に委ねる。StartPanel 表示中も無効化。
- **OS別ショートカット表記**: 新規共有ユーティリティ `src/ui/os_shortcut_format.ts`（`formatModShortcut`）。UX-SHORTCUT-01 のチートシート実装時にも再利用予定。
- **discoverability**（AC-5）: View パネル内に非インタラクティブなヒント文言（「Ctrl+K でコマンドパレットを開く」）のみ追加。ボタン等の常時表示要素は追加していない。
- 検証: typecheck 0 / vitest **894 passed**（182 files。回帰アンカー1件追加）/ e2e 新規5件 passed（開閉・フォーカス復帰／実行／誤発火なし／0件表示／保持系上位固定）+ 既存19件で非回帰確認 / 実機スクショで意図どおりの表示（保留を切り替えが最上位・OS別ショートカット表記）を確認。
