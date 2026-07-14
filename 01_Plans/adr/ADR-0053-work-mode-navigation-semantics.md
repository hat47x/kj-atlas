# ADR-0053: 作業モードのナビゲーション意味論

- Status: Proposed
- Date: 2026-07-15
- Deciders: Productization Program Owner / UX Lead / Project Maintainers
- Scope: `02_Architecture/design/`, `03_Implement/frontend/src/ui/WorkModePanel.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/e2e/`

## 背景

作業モードについて、設計要求では5つの高度機能をタブとして配置し、`role="tablist"` を付与する案が示されています。一方、現在の実装は、画面全体を覆う1つの `role="dialog"` の中に、複数の高度機能を積み重ねて表示する、1つのスクロール領域です。文章化、HILワークフロー、マージ・パッチワークスペース、批評、差分の各機能が、この領域内に順番に表示されます。

したがって、現在の実装はタブリストを提供していません。操作モデルを変更せずに `role="tablist"` を追加すると、キーボード利用者やスクリーンリーダー利用者に実際とは異なる操作方法を伝えてしまいます。タブへ変更する場合は、一部の機能が隠れること、選択中タブの状態管理が必要になること、キーボード操作の契約を新たに定義することを受け入れる必要があります。`ADR-0052` は意図的にこの作業モードの判断を対象外としています。

## 決定（提案）

本ADRでは、次の方針を採用することを提案します。Decidersによる承認までは、提案段階として扱います。

1. MVPから製品化へ移行する段階では、作業モードを1つのモーダルダイアログとして維持し、高度機能を見出し付きのセクションとして積み重ねて表示します。
2. UIが実際に1つのパネルを切り替えるタブ操作へ変更されない限り、`role="tablist"`、`role="tab"`、`aria-selected` は追加しません。
3. 作業モードのタイトルをダイアログ名として扱います。各高度機能には、利用者が視認できる見出しを付け、独立した手順を持つ機能には安定した領域境界を設けます。
4. 設計正本では、5つの高度機能を情報設計上の分類として説明し、実際のタブ操作を必須とする契約とは説明しません。
5. マウスとキーボードによるセクション間の移動、Escapeによる終了、起点へのフォーカス復帰、および実際には存在しないタブ意味論を付与していないことをE2E契約として検証します。

将来、文字どおりのタブインターフェースを採用することは可能です。その場合は、左右矢印、Home/End、選択中タブの読み上げ、非表示パネルへのフォーカス移動、モバイル表示を含む別の操作変更として評価します。

本ADRは、キャンバスの選択ロールとメニューのARIA意味付けを扱う `ADR-0052` の決定を変更しません。

## 影響

- 判断中も、既存のダイアログとフォーカストラップの実装を安定して維持できます。
- 非表示のタブパネルを導入せず、キーボード利用者は通常のTab操作で表示中の高度機能を順番に利用できます。
- 設計要求と実装の関係を明文化でき、暗黙の乖離を防げます。
- 将来タブへ再設計する場合は、別の判断とE2E契約が必要です。ARIA属性だけを追加する変更では対応しません。
- 本ADRが承認されるまでは、`UI-QUALITY-A11Y-02` の作業モード意味論に関する残課題を未完了として扱います。

## 対象外

- 本ADRでは、作業モードの画面実装を変更しません。
- 各高度機能の詳細な表示順やレイアウトは決定しません。
- AI機能、providerの挙動、SafeMode、共有・エクスポート境界は変更しません。

## 追跡関係

- Related: `01_Plans/issues/issue-UI-QUALITY-A11Y-02-per-surface-aria-focus-spec.md`
- Related: `01_Plans/issues/issue-UI-QUALITY-A11Y-04-work-mode-navigation-semantics.md`
- Related: `01_Plans/issues/issue-UX-NAV-01-work-mode-surface-navigation-hierarchy.md`
- Related: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Related: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`
- Related: `01_Plans/adr/ADR-0052-canvas-and-menu-aria-semantics.md`
- Source: `02_Architecture/design/design-request-2026-07-round3.md`
- Source: `02_Architecture/design/design-qa-checklist.md`

---

## 起票チェックリスト

- [x] Status、日付、Deciders、Scopeを記載した。
- [x] 背景、決定案、影響、対象外、追跡関係を記載した。
- [x] 提案する積層セクション方式と、代替案のタブ方式を区別して記載した。
- [ ] Productization Program OwnerとUX Leadが決定案を承認した。
- [ ] 関連issueに最終決定と検証結果を記録した。
