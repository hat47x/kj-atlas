# Issue Draft: HIL-RS-02 次フェーズ実行計画

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
- Delta log: 既存ログを契約固定優先の表現へ整理、未承認論点をheldで固定。

## Phase 2: ADR Consensus
### Context
- 実行計画はA1契約凍結を前提に進行し、例外処理は承認待ちとして隔離する必要がある。

### Decision
- Governance baselineを以下で固定:
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
- A1未完了ならA2/A3 Open不可。
- 判定不能論点はDecision Queueで保留。

### held
- `HIL-RS-02-GOV-EXCEPTION-01`:
  - Status: `held`
  - Blocking: A3 `Draft -> Open`, RS-02 Ready宣言

## Phase 3: Plan
- AC: fixed keys diff=0 / unlockRule一致 / decisionQueueTransition一致。
- DoD: NoGo差戻し先A1固定 / 未承認事項held維持。

## Phase 4: Execute
- A2/A3 Start rule固定:
  - `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`

## Phase 5: Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- self-correctionは最大3回。

## Phase 6: Proceed / Stop
- Proceed: AC/DoD充足かつ`held`以外に未承認なし。
- Stop: 前提崩れ、未定義競合、承認なき確定、self-correction超過。
