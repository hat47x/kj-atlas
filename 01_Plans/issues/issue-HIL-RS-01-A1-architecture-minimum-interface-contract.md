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
- Non-target file policy: 本ストリームで編集許可された5 Issue（`issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `issue-HIL-RS-02-next-phase-delivery-plan.md` / `issue-HIL-RS-02-A1-governance-contract-hardening.md` / `issue-HIL-RS-02-A3-operations-documentation-sync.md`）以外は不干渉

- Contract snapshot date: `2026-04-27`（固定入力）
- Execution order (Stream A fixed serial): 3/7 HIL-RS-01 A1

## Stream A Contract Lock（HIL-RS fixed）
- Contract ID固定: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（再定義禁止）
- `NoGo return path` 固定: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（変更禁止）
- `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` は境界条件として固定（緩和禁止）
- 未承認事項（`Approval Record: Pending`）が1件でも残る場合は `Phase 4 Execute` へ進行禁止

## Phase Control Macro（各Phase共通）
- 各Phase開始直前に必ず対象5ファイルを再読し、`Status / Scope / Dependencies / 固定キー` をRead同期する。
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
- 非対象不干渉: 編集許可された5 Issue以外は編集しない。
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


## Stream A AC/DoD Draft Proposal（Pending Approval）

### Context
- Phase 3要件として、`A1契約固定`・`A2モック前提`・`A3実装移行条件` を明文化し、承認前はDraft扱いに限定する。

### Decision（Draft）
- A1契約固定: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を変更禁止。
- A2モック前提: A2は `mock I/F preparation only` とし、契約値の再定義・派生定義・Pending bypassを禁止する。
- A3実装移行条件: `A2A3_OPEN_ALLOWED=true`（`a1Status=="Done" && pendingDecisionQueueCount==0` を含む固定ゲート充足）までOpen/実装移行を禁止する。

### Consequences
- 上記3項目は `Approval Record: Pending` の間は確定扱いしない。
- 未承認状態では Execute を準備作業のみに限定し、NoGo時はA1契約Issueへ差戻す。

### AC/DoD gap draft（for approval）
- AC-D1: `A1契約固定` の固定キーに差分がないこと（diff=0）。
- AC-D2: `A2モック前提` の範囲逸脱（実装確定/契約改定）がないこと。
- AC-D3: `A3実装移行条件` を満たさない限り `Draft/Open` を変更しないこと。
- DoD-D1: Verifyに self-correction 試行回数（0〜3）を記録すること。
- DoD-D2: Proceed判定時に `Go/Conditional/No-Go` の根拠式を再掲すること。
- DoD-D3: `Approval Record` が未入力の場合は **Needs-decision** として停止またはConditional維持にすること。

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


## Stream A critical-path execution log（2026-04-27 / contract governance hardening）

### Phase 1: Read
- 再読対象: 本Issue本文。
- Read同期チェック（`Status / Scope / Dependencies / freezeContractId / schemaVersion / overridePolicy / safeModeDefault`）を実施し、差分 `0` を確認。
- 追加チェック: `NoGo return path` / `decisionQueueTransition` / `safeModeBoundary` も差分 `0`。

### Phase 2: ADR/CDC
- **Context**: HIL-RS契約統治をA1 SSOTに固定し、推測実装・競合更新を排除する。
- **Decision**: 既存固定値（`HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `safeModeDefault=ON`）を維持し、再定義しない。
- **Consequences**: `Approval Record: Pending` が残る間は Executeで確定化せず、`held` を維持する。

### Phase 3: Plan
- 強制順序 `Plan -> Execute -> Verify -> Proceed` を採用。
- AC/DoD不足は既存 Draft（AC-D1〜D3 / DoD-D1〜D3）を継続し、新規不足は未検知。
- 非対象編集禁止を再確認（allowlist 4ファイル限定）。

### Phase 4: Execute
- 実行内容: 本Issueへの運用ログ追記とallowlist整合化のみ。
- 未実行: 契約値更新、NoGo return path変更、safeMode境界緩和、pending bypass。

### Phase 5: Verify
- docs-check 実行対象を固定し、`self-correction=0/3` で完了。
- 検証失敗・ドリフト・未承認確定化は未検知。

