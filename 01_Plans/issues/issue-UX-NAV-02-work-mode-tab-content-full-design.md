# Issue Draft: UX-NAV-02 作業モード面（領域4）中身のタブ化 ― role=tablist・5タブ完全実装

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-UX-NAV-01-work-mode-surface-navigation-hierarchy.md`（Done。§68で「フルなタブ設計は本Issueの対象外、必要なら別途」と明記済み）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/App.tsx`（advancedWorkModeContent）, `03_Implement/frontend/src/ui/WorkModePanel.tsx`, `03_Implement/frontend/src/ui/HilRsWorkflowPanel.tsx`（新規タブコンテナへ置換またはラップ）
- Related Backlog: `UX-NAV-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0052-canvas-and-menu-aria-semantics.md`（C-5「作業モードタブへの role=tablist 導入要否」を本Issueが解消）, `01_Plans/issues/issue-UI-QUALITY-A11Y-02-per-surface-aria-focus-spec.md`（残課題としてrole=tablist判断を本Issueへ委譲）
- Expected verification level: `e2e`

## 背景

Claude Design 実装照合レビュー（2026-07-11、拡張提案 P21「作業モード面の中身 ― 5タブの完全設計」）で、作業モード面の中身について以下の設計が受領された:

- タブは **`role=tablist`**、矢印キーで移動、Escape段階処理と整合。
- 5タブ: **差分／選択マージ／AI提案／診断／文章化**（「レビュー」は語彙衝突のため不採用、確定名称は「作業」）。
- 各タブの状態遷移（idle→loading→list→applied 等）とCB-1〜4自己申告・5判断軸自己評価まで含め詳細設計済み（`02_Architecture/design/kj-atlas 拡張提案.dc.html` §P21 参照）。

一方、現行実装（`App.tsx` の `advancedWorkModeContent`）は:

- `role=tablist` を一切使っていない。単一の縦スクロールコンテナ内に **NarrativesPanel → HilRsWorkflowPanel（candidateComparison=選択マージ／critiqueInput=AI提案／diffVisualization=差分）** の**4セクション**を積んだ構造。
- 独立した「診断」セクションが**存在しない**（反スコアリング表現を持つ診断タブが未実装）。
- タブ間のキーボードナビゲーション（矢印キー）が無い（そもそもタブでないため）。

この設計と実装の乖離は ADR-0052 の C-5（「作業モードタブへの role=tablist 導入要否の判断」、`UI-QUALITY-A11Y-02` 残課題）そのものであり、本Issueが実装レベルでその判断を解消する。

## 判断基準による優先度評価

- 価値・判断軸: 差分/選択マージ/AI提案/文章化は実装済みで価値提供中。tablist化とキーボード到達性の改善は使い勝手向上（P2、機能欠落ではない）。
- 安全: 診断タブの反スコアリング表現（点数・ランク・%を使わない）は新規実装が必要。既存の反スコアリング原則を診断機能拡張時にも維持する。
- 後方互換: 既存の4セクションの機能・データ・監査ログ・取消動線は一切変更しない。コンテナ構造とナビゲーションのみを変更する。

## 提案する解決策

- `HilRsWorkflowPanel.tsx` を `role=tablist` ベースのタブコンテナへ置換（または新規タブラッパーで包む）。
  - 5タブ: 差分／選択マージ／AI提案／診断／文章化。
  - 矢印キー（左右）でタブ移動、Enter/Spaceでアクティブ化。Escapeは既存の段階閉鎖契約と整合。
  - 各タブ内容は既存コンポーネント（`ReviewDiffPanel`/`HilRsRediffPreview`＝差分、`MergeSuggestionsPanel`+`PatchWorkspacePanel`＝選択マージ、`SuggestionPanel`＝AI提案、`NarrativesPanel`＝文章化）をそのまま移設。ロジック・propsは変更しない。
- **新規: 診断タブ**を追加。反スコアリング原則（点数・ランク・%なし）で「未レビューn・根拠なしn・矛盾n」を確認導線として列挙する（拡張提案P21の設計どおり）。
- QA-MONKEY-12（作業モード内の重なりバグ）の根本原因調査・修正は、タブ化によりセクションが同時に1つしか描画されなくなるため、副次的に解消する可能性が高い。ただし独立したQAとして別途確認する。
- 非目標: タブの永続化（URL/localStorage）、タブ順のカスタマイズ、診断ロジック自体の高度化（初期実装は既存の未レビュー/根拠なし/矛盾カウントの再利用）。

## 受け入れ条件（案）

- [ ] 作業モード面の中身が `role=tablist`／`role=tab`／`role=tabpanel` で実装される。
- [ ] 矢印キーでタブ間を移動でき、Enter/Spaceでアクティブ化する。既存のEscape段階閉鎖・フォーカス復帰契約を破壊しない。
- [ ] 5タブ（差分／選択マージ／AI提案／診断／文章化）が揃い、「レビュー」語を使わない。
- [ ] 診断タブは反スコアリング（点数・ランク・%なし）で「確認が要る箇所」への導線として機能する。
- [ ] 既存4セクションの機能・監査ログ・取消動線に回帰がない（既存テスト・e2eが継続してパスする）。
- [ ] ADR-0052 の C-5 判断が本Issueで解消されたことを `UI-QUALITY-A11Y-02` へ反映する。
- [ ] a11y: フォーカス初期位置・Tab順・Escape挙動・読み上げ順（型→保持系→確認→根拠→本文）の仕様表どおりに実装し、e2eで確認する。

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
