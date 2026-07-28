# Issue Draft: DX-CLEANUP-06 DiffPanelコンポーネントが未使用の可能性

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/DiffPanel.tsx`, `03_Implement/frontend/src/ui/DiffPanel.test.ts`, `03_Implement/frontend/src/ui/i18n_equivalence.integration.test.ts`, `03_Implement/frontend/src/i18n/ui_hardcode_guard.test.ts`, `03_Implement/frontend/src/App.tsx`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

`ui/DiffPanel.tsx:59` は完全に実装された、i18n対応・SafeMode対応のReactコンポーネントを export している（`diff.panel.*` キーが各localeファイルに約33件存在）。しかし `App.tsx:165` がimportしているのは `ReviewDiffPanel`（`./ui/ReviewDiffPanel`）のみで、`DiffPanel` は `App.tsx` からも他の本番コードからも一切importされていない（リポジトリ全体grepで確認、`ReviewDiffPanel`/`structuralDiffPanel` との部分一致誤検出も除外済み）。

`ReviewDiffPanel` への移行後に削除し忘れた残骸である可能性が高い。ただし、3つのテストファイル（`ui/DiffPanel.test.ts`、`ui/i18n_equivalence.integration.test.ts:10,254-260`、`i18n/ui_hardcode_guard.test.ts:33`）が引き続きこのコンポーネントを検証しており、テストスイートが「このUIは生きている」という誤った安心感を与えている。

## 論点（人的判断が必要な理由）

- `DiffPanel` が本当に不要（`ReviewDiffPanel` に完全代替済み）なのか、それとも今後の再利用を見越して意図的に残されているのか、コードだけでは判断できない。
- 削除する場合、コンポーネント本体・専用テスト3件・専用i18nキー（`diff.panel.*`、両locale約33件ずつ）を一括で除去する必要があり、影響範囲の最終確認は人的判断が望ましい。

## 影響

低リスク（未使用コードによるテスト誤検知）だが、削除すればコードベースの保守対象が減り、i18nキー数も削減できる。
