# Issue: UX-NAV-02 作業モード面（領域4）中身のタブ化 ― role=tablist・5タブ完全実装

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-UX-NAV-01-work-mode-surface-navigation-hierarchy.md`（Done。§68で「フルなタブ設計は本Issueの対象外、必要なら別途」と明記済み）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/App.tsx`（advancedWorkModeContent）, `03_Implement/frontend/src/ui/WorkModePanel.tsx`, 新規 `03_Implement/frontend/src/ui/WorkModeTabs.tsx`, `03_Implement/frontend/src/ui/HilRsWorkflowPanel.tsx`（機能slotへの縮約）
- Related Backlog: `UX-NAV-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0055-work-mode-navigation-semantics.md`（作業モードの受理済み方式）, `01_Plans/adr/ADR-0052-canvas-and-menu-aria-semantics.md`（Independent。本ADRはCanvas/Menu限定）, `01_Plans/issues/issue-UI-QUALITY-A11Y-02-per-surface-aria-focus-spec.md`（role=tablist判断の解消先）, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- Expected verification level: `e2e`

## Draft→Open 2026-07-13: 着手ゲート代理裁可

`role=tablist` は、5つの同格な作業面を1つずつ表示する現設計に適合するため採用する。`ADR-0052` はキャンバスカードとメニュー内フォームに限定され、本Issueの形式的依存にはしない。着手時は次の契約を固定する。

- activationはmanual方式: 左右矢印はfocusだけを移動し、Enter/Spaceでactive化する。Home/End、roving `tabIndex`、`aria-controls` / `aria-labelledby` を実装する。
- 作業面を開いた直後はactive tab（未設定なら先頭tab）へfocusする。Closeボタンを初期focusにしない。
- Escapeは `tabpanel内 -> active tab -> panel close -> 起動triggerへ復帰` の段階契約とし、現行の一発closeを置き換える。
- 非active panelはmounted + hiddenを既定とし、入力値、候補、非同期結果をタブ切替で失わない。副作用処理は非active時に新規開始しない。
- 診断タブは文書全体の既存決定論的診断/件数を再利用する。SidePanelの選択対象別診断は残し、重複する新ロジックやscore/rank/%を追加しない。
- 実装境界はApp-levelの新規 `WorkModeTabs` とし、`advancedWorkModeContent` 内でsiblingになっている `NarrativesPanel` と `HilRsWorkflowPanel` の各機能を5つのslotへ再構成する。`HilRsWorkflowPanel` 単体のラップでは完了扱いにしない。
- 390pxではtab stripを横スクロール可能にし、選択中tabを視野内に保つ。390/768/1440pxで見切れ、重なり、focus迷子をE2E確認する。
- 実装完了時、axeの延期対象にはキャンバス/menuの2ルールだけを残し、tablist由来の除外を残さない。

## Requirement meta I/F

- RequirementID: UX-NAV-02
- RequirementStatement: 作業モードの5つの同格面を、状態を失わないmanual-activation tabsとしてキーボード・支援技術・狭幅画面から一貫して操作できるようにする。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario: 前提=作業モードを開く / 操作=矢印・Home/End・Enter/Space・Tab・Escapeで移動する / 期待結果=focusとactive panelが区別され、既存4面の状態が保持され、診断面から対象へ戻れる / 除外=タブ永続化、タブ順カスタマイズ、診断ロジック高度化。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact: SafeMode / proposal-only / anti-scoring（既存境界の非回帰）
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（2026-07-13 maintainer代理裁可）
- DecisionQueueRef: Resolved（本Issueの着手ゲートで固定。ADR-0052とは独立）

## 背景

Claude Design 実装照合レビュー（2026-07-11、拡張提案 P21「作業モード面の中身 ― 5タブの完全設計」）で、作業モード面の中身について以下の設計が受領された:

- タブは **`role=tablist`**、矢印キーで移動、Escape段階処理と整合。
- 5タブ: **差分／選択マージ／AI提案／診断／文章化**（「レビュー」は語彙衝突のため不採用、確定名称は「作業」）。
- 各タブの状態遷移（idle→loading→list→applied 等）とCB-1〜4自己申告・5判断軸自己評価まで含め詳細設計済み（`02_Architecture/design/kj-atlas 拡張提案.dc.html` §P21 参照）。

一方、現行実装（`App.tsx` の `advancedWorkModeContent`）は:

