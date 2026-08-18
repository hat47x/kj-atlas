# Issue: UX-NAV-01 作業モード面（ADR-0031 領域4）の実体化とナビゲーション階層

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex

## Implementation Progress 2026-06-27

### Done
- AC-1: WorkModePanel component (full-screen overlay, Escape close, focus return) ✅
- AC-3: structuralDiff duplicate removal ✅
- AC-5: complexity budget compliance (1 new button, no initial display growth) ✅
- AC-6: SafeMode non-regression ✅
- WorkModePanel toggle button in header toolbar ✅
- Fragment wrapper for Shell+WorkModePanel ✅
- i18n: en/ja labels for title, close, content_pending ✅

## Implementation Closeout 2026-07-04

### Done
- AC-2: `NarrativesPanel`, `HilRsWorkflowPanel`, and the structural diff surface now render inside `WorkModePanel` (`data-ui-region="work-mode"`) instead of `SidePanel.topContent` ✅
- AC-4: The mode label remains `Work mode` / `作業モード`; no `review` tab or additional review-mode name was introduced ✅
- Regression guards: `ux_operability_regression.test.ts` now asserts that advanced narrative/HIL panels are owned by the work-mode surface, not the selection-context side panel ✅
- E2E evidence: `complexity_budget_foregrounding.spec.ts` verifies that selection context excludes Narrative/HIL/diff copy, Work mode contains it, and Escape returns focus to the Work mode trigger ✅

### Deferred
- Phase 2 optional work (URL/history persistence for work-mode state and lighter adjacent-panel migration) remains outside this issue's Phase 1 acceptance scope.

## Follow-up Evidence 2026-07-05: Work-mode focus scope

- `WorkModePanel` now traps `Tab` / `Shift+Tab` within the modal surface and keeps `Escape` / close-button focus return on the Work mode trigger.
- `ux_operability_regression.test.ts` records the dialog, focus-scope, and keyboard-cycle contract so the advanced work surface does not regress into background-focus leakage.

