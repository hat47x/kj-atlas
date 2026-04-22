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

## Phase 1: Read（Plan -> Execute -> Verify -> Proceed）
### Plan
- 対象4ファイル再読と固定キー差分抽出を行う。

### Execute
- Status/Priority/Scope/Related ADRを再読。
- Delta log: 判定語彙をA1契約と一致化、NoGo差戻し先をA1へ固定。

### Verify
- 固定キー4点（`freezeContractId` / `contractLinkLocked` / `sharedResourceFreeze` / `safeModeDefault`）の差分=0を確認。

### Proceed
- Phase 2へ。

## Phase 2: ADR/CDC Consensus（Plan -> Execute -> Verify -> Proceed）
### Plan
- 差分がある場合はContext/Decision/Consequencesで明文化する。

### Execute
#### Context
- RS-01はRS-02の前段であり、状態遷移契約の不一致を許容できない。

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
- Serial protocol（Plan -> Execute -> Verify -> Proceed）を強制。
- A1未完了でA2/A3 Open禁止。

#### held
- 追加ADR起案は不要。未承認論点は `held` で維持。

### Verify
- 4ファイルのDecision一致を確認。

### Proceed
- Phase 3へ。

## Phase 3: Plan（Plan -> Execute -> Verify -> Proceed）
### Plan
- AC/DoD不足を補完し、最上流契約の受入条件を固定する。

### Execute
- AC:
  - 固定キー差分0。
  - `decisionQueueTransition` 固定遷移。
  - A2/A3開放条件固定。
  - `NoGo return path` 一意。
- DoD:
  - `safeModeDefault=ON` 維持。
  - `overridePolicy` 後退禁止。
  - self-correction `<=3`。

### Verify
- AC/DoDの文言が他3ファイルと衝突しないことを確認。

### Proceed
- Phase 4へ。

## Phase 4: Execute（Plan -> Execute -> Verify -> Proceed）
### Plan
- 契約キーをread-only handoffとして固定する。

### Execute
- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `NoGo = !A2A3StartAllowed`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Verify
- 契約キー4点の表記が固定であることを確認。

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
- docs-check + diff check通過。
- self-correction最大3回。

### Proceed
- 通過時のみPhase 6へ。

## Phase 6: Proceed / Stop（Plan -> Execute -> Verify -> Proceed）
### Plan
- handoff要約化と停止条件確認。

### Execute
- Proceed: AC/DoD充足。
- Stop: 前提崩れ、未定義競合、承認なき確定、self-correction超過。

### Verify
- Stop条件非該当を確認。

### Proceed
- Stream A handoffを作成し終了。
