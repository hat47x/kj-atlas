# Issue: UI-QUALITY-A11Y-04 作業モードのナビゲーション意味論

- Type: Architecture / Accessibility
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: TBD (Productization Program Owner / UX Lead)
- Scope: `02_Architecture/design/`, `01_Plans/adr/ADR-0055-work-mode-navigation-semantics.md`, `03_Implement/frontend/src/ui/WorkModePanel.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/WorkModeTabs.tsx`, `03_Implement/frontend/e2e/`
- Related Backlog: `UI-QUALITY-A11Y-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0055-work-mode-navigation-semantics.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/issues/issue-UX-NAV-01-work-mode-surface-navigation-hierarchy.md`, `01_Plans/issues/issue-UX-NAV-02-work-mode-tab-content-full-design.md`
- Expected verification level: `e2e`

## 要求メタデータ

- RequirementID: UI-QUALITY-A11Y-04
- RequirementStatement: 作業モードのナビゲーション意味論を実際の操作モデルと一致させ、キーボード利用者やスクリーンリーダー利用者に存在しないタブリストを提示しない。
- AcceptanceScenario: 作業モードを開いた利用者がマウスまたはキーボードを操作したとき、表示中の高度機能へ予測可能な順序で到達でき、Escapeで閉じられ、起点へフォーカスが戻り、選択した方式に適したdialog/heading/regionのDOM意味論が使われている。
- SecurityGateImpact: N/A

## 1) 課題

設計要求は `role="tablist"` を持つ5つの作業モードタブを示しており、実装も `WorkModeTabs.tsx` による文字どおりのタブ方式へ更新されました。設計・実装・E2Eの契約が個別に更新されると再び乖離するため、方式をADRと本issueで固定します。

## 2) 背景

- `WorkModePanel.tsx` が、画面全体のダイアログ、フォーカスの閉じ込め、Escapeによる終了、起点へのフォーカス復帰を担当しています。
- `App.tsx` は `WorkModeTabs` に5つの作業面を渡します。非選択パネルはアンマウントせず、状態を保持します。
- `design-request-2026-07-round3.md` のタブ要求と `UX-NAV-02` の実装記録が一致しています。
- `ADR-0052` はキャンバス選択とメニューの意味論に限定されるため、このissueの判断には使用しません。

## 3) 解決案

`ADR-0055` で、文字どおりのタブ方式を採用しました。`UX-NAV-02` に記録されたmanual activation、roving `tabIndex`、Home/End、段階Escape、状態保持、狭幅表示の契約を本issueの完了条件とします。

### 判断前のベースライン証跡

- 現行のUI契約テスト `src/ui/ux_operability_regression.test.ts` は、2026-07-15に **32/32** で成功しました。
- このベースラインでは、`role="dialog"`、`aria-modal="true"`、フォーカス可能なパネル起点、Tabの閉じ込め、Escape処理、Narratives/HIL/差分が `SidePanel` ではなく `WorkModePanel` に配置されていることを確認しています。
- これは判断前の証跡であり、AC-1、AC-2、AC-5の完了を意味しません。操作モデルは未承認で、マウス・キーボード操作を対象にした専用Playwrightシナリオも未整備です。

## 4) 受け入れ条件

- [x] AC-1: `ADR-0055` に承認済みの決定と、選択した操作モデルを記録した。
- [x] AC-2: 設計正本、`UX-NAV-01`、`UI-QUALITY-A11Y-02`、`UX-NAV-02` が同じ方式と用語で記述されている。
- [x] AC-3: 5つのタブと対応する `tabpanel` に、選択状態とARIAの関連付けを実装した。
- [x] AC-4: manual activation、矢印キー、Home/End、非表示パネルの状態保持、狭幅表示を実装した。
- [x] AC-5: Playwrightで、マウスによる起動、キーボード移動、Escapeによる終了、フォーカス復帰、DOM契約を検証した。
- [x] AC-6: `validate_active_issue_memos.py`、triage、issue memo単体テストを成功させた。

## 5) 作業分解

- [x] T1: `ADR-0055` に方式を記録し、受理した。
- [x] T2: 設計正本、`UX-NAV-01`、`UI-QUALITY-A11Y-02`、`UX-NAV-02` を同期した。
- [x] T3: 承認方式に必要な意味論を実装した。
- [x] T4: マウス操作とキーボード操作を対象としたPlaywrightの重点テストを追加・更新した。
- [x] T5: 型検査、重点E2E、アクセシビリティスモーク、issue memo検証を実行した。

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

### 完了記録（2026-07-15）

- `ADR-0053` の番号重複を解消するため、作業モードのADRを `ADR-0055` へ移動した。診断バンドルの `ADR-0053` は変更しない。
- `WorkModeTabs.tsx` と `work_mode_tabs.spec.ts` により、5タブ、manual activation、roving `tabIndex`、Home/End、段階Escape、状態保持、390px横スクロールを確認した。
- `a11y_axe_smoke.spec.ts` に作業モードのタブ意味論を含め、tablist由来の延期ルールを残していない。
- `UI-QUALITY-A11Y-02` の作業モード残課題を完了扱いに更新し、本issueもDoneへ変更した。
