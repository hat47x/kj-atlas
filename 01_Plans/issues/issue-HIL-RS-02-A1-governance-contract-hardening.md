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

## Phase 1: Read（Plan -> Execute -> Verify -> Proceed）
### Plan
- 対象4ファイル再読と契約固定キー差分抽出。

### Execute
- Status/Priority/Scope/Related ADRを再読。
- Delta log: Return pathをA1一本化し、`Pending bypass` 禁止を強化。

### Verify
- 固定キー4点（`freezeContractId` / `contractLinkLocked` / `sharedResourceFreeze` / `safeModeDefault`）の差分=0を確認。

### Proceed
- Phase 2へ。

## Phase 2: ADR/CDC Consensus（Plan -> Execute -> Verify -> Proceed）
### Plan
- ガバナンス契約硬化に必要なDecisionを明文化する。

### Execute
#### Context
- RS-02で統治契約を硬化し、誤Open化を防ぐ必要がある。

#### Decision（Hardening baseline）
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

#### Consequences
- A1以外への差戻し禁止。
- 未承認事項は確定不可。

#### held
- `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持。

### Verify
- Decision値が4ファイルで一致することを確認。

### Proceed
- Phase 3へ。

## Phase 3: Plan（Plan -> Execute -> Verify -> Proceed）
### Plan
- AC/DoDを統治硬化向けに具体化。

### Execute
- AC:
  - fixed keys diff=0。
  - return path唯一。
  - `Pending bypass` 禁止を明記。
- DoD:
  - Go/NoGo判定式一貫。
  - self-correction `<=3`。

### Verify
- AC/DoDが検証コマンドと整合することを確認。

### Proceed
- Phase 4へ。

## Phase 4: Execute（Plan -> Execute -> Verify -> Proceed）
### Plan
- Go/NoGo式統一と禁止遷移の明文化を固定。

### Execute
- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `NoGo = !A2A3StartAllowed`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Verify
- 禁止遷移（Pending bypass）不許可を再確認。

### Proceed
- Phase 5へ。

## Phase 5: Verify（Plan -> Execute -> Verify -> Proceed）
### Plan
- docs-check / diff整合 / self-correction制御を確認。

### Execute
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Verify
- docs-check + diff check通過。
- self-correction最大3回。

### Proceed
- 通過時のみPhase 6へ。

## Phase 6: Proceed / Stop（Plan -> Execute -> Verify -> Proceed）
### Plan
- handoff作成可否を最終判定。

### Execute
- Proceed: AC/DoD充足。
- Stop: ドリフト、Pending bypass、未定義競合、self-correction超過。

### Verify
- Stop条件非該当を確認。

### Proceed
- Stream A handoffへ進めて終了。
