# Issue Draft: DX-CLEANUP-06 DiffPanelコンポーネントが未使用の可能性

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/DiffPanel.tsx`, `03_Implement/frontend/src/ui/DiffPanel.test.ts`, `03_Implement/frontend/src/ui/i18n_equivalence.integration.test.ts`, `03_Implement/frontend/src/i18n/ui_hardcode_guard.test.ts`, `03_Implement/frontend/src/App.tsx`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

`ui/DiffPanel.tsx:59` は完全に実装された、i18n対応・SafeMode対応のReactコンポーネントを export している（`diff.panel.*` キーが各localeファイルに約33件存在）。しかし `App.tsx:165` がimportしているのは `ReviewDiffPanel`（`./ui/ReviewDiffPanel`）のみで、`DiffPanel` は `App.tsx` からも他の本番コードからも一切importされていない（リポジトリ全体grepで確認、`ReviewDiffPanel`/`structuralDiffPanel` との部分一致誤検出も除外済み）。

`ReviewDiffPanel` への移行後に削除し忘れた残骸である可能性が高い。ただし、3つのテストファイル（`ui/DiffPanel.test.ts`、`ui/i18n_equivalence.integration.test.ts:10,254-260`、`i18n/ui_hardcode_guard.test.ts:33`）が引き続きこのコンポーネントを検証しており、テストスイートが「このUIは生きている」という誤った安心感を与えている。

## 調査結果（2026-08-05）

`issue-UX-NAV-02-work-mode-tab-content-full-design.md`（Status: Done、2026-07-13完了）が診断タブの実装を確定させており、「ReviewDiffPanel/HilRsRediffPreview＝差分...をそのまま移設」と明記して `ReviewDiffPanel`（`DiffPanel` ではない）を名指ししている。全ての受入項目がチェック済みでテスト・e2e検証も記録済みの完了した設計判断であり、これを覆す後発文書は存在しない。DiffPanelとReviewDiffPanelは機能的に別物（前者は`DiffResult`のカード/島/関係要約/読み順の増減差分表示、後者は`MergeItem[]`のチェックリスト）だが、その差分表示機能の生きた代替はApp.tsx上に存在しない＝単に不要な機能として扱われている。

## 対応

以下を削除した。

- `03_Implement/frontend/src/ui/DiffPanel.tsx`、`03_Implement/frontend/src/ui/DiffPanel.test.ts`（全体削除）
- `03_Implement/frontend/src/ui/i18n_equivalence.integration.test.ts`: DiffPanel importと専用テストケース、`buildDiffProps()`
- `03_Implement/frontend/src/i18n/ui_hardcode_guard.test.ts`: DiffPanel専用ガードケース
- `03_Implement/frontend/src/i18n/translate.test.ts`: 課題記載のスコープ外だが、`diff.panel.*` キーに依存する専用テストケースを発見・削除（削除しないとキー削除で壊れる）
- `diff.panel.*` i18nキー（ja/en各33件）

## 影響

未使用コードとその誤った安心感を与えるテストが解消された。WSL環境でtypecheck・関連5テストファイル（83/83）を確認、CI（Node 20、`.nvmrc`）を全体テストの権威とする。
