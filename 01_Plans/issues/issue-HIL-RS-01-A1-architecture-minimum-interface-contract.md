# Issue Draft: HIL-RS-01 A1 Architecture 最小I/F契約固定

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0026`, `ADR-0027`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`

## Phase 1: Read
- Status/Priority/Scope/Related ADRを再読済み。
- Delta log: 固定キーは整合、NoGo記述をA1差戻しへ一本化。

## Phase 2: ADR Consensus
### Context
- A1契約はRS-01/RS-02両系統の開放ゲートであり、統治判定式を単一化する必要がある。

### Decision
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

### Consequences
- A1未完了時A2/A3 Open禁止。
- NoGo return pathはA1契約Issue固定。

### held
- `HIL-RS-02-GOV-EXCEPTION-01` は `held`。

## Phase 3: Plan
- AC: 固定キー一致 / unlockRule一致 / decisionQueueTransition一致。
- DoD: Go/NoGo判定式一致 / A1差戻し一意 / self-correction<=3。

## Phase 4: Execute
- Go/NoGo:
  - `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
  - `Go = A2A3StartAllowed`
  - `NoGo = !A2A3StartAllowed`
  - `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## Phase 5: Verify
- docs-check + diff check。

## Phase 6: Proceed / Stop
- Proceed: AC/DoD満たす。
- Stop: 前提崩壊、未定義競合、承認なき確定、self-correction超過。
