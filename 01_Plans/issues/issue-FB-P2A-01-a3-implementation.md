# Issue Draft: FB-P2A-01-A3 Island階層モデル導入 / 実装計画接続

- Type: Feature request
- Status: Ready (A3 Handoff Condition Fixed)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-01-a1-interface-contract.md`, `issue-FB-P2A-01-a2-mock-validation.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: A1/A2契約を逸脱せず、実装計画へ接続する。
- Phase: `A3 Implementation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: integration
- DecisionStatus: Fixed

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - A1必須項目とA2検証結果を実装タスクへマッピングする。
2. **Execute**
   - 変更順を `schema -> domain model -> persistence roundtrip` で固定する。
3. **Verify**
   - A2 handoff payloadの各ケースを実装観点で再照合する。
4. **Proceed**
   - GoNoGo判定を満たした項目のみ次タスクへ進める。

## Non-deviation rules

- A1のRequired fields/InvariantsをA3で再定義しない。
- A2でFailとなったケースを未解決のまま「既知課題」扱いで先送りしない。
- AC/DoD不足を検知した場合は、先にドラフト提案を追記してから進行する。

## Acceptance criteria

- [ ] A1/A2の契約ID・ケースIDを使って実装計画へトレース可能。
- [ ] Plan→Execute→Verify→Proceedがチェックリスト化されている。
- [ ] AC/DoD不足のドラフト提案手順が明文化されている。


## A2→A3 接続条件（確定）

- ContractLock: `IslandHierarchyContractV1`（A1定義から変更禁止）
- Required input from A2:
  - `contractVersion=IslandHierarchyContractV1`
  - `mockCaseId in {M1,M2,M3,M4}`
  - `validationResult`
  - `ownerOfFix`
- GoNoGo判定:
  - Go: `M1/M2=pass` かつ `M3/M4=fail` で責務が確定している。
  - NoGo: 上記を満たさない、または責務未確定。

## 実装トレース最小単位

| traceKey | source | destination |
|---|---|---|
| `RQ-2A-01` | A1 RequirementID | A3 task grouping key |
| `M1..M4` | A2 mockCaseId | A3 verification checklist |
| `ownerOfFix` | A2 failure routing | A3 backlog split (A1/A2/A3) |

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-01-a1-interface-contract.md`
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- 自己修復が3回連続で失敗、またはA1/A2契約リンク不整合を検出した場合は停止して指示待ち。
