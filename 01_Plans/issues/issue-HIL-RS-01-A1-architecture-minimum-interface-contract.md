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
- Non-target file policy: 本ストリームで編集許可された7 Issue（`issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` / `issue-HIL-RS-02-A1-governance-contract-hardening.md` / `issue-HIL-RS-02-next-phase-delivery-plan.md` / `issue-HIL-RS-02-A3-operations-documentation-sync.md` / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` / `issue-FB-P2C-01-a1-interface-contract.md`）以外は不干渉

- Contract snapshot date: `2026-04-27`（固定入力）
- Execution order (Stream A fixed serial): 3/7 HIL-RS-01 A1

## Stream A Contract Lock（HIL-RS fixed）
- Contract ID固定: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（再定義禁止）
- `NoGo return path` 固定: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（変更禁止）
- `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` は境界条件として固定（緩和禁止）
- 未承認事項（`Approval Record: Pending`）が1件でも残る場合は `Phase 4 Execute` へ進行禁止

## Phase Control Macro（各Phase共通）
- 各Phase開始直前に必ず対象7ファイルを再読し、`Status / Scope / Dependencies / 固定キー` をRead同期する。
- 各Phaseは `Plan -> Execute -> Verify -> Proceed` の順序を必須とし、スキップ/逆走を禁止する。
- フェイルセーフ検知時（4回目相当self-correction、未承認確定化、未定義競合、指定外編集要求）は即停止し、次の3点を必ず出力する。
  1. 原因
  2. 影響I/F
  3. 人間判断が必要な論点

## Phase 1: Read
- Phase開始直前に本ファイルを再読し、語彙・判定式・held条件の差分有無を確認する。
- Extracted: Status=`Open`, Priority=`P1`, Scope=`planning only`, Dependencies=`A1 -> A2 -> A3`。
- Delta log（現値）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `sharedResourceFreeze=true`
  - `contractLinkLocked=true`
- 事前想定との差分: なし（Proceed可）。
- 固定キー検証（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `unlockRule`, `decisionQueueTransition`）: 差分 `0`。ドリフト検知時は即停止し `held` に記録する。
- Phase gate checklist: `Status / Scope / Dependencies / 固定キー` を各Phase開始時に再確認し、差分が1つでもあれば `held` に記録して停止。

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
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Approval Gate（Execute進行条件）
- ADR/CDC（Context / Decision / Consequences）の承認完了までは Phase 4 Execute へ進まない。
- 未承認事項は `pending/held` のまま保持し、確定扱いしない。
- AC/DoDに不足がある場合はAIが不足項目をDraft提示し、`Approval Record` で合意するまで Execute へ進まない。

### Approval Record（必須）
- Status: `Pending`（承認記録が追記されるまで Phase 4 へ進行禁止）
- Required fields: `approved_by`, `approved_at`, `evidence`

### Consequences
- A1未完了時A2/A3 Open禁止。
- NoGo return pathはA1契約Issue固定。

### held
- `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持。

## Phase 3: Plan
- 対象ファイル差分意図: Go/NoGo判定式とキー定義を統一。
- 非対象不干渉: 編集許可された4 Issue以外は編集しない。
- Scope: HIL-RS 契約/運用ハードニング（Docsのみ）
- Non-goals: 実装コード変更 / README・dashboard更新 / 対象外Issue編集
- Interface placeholder policy: A2/A3依存は mock前提の最小I/F記述に限定し、実装確定を行わない。
- Gate式は固定値を参照のみとし、再定義・派生定義を禁止する。
- AC/DoD
  - AC: 固定キー差分0 / unlockRule一致 / Pending bypass禁止。
  - DoD: NoGo return path一意 / safeModeDefault維持 / self-correction<=3。
- 検証コマンド（Plan時点で固定）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Contract Freeze Snapshot（A2/A3 read-only引き渡し）
- `contract_id=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schema_version=1.0.0`
- `contract_ids=[A1-CRITIQUE-IF, A1-REDIFF-IF, A1-ATTR-IF, A1-ERROR-IF]`
- `ssot=02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- `prohibited_changes`:
  1. Contract ID の追加・削除・改名
  2. `schemaVersion=1.0.0` 以外への更新
  3. `overridePolicy=human_dual_control_only` の緩和
  4. `contractLinkLocked=true` / `sharedResourceFreeze=true` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` の後退
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
- `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
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

## Phase 5: Verify→Proceed
- AC/DoD自己検証を先に実施し、その後 docs-check（validator / unittest / diff check）を順に実行する。
- 失敗時は Self-Correction を最大3回まで実施し、4回目相当はフェイルセーフ停止する。
- Self-Correction counterは `0/3` で開始し、各再試行で `+1` を明示記録する。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Fail-safe held trigger（即停止）
- `self_correction_attempt >= 4`（4回目相当）を検知した場合。
- 未承認事項の確定化（pending bypass）を検知した場合。
- `NoGo return path` の改変要求を検知した場合。
- `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / `overridePolicy=human_dual_control_only` / `sharedResourceFreeze=true` / `contractLinkLocked=true` の後退兆候を検知した場合。
- 上記を検知した場合は推測継続を禁止し、`held` 記録を更新して停止する。

## Phase 6: Proceed/Stop（Go / Conditional / No-Go）
- Go: `ProceedGate=true` かつ AC/DoD充足、`held` 以外の未承認なし。
- Conditional: `ProceedGate=false` だが未承認事項が `held` のみに限定される場合。
- No-Go: 前提崩れ、未定義競合、Self-Correction 3回超過、指定外ファイル変更。
- No-Go時出力: 原因・影響・再開条件を明文化する。
- 記録必須: 成果 / 未解決 / 次の1手（1項目）を残す。


## Stream A handover checkpoint（2026-04-27）

### Phase 6 Proceed判定（今回）
- 判定: **Needs-decision**（`Approval Record: Pending` と `held` 論点が残存）。
- Go/No-Go条件: 既存の `ProceedGate` / `NoGo` 判定式を継続適用（再定義しない）。

### 未確定論点一覧（次回引き継ぎ）
1. `Approval Record` の承認主体・時刻・証跡（`approved_by` / `approved_at` / `evidence`）が未入力。
2. `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持中で、人間判断待ち。
3. A2/A3公開判定は `A1 Done && pendingDecisionQueueCount==0` 未充足のため据え置き。

### No-Go条件の再確認
- self-correction 4回目相当、未承認確定化、未定義競合、allowlist外編集要求を検知した場合は即停止して人間へエスカレーションする。
