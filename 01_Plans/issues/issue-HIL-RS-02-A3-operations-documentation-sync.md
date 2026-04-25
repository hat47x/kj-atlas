# Issue Draft: HIL-RS-02 A3 Operations Documentation Sync（Contract Reference Only）

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: TBD
- Priority: P1
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Out of scope: `03_Implement/**`, `04_Documentation/**`, 対象6Issue以外
- Dependencies: `ADR-0027`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0027`, `ADR-0028`, `02_Architecture/strict_mode_exception_approval_flow.md`
- Expected verification level: `docs-check`
- Non-target file policy: 対象6Issue以外は不干渉

## Phase 1: Read（再読・差分確認）
- 差分検知時は停止候補として `held` に記録し、Executeへ進まない。
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
  - `sourceIssuePolicy=Draft/TBD (README運用基準)`
- 事前想定との差分: なし（A3はread-only参照）。
- 固定キー検証（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `unlockRule`, `decisionQueueTransition`）: 差分 `0`。ドリフト検知時は即停止し `held` に記録する。

## Phase 2: ADR/CDC Consensus（必要時のみ）
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
- 宣言: `Plan -> Execute -> Verify -> Proceed`（直列運用・逆走禁止）。
- 対象差分意図: A3をread-only参照ノードとして固定。
- 非対象不干渉: 6Issue外は編集しない。
- AC（minimum）
  - AC-1: fixed keys diff=0（freezeContractId / contractIds / schemaVersion / overridePolicy / safeModeDefault / sharedResourceFreeze）。
  - AC-2: role語彙（Security Officer / System Owner / Platform Operator）ドリフトなし。
  - AC-3: D1〜D4は参照専用で再定義しない。
  - AC-4: Source Issue運用（Draft=`TBD`）を維持。
- DoD（minimum）
  - DoD-1: A3 Open gateがA1条件従属である。
  - DoD-2: NoGo差戻し先がA1で一意。
  - DoD-3: docs-check証跡を残し、self-correction<=3。

## Phase 4: Execute
- Phase開始直前に本ファイルを再読し、Phase 2承認済みDecisionとの差分があれば `held` を更新して停止する。
- Open/Proceed Gate
  - `ProceedGate = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && validatorPass==true)`
  - `Go = ProceedGate`
  - `Conditional = (!ProceedGate && heldCount>0 && unresolvedApprovalsAreHeldOnly)`
  - `NoGo = (!ProceedGate && !Conditional)`
  - `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `a1Status!="Done"` の間は `Draft` 固定

## Phase 5: Verify
- AC/DoD自己検証を先に実施し、その後 docs-check（validator / unittest / diff check / scope checks）を順に実行する。
- 失敗時は Self-Correction を最大3回まで実施し、4回目相当はフェイルセーフ停止する。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `rg -n "^- Scope:|^- Related ADR/Spec:|^- Expected verification level:" 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- `git diff --check`

## Phase 6: Proceed（Go / Conditional / No-Go）
- Go: `ProceedGate=true` かつ AC/DoD充足、`held` 以外の未承認事項なし。
- Conditional: `ProceedGate=false` だが未承認事項が `held` のみに限定される場合（A3はDraft維持）。
- No-Go: A1未完了でOpen要求、Pending bypass、未定義競合、Self-Correction 3回超過、指定外差分。
- フェイルセーフ停止条件: 未承認確定化 / 語彙ドリフト / 指定外編集。
- No-Go時出力: 原因・影響・再開条件を明文化する。
