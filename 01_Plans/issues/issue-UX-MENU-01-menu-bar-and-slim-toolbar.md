# Issue Draft: UX-MENU-01 メニューバー6分類＋スリムツールバー（幅別畳み込み）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/ui/Shell.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/src/ui/ux_operability_regression.test.ts`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-MENU-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D2 収納5層・第3層=メニューバー）, `01_Plans/issues/issue-UX-OPERABILITY-05-primary-toolbar-task-prioritization.md`（Done・トリガ/フォーカス契約）, `01_Plans/issues/issue-QA-MONKEY-06-header-toolbar-responsive-overlap.md`（Done・レスポンシブ回帰の先行）, `01_Plans/issues/issue-UX-COMPLEXITY-01-core-value-foregrounding.md`（初期表示アンカー上限）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-MENU-01
- RequirementStatement: フラットに並ぶヘッダ操作を「分類済みメニューバー＋最頻操作のスリムバー」へ包含し（ADR-0048 D2 第3層）、機能が増えても常時表示が一定に保たれる構造にする。390/768/960/1440px の各幅で主要操作と SafeMode/AI チップが画面外へ消えない。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=文書を開いた状態 / 操作=各メニューを開閉・項目実行・390px へ縮小 / 期待結果=分類済みメニューに既存コマンドが収まり項目右にショートカット併記、スリムバーは最頻操作のみ、390px ではメニューが集約されても全コマンドへ到達可能で SafeMode/AI チップは常時固定 / 除外=新コマンドの追加、viewMode ピルの改名、⌘K パレット本体（UX-CMDK-01）。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: SafeMode（チップの常時可視性を全幅で維持。共有系メニュー項目は既存確認フロー経由）
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048 D2。ただし**分類名は Pending**: 下記「命名の未確定」参照）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- ヘッダには現在も多数の操作が並び、機能追加のたびに右へ膨張する（UX-COMPLEXITY-01 が初期表示アンカーで上限を固定したが、恒久的な「住所」が無いと追加のたび緊張が生じる）。
- ADR-0048 D2 が「メニューバー=分類済みコマンドの恒久住所」を確定済み。File/Edit メニューは部分実装済みで、全体の分類体系と幅別畳みが未実装。

## 1.1 命名の未確定（実装前に解消必須）

- Round 1 設計の6分類は **ファイル/編集/カード/表示/作業/共有**。Round 5 レッドラインは **ファイル/編集/表示/挿入/レビュー/ヘルプ** を示しており食い違う。
- 後者の「レビュー」メニューは、確定済みの語彙分離（壁打ち課題3: 「レビュー」はデータ状態=人間検証に予約。表示モードは「確認ビュー」へ改名）に**違反**するため採用しない。
- 分類名の確定は Claude Design への Round 6 照会（整合要求済み）の回答を待ち、AC-0 として本Issueのブロッカーにする。

## 3) 判断基準による優先度評価

- 価値: 収納5層の第3層。将来コマンドの住所が決まり「とりあえずツールバーに足す」を構造的に防ぐ（CB-1/CB-3 の恒久化）。
- 安全: SafeMode/AI チップの全幅固定。共有系はメニューから既存確認フローへ。
- 規模拡大: 機能が増えても常時表示一定。
- 後方互換: スキーマ変更なし。既存トリガ/フォーカス契約（UX-OPERABILITY-05・`data-focus-return-id`）は不破壊。

## 3.2 非目標 / Non-goals

- 新コマンドの追加。⌘K 本体（UX-CMDK-01）。viewMode ピル改名。レスポンシブ検証マトリクスの再定義（QA-MONKEY-06/PRODUCT-UX-04 の再決定禁止。本Issueは新構造の適用のみ）。

## 4) 提案する解決策 / Proposed solution

- 既存ヘッダ操作を6分類メニュー＋スリムバー（＋新規カード・島を作成・元に戻す 等の最頻数個）へ**包含**（置換であり純増なし）。項目右に OS 別ショートカット併記（UX-SHORTCUT-01 と共通フォーマッタ）、無効項目は淡色。
- メニューは Alt/矢印巡回・Home/End・Esc 閉じ（ADR-0030 契約）。
- 幅別畳み（Round 5 レッドライン）: 1440/960=全表示、768=メニュー横スクロール、390=≡集約・スリムバー最小・作業モードは下シート52vh・SafeMode/AI チップ全幅固定。
- 初期表示アンカー（`ux_operability_regression.test.ts`）を新構造に合わせて更新（常時表示は現状以下であること）。

## 5) 受け入れ条件 / Acceptance criteria

- [ ] AC-0（ブロッカー）: 6分類の命名が確定し、「レビュー」をメニュー名に用いない（語彙分離の遵守）ことが記録される。
- [ ] AC-1: 既存ヘッダ操作が6分類＋スリムバーへ包含され、常時表示要素数が現状以下であることがアンカーで固定される。
- [ ] AC-2: メニューのキーボード巡回（矢印/Home/End/Esc）とフォーカス復帰契約が e2e で固定される。
- [ ] AC-3: 390/768/960/1440px で主要操作へ到達可能かつ SafeMode/AI チップが画面外へ消えない。
- [ ] AC-4: 項目のショートカット併記が OS 別表記で表示される。
- [ ] AC-5: 既存トリガ（表示・共有と再現・作業モード）の `data-focus-return-id` 契約が非回帰。

## 6) 実装タスク分解 / Task breakdown

- [ ] T0 命名確定（Round 6 回答の反映）。
- [ ] T1 メニューバー構造＋既存コマンドの分類移設。
- [ ] T2 スリムバー＋幅別畳み。
- [ ] T3 ショートカット併記＋i18n。
- [ ] T4 アンカー更新＋e2e。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`
- 390/768/960/1440px の各幅 e2e（QA-MONKEY-06 既存 spec の非回帰含む）。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（既存操作の包含＝むしろ純減方向。アンカーで上限固定） / 保留操作の距離=不変（保持系はメニューの奥へ下げない=①②層に維持） / 取り消し導線=あり（メニューは Esc 閉じ・操作は ⌘Z）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D2）
- Related: `01_Plans/issues/issue-UX-CMDK-01-command-palette.md`, `issue-UX-SHORTCUT-01-keyboard-shortcut-system.md`, `issue-UX-COMPLEXITY-01-core-value-foregrounding.md`
- Related: `02_Architecture/design/kj-atlas UI改善提案.dc.html`（3-1）, `02_Architecture/design/kj-atlas 拡張提案.dc.html`（§段階2・命名は未整合のため AC-0 で確定）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