### Commits
- PR #2490: WorkModePanel component + i18n
- PR #2491: WorkModePanel wiring (import, state, toggle, Fragment)
- 12819a8a: structuralDiff dedup (AC-3)
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/src/ui/Shell.tsx`, `03_Implement/frontend/src/ui/ux_operability_regression.test.ts`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-NAV-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/issues/issue-PRODUCT-UX-02-workspace-information-architecture.md`, `01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`, `01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md`, `01_Plans/issues/issue-UX-COMPLEXITY-01-core-value-foregrounding.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-NAV-01
- RequirementStatement: ADR-0031 が定める5領域のうち「作業モード面（領域4：レビュー/差分/ナラティブ/AI提案/パッチ/診断）」に独立した画面領域（DOM上の home）を与え、現在は選択コンテキスト領域（領域3）の内部に注入されている高度機能群を、既定OFFの明示的モード面へ移設する。これにより、選択直後に選択対象の確認・編集を視野内へ出すという領域3の責務を構造的に回復する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=詳細（advanced）を ON にした状態でカード/島を選択 / 操作=作業モード（差分・ナラティブ・マージ/パッチ・AI提案・診断）を開く / 期待結果=作業モード一式は選択コンテキスト aside の外にある独立領域（`data-ui-region="work-mode"`）に表示され、選択コンテキスト aside には選択対象＋基本編集/レビューのみが残り、Escape で閉じてトリガへフォーカス復帰する / 除外=viewMode ピル（探索/レビュー/要約）の改名、document/view/pack スキーマ変更、レガシー機能削除、ADR-0030/0031/0043 の再決定。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: share-export（共有・再現・差分導線の再配置を含むため非回帰確認が必要）

## 1) 課題 / Problem statement

- ADR-0031 は製品化UIを5領域で定義し、領域4「作業モード面」を高度機能（レビュー/差分/ナラティブ/AI提案/パッチ/診断）の置き場として「タブまたは明示的なモードとして段階的に開く」と定めた。
- しかし現行実装で DOM 上の領域として実体を持つのは4つのみ（`data-ui-region` は `primary-flow`（[App.tsx:9425](../../../03_Implement/frontend/src/App.tsx)）/ `selection-context`（[SidePanel.tsx:1105](../../../03_Implement/frontend/src/ui/SidePanel.tsx)）/ `domain-state-filter` / `stream-b-p2a-readiness`、加えて `data-panel` の `view` / `share-replay` / `start-document-entry`）。**領域4に対応する `data-ui-region` は存在しない**。
- 代わりに作業モード一式が `topContent` という塊（[App.tsx:8871-9002](../../../03_Implement/frontend/src/App.tsx)：旧式共有セクション＋`NarrativesPanel`＋`HilRsWorkflowPanel`（`MergeSuggestionsPanel`/`PatchWorkspacePanel`/`SuggestionPanel`/`HilRsRediffPreview`））として生成され、**選択コンテキスト aside の内部**（[SidePanel.tsx:1248](../../../03_Implement/frontend/src/ui/SidePanel.tsx)、aside は 1105）に注入されている。詳細（advanced）ON 時には、選択直後に最優先で視野へ出すべき選択対象（ADR-0031 領域3の責務）が、AI/HIL の作業ベンチの下へ押し下げられる。
- さらに `structuralDiffPanel`（定義 [App.tsx:8618](../../../03_Implement/frontend/src/App.tsx)）が、`structuralDiffSection` prop（[App.tsx:8835](../../../03_Implement/frontend/src/App.tsx)）に加え、`topContent` 内で**2回**（[App.tsx:8886](../../../03_Implement/frontend/src/App.tsx) と [App.tsx:8997](../../../03_Implement/frontend/src/App.tsx)）描画されており、差分面が複数箇所に重複している。
- 機能が増えるたびに新しい作業モードが同じ `topContent` スクロール列へ積み上がる構造で、ADR-0031 の領域分割が実装上崩れ続ける。

## 2) 背景 / Context

- これは PRODUCT-UX-02（Done）が「フルなタブ設計と URL レベルの作業モード永続化は本Issueの対象外。必要なら別途 ADR-0031 のナビゲーション階層 issue とする」と**明示的に先送りした未起票GAP**を起票するものである。
- UX-COMPLEXITY-01（Done, 2026-06-23）は `data-ui-complexity-tier` と `isAdvancedUiEnabled`（[App.tsx:8872](../../../03_Implement/frontend/src/App.tsx)）による**可視性のゲート（CB-1 既定の静けさ）**を達成した。既定では作業モード blob は非表示で、CB-1 は満たされる。
- 本Issueはそれと**別軸**である。UX-COMPLEXITY-01 は「初期表示の要素数・前景化（可視性）」を扱うのに対し、本Issueは「ADR-0031 の領域4を構造として実体化し、advanced ON 時にも領域3の責務を守る（IA の構造）」を扱う。両者は相補的で重複しない。
- 関連契約: ADR-0030 段階開示＋キーボードスコープ、UX-OPERABILITY-03（選択コンテキストは選択対象を先に出し、advanced グループは初期非表示）、UX-OPERABILITY-04（View / Share-and-Reproduce パネルの Escape 閉鎖＋トリガへの focus 復帰、`data-focus-return-id`）。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001 / domain.md）: コア価値は「少ない操作で曖昧さを保持できる軽さ」。選択対象の確認が作業ベンチの下に沈む現状は、選択直後の見通しを損ない価値の核を侵す。
- 安全（THREAT_MODEL / SafeMode）: 差分・共有・再現の導線が複数箇所に重複（structuralDiff ×2〜3）すると、どこで何を共有・出力するかの判断が分散する。単一実体化は誤操作・誤共有の低減にも資する。
- 規模拡大（enterprise / scale）: 機能追加が続く前提で、領域4に正規の住所がないと新規作業モードが領域3へ積層し続ける。歯止めとして構造の実体化が必要。
- 後方互換: 表示構造の再配置であり、document/view/pack スキーマは変更しない。レガシー機能も削除しない。

## 3.1 依存関係 / Dependencies

- 直前依存: ADR-0031（領域4定義）、PRODUCT-UX-02（再編結果と先送り宣言）、UX-OPERABILITY-03/04（選択コンテキスト責務と Escape/focus 契約）。
- 連携先: UX-COMPLEXITY-01（可視性規律。本Issueの構造変更後も常設要素数アンカーが非回帰であること）、PRODUCT-QA-01（複雑性予算「悪化」時の明示確認ゲート）。
- ブロッカー条件: 上位ADR（0030/0031/0043）に矛盾が生じる設計（例：作業モードを既定ONで常設化する）には進まない。

## 3.2 非目標 / Non-goals

- viewMode ピル（探索/レビュー/要約、`app.view_mode.*`、Cmd/Ctrl+1/2/3）の改名（i18n・操作記憶・公開スクショ同期コストが重く、別ADR）。
- document/view/pack スキーマの変更。
- レガシー import/export・既存機能の削除。
- ADR-0030/0031/0043 の再決定（本Issueは領域4の**実装方式**の提案であり、5領域モデル自体の再定義ではない）。
- UX-COMPLEXITY-01 の AC（初期表示の要素数・前景化監査）の再定義（重複禁止。本Issueは IA 構造の実体化という非重複の角度）。

## 4) 提案する解決策 / Proposed solution

- 変更の最小単位（段階的）:
  - **Phase 1（本Issueの主目的）**: 領域4に独立領域 `data-ui-region="work-mode"` を導入する。既定OFFの**ドロワー/オーバーレイ**として実装し、明示的なモード操作で開く（自動描画しない）。Escape 閉鎖＋トリガへの focus 復帰は ADR-0030 / UX-OPERABILITY-04 契約（`data-focus-return-id`）を再利用する。最重量の `HilRsWorkflowPanel`（Merge/Patch/Suggest/Rediff）＋`NarrativesPanel`＋差分を `SidePanel.topContent`（[App.tsx:8871-9002](../../../03_Implement/frontend/src/App.tsx)）から当該領域へ移設する。
  - **structuralDiff 単一化**: `structuralDiffPanel` の重複描画（[App.tsx:8886](../../../03_Implement/frontend/src/App.tsx) / [App.tsx:8997](../../../03_Implement/frontend/src/App.tsx)）と `structuralDiffSection` prop（8835）を整理し、差分面を1箇所に集約する。
  - **領域3の責務回復**: 移設後、選択コンテキスト aside（`data-ui-region="selection-context"`）は選択対象＋基本編集/レビューのみを保持する（UX-OPERABILITY-03 非回帰）。
  - **命名規律（finding 2.2）**: 領域4の作業モードをタブ/モードとして見せる際、`レビュー/review` を再利用しない（viewMode ピルの `レビュー` と衝突させない）。これはコード/i18n 変更を伴わない純粋な規律で CB-3 純増ゼロ。
  - **Phase 2（先送り可）**: より軽量な選択隣接パネルの移設、作業モード状態の URL/履歴永続化。
- 非目標: 上記「3.2 非目標」を正本とする。

## 5) 受け入れ条件 / Acceptance criteria

- AC-1: 作業モード面が独立領域 `data-ui-region="work-mode"` を持ち、既定OFF・明示操作で開閉し、Escape 閉鎖＋トリガへの focus 復帰が e2e で固定される（ADR-0030 / UX-OPERABILITY-04 契約に整合）。
- AC-2: `HilRsWorkflowPanel`・`NarrativesPanel`・差分が選択コンテキスト aside の**外**（work-mode 領域）に存在し、選択直後に選択対象＋基本編集/レビューが領域3の視野内へ出ることが e2e で固定される（UX-OPERABILITY-03 非回帰）。
- AC-3: `structuralDiff` 面が単一実体に集約され、重複描画が解消される（source-string/DOM 回帰で確認）。
- AC-4: 命名規律（作業モードタブに `レビュー/review` を用いない）が本Issueまたはナビ階層方針として明文化される。
- AC-5: ADR-0043 自己申告として「初期表示への純増=なし（領域4は既定OFF）」が満たされ、`ux_operability_regression.test.ts` の初期表示アンカー（UX-COMPLEXITY-01）が非回帰であること。
- AC-6: SafeMode 既定ON・共有/エクスポート安全導線（PRODUCT-UX-03）が弱まらないこと。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（作業モード領域は既定OFFのドロワー/オーバーレイ。むしろ advanced ON 時に領域3へ積層していた要素を領域4へ移し、構造を整理） / 保留操作の距離=不変または改善（選択コンテキストが作業ベンチの下に沈まなくなるため、保留・違和感の編集到達が改善方向） / 取り消し導線=あり（領域4は Escape で閉じ、focus 復帰）

## Traceability

- Related: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`（領域4 作業モード面の定義）
- Related: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`（Escape/focus 復帰・段階開示）
- Related: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`（CB-1/CB-3/CB-4）
- Related: `01_Plans/issues/issue-PRODUCT-UX-02-workspace-information-architecture.md`（本GAPの先送り元）
- Related: `01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`（選択コンテキスト責務）
- Related: `01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md`（パネル閉鎖・focus 復帰契約）
- Related: `01_Plans/issues/issue-UX-COMPLEXITY-01-core-value-foregrounding.md`（可視性規律。本Issueは構造実体化の別軸）
- Derived-from: `01_Plans/issues/issue-PRODUCT-UX-02-workspace-information-architecture.md`（明示的に先送りされたナビゲーション階層 issue）

