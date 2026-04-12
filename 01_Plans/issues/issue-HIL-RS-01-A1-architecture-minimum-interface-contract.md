# Issue Draft: HIL-RS-01 A1 Architecture最小I/F契約固定

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner (Stream B planning)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`
- Expected verification level: `docs-check`

## 1) Objective

A1を「実装タスク」ではなく、A2/A3を制御する **最小I/F契約の状態遷移ゲート** として固定する。

## 2) Mock Contract Snapshot（固定識別子）

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`

## 3) ADR CDC（Phase 2）

- Context:
  - A1はHIL-RS全体の契約基準点であり、ここが曖昧だとA2/A3のOpen判定が不安定になる。
- Decision:
  - Stream BはA1の **契約識別子と遷移条件のみ** を計画文で固定し、設計実体の編集は行わない。
- Consequences:
  - 契約変更要求はA1に集約し、A2/A3はread-only参照に限定される。

## 4) State Transition Contract

- Unlock rule（唯一）:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Decision Queue:
  - `Pending -> Approved | Rejected`
- Prohibited:
  - `Pending` bypass
  - `A1 Done` 前の `A2/A3 Draft -> Open`
  - A2/A3 issue内での固定識別子再定義

## 5) Acceptance Criteria / DoD

- [x] CDCが明文化されている。
- [x] Unlock ruleが一意である。
- [x] 固定識別子がMock snapshotとして明示されている。
- [x] 安全境界後退禁止が明示されている。
- [x] Verify失敗時の3回上限と停止条件が明示されている。

## 6) Serial Phases（各Phase開始時に再Read）

1. Read: 対象5 issue再Read、差分抽出。
2. ADR CDC: Context/Decision/Consequences再確認。
3. Plan: AC/DoD・遷移契約不足を補完。
4. Execute: issue本文のみ更新（契約識別子/遷移/禁止事項）。
5. Verify: validator + rg、自己修復は最大3回。
6. Proceed: Open化可能項目のみ進行、残件はDecision Queueへ戻す。

## 7) Open化条件

- `A1 Status == Done`
- `pendingDecisionQueueCount == 0`
- Fixed identifiers 完全一致
- 安全境界後退要求なし

## 8) Fail-safe

- 3回修復超過 / 未承認決定確定化 / 固定識別子不一致で停止。
