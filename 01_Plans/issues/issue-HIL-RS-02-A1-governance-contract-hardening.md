# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening

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
- Status/Priority/Scope/Related ADRを再読。
- Delta log: Return pathをA1一本化し、`Pending bypass` 禁止を強化。

## Phase 2: ADR Consensus
### Context
- RS-02で統治契約を硬化し、誤Open化を防ぐ必要がある。

### Decision
- Hardening baseline:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Consequences
- A1以外への差戻し禁止。
- 未承認事項は確定不可。

### held
- `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持。

## Phase 3: Plan
- AC: fixed keys diff=0 / return path唯一。
- DoD: Go/NoGo判定式一貫 / self-correction<=3。

## Phase 4: Execute
- Go/NoGo式を統一し、禁止遷移を明文化。

## Phase 5: Verify
- docs-check + diff check。

## Phase 6: Proceed / Stop
- Proceed: AC/DoD充足。
- Stop: ドリフト、Pending bypass、未定義競合、self-correction超過。
