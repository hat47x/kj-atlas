# Issue Draft: QA-MONKEY-02 Provider-none merge candidate fallback

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend`
- Related Backlog: `QA-MONKEY-02`
- Related ADR/Spec: `04_Documentation/e2e_testing.md`, `01_Plans/issues/issue-CE3-patch-workspace-presets.md`, `03_Implement/frontend/src/domain/merge_candidates.ts`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-02
- RequirementStatement: CE3 candidate collection must remain usable in the documented `KJ_ATLAS_LLM_PROVIDER=none` fallback environment.
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=API starts with `KJ_ATLAS_LLM_PROVIDER=none` / 操作=click `Collect candidates` / 期待結果=UI falls back to deterministic local collection without surfacing `Service Unavailable` / 除外=provider contract validation failures.
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- Manual fallback startup uses `KJ_ATLAS_LLM_PROVIDER=none`.
- Monkey test clicked CE3 `Collect candidates` and the UI showed `Service Unavailable`.
- This blocked CE3 monkey coverage for candidate decisions, preset replay, and rollback paths.

## 2) 背景 / Context

- Frontend already had deterministic `collectMergeCandidates` fallback.
- The UI only fell back on 404/405/501 or network errors, while provider-none backend returns 503.
- E2E docs describe CE3 as deterministic heuristic workflow for verification.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Users should not need an LLM to validate merge decision workflows.
- 安全（THREAT_MODEL / SafeMode）: No direct safety regression.
- 企業・行政要件（enterprise_architecture）: Local/no-provider environments must be verifiable.
- 後方互換（schemas）: No schema change; fallback output uses existing contract.

## 4) 提案する解決策 / Proposed solution

- 変更対象: Frontend.
- 変更の最小単位: Treat 503 provider-unavailable responses as fallback-eligible for merge candidate collection.
- 非目標: Masking invalid contract payloads or actual backend 500 errors.

## 5) 受入条件 / Acceptance criteria

- [x] Provider-none 503 does not surface `Service Unavailable` in the UI.
- [x] UI reports deterministic local candidate result.
- [x] Existing merge candidate unit contract remains unchanged.
- [x] `Expected verification level` is satisfied by unit tests plus browser smoke.

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Add 503 to fallback-eligible API statuses for CE3 candidate collection.
- [x] T2 Re-run frontend regression tests.
- [x] T3 Verify browser smoke on the SQLite/provider-none stack.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test`
  - Browser smoke: click `Collect candidates` with API provider none.
- 期待結果:
  - Tests pass.
  - Browser does not show `Service Unavailable`; status becomes deterministic local result.
- 未実施時の理由・代替検証:
  - N/A.

## 8) 代替案 / Alternatives considered

- 代替案A: Change backend provider-none to return 501. Rejected because frontend already owns local fallback decision.
- 代替案B: Always skip API and use local candidates. Rejected to preserve remote provider path when configured.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: A real 503 outage could be hidden by local fallback in this specific feature.
- 影響範囲: Merge candidate collection UI only.
- ロールバック手順: Remove 503 from the fallback-eligible status list.

## 10) Additional context

- ADR化が必要になる条件: CE3 candidate source priorityを「always local」などに変更する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