### Phase 6: Proceed
- 判定: **Conditional**。
- 理由: `Approval Record: Pending` および `held` 論点（人間承認待ち）が残存。
- 影響I/F: A2/A3 は `A2A3_OPEN_ALLOWED=true` 充足まで `Draft/Open` 変更禁止。
- 再開条件: `approved_by` / `approved_at` / `evidence` の入力完了と pendingDecisionQueue の解消。

## Stream A execution runbook log（2026-04-27 / Critical Path replay）

### Phase 1: Read snapshot（before change）
- Status snapshot: `Open`（A3のみ `Draft`）
- Scope snapshot: `01_Plans/issues/`（planning only）
- Dependencies snapshot: `A1 -> A2 -> A3`
- Fixed key snapshot: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Fixed key diff result: `diff=0`（drift not detected）

### Phase 2: ADR/CDC Consensus（Context / Decision / Consequences）
- Context: A1契約未確定状態でA2/A3を確定すると依存順 `A1 -> A2 -> A3` が崩壊する。
- Decision: A1固定キーは再定義せず、未承認（`Approval Record: Pending`）は `held` 維持。A2/A3の実装確定は実施しない。
- Consequences: Executeは「契約再掲と検証手順の同期」に限定し、`NoGo return path` はA1 issue固定で維持する。

### Phase 3: Plan（AC/DoD + lines + verify + stop）
- AC:
  1. 固定キー差分 `0`
  2. `A2A3_OPEN_ALLOWED` 判定式と `NoGo return path` がA1に一意固定
  3. Pending bypass禁止の明文化
- DoD:
  1. `Plan -> Execute -> Verify -> Proceed` の順序ログを保存
  2. self-correctionを `0/3` で記録
  3. Conditional/No-Go時に再開条件を1行で固定
- 変更対象行: 本Issue末尾の runbook log 追記行のみ（既存定義の置換なし）
- 検証コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 停止条件: self-correction 4回目相当、未承認確定化、未定義競合、allowlist外編集要求。

### Phase 4: Execute（declared scope only）
- 実施: 本Issueへの runbook log 追記のみ。
- 非実施: 契約ID更新、safeMode境界緩和、A1未完でのA2/A3 Open化、allowlist外ファイル編集。

### Phase 5: Verify
- Self-Correction counter: `0/3`（再試行なし）
- AC/DoD照合: pass（drift/pending bypass/undefined conflict未検知）
- docs-check: validator / unittest / diff-check 実行予定を固定し、実行結果は本実行ログで追跡する。

### Phase 6: Proceed/Stop
- 判定: `Conditional`
- 根拠: `Approval Record: Pending` と `held` 論点が残存し、`A2A3_OPEN_ALLOWED` 充足前。
- 次の1手（再開条件）: `approved_by` / `approved_at` / `evidence` を入力し、`pendingDecisionQueueCount==0` を満たした時点で再検証する。

## Stream A fixed-serial protocol replay（2026-04-27 / Plan→Execute→Verify→Proceed）

