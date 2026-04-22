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

## Phase 1: Read（Plan -> Execute -> Verify -> Proceed）
### Plan
- 対象4ファイルを再読し、契約キーと判定式の差分抽出を行う。

### Execute
- Status/Priority/Scope/Related ADRを再読済み。
- Delta log: 固定キーは整合。NoGo差戻し先をA1契約Issueへ一本化。

### Verify
- 固定キー4点（`freezeContractId` / `contractLinkLocked` / `sharedResourceFreeze` / `safeModeDefault`）の差分=0を確認。

### Proceed
- Phase 2へ進行。

## Phase 2: ADR/CDC Consensus（Plan -> Execute -> Verify -> Proceed）
### Plan
- Decision差分の有無をContext/Decision/Consequences形式で明文化する。

### Execute
#### Context
- A1契約はRS-01/RS-02両系統の開放ゲートであり、統治判定式を単一化する必要がある。

#### Decision（Contract Freeze SSOT）
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
- A1未完了時A2/A3 Open禁止。
- NoGo return pathはA1契約Issue固定。

#### held
- `HIL-RS-02-GOV-EXCEPTION-01` は `held`。

### Verify
- 4ファイルでDecision値が一致することを確認。

### Proceed
- 差分なしのため追加ADR起票なしでPhase 3へ。

## Phase 3: Plan（Plan -> Execute -> Verify -> Proceed）
### Plan
- AC/DoDの不足を補い、検証可能な文面へ固定する。

### Execute
- AC:
  - 固定キー一致（4ファイル差分0）。
  - `unlockRule` 一致。
  - `decisionQueueTransition` 一致。
  - `NoGo return path` がA1契約Issueで一意。
- DoD:
  - Go/NoGo判定式一致。
  - A1差戻し先一意。
  - `safeModeDefault=ON` 維持。
  - self-correction `<=3`。

### Verify
- AC/DoDがPhase 4の判定式で機械的に照合可能であることを確認。

### Proceed
- Phase 4へ。

## Phase 4: Execute（Plan -> Execute -> Verify -> Proceed）
### Plan
- 契約キーとGo/NoGo判定式を固定し、ドリフト余地を排除する。

### Execute
- Go/NoGo:
  - `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
  - `Go = A2A3StartAllowed`
  - `NoGo = !A2A3StartAllowed`
  - `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Verify
- 契約キー4点の記載揺れなし。

### Proceed
- Phase 5へ。

## Phase 5: Verify（Plan -> Execute -> Verify -> Proceed）
### Plan
- docs-check / diff整合 / 自己修復上限を検証する。

### Execute
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Verify
- docs-check相当とdiff整合を確認。
- self-correction は最大3回。

### Proceed
- すべて通過時のみPhase 6へ。

## Phase 6: Proceed / Stop（Plan -> Execute -> Verify -> Proceed）
### Plan
- handoff要約を作成し、停止条件の有無を最終確認する。

### Execute
- Proceed条件: AC/DoD充足、`held`以外に未承認なし。
- Stop条件: 前提崩壊、未定義競合、承認なき確定、self-correction超過。

### Verify
- Stop条件非該当を確認。

### Proceed
- Stream A handoffへ引き継いで終了。