- `role=tablist` を一切使っていない。単一の縦スクロールコンテナ内に **NarrativesPanel → HilRsWorkflowPanel（candidateComparison=選択マージ／critiqueInput=AI提案／diffVisualization=差分）** の**4セクション**を積んだ構造。
- 独立した「診断」セクションが**存在しない**（反スコアリング表現を持つ診断タブが未実装）。
- タブ間のキーボードナビゲーション（矢印キー）が無い（そもそもタブでないため）。

この設計と実装の乖離は、起票時点では `ADR-0052` の追跡記録に残る C-5（「作業モードタブへの role=tablist 導入要否の判断」、`UI-QUALITY-A11Y-02` 残課題）として扱った。本Issueの実装と `ADR-0055` の受理により、その判断を解消した。

## 判断基準による優先度評価

- 価値・判断軸: 差分/選択マージ/AI提案/文章化は実装済みで価値提供中。tablist化とキーボード到達性の改善は使い勝手向上（P2、機能欠落ではない）。
- 安全: 診断タブの反スコアリング表現（点数・ランク・%を使わない）は新規実装が必要。既存の反スコアリング原則を診断機能拡張時にも維持する。
- 後方互換: 既存の4セクションの機能・データ・監査ログ・取消動線は一切変更しない。コンテナ構造とナビゲーションのみを変更する。

## 提案する解決策

- App-levelに `WorkModeTabs` を新設し、`advancedWorkModeContent` の `NarrativesPanel` と `HilRsWorkflowPanel` 内の機能を `role=tablist` ベースのタブコンテナへ再構成する。
  - 5タブ: 差分／選択マージ／AI提案／診断／文章化。
  - 左右矢印でfocus移動、Enter/Spaceでアクティブ化するmanual activation。Home/End、roving `tabIndex`、`aria-controls` / `aria-labelledby` を含む。Escapeは上記の段階閉鎖契約へ更新する。
  - 各タブ内容は既存コンポーネント（`ReviewDiffPanel`/`HilRsRediffPreview`＝差分、`MergeSuggestionsPanel`+`PatchWorkspacePanel`＝選択マージ、`SuggestionPanel`＝AI提案、`NarrativesPanel`＝文章化）をそのまま移設。ロジック・propsは変更しない。
- **新規: 診断タブ**を追加。反スコアリング原則（点数・ランク・%なし）で「未レビューn・根拠なしn・矛盾n」を確認導線として列挙する（拡張提案P21の設計どおり）。
- QA-MONKEY-12（作業モード内の重なりバグ）の根本原因調査・修正は、タブ化によりセクションが同時に1つしか描画されなくなるため、副次的に解消する可能性が高い。ただし独立したQAとして別途確認する。
- 非目標: タブの永続化（URL/localStorage）、タブ順のカスタマイズ、診断ロジック自体の高度化（初期実装は既存の未レビュー/根拠なし/矛盾カウントの再利用）。

## 受け入れ条件（案）

- [x] 作業モード面の中身が `role=tablist`／`role=tab`／`role=tabpanel` で実装される。
- [x] manual activation、Home/End、roving `tabIndex`、`aria-controls` / `aria-labelledby` を実装し、Escapeの段階閉鎖と起動triggerへのfocus復帰を満たす。
- [x] 5タブ（差分／選択マージ／AI提案／診断／文章化）が揃い、「レビュー」語を使わない。
- [x] 診断タブは反スコアリング（点数・ランク・%なし）で「確認が要る箇所」への導線として機能する。
- [x] 非active panelの入力値・候補・非同期結果が保持され、非active化だけで破棄・再実行されない。
- [x] 390/768/1440pxでtab stripとtabpanelに見切れ・重なり・focus迷子がない。
- [x] 既存4セクションの機能・監査ログ・取消動線に回帰がない（既存テスト・e2eが継続してパスする）。
- [x] 起票時の C-5 判断が本Issueで解消されたことを `ADR-0055` と `UI-QUALITY-A11Y-02` へ反映する。
- [x] a11y: 開いた直後のactive tab focus、tabの名称/選択状態/tabpanel関連、Tab順、Escape挙動を仕様どおりに実装し、axeとe2eで確認する。

## 検証計画

- `cd 03_Implement/frontend && npm run typecheck`
- `cd 03_Implement/frontend && npx vitest run`
- 新規/更新e2e: 作業モードタブの矢印キー操作・Escape・フォーカス復帰・診断タブの反スコアリング表現を確認。
- 既存の関連e2e（`domain_expression_keyboard_access.spec.ts` 等）の非回帰確認。

## Traceability

