# Issue Draft: HIL-RS-01 次フェーズ計画（Human-in-the-loop 可逆統合）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner (Stream C contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（contract reference only）, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`（SSOT）, `A1 -> A2 -> A3`（gate reference）
- Related ADR/Spec: `ADR-0026`（Context）, `ADR-0027`（Decision）, `ADR-0001`（Consequences）, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`（contract SSOT）
- Expected verification level: `docs-check`
- Non-target file policy: 本ストリームで編集許可された4 Issue（`issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `issue-HIL-RS-02-next-phase-delivery-plan.md` / `issue-HIL-RS-02-A1-governance-contract-hardening.md`）以外は不干渉

- Contract snapshot date: `2026-04-27`（固定入力）
- Execution order (Stream C fixed serial): 2/4 HIL-RS-01 umbrella

## Stream C Contract Lock（HIL-RS fixed）
- Contract ID固定: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（再定義禁止）
- `NoGo return path` 固定: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（変更禁止）
- `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` は境界条件として固定（緩和禁止）
- 未承認事項（`Approval Record: Pending`）が1件でも残る場合は `Phase 4 Execute` へ進行禁止

## Phase Control Macro（各Phase共通）
- 各Phase開始直前に必ず対象4ファイルを再読し、`Status / Scope / Dependencies / 固定キー` をRead同期する。
- 各Phaseは `Plan -> Execute -> Verify -> Proceed` の順序を必須とし、スキップ/逆走を禁止する。
- フェイルセーフ検知時（4回目相当self-correction、未承認確定化、未定義競合、指定外編集要求）は即停止し、次の3点を必ず出力する。
  1. 原因
  2. 影響I/F
  3. 人間判断が必要な論点


### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read（再読・差分確認）
- 差分検知時は停止候補として `held` に記録し、Executeへ進まない。
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
- RS-01はRS-02の前段であり、状態遷移契約の不一致を許容しない。

### Decision
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
- A1未完了でA2/A3 Open禁止。
- Plan -> Execute -> Verify -> Proceed の直列運用を固定。

### held
- 未承認事項は `held` のまま固定（確定扱いしない）。

## Phase 3: Plan
- 宣言: `Plan -> Execute -> Verify -> Proceed`（直列運用・逆走禁止・各Phaseで必須）。
- 対象差分意図: RS-01の開放条件をA1 SSOTへ揃える。
- 非対象不干渉: 編集許可された4 Issue以外は編集しない。
- Scope: HIL-RS 契約/運用ハードニング（Docsのみ）
- Non-goals: 実装コード変更 / README・dashboard更新 / 対象外Issue編集
- Interface placeholder policy: A2/A3依存は mock前提の最小I/F記述に限定し、実装確定を行わない。
- Gate式は固定値を参照のみとし、再定義・派生定義を禁止する。
- AC/DoD
  - AC: fixed keys差分0 / decisionQueueTransition固定 / NoGo return path一意。
  - DoD: safeModeDefault=ON維持 / overridePolicy後退なし / self-correction<=3。
- 検証コマンド（Plan時点で固定）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Contract Freeze Snapshot（A2/A3 read-only引き渡し）
- `contract_id=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schema_version=1.0.0`
- `contract_ids=[A1-CRITIQUE-IF, A1-REDIFF-IF, A1-ATTR-IF, A1-ERROR-IF]`
- `prohibited_changes`:
  1. Contract IDs / `schemaVersion` / `overridePolicy` の変更
  2. `contractLinkLocked=true` / `sharedResourceFreeze=true` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` の後退
  3. Decision Queue の `Pending` bypass
  4. A1 完了前の A2/A3 Open 化

### Mock可能な最小シグネチャ（Contract-only）
```yaml
stream_a_freeze:
  contract_id: "HIL-RS-02-A1-CONTRACT-FREEZE-v1"
  schema_version: "1.0.0"
  must_match:
    override_policy: "human_dual_control_only"
    contract_link_locked: true
    shared_resource_freeze: true
    safe_mode_default: "ON"
    safe_mode_boundary: "SAFE_MODE_STRICT_ON"
