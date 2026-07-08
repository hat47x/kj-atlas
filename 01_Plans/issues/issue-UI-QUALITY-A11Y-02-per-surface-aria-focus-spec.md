# Issue Draft: UI-QUALITY-A11Y-02 新設サーフェスの画面別 ARIA・フォーカス仕様適用

- Type: Feature request
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Claude Code
- Scope: `03_Implement/frontend/src/ui/WorkModePanel.tsx`, `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UI-QUALITY-A11Y-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-2 の拡充）, `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`, `01_Plans/issues/issue-UI-QUALITY-A11Y-01-accessibility-test-expansion.md`（Done・既存面の拡充。本Issueは新設面への適用で非重複）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UI-QUALITY-A11Y-02
- RequirementStatement: 壁打ち Round 4 で確定した画面別 a11y 仕様（フォーカス初期位置・Tab順・Escape挙動・読み上げ順・aria 属性）を、新設・改修サーフェス（作業モードタブ／選択コンテキスト／共有前確認／凡例／一括操作バー）へ適用し、e2e で固定する。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=キーボード/スクリーンリーダで操作 / 操作=作業モードを開く→タブ移動→Esc、カード選択→読み上げ、共有直前サマリ→Esc / 期待結果=仕様表どおりのフォーカス遷移・読み上げ順（型→保持系→確認→根拠→本文）・aria 属性が観測される / 除外=既存 Done 面（StartPanel 等 A11Y-01/QA-MONKEY-09 の再検証）、視覚デザイン変更。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: N/A
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（Round 4 §a11y 仕様）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- ADR-0044 は UQ-2（a11y）を最薄次元と認定し、UI-QUALITY-A11Y-01（Done）が既存面を拡充した。しかし本ラウンドで新設される面（作業モード5タブ・凡例・一括操作バー・共有直前サマリ）と改修される面（選択コンテキストの読み上げ順）には、確定済みの画面別仕様がまだ適用されていない。
- 個別実装 issue に散らすと読み上げ順など横断規則（型→保持系→確認→根拠→本文）の一貫性が崩れやすい。Round 4 も「段階2で全面対応が効率的」と提案。

## 2) 背景 / Context

- 仕様正本: `02_Architecture/design/kj-atlas 拡張提案.dc.html` §アクセシビリティ画面別仕様（2026-07-04 版）。要点: 作業モード=role=dialog aria-modal＋role=tablist 矢印移動＋Esc段階／選択コンテキスト=aria-live=polite・読み上げ順固定／共有前確認=トラップ＋aria-describedby 警告／凡例=非モーダル dialog／一括操作バー=aria-live「n件選択」（評価語なし）。
- 各実装 issue（UX-NAV-01 AC-2・UX-VISUAL-01・UX-SHARE-01・UX-SCALE-01）は自面の基本契約を実装し、本Issueは**横断の一貫性検証と残補完**を担う（重複させない: 実装済み属性の再実装はしない）。

## 3) 判断基準による優先度評価

- 価値（ADR-0044 UQ-2）: 宣言済みの最薄品質次元の底上げ。キーボード完結（ADR-0030）と一体。
- 安全: N/A。
- 規模拡大: 新設面が増えるほど横断規則の価値が上がる。
- 後方互換: 属性付与・フォーカス管理のみ。スキーマ不変。

## 3.2 非目標 / Non-goals

- 既存 Done 面（StartPanel・View/Share の既契約）の再検証。スクリーンリーダ実機の人間受け入れ（別途 H 系ゲート）。視覚デザイン変更。各実装 issue が自ら固定する基本契約の重複実装。

## 4) 提案する解決策 / Proposed solution

- 仕様表を `value_traceability.md` の UQ-2 行に接続し、面×属性のチェックリスト化。
- 各面の実装後に横断 e2e（axe 系スモーク＋フォーカス遷移・読み上げ順のアサーション）を1スイートに集約。
- 読み上げ順（型→保持系→確認→根拠→本文）を CardView/SidePanel の DOM 順・aria-label で保証。
- 不足属性（aria-describedby・aria-activedescendant 等）の補完実装。

## 5) 受け入れ条件 / Acceptance criteria

- [~] AC-1: 5面のうち3面（選択コンテキスト・共有前確認・一括操作バー）を本スライスで確認・固定。凡例・作業モードタブは対象外（理由は完了記録参照）。
- [x] AC-2: カード選択時の読み上げ順が仕様どおり（型→保持系→確認→根拠→本文。カード選択の範囲に限る）。
- [x] AC-3: Esc 段階処理は既存のグローバルホットキー機構（`resolveHotkeyAction`: dismiss-top-layer→clear-selection）で一括操作バーを含め既に仕様どおりであることを確認（コード変更不要）。
- [x] AC-4: 一括操作バーの読み上げに評価語が含まれない（件数のみ）ことを確認（既存実装で充足）。
- [x] AC-5: `value_traceability.md` UQ-2 行を更新（2026-07-09）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 仕様表→チェックリスト化（本完了記録に記載）。UQ-2 接続は未実施（残課題）。
- [x] T2 不足 aria/フォーカス管理の補完（選択コンテキスト・共有前確認の2面）。一括操作バーは既存実装で充足済みと確認。凡例・作業モードタブは対象外。
- [x] T3 e2e（選択コンテキストの読み上げ順・aria-live／共有前確認のaria-describedby）＋回帰アンカー。axe スモークは未導入（残課題）。
- [x] T4 記録（value_traceability 更新、2026-07-09）。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`（a11y スイート含む）

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（属性・フォーカス管理のみ） / 保留操作の距離=不変（読み上げ順で保持系を確認より先に置く） / 取り消し導線=N/A

