# Issue Draft: DX-CLEANUP-08 deterministic tiebreak worker adapter の参照源が `src/` 外に偏在

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/worker/tiebreak/deterministic_tiebreak_worker_adapter.ts`, `03_Implement/frontend/tests/tiebreak/deterministic_tie_break.integration.test.ts`, `03_Implement/frontend/tests/tiebreak/vitest.config.tiebreak.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題（訂正版 2026-08-06）

`src/worker/tiebreak/deterministic_tiebreak_worker_adapter.ts` は `runDeterministicTieBreakWorker` を export し、`tests/tiebreak/deterministic_tie_break.integration.test.ts`（3 tests）から import されている。`src/` 配下の本番コードからの参照は無いが、**統合テストから参照されているため削除してはならない**。

**初版の誤り**: `src/` 配下だけを grep して「未使用」と判定し、削除してしまった。`tests/tiebreak/vitest.config.tiebreak.ts` が `include: ["tests/tiebreak/**/*.test.ts"]` で別設定として実行しており、通常の `vitest run`（`src/` を include）では検出されない。この「別設定で実行される統合テスト」が参照していることを見落とした。ファイルは `62dca731~1` から復元済み（2026-08-06）。

## 現状

- ファイルは復元済み。`npx vitest run --config tests/tiebreak/vitest.config.tiebreak.ts` で 3 tests pass を確認。
- 本issueの本来の論点は「本番コードから参照されない adapter を統合テストだけが使っている構造」であり、削除ではなく**配置の妥当性**の検討対象。

## 対応方針（再考案）

- (a) 統合テストが adapter の薄いラッパー経由で domain 関数を検証するのが意図的なら、その旨をテストにコメントで明記し、現状維持。
- (b) adapter が不要なら、統合テストを domain 関数（`pickDeterministicTieBreakWinner` 等）を直接呼ぶ形へ書き換えてから adapter を削除する。
- どちらも本issueの受入条件は「削除または利用を決定し、決定後の整合性を確認する」。

## 受入条件

- [ ] (a) 現状維持または (b) テスト書き換え＋削除のどちらかを決定し、実施する。
- [ ] 実施後、`npx vitest run --config tests/tiebreak/vitest.config.tiebreak.ts` と `npx vitest run` が両方通る。

## 検証計画

- `cd 03_Implement/frontend && npx vitest run --config tests/tiebreak/vitest.config.tiebreak.ts`
- `cd 03_Implement/frontend && npx tsc --noEmit`
