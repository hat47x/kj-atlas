# Issue Draft: SEC-EXPORT-BUNDLE-02 SafeModeエクスポートテストが未出荷の経路を検証している

- Type: Security
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/export/bundle_export.ts`, `03_Implement/frontend/src/export/bundle_export.test.ts`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/worker/diagnostics_compute.ts`
- Related ADR/Spec: `ADR-0041`（CVI-1 SafeMode）, `issue-SEC-EXPORT-BUNDLE-01`（document.jsonのSafeMode漏えい、関連するが別問題）
- Expected verification level: `unit`

## 課題

`bundle_export.ts` には2つの独立したエクスポート実装が存在する。

- `buildExportBundle`（`bundle_export.ts:248`、同期実装）
- `buildExportBundleWithWorkers`（`bundle_export.ts:302`、worker経由でdiagnostics/traceを生成し、`integrity.json` も追加で出力する）

`App.tsx`（`:103`, `:9310`）は `buildExportBundleWithWorkers` のみを呼び出しており、実際に出荷されるのはこちらの経路である。`buildExportBundle` は非テストの呼び出し元がリポジトリ全体でゼロ（grep確認済み）。

一方、SafeModeの秘匿化を実際に検証しているテスト——`bundle_export.test.ts:337`「hides unreviewed outline text and diagnostic detail」および `:387-417`「defaults to safe mode... SECRET_TEXT_DO_NOT_LEAK」——は、いずれも出荷されない `buildExportBundle` を呼び出している。出荷経路（`buildExportBundleWithWorkers`）の診断文字列は `worker/diagnostics_compute.ts` の別実装（`buildDiagnosticsMd`）が生成しており、これらのテストは出荷経路のSafeMode漏えいを一切検証していない。

## 論点（人的判断が必要な理由）

以下いずれの方向で解消すべきかは製品判断であり、機械的に決められない。

1. テストの対象を `buildExportBundleWithWorkers` に retarget する（出荷経路を直接検証する形にする）。
2. 2つの実装を統合し、`buildExportBundle` を削除する（worker版に一本化）。
3. `buildExportBundle` を意図的に維持する理由（例: 将来のnon-worker環境向けフォールバック）があるなら、その理由を明文化した上で、出荷経路用の同等テストを別途追加する。

## 影響

現状、SafeModeの中核保証（未レビュー本文・診断詳細の匿名化）について、実際に出荷されるエクスポート経路への直接的な回帰テストが存在しない。`worker/diagnostics_compute.ts` 側の変更（本セッションの別PRで修正した tautological gate のような）が将来再発しても、既存テストスイートは検出できない。

## 解決記録（2026-08-07）

- **対応**: 論点3（出荷経路用の同等テストを追加）を採用。`buildExportBundleWithWorkers`（出荷経路）に対し、SafeMode ONで未レビュー島summaryとカード本文に秘密文字列を含むdocを渡し、`diagnostics.md`・`outline.md`・全文書バンドルに秘密が含まれないことを検証するテストを `bundle_export.test.ts` に追加（「shipped worker path hides unreviewed text and diagnostic detail under SafeMode」）。
- **テストがworker fallback経路を検証する理由**: `DiagnosticsWorkerClient.computeDiagnostics` はworker非利用環境で `computeDiagnostics`（`worker/diagnostics_compute.ts`）を直接呼ぶfallbackを持つため、unit testで出荷経路の `buildDiagnosticsMd` のSafeMode秘匿を実際に検証できる。
- **検証**: frontend 234 files / 1398 tests（+1）pass、typecheck 0 errors。
- Status: Done
