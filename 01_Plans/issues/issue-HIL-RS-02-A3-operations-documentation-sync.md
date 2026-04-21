# Issue Draft: HIL-RS-02 A3 Operations Documentation Sync（Contract Reference Only）

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: TBD
- Priority: P1
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Out of scope: `03_Implement/**`, `04_Documentation/**`, 対象7Issue以外
- Dependencies: `ADR-0027`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0027`, `ADR-0028`, `02_Architecture/strict_mode_exception_approval_flow.md`
- Expected verification level: `docs-check`

## Phase 1: Read
- Status/Priority/Scope/Related ADRを再読。
- Delta log: A3はread-only reference onlyを維持。Open条件をA1ゲートで明確化。

## Phase 2: ADR Consensus
### Context
- A3は運用文書同期の参照ノードであり、契約再定義をしてはいけない。

### Decision
- Contract Freeze（read-only）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Sync route固定: `02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md`
- Role vocabulary固定: `Security Officer`, `System Owner`, `Platform Operator`
- D1〜D4固定値は参照専用（A3再定義禁止）。

### Consequences
- A1未完了時A3 Open禁止。
- NoGo時差戻しはA1のみ。

### held
- A3単独での契約改定要求は `held` として却下対象。

## Phase 3: Plan
- AC: fixed keys diff=0 / role語彙固定 / D1〜D4参照固定。
- DoD: A3 Open gateがA1条件に従う / NoGo差戻し先A1一意。

## Phase 4: Execute
- Open/Proceed Gate:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
  - `NoGo = !Go`
  - `a1Status!="Done"` の間は `Draft` 固定。

## Phase 5: Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `git diff --check`
- self-correction最大3回。

## Phase 6: Proceed / Stop
- Proceed: AC/DoD充足時のみ。
- Stop: A1未完了でOpen要求、Pending bypass、未定義競合、self-correction超過。
