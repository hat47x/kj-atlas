# Issue: QA-MONKEY-14 島エディタの入力欄が未ラベルでaxe criticalに該当する

- Type: Bug
- Status: Done
- Source Issue: `MVP-EXIT-01`（人間受入項目の機械代替検証後に実施したモンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/src/canvas/CardView.accessibility.test.ts`, `03_Implement/frontend/e2e/a11y_axe_smoke.spec.ts`
- Related Backlog: `QA-MONKEY-14`
- Related ADR/Spec: `01_Plans/issues/done/issue-MVP-EXIT-01-productization-readiness.md`, `01_Plans/issues/done/issue-UI-QUALITY-A11Y-07-card-inline-editor-missing-accessible-name.md`
- Expected verification level: `e2e`

## 課題

島を選択している状態で axe を実行すると、**impact `critical` の `label`（Form elements must have labels）が2件**検出される。`MVP-EXIT-01` の出口条件「accessibility: 自動axeで既知の重大違反がなく」に反する。

原因は、右側パネルの島エディタで `<label>` が入力欄と関連付けられていないこと。`htmlFor` も無く、`<label>` が `<input>` を包んでもいないため、視覚的にはラベルが見えているのに accessible name は空になる。

```tsx
// src/ui/SidePanel.tsx 付近
<label style={{ ... }}>ID</label>
<input type="text" readOnly value={selectedIsland.id} ... />   // ← name が空

<label style={{ ... }}>{t("side_panel.island_editor.title_label")}</label>
<input type="text" value={selectedIsland.title ?? ""} ... />    // ← name が空
```

同じファイルの `parent` の `<select>` には `aria-label` が付いており、同一パネル内で扱いが揃っていない。

同じ書き方は選択カードの `canonicalId` 欄（`SidePanel.tsx`）にもある。こちらは `selectedCard.canonicalId` が存在する文書でのみ描画されるため、今回の実行では実画面での再現を取れていない（ソース上の同型と判断）。

利用者への影響: スクリーンリーダー利用者は、島の**タイトル編集欄**が何の入力欄か分からない。島のタイトルは共有成果物にそのまま載るため、内容を確認・修正する経路が音声だけでは辿れない。

## 再現手順

1. `?locale=ja` でアプリを開き、サンプル文書を開く。
2. カードを2枚選択し、ヘッダーの「島を作成」を実行する（作成した島が自動選択される）。
3. 右側パネルに島エディタが表示された状態で axe（`wcag2a, wcag2aa, wcag21a, wcag21aa`）を実行する。

観測結果:

```
violations: 1
 [critical] label: Form elements must have labels (2件)
   例: <input type="text" readonly="" value="3c90c349-79e2-41f9-b7d6-bb1e3dd4a391" ...>
```

DOM側の確認:

```
NAMELESS in aside:
 { tag: "input", type: "text", value: "828f6a6c-…", readonly: true,  precedingLabelText: "ID" }
 { tag: "input", type: "text", value: "Island 1",   readonly: false, precedingLabelText: "タイトル" }
```

## 自動検査が見逃していた理由

`e2e/a11y_axe_smoke.spec.ts` が走査するのは次の8状態で、**島を選択した状態が含まれていない**。

start panel / カード選択 / 凡例 / 共有パネル / 作業モード / エージェント依頼 / エージェント応答取り込み / メニューバー

`UI-QUALITY-A11Y-07`（カード本文インライン編集欄の無名）も同じ理由（編集中の状態を走査していない）で残っていた。単発の欠陥ではなくカバレッジの穴として扱う。

## 対応方針

- 実施すること:
  - 島エディタの `ID` 欄・`タイトル` 欄とカードの `canonicalId` 欄を `<label htmlFor>` + `id` で関連付けた。
  - `a11y_axe_smoke.spec.ts` に「島を選択した状態」と「カード本文インライン編集中の状態」を追加した。
  - 追加したインライン編集状態で既知の `aria-prohibited-attr` が顕在化したため、未レビュー標識へ `role="img"` を付与し、既存の見た目と音声ラベルを維持した。カード名から状態を分離する残課題は `QA-MONKEY-16` の範囲に残す。
- 実施しないこと:
  - 島エディタの項目構成やレイアウトの変更。
  - `ID` 欄を非表示にすること（表示可否は別途 `CARD-META-UI-01` の範囲）。

## 予算申告

- 複雑性予算（`ADR-0043`）: N/A（表示要素の増減なし）
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [x] 島を選択した状態で axe の `label` 違反が0件になる。
- [x] 島の `ID` 欄・`タイトル` 欄の accessible name が、画面上の見出し文言と一致する。
- [x] `a11y_axe_smoke.spec.ts` が島選択状態とインライン編集状態を走査し、成功する。
- [x] 既存のaxe対象8状態に退行がない。

## 検証結果

- `playwright test e2e/a11y_axe_smoke.spec.ts`: `10 passed`。追加2状態を含めaxe violations 0件。
- `playwright test e2e/canvas_focus_order.spec.ts e2e/retention_keyboard_shortcuts.spec.ts`: `5 passed`。
- `vitest run`: `226 files / 1320 tests passed`。
- `tsc --noEmit`: pass。
- `vite build`: pass（既知のchunk-size warningのみ）。
- `git diff --check`（対象ファイル）: pass。

## 補足

- 同じモンキー実行で、カードのコンテキストメニュー `[role="menu"]` に accessible name が無いことも観測した（`aria-label` / `aria-labelledby` いずれも無し）。axeのWCAGルールでは検出されないため本issueの必須受入条件には含めないが、上記の修正と同時に付けるのが自然。
- 調査記録: `03_Implement/frontend/docs/mvp_exit_monkey_test_log_2026-07-29.md`
