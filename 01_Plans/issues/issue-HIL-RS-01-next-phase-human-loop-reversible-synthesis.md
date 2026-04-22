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
- Non-target file policy: 対象7Issue以外は不干渉

## Phase 1: Read
- Extracted: Status=`Open`, Priority=`P1`, Scope=`planning only`, Dependencies=`A1 -> A2 -> A3`。
- Delta log（現値）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
- 事前想定との差分: なし（Proceed可）。

## Phase 2: ADR/CDC Consensus
### Context
- RS-01はRS-02の前段であり、状態遷移契約の不一致を許容しない。

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
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Consequences
- A1未完了でA2/A3 Open禁止。
- Plan -> Execute -> Verify -> Proceed の直列運用を固定。

### held
- 未承認事項は `held` のまま固定（確定扱いしない）。

## Phase 3: Plan
- 対象差分意図: RS-01の開放条件をA1 SSOTへ揃える。
- 非対象不干渉: 7Issue外は編集しない。
- AC/DoD
  - AC: fixed keys差分0 / decisionQueueTransition固定 / NoGo return path一意。
  - DoD: safeModeDefault=ON維持 / overridePolicy後退なし / self-correction<=3。

## Phase 4: Execute
- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `NoGo = !A2A3StartAllowed`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## Phase 5: Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

## Phase 6: Proceed / Stop
- Proceed: AC/DoD充足。
- Stop: 前提崩れ、未定義競合、未承認確定、3回超過、指定外差分。
