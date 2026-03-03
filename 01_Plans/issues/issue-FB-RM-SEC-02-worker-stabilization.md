# Issue Draft: FB-RM-SEC-02 Worker安定化（bundle zip を off-main-thread へ移管）

- Type: Security / Process
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/worker/`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/export/*.test.ts`, `01_Plans/adr/ADR-0007-future-backlog.md`, `01_Plans/issues/README.md`
- Related Backlog: `FB-RM-SEC-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0007-future-backlog.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Expected verification level: `integration`

## 1) 課題 / Problem statement

- Bundle export の zip 圧縮はメインスレッドで実行され、ドキュメント規模次第で UI 応答を阻害する。
- 既存の diagnostics/trace/diff は worker 経路を持つが、zip 生成は off-main-thread 化されていない。

## 2) 提案する解決策 / Proposed solution

- `bundle_zip.worker.ts` + `bundle_zip_client.ts` を追加し、zip 生成を worker へ移管する。
- Worker 非利用時は既存の main-thread fallback を維持し、動作互換を保つ。
- Export フローに cancellation/progress を接続し、UI から中断可能にする。

## 3) 受入条件 / Acceptance criteria

- [x] zip 生成が worker 経路で実行可能。
- [x] worker 利用不能時に fallback で zip 生成が継続。
- [x] abort 時に cancelled として扱える。
- [x] `bundle_export.test.ts` で worker/fallback/cancel を回帰固定。
- [x] `FB-RM-SEC-02` の状態が `01_Plans` 文書に反映される。

## 4) 実装タスク分解 / Task breakdown

- [x] T1 `bundle_zip_protocol.ts` を追加。
- [x] T2 `bundle_zip.worker.ts` を追加。
- [x] T3 `bundle_zip_client.ts` を追加。
- [x] T4 `bundle_export.ts` の zip 生成経路を client 経由へ置換。
- [x] T5 `App.tsx` で zip 進捗表示/キャンセル扱いを同期。
- [x] T6 `bundle_export.test.ts` に worker/fallback/cancel テストを追加。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- src/export/bundle_export.test.ts`
  - `npm run test -- src/worker/diff_client.test.ts src/worker/trace_client.test.ts src/worker/diagnostics_client.test.ts`
  - `npm run typecheck`
  - `npm run test:regression-guards`
- 期待結果:
  - bundle zip 経路の worker/fallback/cancel がテストで固定される。
  - 既存 worker client 群の回帰がない。

## 6) Progress log

- 2026-02-28: `bundle_zip` worker/client/protocol を追加し zip 生成を off-main-thread 化。
- 2026-02-28: `buildBundleZipBlob` を worker client 経由に更新し、fallback/cancel を実装。
- 2026-02-28: `App.tsx` の bundle export へ zip 進捗と cancellation handling を反映。
- 2026-02-28: `bundle_export.test.ts` に worker/fallback/cancel 回帰テストを追加し、関連テストを実行して完了確認。