gate:
  a2a3_unlock: "a1Status == Done && pendingDecisionQueueCount == 0"
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
- Go: `ProceedGate=true` かつ AC/DoD充足、`held` 以外の未承認事項なし。
- Conditional: `ProceedGate=false` だが未承認事項が `held` のみに限定される場合。
- No-Go: 前提崩れ、未定義競合、未承認確定、Self-Correction 3回超過、指定外差分。
- No-Go時出力: 原因・影響・再開条件を明文化する。
- 記録必須: 成果 / 未解決 / 次の1手（1項目）を残す。


## Stream C AC/DoD Draft Proposal（Pending Approval）

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

## Stream C handover checkpoint（2026-04-27）

### Phase 6 Proceed判定（今回）
- 判定: **Needs-decision**（`Approval Record: Pending` と `held` 論点が残存）。
- Go/No-Go条件: 既存の `ProceedGate` / `NoGo` 判定式を継続適用（再定義しない）。

### 未確定論点一覧（次回引き継ぎ）
1. `Approval Record` の承認主体・時刻・証跡（`approved_by` / `approved_at` / `evidence`）が未入力。
2. `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持中で、人間判断待ち。
3. A2/A3公開判定は `A1 Done && pendingDecisionQueueCount==0` 未充足のため据え置き。

### No-Go条件の再確認
- self-correction 4回目相当、未承認確定化、未定義競合、allowlist外編集要求を検知した場合は即停止して人間へエスカレーションする。


## Stream C critical-path execution log（2026-04-27 / contract governance hardening）

#
### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read
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

## Stream C execution runbook log（2026-04-27 / Critical Path replay）

#
### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read snapshot（before change）
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

## Stream C fixed-serial protocol replay（2026-04-27 / Plan→Execute→Verify→Proceed）

- Issue order position: `2/4 HIL-RS-01 umbrella`
- Protocol lock: 各Phaseで `Plan -> Execute -> Verify -> Proceed` を維持（逆走・省略禁止）。
- Contract lock: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` を固定。

#
### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read
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

## Stream C execution log（2026-04-28 / HIL-RS critical path replay）

#
### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read（状態同期）
- 対象4ファイルを再読し、`Status / Priority / Scope / Dependencies / Approval Record / held` を同期確認。
- 結果: `Status=Open`（A3のみDraft）/ `Priority=P1` / `Scope=planning only` / `Dependencies=A1 -> A2 -> A3` / `Approval Record=Pending` / `held` 論点継続。
- 事前想定との差分: なし（`held` 追加なし）。