## 実装設計の到着（2026-07-04）

- Claude Design Round 4 成果（`02_Architecture/design/kj-atlas 拡張提案.dc.html` §領域4）に、Deferred 中の AC-2 実装に必要な**5タブ（差分/選択マージ/AI提案/診断/文章化）の完全設計**（状態機械・監査ログ・provider=none 肯定提示・診断の反スコアリング所在提示・role=tablist/Esc段階の a11y 仕様）が到着。プロトタイプで差分タブ全状態が操作可能。AC-2 着手時の設計正本として参照のこと。

## 実装設計の到着（2026-07-04 Round 5）

- パッチワークスペース（CE3）の居場所について Claude Design の比較評価が到着し、**(a) 選択マージタブへ統合** を採用する（タブ純増なし=CB-1・既存タブへ包含=CB-3・ロールバック＝取消を監査と一体化=CB-4）。AC-2 実装時は選択マージタブにパッチの粒度別採否・プリセット・ロールバックを包含し、独立タブ・現状維持は採らない。

### 追記 2026-07-09: 実装照合レビュー（design-qa-checklist）で実バグを発見・修正

`02_Architecture/design/design-qa-checklist.md` 第6回として実施。`03_Implement/frontend/scripts/capture_design_conformance_navmode_20260709.mjs` で「詳細」OFF/ON双方の作業モード・選択コンテキスト・Escapeフォーカス復帰を実機取得し照合。

