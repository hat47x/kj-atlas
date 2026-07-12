# ADR-0052: キャンバス選択とメニュー内フォームのARIA意味付け

- Status: Proposed
- Date: 2026-07-10
- Deciders: Productization Program Owner / UX Lead / Project Maintainers
- Scope: `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/src/canvas/CanvasShell.tsx`, `03_Implement/frontend/src/ui/MenuBar.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/e2e/a11y_axe_smoke.spec.ts`

## Context

axeの横断スモークテストで、現在のUIに2つのARIA構造上の課題が残っている。

1. キャンバス上のカードは自由配置・ドラッグ・複数選択を行う要素だが、現在は `role="option"` を使っており、`role="listbox"` の親を持たない。
2. Fileメニューの `extraContent` に最近のドキュメント選択や操作ボタンが含まれ、`role="menu"` の直接の子としてフォーム要素が現れる。

どちらも属性を追加するだけでは解決しない。listboxは選択肢一覧の意味を、menuはコマンド一覧の意味を持つため、自由配置キャンバスやフォーム付きメニューへ機械的に適用すると、支援技術へ誤った操作モデルを伝える可能性がある。

## Decision

このADRがAcceptedされるまで、2つのARIA構造を機械的に変更しない。`UI-QUALITY-A11Y-03` では、該当するaxeルールを明示的に延期し、設計課題として追跡する。

次の候補を、実装前に利用者の操作モデルとキーボード仕様を比較する。

- キャンバス: `listbox/option`を維持して親ロールを追加する、カードを`button/aria-pressed`へ移行する、または自由配置キャンバスとして別の説明・選択ロールを採用する。
- メニューバー: フォームをメニュー外の兄弟領域へ移す、フォームを`role="none"`のラッパー内に置く、またはメニューをコマンド部分と補助操作部分へ分離する。

採用案では、マウス操作、Tab/矢印/Enter/Space/Escape、スクリーンリーダーの読み上げ、ドラッグ中のフォーカス保持、モバイル幅の表示を同じE2E仕様で検証する。カードの複数選択と島作成の単一主対象モデルは変更しない。

## Non-goals

- このADRでは `role="application"` を導入しない。
- axeの警告を無言で無効化しない。延期するルールIDと判断理由をテスト・issueに残す。
- 見出し構造、コントラスト、フォームラベルなど、設計判断を要しないa11y課題をこのADRへ戻さない。

## Consequences

- 短期的には、axeスモークに2つの明示的な除外が残る。
- 誤ったlistbox/menu意味付けによるキーボード操作の混乱を避けられる。
- Accepted後は、候補の比較、代表操作のE2E、支援技術による人間確認を含む実装issueへ分割できる。

## Traceability

- Related: `01_Plans/issues/issue-UI-QUALITY-A11Y-03-structural-aria-findings.md`
- Related: `01_Plans/issues/issue-UI-QUALITY-A11Y-02-per-surface-aria-focus-spec.md`
- Related: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Related: `03_Implement/frontend/e2e/a11y_axe_smoke.spec.ts`

## 追記 2026-07-12: 作業モードタブの role=tablist 判断（C-5）

Claude Design 実装照合レビュー（拡張提案 P21、2026-07-11）が作業モード面の中身について
「タブは role=tablist、矢印キーで移動、5タブ（差分／選択マージ／AI提案／診断／文章化）」の
完全設計を提示した。これにより本ADRのメニュー内フォームに関する論点（項目2）は変更なく
Proposed のままだが、作業モードタブに関する論点（項目1と重なる部分、`UI-QUALITY-A11Y-02` の
C-5残課題）は設計判断が到着したものとして扱い、実装Issue
`01_Plans/issues/issue-UX-NAV-02-work-mode-tab-content-full-design.md` を起票した。
本ADR自体のAcceptedはまだ人間の受理を要するが、実装検討の材料は揃った。