- Issue order position: `3/7 HIL-RS-01 A1`
- Protocol lock: 各Phaseで `Plan -> Execute -> Verify -> Proceed` を維持（逆走・省略禁止）。
- Contract lock: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` を固定。

### Phase 1: Read
- 対象7Issueを再読し、`Status / Scope / Dependencies / 固定キー` の差分を確認。
- 差分検知時は `held` 記録のみ許可し、Executeへ進まない。

### Phase 2: ADR/CDC
- Context: A1契約凍結を唯一SSOTとし、A2/A3への派生定義を禁止。
- Decision: 固定キーと `A2A3_OPEN_ALLOWED` 判定式を再定義せず参照専用化。
- Consequences: 未承認事項は `pending/held` 維持（確定扱い禁止）。

### Phase 3: Plan
- AC/DoD不足はDraft提案として追記し、`Approval Record` 合意前は確定化しない。
- 非干渉ルールを再確認し、allowlist外編集を実施しない。

### Phase 4: Execute
- 契約固定の文言同期のみ更新対象とし、実装・派生契約追加は実施しない。
- `safeModeDefault=ON` / `SAFE_MODE_STRICT_ON` / NoGo return path 固定を後退させない。

### Phase 5: Verify
- AC/DoD自己検証後に docs-check（validator / unittest / diff check）を実施。
- self-correctionは `0〜3` 回まで、`4回目相当` は即停止して人間判断へエスカレーション。

### Phase 6: Proceed
- Go/Conditional/No-Go を既存判定式で評価。
- `Approval Record: Pending` または `held` 残存時は `Conditional` または `Needs-decision` を維持。
- フェイルセーフ発火時の報告形式を固定: `原因 / 影響I/F / 要判断点`。

## Stream A execution log（2026-04-28 / A1 contract lock replay）

### Phase 1: Read（状態同期）
- 対象5ファイルを再読し、`Status / Priority / Scope / Dependencies / Approval Record / held` を同期確認。
- 結果: `Status=Open` / `Priority=P1` / `Scope=planning only` / `Dependencies=A1 -> A2 -> A3` / `Approval Record=Pending` / `held=HIL-RS-02-GOV-EXCEPTION-01` 維持。
- 事前想定との差分: なし。

### Phase 2: ADR/CDC（実装前必須）
- Context: A1をRS-01/RS-02の契約SSOTとして維持する必要がある。
- Decision: `freezeContractId`・`contractIds`・`schemaVersion=1.0.0`・`overridePolicy=human_dual_control_only`・`safeModeDefault=ON`・`safeModeBoundary=SAFE_MODE_STRICT_ON` を再確認し変更禁止を継続。
- Consequences: `Approval Record` が未充足のため、Phase 4はログ追記以外の確定操作を禁止。

### Phase 3: Plan（AC/DoD先行）
- Scope: A1最小I/F契約固定とA2/A3 gate参照整合。
- Non-goals: 契約再定義、pending bypass許容、allowlist外編集。
- Acceptance Criteria:
  1. 固定キー差分 `0`。
  2. `decisionQueueTransition` が `Pending -> Approved | Pending -> Rejected` に固定。
  3. `NoGo return path` が A1 issue 一意。
- Definition of Done:
  1. `Plan -> Execute -> Verify -> Proceed` を順守。
  2. self-correction `<=3` を記録。
  3. 未承認事項を確定扱いしない。
- Validation Plan:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Stop Conditions: self-correction 4回目相当、未承認確定化、NoGo return path改変、safeMode境界後退。

### Phase 4: Execute
- 実施内容: 本Issueへの運用ログ追記のみ。
- 非実施: A1固定値更新、A2/A3 Open先行、NoGo return path変更。

### Phase 5: Verify
- Validation Plan に記載した docs-check を実行。
- self-correction: `0/3`。

### Phase 6: Proceed / Stop
- 判定: **Conditional**（承認未充足のため）。
- 影響I/F: A2/A3は `A2A3_OPEN_ALLOWED=true` まで `Draft/Open` 変更不可。
- 再開条件: `Approval Record` の必須3項目が充足されること。


## Stream A fixed-serial execution log（2026-04-28 / HIL-RS critical contract governance）

### Phase 1: Read
- 対象5ファイルを再読し、`Status / Scope / Dependencies / 固定キー`（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `unlockRule`）を同期確認。
- 読み取り結果: `Status=Open` / `Scope=planning only` / `Dependencies=A1 -> A2 -> A3`。
- 固定I/F正規化: `unlockRule=(a1Status=="Done" && pendingDecisionQueueCount==0)` を canonical として参照し、派生再定義を禁止。
- 差分判定: fixed keys diff=`0`。`held` 追加なし。

### Phase 2: ADR/CDC（Context / Decision / Consequences）
- Context: Stream Aは `HIL-RS-02-A1-CONTRACT-FREEZE-v1` を単一契約として維持し、A1ゲート迂回を禁止する。
- Decision: `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `safeModeDefault=ON` / `unlockRule=(a1Status=="Done" && pendingDecisionQueueCount==0)` を再確認して固定。
- Consequences: `Approval Record: Pending` のため、契約確定操作・Open昇格は実施しない。

