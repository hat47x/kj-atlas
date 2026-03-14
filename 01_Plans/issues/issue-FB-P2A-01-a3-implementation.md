# Issue Draft: FB-P2A-01-A3 Island階層モデル導入 / 実装計画接続

- Type: Feature request
- Status: Ready (A3 Handoff Condition Fixed)
- Priority: P0
- Owner: Stream E
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

- [x] A1/A2の契約ID・ケースIDを使って実装計画へトレース可能。
- [x] Plan→Execute→Verify→Proceedがチェックリスト化されている。
- [x] AC/DoD不足のドラフト提案手順が明文化されている。


## Phase execution log（A3）

### Read sync（Phase開始時）

- `issue-FB-P2A-01-a1-interface-contract.md`
- `issue-FB-P2A-01-a2-mock-validation.md`
- `issue-FB-P2A-01-a3-implementation.md`

### Plan

- A1契約IDとA2ケースIDを実装タスクへトレース可能にマッピングする。
- GoNoGo判定条件（M1/M2 pass, M3/M4 fail, owner確定）を前提条件として固定する。

### Execute

- 実装順序を `schema -> domain model -> persistence roundtrip` で維持する。
- A2の handoff payload を実装チェックリストへ転写する。

### Verify

- `contractVersion=IslandHierarchyContractV1` を契約ロックとして再確認する。
- `ownerOfFix` 未確定ケースが残っていないことを検証する。

### Proceed

- Go判定成立時のみ次タスクへ進行し、NoGo時はA1/A2/A3責務へ即時返却する。

## ADR change handling

- ADR change involved: **No**（A3は既定契約の実装接続であり、ADR改定は不要）
- C/D/C + approval: **N/A**

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


### Stream B execution note（A3 implementation）

- 実装順序を `schema -> domain model -> persistence roundtrip` として最小実装で接続。
  - schema: `IslandHierarchyContractV1` を `projectIslandHierarchyContractV1` で投影
  - domain model: `toIslandHierarchyValidationLog` / `evaluateIslandHierarchyA3GoNoGo` で A2→A3 I/F 固定
  - persistence roundtrip: `validateIslandHierarchyRoundTrip` で JSON roundtrip 後の契約妥当性を検証
- GoNoGo条件を実コードで固定。
  - Go: `M1/M2=pass` かつ `M3/M4=fail` かつ owner確定
  - NoGo: case不足または上記不一致
