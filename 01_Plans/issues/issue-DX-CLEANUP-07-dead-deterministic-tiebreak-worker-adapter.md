# Issue Draft: DX-CLEANUP-07 deterministic tiebreak worker adapter が未使用

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/worker/tiebreak/deterministic_tiebreak_worker_adapter.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

`src/worker/tiebreak/deterministic_tiebreak_worker_adapter.ts` は `runDeterministicTieBreakWorker` を export する完全に実装されたモジュールだが、リポジトリ全体を検索してもこの関数を import する箇所は存在しない（`src/` 全体の grep でゼロ件。自モジュール内の定義のみ）。テスト・worker登録・vite設定・tsconfigにも言及がない。

追加は単一コミット `bfd06d39`（feat(frontend): add deterministic tiebreak module and QA fixtures）で、domain層（`deterministic_tie_break.ts`）と fixture が同一コミットに含まれる。domain層とfixtureは生きているが、この adapter だけが取り残されている。domain層の関数は `DETERMINISTIC_TIE_BREAK_ORDER` / `pickDeterministicTieBreakWinner` / `toReproductionEvidence` で、これらは他モジュールから参照されている（adapter はそれらの薄いラッパー）。

## 対応方針

- 削除する場合: `deterministic_tiebreak_worker_adapter.ts` を削除する。domain層とfixtureは維持する。
- 将来workerとして使う予定がある場合: 少なくとも `vite.config.ts` の worker 登録または App 側の `new Worker(...)` 呼び出しを追加する。

## 受入条件

- [ ] 上記のどちらかを決定し、実施する（削除またはworker登録）。
- [ ] 削除の場合、`git grep -l "deterministic_tiebreak_worker_adapter"` がゼロ件になる。

## 検証計画

- `git grep -rn "runDeterministicTieBreakWorker\|deterministic_tiebreak_worker_adapter" 03_Implement/frontend/src/` が期待どおりの結果。
- `cd 03_Implement/frontend && npx tsc --noEmit` が通る。