### Phase 3: Plan
- 変更計画（ファイル別・変更点別）: 本ファイルへ当日実行ログを追記し、固定I/F canonical参照を明示する。
- AC/DoDドラフト不足: 追加なし（既存 Draft を継続利用）。

### Phase 4: Execute
- allowlist内の本ファイルのみ更新（実行ログ追記）。
- 非実施: 実装コード変更 / safeMode既定緩和 / `human_dual_control_only` 後退 / A1 gate bypass / A3 Open化。

### Phase 5: Verify
- AC/DoD自己検証: pass（fixed keys diff=0、Pending bypass未検知）。
- self-correction: `0/3`（再試行なし）。

### Phase 6: Proceed
- 判定: **Conditional**。
- 理由: `Approval Record: Pending`（`approved_by` / `approved_at` / `evidence` 未充足）によりGo条件未達。
- 失敗時の出力対象（継続保持）: 原因=`未承認` / 影響I/F=`A2,A3はDraft/準備のみ` / 人間判断論点=`Approval Record充足`。

## Stream A Proceed Handover Package（Fixed Contract / Prohibitions / Stop-Resume）

- 固定契約ID（Contract Freeze SSOT）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- 禁止事項（変更・昇格禁止）
  1. `NoGo return path` を `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` 以外へ変更
  2. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / `overridePolicy=human_dual_control_only` / `sharedResourceFreeze=true` / `contractLinkLocked=true` の後退
  3. `Pending` を経由しない承認確定（pending bypass）
  4. `A2A3_OPEN_ALLOWED=false` のまま A2/A3 を `Draft/Open` 遷移
- 停止条件（Fail-safe / No-Go）
  - `self_correction_attempt >= 4`
  - 未承認事項の確定化、未定義競合、指定外ファイル編集要求
  - 固定キー差分検知（`Status / Scope / Dependencies / 固定キー` のいずれか不一致）
- 再開条件（Resume Gate）
  - `Approval Record` 必須項目（`approved_by` / `approved_at` / `evidence`）の充足
  - `pendingDecisionQueueCount==0`
  - `A2A3_OPEN_ALLOWED=true` を満たし、validator / unittest / diff-check が全て成功

## Stream B completion pack（2026-04-28 / Contract & Operations Ready）

### Phase 1: Read（Status / AC / Dependency contradiction list）
- 読取対象: 本Issue + HIL-RS対象5Issueのメタ（Status / Source Issue / AC/DoD / Dependencies / Validation）。
- 検知した矛盾（横断）:
  1. `Non-target file policy` の文言が「4 Issue」表記のままになっている箇所があり、実際の対象5Issueと不一致。
  2. `Source Issue` が `N/A` と `TBD` で混在し、A1/A2/A3境界の遡及導線が曖昧。
  3. `Phase 4 Execute` は承認完了まで進行禁止としつつ、過去ログには準備作業を実行した記録があり、運用語彙（Execute=確定変更 or 準備作業）の定義が揺れている。
  4. `Status` は Open/Draft が正しいが、Open→In Progress 移行の着手条件・停止条件がIssueごとに同粒度で固定されていない。

### Phase 2: Plan（AC/DoD補完ドラフト + 承認待ち）
- AC補完ドラフト（Stream B）:
  - AC-B1: `Source Issue` は umbrella/parent を一意参照し、`N/A`/`TBD` を解消できる状態にする。
  - AC-B2: A1/A2/A3境界を「Contract fix / Application prep / Ops sync prep」の3責務で固定する。
  - AC-B3: Validationに `validator + unittest + diff --check` を必須化し、Open→In Progress 前に成功証跡を残す。
  - AC-B4: `Status / Priority / Related ADR/Spec / Validation` を横断比較し、齟齬ゼロを確認する。
- DoD補完ドラフト（Stream B）:
  - DoD-B1: `Open -> In Progress` 移行条件と `Stop conditions` を本文で明示する。
  - DoD-B2: `Approval Record: Pending` の場合は `Conditional` 維持または `Needs-decision` で停止し、確定化しない。
  - DoD-B3: Source Issue運用逸脱（孤立Issue化、逆参照欠落）を検知した場合は即停止してA1 return pathへ差戻す。