## Traceability

- Related: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-2）
- Related: `01_Plans/issues/issue-UI-QUALITY-A11Y-01-accessibility-test-expansion.md`（Done・非重複の適用先違い）
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（§a11y 画面別仕様・2026-07-04 版）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 完了記録（部分）2026-07-09（Claude Code）

5面のうち3面を本スライスで対応。残り2面は明確な理由により対象外とした（要件の再定義）。

### 対象外とした2面とその理由

- **凡例（CanvasLegend.tsx）**: 利用者が別セッションで同ファイルへの関係記号エントリ追加作業（`task_2ab8e3e8`）を進行中のため、コンフリクトを避けて本スライスでは触れなかった。当該作業の完了後に別スライスで対応する。
- **作業モードタブ**: 仕様表は `role=tablist＋矢印移動、aria-selected` を要求するが、実装を確認したところ `WorkModePanel.tsx` は単一スクロール領域に複数パネル（文章化・HIL-RS・マージ提案・PatchWorkspace 等）を積み重ねる構成であり、**文字どおりのタブ切替UIは存在しない**。`UX-NAV-01`（Done）の完了記録が明記する「フルなタブ設計...は本Issueの対象外。必要なら別途ADR」という決定を踏まえると、本Issueの範囲でタブ機構を新設することは、既存のDone issueが明示的に見送った設計判断を覆すことになり、a11y補完の範囲を超える。ADRなしに一方的に着手すべきでないと判断し、対象外とした。タブUIの新設要否は別途、人間の判断（ADR）を要する。

### 対応した3面

1. **一括操作バー**: 調査の結果、**追加実装は不要**と判明。`aria-live="polite"` による件数読み上げ・Tab操作・**Escapeでの選択解除**は、既存のグローバルホットキー機構（`useHotkeys.ts` の `resolveHotkeyAction`: `dismiss-top-layer` → `clear-selection` の段階フォールバック）で既に実現されており、`bulk_operations_bar.spec.ts` の既存e2eで検証済みだった。件数表示（`side_panel.selection.card_multiple`）にも評価語は含まれない。
2. **選択コンテキスト**: `data-panel="selection-context"` に `aria-live="polite"` を追加（選択変更時にスクリーンリーダーへ自動通知）。サマリチップの並びを仕様どおり 型→保持系→確認→根拠（claimType→holdState→reviewState→evidence）へ並べ替え（従来は 確認→型→根拠→保持系 の順だった）。
3. **共有前確認**: 「出典参照を含める」トグルの警告文を `aria-describedby` で関連付け（`useId()` で警告divのidを生成し、チェック時のみトグルの `aria-describedby` に設定）。UX-SHARE-01で構築した確認ゲート自体は開時のフォーカス・Escapeでのトリガー復帰を既に満たしている（同一パターンの踏襲）。

### 検証

- typecheck 0 / vitest **962 passed**（185 files。回帰アンカー1件を追加）
- backend: 変更なし
- e2e 新規 `a11y_selection_and_share_gate.spec.ts` **2/2 passed**（選択コンテキストの `aria-live` と読み上げ順／共有前確認の `aria-describedby` 関連付け）
- 関連 e2e 18件（domain_expression_keyboard_access／complexity_budget_foregrounding／pre_share_summary_gate／bulk_operations_bar／first_meaningful_map_mouse_flow）非回帰確認

### 残課題（次スライス）

- 凡例面への適用（`task_2ab8e3e8` 完了後）。
- 作業モードタブへの `role=tablist` 導入要否のADR判断（Owner: Productization Program Owner / UX Lead 相当）。
- axe 系スモークテストの導入（横断 e2e スイートの拡充）。

### 追記 2026-07-09

- `value_traceability.md` §2.7 UQ-2 行に本スライスの結果を反映（T4/AC-5 完了）。
