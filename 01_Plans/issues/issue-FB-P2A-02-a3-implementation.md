# Issue Draft: FB-P2A-02-A3 Collapse/Expand操作 / 実装計画接続

- Type: Feature request
- Status: Ready (A3 Handoff Condition Fixed)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`, `issue-FB-P2A-02-a2-mock-validation.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1/A2契約を逸脱せず、Collapse/Expand実装計画へ接続する。
- Phase: `A3 Implementation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: integration
- DecisionStatus: Fixed

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - `isCollapsed` と `hidden*Ids` の更新責務を分離して作業計画化。
2. **Execute**
   - `state transition -> render filter -> hit-test filter` の順で設計反映。
3. **Verify**
   - A2 mockCaseを使って遷移前後の整合をチェック。
4. **Proceed**
   - GoNoGoを満たした観点のみ次タスクへ進行。

## Non-deviation rules

- A1契約をA3で再解釈しない。
- A2 Failケースを未解決のまま先送りしない。
- AC/DoD不足を検知した場合は、先にドラフト提案を追記して合意後に進行する。

## Acceptance criteria

- [ ] A1/A2契約IDで実装計画トレースが可能。
- [ ] Plan→Execute→Verify→Proceedの順序が固定される。
- [ ] AC/DoD不足時のドラフト提案手順が明文化される。


## A2→A3 接続条件（確定）

- ContractLock: `IslandVisibilityContractV1`（A1定義から変更禁止）
- Required input from A2:
  - `contractVersion=IslandVisibilityContractV1`
  - `mockCaseId in {M1,M2,M3,M4}`
  - `validationResult`
  - `ownerOfFix`
- GoNoGo判定:
  - Go: `M1/M2/M3=pass` かつ `M4=fail`、責務が確定。
  - NoGo: 判定不一致、または責務未確定。

## 実装トレース最小単位

| traceKey | source | destination |
|---|---|---|
| `RQ-2A-02` | A1 RequirementID | A3 task grouping key |
| `M1..M4` | A2 mockCaseId | A3 verification checklist |
| `ownerOfFix` | A2 failure routing | A3 backlog split (A1/A2/A3) |

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- 自己修復が3回連続で失敗、またはA1/A2契約リンク不整合を検出した場合は停止して指示待ち。