- Derived-from: `01_Plans/issues/issue-UX-NAV-01-work-mode-surface-navigation-hierarchy.md`（§68でスコープ外と明記済み）
- Related: `01_Plans/adr/ADR-0052-canvas-and-menu-aria-semantics.md`（C-5の解消先）
- Related: `01_Plans/issues/issue-UI-QUALITY-A11Y-02-per-surface-aria-focus-spec.md`（作業モードタブ role=tablist 残課題の解消先）
- Related: `01_Plans/issues/issue-QA-MONKEY-12-work-mode-suggest-layout-button-overlap.md`（タブ化で副次的に解消する可能性がある重なりバグ）
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html` §P21（完全設計の正本）

## 完了記録 2026-07-13（Claude Code）

- **実装**: 新規 `03_Implement/frontend/src/ui/WorkModeTabs.tsx`。role=tablist/tab/tabpanel、manual activation（矢印はfocusのみ移動、ネイティブbuttonのonClickがEnter/Space/クリックいずれでも活性化を兼ねる）、roving tabIndex、Home/End、非active tabpanelは`hidden`属性で非表示（アンマウントしない）。
- **段階Escape**: tabpanel側`onKeyDown`でEscapeを`stopPropagation`し、active tabへfocusを戻す（第1段）。tab自体にはEscapeハンドラを付けないため、tab上でのEscapeは`WorkModePanel`既存のハンドラへ素通りし、パネル終了＋起動triggerへのfocus復帰（第2段）が既存ロジックのまま機能する。
- **HilRsWorkflowPanel.tsx を削除**: 3スロット（候補比較／違和感入力／差分）を独立タブへ再構成したことで、単なる見出し付きラッパーだった同コンポーネントは完全に不要になった。対応するテストも削除し、`hil_rs_workflow.*.title`（3キー）も未使用になったためja/en両ロケールから削除（`.description`キーは各タブの説明文として存続）。
- **診断タブ**: 新規ロジックなし。App.tsx既存の`domainExpressionShareSummary`（`SharePanel`の共有前チェックと同一の算出）をそのまま再利用し、同一のi18nキー（`share.panel.preflight.domain_summary_*`）で表示。
- **横断ナビゲーション対応**: SidePanelの「Review reproposal」リンク（`handleOpenCritiqueWorkflow`）がAI提案タブへ直接遷移＋フォーカスできるよう、`WorkModeTabs`に`activateRequest`（外部からのタブ活性化要求）を追加。既存の`critiqueWorkflowFocusRequest`カウンタをそのまま再利用（App.tsx側に新規stateは追加していない）。
- **既知のタイミングバグと対処**: 当初`requestAnimationFrame`でフォーカスを遅延させたところ、`WorkModePanel`自身の「開いた直後にactive tabへfocus」効果（React 18 StrictModeの二重effect実行と絡む）と競合し、フォーカスが「Diff」タブへ戻ってしまう再現性のある不具合を発見。`setTimeout(fn, 0)`（マクロタスク、同一フレーム内のrAF処理より確実に後段）へ変更して解消した。あわせて、活性化要求の再処理ガードを「nonceを記憶するref」から「`nonce === 0`を除外する値ベースの判定」へ変更し、StrictModeの二重実行時にrefガードが2回目の実行を止めてフォーカス処理自体が消えてしまう別の不具合も修正した。
- **テスト**: `WorkModeTabs.test.ts`（4 unit、静的マークアップ）、`e2e/work_mode_tabs.spec.ts`（9 e2e：初期focus・manual activation・ArrowLeft折返しとHome/End・roving tabIndex・状態保持・段階Escape・診断タブの反スコアリング内容・390px横スクロール）。既存`domain_expression_keyboard_access.spec.ts`のクロスナビゲーションテストを新構造に合わせて更新（`data-domain-workflow`マーカーは維持、期待文言をタブ切替後のものへ更新）。`ux_operability_regression.test.ts`のPhase 5bアンカーも新構造（`<WorkModeTabs`）に更新。
- **検証**: typecheck 0 / vitest 190 files・1033 tests / e2e: `work_mode_tabs.spec.ts`（9/9）・`a11y_axe_smoke.spec.ts`（8/8、tablist由来の延期ルールなし）・`domain_expression_keyboard_access.spec.ts`・`agent_response_import.spec.ts`・`keyboard_release_candidate_flow.spec.ts`（既存27件、非回帰）。フルe2eスイートも実行済み（結果は本Issueのショップ時コミットメッセージ参照）。