### Phase 2: ADR/CDC（実装前必須）
- Context: A1契約凍結をSSOTとして維持し、A2/A3を誤って先行確定しない。
- Decision: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`・`safeModeDefault=ON`・`safeModeBoundary=SAFE_MODE_STRICT_ON`・`NoGo return path=A1 issue` を再確認し固定維持。
- Consequences: `Approval Record` 未充足（`approved_by` / `approved_at` / `evidence` 未入力）のため Execute での確定化は継続禁止。

### Phase 3: Plan（AC/DoD先行）
- Scope: 4 Issue間の契約固定・ゲート条件・運用記録の同期（docs-only）。
- Non-goals: 実装コード変更、allowlist外編集、pending bypass確定化。
- Acceptance Criteria:
  1. 固定キー差分 `0`。
  2. `A2A3_OPEN_ALLOWED` 判定式の再定義なし。
  3. `NoGo return path` がA1 issue一意固定。
  4. `Approval Record: Pending` を確定扱いしない。
- Definition of Done:
  1. `Plan -> Execute -> Verify -> Proceed` の順序ログを記録。
  2. self-correction 回数を `0-3` で記録。
  3. Go/Conditional/No-Go 判定根拠を明記。
- Validation Plan:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Stop Conditions: self-correction 4回目相当、未承認確定化、NoGo return path改変要求、safeMode境界後退検知。

### Phase 4: Execute
- 実施内容: 本Issueへの運用ログ追記のみ。
- 非実施: 固定契約値の更新、NoGo return path改変、safeMode境界緩和、allowlist外ファイル編集。

### Phase 5: Verify
- docs-check を Phase 3 の Validation Plan に従って実施。
- self-correction: `0/3`（再試行なし）。

### Phase 6: Proceed / Stop
- 判定: **Conditional**。
- 理由: `Approval Record: Pending` および `held` 論点が残存し、Go条件が未充足。
- 継続条件: 人間承認フィールドの充足（`approved_by` / `approved_at` / `evidence`）と pendingDecisionQueue 解消。


## Stream C fixed-serial execution log（2026-04-28 / HIL-RS critical contract governance）

#
### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read
- 対象4ファイルを再読し、`Status / Scope / Dependencies / 固定キー`（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `unlockRule`）を同期確認。
- 読み取り結果: `Status=Open` / `Scope=planning only` / `Dependencies=A1 -> A2 -> A3`。
- 固定I/F正規化: `unlockRule=(a1Status=="Done" && pendingDecisionQueueCount==0)` を canonical として参照し、派生再定義を禁止。
- 差分判定: fixed keys diff=`0`。`held` 追加なし。

### Phase 2: ADR/CDC（Context / Decision / Consequences）
- Context: Stream Cは `HIL-RS-02-A1-CONTRACT-FREEZE-v1` を単一契約として維持し、A1ゲート迂回を禁止する。
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

## Stream C Proceed Handover Package（Fixed Contract / Prohibitions / Stop-Resume）

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

#
### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read（Status / AC / Dependency contradiction list）
- 読取対象: 本Issue + HIL-RS対象4Issueのメタ（Status / Source Issue / AC/DoD / Dependencies / Validation）。
- 検知した矛盾（横断）:
  1. `Non-target file policy` の文言が「4 Issue」表記のままになっている箇所があり、実際の対象4Issueと不一致。
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


## Stream C serial execution log（2026-04-28 / 固定順 Phase 4）

### Fixed Phase
- Phase 4: `HIL-RS-01 umbrella`（本Issue）

### Read Sync
- 対象4Issueを再読し、`Status / Scope / Dependencies / 固定キー` を横断照合。
- 判定: 固定キー差分0、`NoGo return path` はA1 issueで一意。

### Plan
- Umbrellaとしての契約統治・停止条件の固定に限定。
- A2/A3依存は mock前提シグネチャ参照のみ、実装確定は行わない。

### ADR合意ゲート（必須）
- Context: Umbrellaが依存順/停止条件を保持しないと各A系Issueが独立ドリフトする。
- Decision: `Plan -> Execute -> Verify -> Proceed` と fail-safe停止条件を再固定。
- Consequences: 未承認事項は`held`維持、承認完了まで確定化禁止。
- Approval Record: `Pending`（`approved_by` / `approved_at` / `evidence` 未入力）。

### Execute
- 実施: 本Issue内のガードレール再確認ログ追記のみ。

### Verify
- 自己検証: safe mode境界後退なし、NoGo return path改変なし、未定義競合なし。
- self-correction: `0/3`。

### Proceed
- 判定: `Conditional`。
- 根拠: `Approval Record: Pending` が残存し、次Phaseは承認確定後にのみ進行可能。


## Stream C Phase checkpoint（2026-04-29）

### Contract Baseline Read
- 再読対象: RS-01 umbrella / RS-01 A1 / RS-02 umbrella / RS-02 A1 / RS-02 A3。
- 依存: `A1 -> A2 -> A3` を維持。
- Pending承認: `Approval Record` が未入力のため **承認待ち**。

### AC/DoD draft補完（承認待ち）
- AC案: `Status/Dependencies/fixed keys` の差分ゼロを Proceed前提にする。
- DoD案: `Needs-decision` 判定時は Execute確定を停止し、`原因/影響I/F/再開条件` を記録する。
- 合意状態: **Pending**（人間承認待ち）。

## Stream C serial phase checkpoint（2026-04-29）

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

## Stream C execution snapshot（2026-04-29 / serial-phase sync）

#
### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read & Snapshot
- 対象4Issueを再読し、`Status / Scope / Dependencies / 固定キー` の想定との差分を確認。
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


## Stream C alignment note (2026-04-29)
- Phase 1-5の直列運用（Plan -> Execute -> Verify -> Proceed）を再確認。
- 承認未充足時は `Needs-decision` を維持し、下流の確定化へ進まない。
- A1契約凍結値は参照専用（再定義禁止）。


## Stream B execution update（2026-05-01 / HIL-RS execution-plan alignment）

#
### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read同期
- allowlist 2ファイル（本Issue / `issue-HIL-RS-02-next-phase-delivery-plan.md`）を再読し、`Status / Scope / Dependencies / 固定キー` を照合。
- Stream C 凍結I/F（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `NoGo return path`）との矛盾を確認し、差分 `0`。
- 結果: **Proceed可**（矛盾検知なし）。

### Phase 2: ADR/CDC（必要時）
- 新規方針差分は未検知のため、C/D/Cの追加定義は実施しない（既存契約を参照のみ）。
- `Approval Record: Pending` は維持し、未承認事項の確定化は行わない。

### Phase 3: Plan（A1→A2→A3 直列化の明文化）
- 実行順序を `A1 (contract freeze complete) -> A2 (mock I/F preparation) -> A3 (delivery/ops sync)` に固定。
- A2着手条件: `a1Status=="Done" && pendingDecisionQueueCount==0` かつ固定キー差分 `0`。
- A3着手条件: A2で `validatorPass==true`、`pending bypass` なし、`held` が未承認論点のみに限定。
- 停止条件: 未承認確定化、Stream C契約矛盾、allowlist外編集要求、`self_correction_attempt>=4`。

### Phase 4: Execute（planning docs only）
- 契約本体は変更せず、実行計画の着手条件/停止条件のみを明文化（本追記）。
- 実装コード・共有3ファイル・allowlist外ファイルは未編集。

### Phase 5: Verify
- AC照合:
  - `A1 -> A2 -> A3` の順序で実行可能: **pass**
- DoD照合:
  - A2着手条件を明示: **pass**
  - A3着手条件を明示: **pass**
  - 停止条件を明示: **pass**
- Self-Correction: `0/3`（再試行なし）。

### Phase 6: Proceed
- 判定: **Needs-decision**。
- 理由: `Approval Record: Pending` と `held` 論点が残存し、人間承認待ちのため。
- 次へ渡す着手条件:
  1. `approved_by` / `approved_at` / `evidence` を充足。
  2. `pendingDecisionQueueCount==0` を確認。
  3. 固定キー差分 `0` を再確認後に A2 を開始。


## Stream B serial checkpoint（2026-05-01 / HIL-RS contract-governance alignment）

### Phase 1 Read
- 対象4Issueを再読し、`Status / Scope / Dependencies / 固定キー` を同期。
- 固定キー（`freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault / safeModeBoundary / unlockRule / decisionQueueTransition`）差分は `0`。

### Phase 2 ADR/CDC
- Context: A1固定を崩さず、A2/A3の契約再定義を禁止する。
- Decision: `safeModeDefault=ON` 維持、Contract ID凍結値再定義なし、`A1 -> A2 -> A3` 順序維持。
- Consequences: `Approval Record: Pending` が残るため、Executeで確定化は実施しない。

### Phase 3 Plan
- AC/DoD不足は追加未検知（既存Draft継続）。
- A3は `mock I/F preparation only` を維持し、実装確定を禁止。

### Phase 4 Execute
- 実施: 本5Issueへの整合ログ追記のみ。
- 非実施: allowlist外編集、契約値変更、Pending bypass、Open強行。

### Phase 5 Verify
- self-correction: `0/3`。
- Verify失敗・未定義競合・allowlist外編集要求は未検知。

### Phase 6 Proceed/Stop
- 判定: **Conditional / Needs-decision**。
- 理由: 未承認事項（`Approval Record: Pending`）が残存。
- Stop条件の再掲: 4回目相当self-correction、未定義競合、allowlist外編集要求を検知した場合は即停止。


## Stream F serial execution log（2026-05-02）

### Phase 1 Read
- A1完了後に本Issue本文を再読し、Status=`Open` / Dependencies=`A1 -> A2 -> A3` / `Approval Record: Pending` を抽出。
- 想定との差分: 既存本文のOwner/allowlist表記がStream C前提のまま残存（本実行はStream F専任）。

### Phase 2 CDC
- Context: HILループ未固定境界をA1契約へ従属させ、直列依存を破らない。
- Decision:
  1. 人間承認が必要な遷移は `Pending -> Approved|Rejected` のみ。
  2. 可逆性境界は `NoGo return path` をA1へ固定し、A2/A3開放条件を厳守。
  3. 監査ログ要件は `approved_by` / `approved_at` / `evidence` 必須を維持。
- Consequences: 即時自動化は抑制されるが、統治性と監査可能性を優先できる。

### Phase 3 Plan
- AC/DoD不足は新規なし。既存 AC-D1〜D3 / DoD-D1〜D3 を継続。
- 最低要件の充足確認:
  - 決定キュー状態定義あり（Pending起点のみ）。
  - Go/Conditional/No-Go 判定条件あり（既存式を再利用）。
  - review状態の自動昇格禁止あり（Pending bypass禁止）。

### Phase 4 Execute
- 直列順2件目として本Issueを更新。
- 他ファイルへ依存を追加せず、本Issue内の契約運用ログのみ追記。

### Phase 5 Verify
- A1との契約照合を実施し、`freezeContractId` / `schemaVersion` / `overridePolicy` / `safeMode` / `decisionQueueTransition` の矛盾なし。
- Self-repair実績: `0/3`。

### Phase 6 Proceed
- Issue判定: **Conditional**。
- 根拠: `Approval Record: Pending` と held論点が残存。
- 次の1手: 人間承認レコード入力後に `A2A3_OPEN_ALLOWED` を再評価。

## Stream F final integrated verdict（2026-05-02）
- A1判定: **Conditional**（承認待ち）。
- Next-phase判定: **Conditional**（承認待ち）。
- 総合判定: **Conditional / Stop**（未承認事項の既成事実化を避けるため、ここで停止）。

## Stream A contract fixation sync（2026-05-02 / A1 critical path）

#
### Phase 1 normalization rule（dependency）
- 依存記述は **contract reference only** とし、実装タスク・実装順の依存は記述しない。
- 参照先は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の2点へ正規化する。
- 契約参照差分が発生した場合は Executeへ進まず、ADRの **Context / Decision / Consequences** を先に確定して承認待ちへ移行する。

## Phase 1: Read同期（Plan → Execute → Verify → Proceed）
- 対象再読: 本Issue + A1契約Issue群。
- 未確定項目: `Approval Record`（`approved_by` / `approved_at` / `evidence` 未入力）, `HIL-RS-02-GOV-EXCEPTION-01`（`held`）。
- 差分判定: 固定キー（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）は差分 `0`。

### Phase 2: ADR明文化ゲート（Context / Decision / Consequences）
- Context: `A1 -> A2 -> A3` 依存の唯一ゲートをA1契約に固定し、派生再定義を禁止する。
- Decision: `A2A3_OPEN_ALLOWED` を唯一判定式として固定し、A2/A3は read-only 参照のみ許可。
- Consequences: 未承認事項は `Needs-decision` を維持し、承認完了まで Executeを契約同期（docs）に限定。

### Phase 3: 契約固定（A2/A3変更禁止範囲を明示）
- Frozen IDs: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`。
- Frozen gate: `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`。
- Prohibited mutations: 契約ID変更、`schemaVersion`改版、Pending bypass、`safeModeDefault=ON`/`safeModeBoundary=SAFE_MODE_STRICT_ON` 緩和、`NoGo return path` 変更。

