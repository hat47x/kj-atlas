# Issue Draft: HIL-RS-01 次フェーズ計画（Human-in-the-loop 可逆統合）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0026`, `ADR-0027`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0001`
- Expected verification level: `docs-check`

## Phase 1: Read
- Status/Priority/Scope/Related ADRを再読。
- Delta log: 判定語彙をA1契約と一致化し、NoGo差戻し先をA1へ固定。

## Phase 2: ADR Consensus
### Context
- RS-01はRS-02の前段であり、状態遷移契約の不一致を許容できない。

### Decision
- Contract Freeze（SSOT）:
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
- Serial protocol（Plan -> Execute -> Verify -> Proceed）を強制。
- A1未完了でA2/A3 Open禁止。

### held
- 追加ADR起案は不要だが、未承認論点は `held` で維持。

## Phase 3: Plan
- AC: 固定キー差分0 / Decision Queue固定遷移 / A2/A3開放条件固定。
- DoD: NoGo差戻し先A1固定 / safeModeDefault=ON維持 / overridePolicy後退禁止。

## Phase 4: Execute
- Next step fixed I/Fをread-only handoffとして確定。

## Phase 5: Verify
- docs-check + diff check。self-correction最大3回。

## Phase 6: Proceed / Stop
- Proceed: AC/DoD充足。
- Stop: 前提崩れ、未定義競合、承認なき確定、self-correction超過。
