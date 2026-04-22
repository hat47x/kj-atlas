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
- Non-target file policy: 対象7Issue以外は不干渉

## Phase 1: Read
- Phase開始直前に本ファイルを再読し、語彙・判定式・held条件の差分有無を確認する。
### Extracted
- Status: `Draft`
- Priority: `P1`
- Scope: operations documentation sync の契約参照のみ
- Dependencies: `A1 -> A2 -> A3`（A1完了までDraft固定）
- Related ADR/Spec: `ADR-0027/0028`

### Delta log
- 現値
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
- 事前想定との差分: なし（A3はread-only参照）。

## Phase 2: ADR/CDC Consensus
### Context
- A3は運用文書同期の参照ノードであり、契約再定義を許容しない。

### Decision
- Contract Freeze（read-only）
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
- D1〜D4固定値: 参照専用（A3再定義禁止）

### Approval Gate（Execute進行条件）
- ADR/CDC（Context / Decision / Consequences）の承認完了までは Phase 4 Execute へ進まない。
- 未承認事項は `pending/held` のまま保持し、確定扱いしない。

### Consequences
- A1未完了時A3 Open禁止。
- NoGo差戻しはA1のみ。
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### held
- A3単独での契約改定要求は `held`。

## Phase 3: Plan
- 対象差分意図: A3をread-only参照ノードとして固定。
- 非対象不干渉: 7Issue外は編集しない。
- AC/DoD
  - AC: fixed keys diff=0 / role語彙固定 / D1〜D4参照固定。
  - DoD: A3 Open gateがA1条件従属 / NoGo差戻し先A1一意 / self-correction<=3。

## Phase 4: Execute
- Phase開始直前に本ファイルを再読し、Phase 2承認済みDecisionとの差分があれば `held` を更新して停止する。
- Open/Proceed Gate
  - `ProceedGate = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && validatorPass==true)`
  - `Go = ProceedGate`
  - `Conditional = (!ProceedGate && heldCount>0 && unresolvedApprovalsAreHeldOnly)`
  - `NoGo = (!ProceedGate && !Conditional)`
  - `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `a1Status!="Done"` の間は `Draft` 固定

## Phase 5: Verify
- AC/DoD自己検証を先に実施し、その後 docs-check（validator / unittest / diff check）を順に実行する。
- 失敗時は Self-Correction を最大3回まで実施し、4回目相当はフェイルセーフ停止する。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

## Phase 6: Proceed（Go / Conditional / No-Go）
- Go: `ProceedGate=true` かつ AC/DoD充足、`held` 以外の未承認事項なし。
- Conditional: `ProceedGate=false` だが未承認事項が `held` のみに限定される場合（A3はDraft維持）。
- No-Go: A1未完了でOpen要求、Pending bypass、未定義競合、Self-Correction 3回超過、指定外差分。
- No-Go時出力: 原因・影響・再開条件を明文化する。
