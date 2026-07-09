# Issue Draft: UI-QUALITY-A11Y-03 axe スモークで発見した構造的ARIA課題（未修正・要設計判断）

- Type: Bug / Design decision
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: TBD
- Scope: `03_Implement/frontend/src/canvas/`（role=option/listbox構造）, `03_Implement/frontend/src/ui/MenuBar.tsx`（role=menu構造）, `03_Implement/frontend/src/App.tsx`（h1・DomainStateFilterBarの配色）
- Related Backlog: `UI-QUALITY-A11Y-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-2）, `01_Plans/issues/issue-UI-QUALITY-A11Y-02-per-surface-aria-focus-spec.md`（本Issueの発見元）
- Expected verification level: `e2e`

## 背景

`UI-QUALITY-A11Y-02` の残課題「axe系スモークテストの導入」を実施した際（`e2e/a11y_axe_smoke.spec.ts`、2026-07-09）、axe-core の自動検査で以下4種類の構造的な違反が全面的に見つかった。うち `select-name`/`label`（アクセシブルネーム欠落）は同ラウンドで機械的に修正済みだが、以下4種は**設計判断を要するため未修正**とし、スモークテスト自身も `disableRules([...])` で明示的に除外した（サイレントに握り潰さず、コード内コメントと本Issueで追跡する）。

## 発見内容

### 1. `aria-required-parent`（critical・最多7箇所）

キャンバス上のカードが `role="option"` で描画されるが、`role="listbox"`（またはそれに準ずる親ロール）に包まれていない。KJ法のキャンバスは自由配置のボードであり、線形リストの `listbox` セマンティクスが本当に適切かどうか自体が設計判断を要する（例: `role="grid"`や`role="application"`＋独自キーボード契約の方が実態に近い可能性がある）。`CardView.tsx`/`CanvasShell.tsx` の描画構造全体に関わる。

### 2. `aria-required-children`（critical・1箇所）

`MenuBar.tsx` の「ファイル」メニューの `role="menu"` ドロップダウン内に、`extraContent`（`App.tsx` の `openRecentExtraContent`、最近使ったドキュメントの `<select>` と関連ボタン）が直接の子要素として混在している。ARIA仕様は `role="menu"` の直接子を `menuitem`系ロールに限定するため、`<select>`/`<button>` を `role="none"` でラップするか、この場所自体に生の form 要素を置く設計を見直すかの判断が必要。

### 3. `page-has-heading-one`（moderate・全ページ）

アプリ全体に `<h1>` が一つも存在しない。単一ページのキャンバスアプリのため、どこに（ドキュメントタイトル？ロゴ？視覚的に非表示の見出し？）`h1` を置くべきかは設計判断。

### 4. `color-contrast`（serious・2箇所）

`div[data-panel="domain-detail-filters"] > div > span` が最低コントラスト比を満たさない。配色調整のみで直せる可能性が高く、4種の中では最も軽量だが、他の3件と合わせて発見されたため本Issueにまとめて記録する。

## 非目標

- `UI-QUALITY-A11Y-02` が対象外とした凡例（CanvasLegend）・作業モードタブの `role=tablist` は本Issueの対象外（それぞれ別の理由で別途扱う）。

## 受け入れ条件（案）

- [ ] AC-1: `role=option`/`listbox` 構造について、キャンバスの操作性（ドラッグ配置・自由配置）を損なわない設計を決定し実装する。
- [ ] AC-2: MenuBar の `extraContent` パターンについて、`role=menu` の直接子制約を満たす構造（ラップ or 配置変更）を決定し実装する。
- [x] AC-3: `h1` の配置場所を決定し実装する。
- [x] AC-4: `domain-detail-filters` の該当spanの配色をコントラスト比 4.5:1 以上に調整する。
- [x] AC-5: `e2e/a11y_axe_smoke.spec.ts` の `DEFERRED_RULE_IDS` から対応済みのルールIDを除去する。

## Traceability

- Related: `01_Plans/issues/issue-UI-QUALITY-A11Y-02-per-surface-aria-focus-spec.md`
- Related: `03_Implement/frontend/e2e/a11y_axe_smoke.spec.ts`（`DEFERRED_RULE_IDS` 定数）
- Derived-from: `01_Plans/issues/issue-UI-QUALITY-A11Y-02-per-surface-aria-focus-spec.md`（axe スモーク導入時の発見）

## 対応記録（2026-07-10）

- `Shell`のプロダクト名を実ページ見出しの`h1`へ変更した。
- `DomainStateFilterBar`の補助ラベル色を`#475569`へ変更し、axeの`color-contrast`除外を解除した。
- `aria-required-parent` と `aria-required-children` は、キャンバス選択ロールとメニュー内フォームの意味付けを決めるADR-0052の対象として残した。