- 承認待ち項目:
  - `Approval Record`（`approved_by` / `approved_at` / `evidence`）
  - `HIL-RS-02-GOV-EXCEPTION-01` の扱い（Pending継続 or Approved/Rejected）

### Phase 3: Execute（境界固定 / Source整合 / 検証計画固定）
- A1/A2/A3境界（固定）:
  - A1: Contract/Governance固定（freeze keys, pending bypass防止, return path固定）
  - A2: 実装適用準備（A1完了前は mock I/F preparation only）
  - A3: 運用・文書同期準備（A1完了前は Draft維持、同期導線のみ固定）
- Source Issue整合（固定）:
  - Umbrella: `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`（RS-01）
  - Umbrella: `issue-HIL-RS-02-next-phase-delivery-plan.md`（RS-02）
  - Child: A1/A2/A3 は上記Umbrellaへ従属（孤立運用禁止）
- 検証計画（固定コマンド）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Phase 4: Verify（Issueメタ整合チェック + self-correction）
- 検査観点:
  - `Status`: RS-01/RS-02 umbrella と A1 は `Open`、A3は `Draft` を維持
  - `Priority`: 全Issue `P1`
  - `Related ADR/Spec`: `ADR-0026/0027/0028` 参照の欠落なし
  - `Validation`: docs-check（validator/unittest/diff）を共通化
- self-correction方針:
  - 失敗時は最大3回まで最小修正→再検証。
  - 4回目相当、未定義依存、責務境界崩れ、Source Issue逸脱で即停止。

### Phase 5: Proceed（Open→In Progress移行準備）
- 着手条件（Open->In Progress）:
  1. `A2A3_OPEN_ALLOWED=true`（A1 Done + pendingDecisionQueueCount=0 + freeze keys一致）
  2. `Approval Record` 必須フィールドが入力済み
  3. docs-check成功（validator/unittest/diff）
- 停止条件（No-Go / 即停止）:
  1. `pending bypass` または未承認事項の確定化
  2. `safeModeDefault=ON` / `overridePolicy=human_dual_control_only` / `sharedResourceFreeze=true` の後退要求
  3. `Source Issue` 運用逸脱（親子関係喪失・return path改変）
- 現在判定:
  - `Approval Record: Pending` と Decision Queue未解消のため **Conditional（準備継続）**。


## Stream A serial execution log（2026-04-28 / 固定順 Phase 3）

### Fixed Phase
- Phase 3: `HIL-RS-01 A1 minimum I/F`（本Issue）

### Read Sync
- 対象5Issueを再読し、`Status / Scope / Dependencies / 固定キー` の一致を確認。
- 判定: 差分0、`A1 -> A2 -> A3` 依存順を維持。

### Plan
- 最小I/Fシグネチャ定義のみを扱い、契約値再定義・実装確定は禁止。
- A2/A3向けには `mock可能な最小シグネチャ` のread-only引き渡しに限定。