### Phase 4: Stream B/C handoff（mock-first）
- Mock contract: `A1-CONTRACT-MOCK-v1`（実装依存なし）。
- Handoff package:
  1. SSOT参照: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
  2. 固定値一覧: 本セクション Phase 3
  3. 変更禁止範囲: `03_Implement/**` と A1以外での契約再定義
- Stop conditions: self-correction 4回目相当 / allowlist外編集要求 / 前提崩壊 / 未承認確定化。
## Stream C fixed-order sync log（2026-05-02 / HIL-RS Contract Lane）

### Phase alignment check
- 固定実行順を再確認: `Phase 1 (HIL-RS-01 A1) -> Phase 2 (HIL-RS-01 umbrella) -> Phase 3 (HIL-RS-02 A1) -> Phase 4 (HIL-RS-02 delivery)`。
- 開始時Read同期（`Status / Dependencies / 固定キー`）を実施し、4ファイル間で `diff=0` を確認。

### ADR/CDC + Approval handling
- ADR/CDCは既存Decisionを再定義せず維持（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`）。
- `Approval Record: Pending` を未承認確定化せず、`held` 維持を継続。

### Plan -> Execute -> Verify -> Proceed
- Plan: allowlist 4ファイル内のみで運用記録を更新。
- Execute: 本文末尾への固定順運用ログ追記のみ（契約値変更なし）。
- Verify: 判定式・固定キー・NoGo return path の不変を再確認。
- Proceed: 判定は `Conditional` 維持（未承認/held 残存のため）。

### Self-Correction / Stop conditions
- Self-Correction counter: `0/3`（再試行なし）。
- 4回目相当、未承認確定化、未定義競合は未検知。
- 継続条件: `approved_by` / `approved_at` / `evidence` の充足後に次段階再判定。
