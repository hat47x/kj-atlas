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
- Non-target file policy: 対象7Issue以外は不干渉

## Phase 1: Read
- Phase開始直前に本ファイルを再読し、語彙・判定式・held条件の差分有無を確認する。
- Extracted: Status=`Open`, Priority=`P1`, Scope=`planning only`, Dependencies=`A1 -> A2 -> A3`。
- Delta log（現値）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
- 事前想定との差分: なし（Proceed可）。
- 固定キー検証（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `unlockRule`, `decisionQueueTransition`）: 差分 `0`。ドリフト検知時は即停止し `held` に記録する。

## Phase 2: ADR/CDC Consensus
### Context
- A1契約はRS-01/RS-02共通ゲートであり、判定式を単一化する必要がある。

### Decision（Contract Freeze SSOT）
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

### Approval Gate（Execute進行条件）
- ADR/CDC（Context / Decision / Consequences）の承認完了までは Phase 4 Execute へ進まない。
- 未承認事項は `pending/held` のまま保持し、確定扱いしない。

### Consequences
- A1未完了時A2/A3 Open禁止。
- NoGo return pathはA1契約Issue固定。

### held
- `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持。

## Phase 3: Plan
- 対象ファイル差分意図: Go/NoGo判定式とキー定義を統一。
- 非対象不干渉: 7Issue外は編集しない。
- AC/DoD
  - AC: 固定キー差分0 / unlockRule一致 / Pending bypass禁止。
  - DoD: NoGo return path一意 / safeModeDefault維持 / self-correction<=3。

### Contract Freeze Snapshot（A2/A3 read-only引き渡し）
- `contract_id=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schema_version=1.0.0`
- `contract_ids=[A1-CRITIQUE-IF, A1-REDIFF-IF, A1-ATTR-IF, A1-ERROR-IF]`
- `ssot=02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- `prohibited_changes`:
  1. Contract ID の追加・削除・改名
  2. `schemaVersion=1.0.0` 以外への更新
  3. `overridePolicy=human_dual_control_only` の緩和
  4. `contractLinkLocked=true` / `sharedResourceFreeze=true` / `safeModeDefault=ON` の後退
  5. `DecisionQueue` の `Pending` 経由なし確定（bypass）
  6. A1 Done 前の A2/A3 `Draft -> Open`

### Mock可能な最小シグネチャ（Contract-only）
```yaml
freeze_pack:
  contract_id: "HIL-RS-02-A1-CONTRACT-FREEZE-v1"
  schema_version: "1.0.0"
  contracts:
    - id: "A1-CRITIQUE-IF"
    - id: "A1-REDIFF-IF"
    - id: "A1-ATTR-IF"
    - id: "A1-ERROR-IF"
gate:
  a2a3_unlock_if:
    a1_status: "Done"
    pending_decision_queue_count: 0
  decision_queue_transition:
    - "Pending -> Approved"
    - "Pending -> Rejected"
```

### A1->A2->A3 Gate Contract（Canonical / SSOT）
- `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON")`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（一意・固定）
- `NoGo判定 = (!A2A3_OPEN_ALLOWED) || pendingBypassDetected || undefinedConflictDetected`
- A2/A3 は `A2A3_OPEN_ALLOWED=true` を満たすまで `Draft/Open` 変更禁止。

## Phase 4: Execute
- Phase開始直前に本ファイルを再読し、Phase 2承認済みDecisionとの差分があれば `held` を更新して停止する。
- `ProceedGate = (A2A3_OPEN_ALLOWED && validatorPass==true)`
- `Go = ProceedGate`
- `Conditional = (!ProceedGate && heldCount>0 && unresolvedApprovalsAreHeldOnly)`
- `NoGo = (!ProceedGate && !Conditional)`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## Phase 5: Verify
- AC/DoD自己検証を先に実施し、その後 docs-check（validator / unittest / diff check）を順に実行する。
- 失敗時は Self-Correction を最大3回まで実施し、4回目相当はフェイルセーフ停止する。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

## Phase 6: Proceed（Go / Conditional / No-Go）
- Go: `ProceedGate=true` かつ AC/DoD充足、`held` 以外の未承認なし。
- Conditional: `ProceedGate=false` だが未承認事項が `held` のみに限定される場合。
- No-Go: 前提崩れ、未定義競合、Self-Correction 3回超過、指定外ファイル変更。
- No-Go時出力: 原因・影響・再開条件を明文化する。
