# Issue: QA-MONKEY-15 ja localeで島の既定名が「Island N」になる

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Done
- Source Issue: `MVP-EXIT-01`（人間受入項目の機械代替検証後に実施したモンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/i18n/`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/e2e/first_meaningful_map_mouse_flow.spec.ts`
- Related Backlog: `QA-MONKEY-15`
- Related ADR/Spec: `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`（G3 日本語UI / V0-V1 初回価値）, `04_Documentation/acceptance_check.md`
- Expected verification level: `e2e`

## 課題

日本語UIで「島を作成」すると、島の既定名が **`Island 1`（英語）** になる。この文字列はキャンバス上の島の見出しと右側パネルの「現在の選択」「タイトル」欄に表示され、そのまま `document.json` に保存される。

`MVP-EXIT-01` の出口条件「日本語UI: 主要な操作、状態、警告に未翻訳または内部都合の語が残らない」および `PRODUCT-QA-01` G3 の No-Go条件「主要ボタン、警告、状態に英語や内部語が残る」に該当する。

さらに、島を作ることは `PRODUCT-VALUE-01`（初回価値 = 最初の意味あるカード配置）の到達点そのものである。日本語利用者が最初に作る成果物に英語の既定名が付く。

## 原因

`src/App.tsx` の島生成が、i18nを経由せず英語リテラルを文書へ書き込んでいる。

```ts
function createIslandFromSelection(selectedCardIds: string[], existingIslands: Island[]): Island {
  ...
  title: `Island ${existingIslands.length + 1}`,
```

一方で `canvas.island.default_title`（ja: `島` / en: `Island`）というキーは存在し、`CanvasShell.tsx` と `IslandView.tsx` で **タイトルが空のときのフォールバック**としてのみ使われている。生成時に英語リテラルを実体として書き込むため、このフォールバックが働く余地がない。

## 再現手順

1. `?locale=ja` でアプリを開き、サンプル文書を開く。
2. カードを2枚選択する。
3. ヘッダーの「島を作成」を押す。

観測結果（`main` と `aside` のテキスト）:

```
Island 1 | 選択したカード 2 件から島を作成しました | 島を選択中 | 対象: Island 1 | 選択中の島を表示 | 島: 1
side panel タイトル欄の値: Island 1
```

## 対応方針

判断が必要な点があるため、方針を選んでから実装する。

- **案A（既定タイトルを空にする）**: 生成時は `title: ""` とし、表示は既存の `canvas.island.default_title` フォールバックに任せる。利用者がタイトルを付けるまで locale に応じた表示になり、文書には locale 依存の文字列が入らない。連番を残したい場合は表示側で付ける。
- **案B（生成時にlocaleで解決する）**: 生成時に `t("canvas.island.default_title")` + 連番で `島 1` を書き込む。実装は簡単だが、**文書内容が作成時のlocaleに依存する**ため、`src/i18n/document_locale_invariance.test.ts` が守ろうとしている性質と衝突しないか確認が必要。

実施しないこと: 既存文書に入っている `Island N` の一括書き換え（利用者が付けた名前と区別できないため）。

### 採用判断

案Aを採用する。新規島の `title` は空文字として保存し、表示時に文書内の安定した島順序から連番を求め、localeに応じて `島 N` / `Island N` を組み立てる。これにより文書内容のlocale不変性を維持しつつ、従来の英語表示と連番を保つ。利用者が付けたタイトル、および既存文書に保存済みの `Island N` はそのまま表示し、自動変換しない。

## 予算申告

- 複雑性予算（`ADR-0043`）: N/A
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [x] 案Aまたは案Bを選び、理由を記録する。
- [x] `?locale=ja` で島を作成したとき、キャンバスと右側パネルに英語の既定名が表示されない。
- [x] `?locale=en` の表示が退行しない。
- [x] 文書のlocale不変性に関する既存テスト（`document_locale_invariance.test.ts`）が成功する。
- [x] 既存文書に保存済みの `Island N` を開いても表示が壊れない。

## 検証計画

- 実行する確認: 上記再現手順を ja / en の双方で実行。`vitest run src/i18n/`。島作成を含む既存E2E（`first_meaningful_map_mouse_flow.spec.ts` ほか）。
- 期待結果: ja で英語の既定名が出ない。en が従来どおり。i18n・E2Eに退行なし。

## 検証結果

- `tsc --noEmit`: 成功。
- `vitest run`: 227 files / 1324 tests 成功。locale不変性、日英の派生表示、利用者タイトル、既存 `Island N` の互換性を含む。
- `playwright test e2e/first_meaningful_map_mouse_flow.spec.ts e2e/selection_target_after_island_creation.spec.ts`: 4 tests 成功。日本語の `島 1`、英語の `Island 1`、空タイトルの保存、島作成後の選択対象を実ブラウザで確認。
- `vite build`: 成功。
- `python 01_Plans/docs_check.py`: 成功。

## 補足

- `src/i18n/ui_hardcode_guard.test.ts` はUI表示のハードコードを検出するが、**ドメイン値の生成時に書き込まれる文字列**は対象外だったと考えられる。同種の混入を防げるようガード範囲の拡張を検討する（本issueの必須受入条件には含めない）。
- 調査記録: `03_Implement/frontend/docs/mvp_exit_monkey_test_log_2026-07-29.md`
