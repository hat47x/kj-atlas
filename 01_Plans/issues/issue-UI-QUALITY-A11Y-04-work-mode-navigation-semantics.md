# Issue Draft: UI-QUALITY-A11Y-04 作業モードのナビゲーション意味論

- Type: Architecture / Accessibility
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: TBD (Productization Program Owner / UX Lead)
- Scope: `02_Architecture/design/`, `01_Plans/adr/ADR-0053-work-mode-navigation-semantics.md`, `03_Implement/frontend/src/ui/WorkModePanel.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/e2e/`
- Related Backlog: `UI-QUALITY-A11Y-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0053-work-mode-navigation-semantics.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/issues/issue-UX-NAV-01-work-mode-surface-navigation-hierarchy.md`
- Expected verification level: `e2e`

## 要求メタデータ

- RequirementID: UI-QUALITY-A11Y-04
- RequirementStatement: 作業モードのナビゲーション意味論を実際の操作モデルと一致させ、キーボード利用者やスクリーンリーダー利用者に存在しないタブリストを提示しない。
- PriorityClass: Should
- AcceptanceScenario: 作業モードを開いた利用者がマウスまたはキーボードを操作したとき、表示中の高度機能へ予測可能な順序で到達でき、Escapeで閉じられ、起点へフォーカスが戻り、選択した方式に適したdialog/heading/regionのDOM意味論が使われている。
- GoNoGoGate: Optional
- SecurityGateImpact: N/A
- VerificationLevel: e2e
- DecisionStatus: Pending
- DecisionQueueRef: `ADR-0053`

## 1) 課題

設計要求は `role="tablist"` を持つ5つの作業モードタブを示していますが、実装は複数のセクションを含む1つのモーダルダイアログです。実装には文字どおりのタブがないため、アクセシビリティissue `UI-QUALITY-A11Y-02` はこの点を未決定のまま残しています。明示的な判断がないまま、将来ARIAのタブロールだけを追加したり、設計正本だけを変更したりすると、実際の操作と読み上げ内容が乖離します。

## 2) 背景

- `WorkModePanel.tsx` が、画面全体のダイアログ、フォーカスの閉じ込め、Escapeによる終了、起点へのフォーカス復帰を担当しています。
- `App.tsx` は高度機能を1つの `advancedWorkModeContent` ツリーとして渡しています。
- `design-request-2026-07-round3.md` は5機能のタブ配置を要求しています。一方、`design-qa-checklist.md` は現行の積層領域方式を設計判断として記録しています。
- `ADR-0052` はキャンバス選択とメニューの意味論に限定されるため、このissueの判断には使用しません。

## 3) 解決案

`ADR-0053` で、次のいずれかを明示的に選択します。

1. 積層セクション方式: 1つのダイアログを維持し、見出し・領域を付与し、表示中の全ワークフローを通常のTab操作で移動できるようにします。
2. 文字どおりのタブ方式: 選択状態、矢印キー操作、非表示パネルのフォーカス規則、レスポンシブ表示を実装したうえで、タブロールを付与します。

現時点の推奨は、実装と一致し、製品化移行中も高度機能を同時に確認できる1の積層セクション方式です。ただし、DecidersがADRを承認するまでは最終決定ではありません。

### 判断前のベースライン証跡

- 現行のUI契約テスト `src/ui/ux_operability_regression.test.ts` は、2026-07-15に **32/32** で成功しました。
- このベースラインでは、`role="dialog"`、`aria-modal="true"`、フォーカス可能なパネル起点、Tabの閉じ込め、Escape処理、Narratives/HIL/差分が `SidePanel` ではなく `WorkModePanel` に配置されていることを確認しています。
- これは判断前の証跡であり、AC-1、AC-2、AC-5の完了を意味しません。操作モデルは未承認で、マウス・キーボード操作を対象にした専用Playwrightシナリオも未整備です。

## 4) 受け入れ条件

- [ ] AC-1: `ADR-0053` に承認済みの決定と、選択した操作モデルが記録されている。
- [ ] AC-2: 設計正本、`UX-NAV-01`、`UI-QUALITY-A11Y-02` が同じ方式と用語で記述されている。
- [ ] AC-3: 積層セクション方式を採用する場合、ダイアログに各ワークフローの見出しまたは名前付き領域があり、存在しないタブロールが付与されていない。
- [ ] AC-4: 文字どおりのタブ方式を採用する場合、`role="tab"` を追加する前に、選択状態、矢印キー操作、非表示パネルのフォーカス処理、レスポンシブ表示が実装されている。
- [ ] AC-5: Playwrightで、マウスによる起動、キーボード移動、Escapeによる終了、フォーカス復帰、および選択方式に関係するDOM契約を検証する。
- [ ] AC-6: Statusを変更した後、`validate_active_issue_memos.py` とissue memoの単体テストが成功する。

## 5) 作業分解

- [ ] T1: Productization Program OwnerとUX Leadが `ADR-0053` を確認し、承認または修正する。
- [ ] T2: 承認された方式に合わせて、設計正本、`UX-NAV-01`、`UI-QUALITY-A11Y-02` を同期する。
- [ ] T3: 承認された方式に必要な意味論だけを実装する。
- [ ] T4: マウス操作とキーボード操作を対象としたPlaywrightの重点テストを追加または更新する。
- [ ] T5: 型検査、重点E2E、アクセシビリティスモーク、issue memo検証を実行する。

## 6) 検証計画

- 実装前: DOMと設計正本を照合し、提案するロールが実際の操作モデルを表していることを確認する。
- 実装後:
  - `node node_modules/@playwright/test/cli.js test e2e/a11y_axe_smoke.spec.ts e2e/<work-mode-spec>.spec.ts --reporter=line`
  - `node node_modules/typescript/bin/tsc --noEmit`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- 期待結果: 存在しないタブ意味論がなく、マウス・キーボード操作が予測可能で、Escapeとフォーカス復帰に回帰がないこと。

## 7) 検討した代替案

- 現在の積層コンテンツに `role="tablist"` を追加する: 実際の操作モデルとARIAロールが一致しないため採用しません。
- 判断なしで `UI-QUALITY-A11Y-02` を完了する: 設計正本と実装の曖昧さが残るため採用しません。
- 作業モード全体を直ちに再設計する: 意味論の判断と大規模なUX変更が混在するため、別作業へ延期します。

## 8) リスクと切り戻し

- リスク: タブ方式を採用すると機能が隠れ、キーボード操作の手数が増える可能性があります。対策として、AC-4に矢印キーとフォーカス挙動を必須化します。
- リスク: 文書だけを変更すると再び実装と乖離する可能性があります。設計正本、ADR、issue、E2E契約を1つの追跡関係で維持します。
- 切り戻し: 承認した方式で操作性またはアクセシビリティに問題が出た場合は、検証済みの方式へ戻し、新しい判断で `ADR-0053` を置き換えます。中途半端なARIAロールだけを残しません。

## 9) 補足

- このissueは設計・責任者による判断が得られるまでDraftとします。
- `UI-QUALITY-A11Y-02` の残課題から派生したタスクであり、既存の `ADR-0052` の範囲を変更するものではありません。
