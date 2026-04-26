# Issue Draft: FB-P2C-01 A1 interface contract freeze（Stream A critical path）

- Type: Feature request
- Status: Open（A1 contract freeze active）
- Priority: P0
- Owner: Stream A（Critical Path）
- Scope: A1最小I/F契約の固定（Contract ID / Signature / Deterministic Rule）
- Dependencies: `A1 -> A2 -> A3`, A2/A3はA1 read-only参照
- Related ADR: `ADR-0001`, `ADR-0026`, `ADR-0027`, `ADR-0028`
- Verification level: `docs-check`
- Non-target file policy: 対象6Issue以外は不干渉

- Execution order (Stream A fixed serial): 2/6 FB-P2C A1契約凍結

---

## Phase 1: Read（再読・差分確認）
- 差分検知時は停止候補として `held` に記録し、Executeへ進まない。
- Phase開始直前に本ファイルを再読し、語彙・判定式・held条件の差分有無を確認する。
### Extracted
- Status: `Open`
- Priority: `P0`
- Scope: A1契約固定のみ
- Dependencies: 下流A2/A3はA1契約の参照専用
- Related ADR: `ADR-0001/0026/0027/0028`

### Delta log
- 現値（critical-path freeze）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
- 事前想定との差分
  - `CTR-FB-P2C-01-A1-TIEBREAK-V1` は legacy候補として凍結し、判定ゲートから除外済み（read-only参照のみ）。
- 判定: A1 SSOTとの差分なし（Proceed可）。
- 固定キー検証（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `unlockRule`, `decisionQueueTransition`）: 差分 `0`。ドリフト検知時は即停止し `held` に記録する。
- Phase gate checklist: `Status / Scope / Dependencies / 固定キー` を各Phase開始時に再確認し、差分が1つでもあれば `held` に記録して停止。

### held record
- `HIL-RS-02-GOV-EXCEPTION-01`: 未承認事項として `held` 維持（確定扱い禁止）

## Phase 2: ADR/CDC Consensus
### Context
- A1は全下流判定ゲートであり、Contract IDを単一SSOTへ収束させる必要がある。

### Decision
- 固定（採用）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
  - `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 保留
  - `HIL-RS-02-GOV-EXCEPTION-01`: `held` 維持（未承認事項）。
  - `CTR-FB-P2C-01-A1-TIEBREAK-V1`: legacy参照のみ（判定ゲート非採用、確定扱いしない）。

### Approval Gate（Execute進行条件）
- ADR/CDC（Context / Decision / Consequences）の承認完了までは Phase 4 Execute へ進まない。
- 未承認事項は `pending/held` のまま保持し、確定扱いしない。

### Consequences
- A2/A3はA1 freeze contract参照のみ（再定義禁止）。
- 未承認アルゴリズム詳細は開始条件に使わない。

## Phase 3: Plan
- 宣言: `Plan -> Execute -> Verify -> Proceed`（直列運用・逆走禁止）。
- 差分意図: A1契約を「唯一ゲート」に戻す。
- 非対象不干渉: 対象6Issue外は編集しない。

### AC / DoD
- AC
  1. A1 SSOTキーが他Issueと一致。
  2. `held` 論点を確定扱いしない。
  3. A2/A3 read-only参照を明記。
  4. `A2A3_OPEN_ALLOWED` をA1/A2/A3共通判定式として固定。
- DoD
  1. Go/NoGo判定でA1 freeze値のみ参照（`schemaVersion/overridePolicy/contractLinkLocked/sharedResourceFreeze` を含む）。
  2. 指定外ファイル差分0。

## Phase 4: Execute
- Phase開始直前に本ファイルを再読し、Phase 2承認済みDecisionとの差分があれば `held` を更新して停止する。
- `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON")`
- `NoGo判定 = (!A2A3_OPEN_ALLOWED) || pendingBypassDetected || undefinedConflictDetected`
- `ProceedGate = (A2A3_OPEN_ALLOWED && validatorPass==true)`
- `Go = ProceedGate`
- `Conditional = (!ProceedGate && heldCount>0 && unresolvedApprovalsAreHeldOnly)`
- `NoGo = (!ProceedGate && !Conditional)`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Handoff snapshot（read-only）
  - `SnapshotID=SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
  - `MutationPolicy=read-only`

## Phase 5: Verify
- AC/DoD自己検証を先に実施し、その後 docs-check（validator / unittest / diff check）を順に実行する。
- 失敗時は Self-Correction を最大3回まで実施し、4回目相当はフェイルセーフ停止する。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

## Phase 6: Proceed（Go / Conditional / No-Go）
- Go: `ProceedGate=true` かつ AC/DoD全充足、`held` 以外の未承認事項なし。
- Conditional: `ProceedGate=false` だが未承認事項が `held` のみに限定される場合。
- No-Go: SSOT競合、未承認確定、Self-Correction 3回超過、指定外差分。
- No-Go時出力: 原因・影響・再開条件を明文化する。
