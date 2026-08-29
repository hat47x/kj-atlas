# Issue: QA-MONKEY-21 カードのコンテキストメニューへキーボードフォーカスが移らず名前もない

- Type: Bug / Accessibility
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/ContextMenu.tsx`, `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`, `03_Implement/frontend/src/ui/ux_operability_regression.test.ts`
- Related Backlog: `QA-MONKEY-21`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）, `01_Plans/issues/done/issue-QA-MONKEY-14-island-editor-fields-unlabeled-axe-critical.md`
- Expected verification level: `e2e`

## 課題

カードを右クリックすると`role="menu"`が表示されるが、実操作で次を確認した。

- メニューには`aria-label`も`aria-labelledby`もない。
- 表示直後も`ArrowDown`後も、フォーカスされた`menuitem`は0件で、フォーカスはカード側に残る。
- `ContextMenu.tsx`はEscapeをwindowで監視するだけで、初期focus、ArrowUp/Down、Home/Endの処理を持たない。

視覚的にはメニューが表示されても、キーボード利用者はメニュー項目へ作業文脈を移せない。既存の`MenuBar`は同じARIA menu系UIで矢印移動・Home/End・Escape focus returnを実装済みであり、操作契約が不統一である。

## 対応方針

- `ContextMenu`へ用途を示すaccessible nameを付ける。
- 表示時に最初の有効項目へfocusし、ArrowUp/Downを循環、Home/Endを端へ移動する。
- Escapeでは閉じた後に、表示前にfocusされていた要素へ戻す。外側pointer clickでは利用者が新たに選んだ対象からfocusを奪わない。
- disabled itemをfocus対象から除外し、項目実行・SafeMode・文書変更ロジックは変えない。

三要素牽制: 業務上はポインタを使えない利用者にも既存操作を提供する。データ設計と保存境界は不変。機能上は既存メニューのfocus状態遷移だけをWAI-ARIA系の既存`MenuBar`パターンへ揃え、操作内容・権限・SafeMode判定は変更しない。新しい製品判断ではないためADRは不要。

## 受入条件

- [x] role=menuにaccessible nameがある。
- [x] 表示時に最初の有効menuitemへfocusする。
- [x] ArrowUp/Down、Home/Endで有効menuitem間を移動できる。
- [x] Escapeで閉じ、表示前のfocusへ戻る。
- [x] 外側pointer clickはメニューだけを閉じ、クリック先のfocusを奪わない。
- [x] disabled itemはfocus・実行対象にならない。

## 検証計画

- `monkey_adversarial_probes.mjs` A3/A10でEscapeとキーボードfocusを実画面確認する。
- `ux_operability_regression.test.ts`へContextMenuのsource contractを追加する。
- frontend typecheck、対象unit test、docs-check、active issue validatorを実行する。

## 対応結果（2026-08-16）

- `ContextMenu`へ日英のaccessible nameを追加した。
- 有効項目だけを対象に、表示時の先頭focus、ArrowUp/Down循環、Home/End移動を実装した。各menuitemはroving操作用に`tabIndex=-1`とし、disabled itemは候補から除外する。
- カードのコンテキストメニューを開いたtriggerをApp側で保持し、Escape時にその実DOMへfocusを戻す。外側pointer clickは従来どおり`onClose`だけを行い、focus復帰を実行しない。
- 修正前A10: `menu名=(なし) / open時focus=0 / ArrowDown後focus=0`。
- 修正後A10: `menu名=キャンバス操作メニュー / open時=カードを編集 / ArrowDown後=関係線でつなぐ / Escape閉鎖=true / focus復帰=true`。
- 全明示プローブ10件: 10 `ok` / 0 `SUSPECT`。
- frontend typecheck成功。`ux_operability_regression`とi18n key/catalogの対象3 files・39 tests成功。
- SafeMode、項目の実処理、文書保存・共有・import境界は変更していない。