### ADR合意ゲート（必須）
- Context: A1最小I/Fの曖昧さはA2/A3での未定義競合を誘発する。
- Decision: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` と関連固定キーを不変とする。
- Consequences: A1完了前のA2/A3 Open禁止、NoGo pathはA1へ固定。
- Approval Record: `Pending`（`approved_by` / `approved_at` / `evidence` 未入力）。

### Execute
- 実施: I/F契約記述の整合チェックとログ化のみ。

### Verify
- 自己検証: 固定キー後退兆候なし、Pending bypassなし、NoGo path改変なし。
- self-correction: `0/3`。

### Proceed
- 判定: `Conditional`。
- 根拠: 承認記録未確定のため、Phase 4（RS-01 umbrella）への進行は保留。


## Stream A proceed gate replay（2026-04-29）

- Phase再読結果: fixed keys diff=`0`。
- 承認状態: `Approval Record: Pending`（`approved_by` / `approved_at` / `evidence` 未入力）。
- Proceed判定: **Conditional / Needs-decision**。
- 停止理由: 承認未充足のため、A2/A3へのOpen昇格不可。
- 再開条件: 承認証跡入力完了 + `pendingDecisionQueueCount==0`。

## Stream A serial phase checkpoint（2026-04-29）

### Phase 1: RS-01 A1 契約固定確認（Read -> Verify）
- Context: A1契約は全後続Phaseの唯一参照点であり、再定義を許容しない。
- Decision: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / gate式固定を再確認し、差分0を維持する。
- Consequences: 承認記録が `Pending` の間は Execute確定化を禁止し、`held` 維持で進行する。

### Phase 2: RS-01 Umbrella整合（Plan -> Execute）
- Context: Umbrella側の依存ゲート記述がA1契約と不整合だと依存順が逆転する。
- Decision: A1契約を参照する記法（再定義禁止）へ統一し、`A1 -> A2 -> A3` を固定順として再確認した。
- Consequences: 後続Phaseは参照整合を前提に進行可能。契約値更新要求は `NoGo` 扱い。

### Phase 3: RS-02 Delivery Plan整合（Verify）
- Context: Delivery PlanはA1完了前提・hold条件・Proceed条件を明確に切り分ける必要がある。
- Decision: 実装記述は契約参照型へ統一し、固定キーの再掲は参照のみ（再定義なし）とする。
- Consequences: `Approval Record: Pending` と `held` が残る間は Conditional運用を維持する。

### Phase 4: RS-02 A1 Governance Hardening（Plan -> Execute -> Verify）
- Context: 例外系（held）を曖昧にすると pending bypass の温床になる。
- Decision: heldは「未承認確定化禁止」のための隔離状態として定義を維持し、確定遷移を禁止する。
- Consequences: 未定義競合・4回目相当self-correction・allowlist外編集要求は即停止トリガーとして継続適用。

### Phase 5: RS-02 A3 Draft gate管理（Proceed）
- Context: A3はA1依存解消前にOpen化してはならない。
- Decision: `Status: Draft` 維持、Open化は `a1Status=="Done" && pendingDecisionQueueCount==0` 充足時のみ許可、運用ドキュメント同期は前提固定のみ実施。
- Consequences: 判定は **Conditional**（準備継続）で据え置き、NoGo差戻し先はA1 issueに固定。

### Phase verification mini-checklist（本チェックポイント）
- Header整合（Status/Priority/Scope/Related ADR/Spec）: 確認済み。
- 固定キー不変性（freezeContractId / NoGo return path / safeMode固定値 / gate式）: 差分0。
- 依存順序逆転（A1 -> A2 -> A3）: 未検知。
- 変更差分allowlist（許可5ファイル内のみ）: 準拠。

## Stream A execution snapshot（2026-04-29 / serial-phase sync）

### Phase 1: Read & Snapshot
- 対象5Issueを再読し、`Status / Scope / Dependencies / 固定キー` の想定との差分を確認。
- 差分判定: `no unexpected drift`（Proceed可）。

### Phase 2: ADR/CDC明文化
- **Context**: A1契約固定値を変更せず、A2/A3は参照専用で運用する必要がある。
- **Decision**: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を再確認し再定義しない。
- **Consequences**: `Approval Record: Pending` が残る限り、Open化や契約確定化は行わない。
- **Approval log**: `Pending`（required fields: `approved_by`, `approved_at`, `evidence` 未入力）。

### Phase 3: Plan（A1→A2→A3直列）
- 対象: 本Issue内の計画/ゲート/検証記述の整合維持。
- AC/DoD不足: 追加不足なし（既存Draft AC/DoDを継続）。
- 非対象: 5Issue以外の編集、実装コード変更、他ストリーム依存追加。

### Phase 4: Execute
- 実施: 本Issueへの実行スナップショット追記のみ。
- 非実施: 契約値更新、NoGo return path変更、safeMode境界緩和、pending bypass。

### Phase 5: Verify（self-correction max 3）
- self-correction: `0/3`。
- docs-checkはPhase 6判定前提として実行し、失敗時のみ再試行カウントを加算する。

### Phase 6: Proceed or Stop
- 判定: **Conditional / Needs-decision**。
- 理由: `Approval Record: Pending` および `held` 論点が残存。
- 再開条件: `approved_by` / `approved_at` / `evidence` の入力完了、かつ `a1Status=="Done" && pendingDecisionQueueCount==0` の充足。