- **発見・修正**: 「詳細」OFF時に作業モードを開くと表示される空状態文言（`work_mode.content_pending`）が「現在は詳細表示を有効にしてサイドバーから利用できます」という、AC-2でのサイドバーからの完全移設より前の古い案内文のまま残っていた。`SidePanel.tsx` に `NarrativesPanel`/`HilRsWorkflowPanel` の参照が実際にゼロであることを確認済みのため、この文言は誤ったナビゲーション誘導になっていた（実際には「詳細」を有効にすると同じ作業モード内にそのまま表示される）。両ロケール（ja/en）の文言を実態に合わせて修正し、`ux_operability_regression.test.ts`（Phase 5b）に「サイドバー」という語を含まないことのアンカーを追加。
- **確認（乖離なし）**: AC-2の移設対象3パネル（NarrativesPanel/HilRsWorkflowPanel/差分）は選択コンテキストasideに存在しないこと、作業モード内にのみ存在することをスクショと既存ソースの双方で再確認。role="dialog"・aria-modal・Escapeフォーカス復帰・命名規律（AC-4、「レビュー」不使用）も乖離なし。
- 検証: typecheck 0 / vitest 963 passed（`nix develop` の Node 20 devShell経由。同一の `npx vitest run` をWSLシステムnode 18で先に実行した際は無関係な26件が `crypto is not defined` で誤って失敗したため、正しいdevShell入り口で再実行し解消を確認） / e2e `complexity_budget_foregrounding.spec.ts` 3/3 passed。
