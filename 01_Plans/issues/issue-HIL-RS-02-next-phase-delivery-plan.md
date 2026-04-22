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

## Phase 1: Read（Plan -> Execute -> Verify -> Proceed）
### Plan
- 対象4ファイル再読と固定キー差分抽出を実施。

### Execute
- Status/Priority/Scope/Related ADRを再読。
- Delta log: 契約固定優先へ表現整理、未承認論点はheldで固定。

### Verify
- 固定キー4点（`freezeContractId` / `contractLinkLocked` / `sharedResourceFreeze` / `safeModeDefault`）の差分=0を確認。

### Proceed
- Phase 2へ。

## Phase 2: ADR/CDC Consensus（Plan -> Execute -> Verify -> Proceed）
### Plan
- 実行計画上のDecisionをSSOTとして確定文面へ統一する。

### Execute
#### Context
- 実行計画はA1契約凍結を前提に進行し、例外処理は承認待ちとして隔離する必要がある。

#### Decision（Governance baseline）
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
- A1未完了ならA2/A3 Open不可。
- 判定不能論点はDecision Queueで保留。

#### held
- `HIL-RS-02-GOV-EXCEPTION-01`:
  - Status: `held`
  - Blocking: A3 `Draft -> Open`, RS-02 Ready宣言

### Verify
- Decisionの値・語彙が他3ファイルと一致することを確認。

### Proceed
- Phase 3へ。

## Phase 3: Plan（Plan -> Execute -> Verify -> Proceed）
### Plan
- AC/DoD不足を補完し、次フェーズ開始判定を固定化する。

### Execute
- AC:
  - fixed keys diff=0。
  - `unlockRule` 一致。
  - `decisionQueueTransition` 一致。
- DoD:
  - `NoGo return path` A1固定。
  - 未承認事項 `held` 維持。
  - self-correction `<=3`。

### Verify
- AC/DoDがPhase 4/5の検証内容と矛盾しないことを確認。

### Proceed
- Phase 4へ。

## Phase 4: Execute（Plan -> Execute -> Verify -> Proceed）
### Plan
- 契約キーと開始判定式を完全固定する。

### Execute
- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `NoGo = !A2A3StartAllowed`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Verify
- 契約キー4点と開放条件の表記揺れなし。

### Proceed
- Phase 5へ。

## Phase 5: Verify（Plan -> Execute -> Verify -> Proceed）
### Plan
- docs-check / diff整合 / 自己修復上限を実行確認する。

### Execute
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Verify
- docs-check + diff check通過。
- self-correctionは最大3回。

### Proceed
- 通過時のみPhase 6へ。

## Phase 6: Proceed / Stop（Plan -> Execute -> Verify -> Proceed）
### Plan
- handoff要約作成と停止判定を実施。

### Execute
- Proceed: AC/DoD充足かつ`held`以外に未承認なし。
- Stop: 前提崩れ、未定義競合、承認なき確定、self-correction超過。

### Verify
- Stop条件非該当を確認。

### Proceed
- Stream A handoff要約を作成して終了。
