# Issue Draft: QA-MONKEY-04 Worker golden line-ending portability

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/worker`
- Related Backlog: `QA-MONKEY-04`
- Related ADR/Spec: `04_Documentation/e2e_testing.md`, `03_Implement/frontend/src/worker/worker_golden.test.ts`
- Expected verification level: `unit`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-04
- RequirementStatement: Worker golden tests must be stable across Windows CRLF and LF working trees.
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=Windows checkout / 操作=`npm run test` / 期待結果=golden markdown comparisons pass regardless of CRLF fixture checkout / 除外=semantic golden content changes.
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A

## 1) 課題 / Problem statement

- Full frontend test run failed on Windows in `worker_golden.test.ts`.
- The computed markdown used LF while golden fixtures were read with CRLF.
- The failures blocked local validation even though semantic output matched.

## 2) 背景 / Context

- Golden fixtures are markdown files and may be checked out with platform-native line endings.
- Worker outputs are generated with LF.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Contributors need deterministic local verification.
- 安全（THREAT_MODEL / SafeMode）: No direct safety impact.
- 企業・行政要件（enterprise_architecture）: Improves reproducible verification on Windows workstations.
- 後方互換（schemas）: Test-only change.

## 4) 提案する解決策 / Proposed solution

- 変更対象: Frontend tests.
- 変更の最小単位: Normalize CRLF to LF when reading worker golden fixtures.
- 非目標: Rewriting fixture contents or changing worker output formatting.

## 5) 受入条件 / Acceptance criteria

- [x] Worker golden tests pass on Windows.
- [x] Full frontend test suite passes.
- [x] No production code changes are required for this issue.

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Add `readGolden` helper that normalizes line endings.
- [x] T2 Use helper for markdown golden reads.
- [x] T3 Re-run targeted and full frontend tests.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- src/worker/worker_golden.test.ts`
  - `npm run test`
- 期待結果:
  - Worker golden and full frontend tests pass.
- 未実施時の理由・代替検証:
  - N/A.

## 8) 代替案 / Alternatives considered

- 代替案A: Add `.gitattributes` for markdown fixtures. Rejected as broader repo policy.
- 代替案B: Change worker output to CRLF on Windows. Rejected because exported markdown should remain deterministic.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: A meaningful CRLF-only golden difference would be hidden.
- 影響範囲: Worker golden tests only.
- ロールバック手順: Revert `readGolden` helper usage.

## 10) Additional context

- ADR化が必要になる条件: Repository-wide line-ending policy is changed.

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
