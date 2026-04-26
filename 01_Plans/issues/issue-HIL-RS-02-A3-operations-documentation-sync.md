# Issue Draft: HIL-RS-02 A3 Operations Documentation Sync（Mock I/F Preparation）

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: TBD
- Priority: P1
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Out of scope: `03_Implement/**`, `04_Documentation/**`, 対象5Issue以外
- Dependencies: `ADR-0027`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0027`, `ADR-0028`, `02_Architecture/strict_mode_exception_approval_flow.md`
- Expected verification level: `docs-check`
- Non-target file policy: 本指示で許可された5 Issue以外は不干渉

## Operating Premise（Prompt G適用）
- A1未完前提でA3は **mock I/Fベースの準備タスクのみ** 実施する。
- 依存待ちで全面停止せず、準備可能範囲（語彙固定・導線固定・検証式固定・held整理）を前進させる。
- 各Phase開始時に本ファイルを再読し、Read同期を実施する。
- 各Phaseで `Context / Decision / Consequences` を明文化する。
- Self-Correction は最大3回、4回目相当でフェイルセーフ停止する。

## Phase 1: Read（再読・差分確認）
### Context
- A3は契約再定義ではなく、A1契約凍結を参照する運用同期ノードである。

### Decision
- Phase開始時に本ファイルを再読し、以下固定キーの差分検知を必須化する。
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

### Consequences
- 固定キー差分が1件でもあれば `held` に記録し、A3での契約改定は実施しない。

### Extracted
- Status: `Draft`
- Priority: `P1`
- Scope: operations documentation sync の契約参照のみ
- Dependencies: `A1 -> A2 -> A3`（A1完了までDraft固定）
- Related ADR/Spec: `ADR-0027/0028`

## Phase 2: ADR/CDC Consensus（A3準備範囲の固定）
### Context
- A1未完のため、A3でのOpen化や契約更新は不可。
- ただし、A3の準備項目（mock I/F参照整備）は先行実施可能。

### Decision
- A3実行範囲を `mock I/F preparation only` に固定する。
- Sync route固定: `02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md`
- Role vocabulary固定: `Security Officer`, `System Owner`, `Platform Operator`
- D1〜D4固定値は参照専用とし、A3で再定義しない。
- Approval Recordが `Pending` でも、A3は「準備作業のみ」継続可（Open化は不可）。

### Consequences
- A3は `Draft` 維持のまま準備成果を蓄積できる。
- A1未完時の停止対象は「Open化要求」「契約改定要求」に限定される。

### Approval Record（必須）
- Status: `Pending`（A3 Open gateの承認は未充足）
- Required fields: `approved_by`, `approved_at`, `evidence`
- AC/DoDに不足がある場合はAIが不足項目をDraft提示し、`Approval Record` で合意するまで Execute へ進まない。

### held
- A3単独での契約改定要求。
- A1完了前のA3 Open要求。

## Phase 3: Plan（準備タスク計画）
### Context
- 依存待ち中でも、将来のA3 Openに向けた検証式・語彙・導線のドリフト防止は実施可能。

### Decision
- 宣言: `Plan -> Execute -> Verify -> Proceed`（直列運用・逆走禁止）。
- Scope: HIL-RS 契約/運用ハードニング（Docsのみ）
- Non-goals: 実装コード変更 / README・dashboard更新 / 対象外Issue編集
- Gate式は固定値を参照のみとし、再定義・派生定義を禁止する。
- AC（minimum）
  - AC-1: fixed keys diff=0（freezeContractId / contractIds / schemaVersion / overridePolicy / safeModeDefault / sharedResourceFreeze）。
  - AC-2: role語彙（Security Officer / System Owner / Platform Operator）ドリフトなし。
  - AC-3: D1〜D4は参照専用で再定義しない。
  - AC-4: Source Issue運用（Draft=`TBD`）を維持。
- DoD（minimum）
  - DoD-1: A3 Open gateがA1条件従属である。
  - DoD-2: NoGo差戻し先がA1で一意。
  - DoD-3: docs-check証跡を残し、self-correction<=3。

### Consequences
- A1依存が残っていても、A3準備タスクは前進可能。
- 実行時は契約凍結条件とDraft制約を同時に維持する。

### 検証コマンド（Plan時点で固定）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `rg -n "^- Scope:|^- Related ADR/Spec:|^- Expected verification level:" 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- `git diff --check`

## Phase 4: Execute（mock I/F preparation only）
### Context
- A1未完のためA3 Open不可。ただし準備作業は継続する。

### Decision
- Open/Proceed Gate
  - `ProceedGate = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && validatorPass==true)`
  - `PrepGate = (a1Status!="Done" && fixedKeysDiff==0 && roleVocabularyDrift==false && validatorPass==true)`
  - `Go = ProceedGate`
  - `Conditional = PrepGate`
  - `NoGo = (!ProceedGate && !PrepGate)`
  - `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- `a1Status!="Done"` の間は `Draft` 固定。

### Consequences
- `Conditional` は「準備継続」を意味し、Open化を意味しない。
- A1完了後にのみ `Go` 判定でA3 Openへ進行する。

## Phase 5: Verify
### Context
- 準備タスクでも検証証跡を必須化し、A1完了後の再開負荷を下げる。

### Decision
- AC/DoD自己検証を先に実施し、その後 docs-check（validator / unittest / diff check / scope checks）を順に実行する。
- 失敗時は Self-Correction を最大3回まで実施し、4回目相当はフェイルセーフ停止する。
- 実行コマンド
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "^- Scope:|^- Related ADR/Spec:|^- Expected verification level:" 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
  - `git diff --check`

### Consequences
- 検証失敗の持ち越しを防ぎ、A3 Open前に準備品質を担保できる。

### Fail-safe held trigger（即停止）
- `self_correction_attempt >= 4`（4回目相当）を検知した場合。
- 未承認事項の確定化（pending bypass）を検知した場合。
- `NoGo return path` の改変要求を検知した場合。
- `safeModeDefault=ON` / `overridePolicy=human_dual_control_only` / `sharedResourceFreeze=true` の後退兆候を検知した場合。
- 上記を検知した場合は推測継続を禁止し、`held` 記録を更新して停止する。

## Phase 6: Proceed/Stop（Go / Conditional / No-Go）
### Context
- A3はA1依存を維持しつつ、準備継続と停止条件を明確に分離する必要がある。

### Decision
- Go: `ProceedGate=true` かつ AC/DoD充足、`held` 以外の未承認事項なし。
- Conditional: `PrepGate=true` かつ `a1Status!="Done"`（A3はDraft維持で準備のみ継続）。
- No-Go: Open要求の先行、Pending bypass、未定義競合、Self-Correction 3回超過、指定外差分。
- フェイルセーフ停止条件: 未承認確定化 / 語彙ドリフト / 指定外編集。
- No-Go時出力: 原因・影響・再開条件を明文化する。

### Consequences
- 依存待ちによる無為停止を回避しつつ、契約凍結と安全境界を維持する。
- 記録必須: 成果 / 未解決 / 次の1手（1項目）を残す。
