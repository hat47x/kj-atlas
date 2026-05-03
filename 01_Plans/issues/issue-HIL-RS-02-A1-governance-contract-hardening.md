# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening (Stream B)

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner (Stream B governance contract)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（contract reference only）, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`（SSOT）, `A1 -> A2 -> A3`（gate reference）
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`
- Non-target file policy: Stream C allowlist（`issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `issue-HIL-RS-02-A1-governance-contract-hardening.md` / 必要時 `ADR-0026/0027/0028`）以外は編集禁止

- Contract snapshot date: `2026-04-27`（固定入力）
- Execution order (Stream B fixed serial): HIL-RS-02 A1 single-scope

## Stream B Operating Boundary（越境防止）
- このストリームは **A1契約ハードニングのみ** を扱う。
- A2/A3 の `Draft -> Open` 判定は **本ストリームで実行しない**（read-only参照のみ）。
- `human_dual_control_only` は固定値であり、緩和/別名化/派生定義を禁止する。
- Decision Queue は `Pending` を省略せず、`Pending -> Approved | Pending -> Rejected` のみ許可する。
- フェイルセーフ（即停止）:
  1. 契約ID齟齬
  2. safeMode後退要求
  3. 共有リソース競合（freeze対象への未承認変更要求）

## Stream C Contract Lock（HIL-RS fixed）
- Contract ID固定: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（再定義禁止）
- `NoGo return path` 固定: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（変更禁止）
- `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` は境界条件として固定（緩和禁止）
- 未承認事項（`Approval Record: Pending`）が1件でも残る場合は `Phase 4 Execute` へ進行禁止


## Contract Vocabulary Sync Baseline（HIL-RS-02-A1-CONTRACT-FREEZE-v1）
- Canonical vocabulary（再定義禁止）: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `unlockRule`, `decisionQueueTransition`, `NoGo return path`
- Canonical values（固定）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Execute prohibition: `Approval Record: Pending` が1件でも残る場合は `Execute=Forbidden`（`Plan/Verify` のみ許可）。

## Phase Control Macro（各Phase共通）
- **Execute gate hard-stop**: `Approval Record: Pending` が1件でも残存する場合、`Phase 4 Execute` は常に禁止（Go/Conditional判定前に停止）。
- 各Phase開始直前に必ず対象4ファイルを再読し、`Status / Scope / Dependencies / 固定キー` をRead同期する。
- 各Phaseは `Plan -> Execute -> Verify -> Proceed` の順序を必須とし、スキップ/逆走を禁止する。
- フェイルセーフ検知時（4回目相当self-correction、未承認確定化、未定義競合、指定外編集要求）は即停止し、次の3点を必ず出力する。
  1. 原因
  2. 影響I/F
  3. 人間判断が必要な論点

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
- RS-02では誤OpenとPending bypassを防ぐ統治硬化が必要。

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

### Approval Record（必須 / 承認待ち）
- Status: `Pending`（未承認のため確定実装扱い禁止）
- requested_by: `Stream C agent`
- requested_at: `2026-04-30T00:00:00Z`
- required_approvers: `Stream C Architecture Owner` + `Governance reviewer (dual-control)`
- approval_evidence_required:
  1. `ADR-0027 D5/D6` の固定キー・停止条件との整合確認。
  2. `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の Freeze keys 一致確認。
  3. AC/DoD（Gate式・No-Go条件・依存切断性）の明示確認。
- note: 承認が完了するまで本IssueのDecisionは `contract-only draft` として扱い、A2/A3のOpen判定に使う実装確定値へ昇格させない。

### Consequences
- A1以外への差戻し禁止。
- `Pending bypass` 禁止。
- A2/A3 Open化判断は A1完了後の別ストリーム責務として保持し、本ストリームでは未決のまま維持する。

### held
- `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持。

## Phase 3: Plan
- 宣言: `Plan -> Execute -> Verify -> Proceed`（直列運用・逆走禁止・各Phaseで必須）。
- 対象差分意図: Go/NoGo判定式と禁止遷移を固定。
- 非対象不干渉: 編集許可された4 Issue以外は編集しない。
- Scope: HIL-RS 契約/運用ハードニング（Docsのみ）
- Non-goals: 実装コード変更 / README・dashboard更新 / 対象外Issue編集
- Interface placeholder policy: A2/A3依存は mock前提の最小I/F記述に限定し、実装確定を行わない。
- Gate式は固定値を参照のみとし、再定義・派生定義を禁止する。
- AC/DoD
  - AC: fixed keys diff=0 / return path唯一 / Pending bypass禁止明記。
  - AC: `human_dual_control_only` 後退要求を 0 件で維持。
  - DoD: 判定式一貫 / self-correction<=3 / 未承認を確定扱いしない / A2A3 Open判定を行わない。
- 検証コマンド（Plan時点で固定）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### 依存マップ更新（ADR -> Issue -> 契約）
- ADR:
  - `ADR-0026`: HIL-RS-01 の価値軸・A1先行原則
  - `ADR-0027`: HIL-RS-02 の固定遷移・停止条件・Freeze ID
  - `ADR-0028`: 認知外在化要件のフェーズ接続
- Issue:
  - `issue-HIL-RS-02-next-phase-delivery-plan.md`（Umbrella）
  - `issue-HIL-RS-02-A1-governance-contract-hardening.md`（本Issue / 先行必須）
  - `issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`（A1完了後Open）
  - `issue-HIL-RS-02-A3-operations-documentation-sync.md`（A1完了後Open）
- Contract SSOT:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
  - freeze: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`

### A2/A3向けモック契約断面（read-only handoff）
- mock利用可（実装依存なし）:
  - `A1-CRITIQUE-IF -> CritiqueV1`
  - `A1-REDIFF-IF -> ReDiffV1`
  - `A1-ATTR-IF -> AttributionV1`
  - `A1-ERROR-IF -> A1ErrorV1`
- 固定条件:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 禁止:
  - 契約ID再定義
  - `Pending` bypass
  - safeMode / share-export 境界の緩和

### Contract Freeze Snapshot（A2/A3 read-only引き渡し）
- `contract_id=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schema_version=1.0.0`
- `contract_ids=[A1-CRITIQUE-IF, A1-REDIFF-IF, A1-ATTR-IF, A1-ERROR-IF]`
- `governance_fixed`:
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `prohibited_changes`:
  1. Pending bypass（未承認確定）
  2. A1外への NoGo return path 変更
  3. A1未完了での A2/A3 Open
  4. safeMode / dual-control / freeze keys の後退

### Freeze判定条件（contractLinkLocked / sharedResourceFreeze）
- `contractLinkLocked=true` の成立条件（全て必須）
  1. `freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1"` が一致していること。
  2. `contract_ids` の4要素（`A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`）が同一順序で一致していること。
  3. `NoGo return path` が `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` に固定されていること。
  4. A2/A3側文書が `DependsOnContractID/ReferenceContractID` でA1契約を参照し、再定義していないこと。
- `sharedResourceFreeze=true` の成立条件（全て必須）
  1. `schemaVersion=="1.0.0"` かつ `overridePolicy=="human_dual_control_only"` が一致していること。
  2. `safeModeDefault=="ON"` かつ `safeModeBoundary=="SAFE_MODE_STRICT_ON"` が一致していること。
  3. `decisionQueueTransition=="Pending -> Approved | Pending -> Rejected"` が一致していること。
  4. `pendingBypassDetected==false` かつ `undefinedConflictDetected==false` であること。
- いずれか1条件でも不一致の場合は `NoGo` とし、A2/A3の更新を停止してA1へ差し戻す。

### A2/A3参照固定値（変更禁止）
- Fixed IDs:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `SnapshotID=SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Fixed value set:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Prohibited mutation:
  - enum追加・判定式派生・ID改名・NoGo return path変更・Pending bypass。

### Mock可能な最小シグネチャ（Governance Gate）
```yaml
governance_gate_v1:
  freeze_contract_id: "HIL-RS-02-A1-CONTRACT-FREEZE-v1"
  schema_version: "1.0.0"
  require:
    override_policy: "human_dual_control_only"
    contract_link_locked: true
    shared_resource_freeze: true
    safe_mode_default: "ON"
    safe_mode_boundary: "SAFE_MODE_STRICT_ON"
  reject_if:
    - "pending_bypass_detected == true"
    - "a1_status != Done && a2_or_a3_open_requested == true"
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

## Workflow Trace（Read同期 → Plan → ADR合意 → Execute → Verify → Proceed）
### Step 1: Read同期（single-scope）
- Read同期対象（固定）:
  1. `issue-HIL-RS-02-A1-governance-contract-hardening.md`（本Issue）
  2. `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（NoGo return path）
  3. `ADR-0026` / `ADR-0027` / `ADR-0028`（read-only）
- Read同期出力（固定）:
  - `Status=Open`
  - `Scope=planning only`
  - `Dependencies=A1 -> A2 -> A3`
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`
- 判定: 上記固定値に差分が1件でもあれば `held` へ記録し即停止（Execute進行禁止）。

### Step 2: Plan（AC/DoD不足補完提案）
- 補完提案（Draft; Approval Record合意まで未確定）:
  1. **AC-ADD-01**: `decisionQueueTransition` が `Pending -> Approved | Pending -> Rejected` 以外を許容しないことを明文化。
  2. **AC-ADD-02**: `NoGo return path` が単一固定値であることを `diff=0` で検証することを明文化。
  3. **DoD-ADD-01**: `human_dual_control_only` の同義語・別名・派生キー追加を禁止することを明文化。
  4. **DoD-ADD-02**: A2/A3向け記述は mock I/F のみ（実装確定禁止）を検証項目として明文化。
- self-correction policy:
  - 許容回数は最大3回（4回目相当は fail-safe 即停止）。
  - 各再試行で「原因 / 修正内容 / 未解決論点」を更新し、未承認事項は `held` に維持する。

### Step 3: ADR合意（必要時）
- ADR更新が必要となる条件:
  1. `freezeContractId` / `contractIds` / `overridePolicy` / `safeMode*` の定義変更が必要になった場合。
  2. `A2A3_OPEN_ALLOWED` の論理式に変更要求が入った場合。
- 上記条件に1つでも該当する場合は `ADR-0027` を起点に合意完了まで `Execute=NoGo`。
- 本Issue単独で確定できるのは **契約固定の文書化** のみ（規範変更は不可）。

### Step 4: Execute（contract hardening doc fix）
- 実施内容は本Issue文書内の固定キー・判定式・禁止遷移の整形/明確化に限定する。
- scope外編集は禁止（allowlist外ファイル変更は fail-safe 即停止）。
- 依存は mock可能I/F で切断し、A2/A3の状態遷移確定を実施しない。

### Step 5: Verify
- 実行順序（固定）:
  1. AC/DoD自己検証
  2. `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  3. `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  4. `git diff --check`
- 失敗時は self-correction を最大3回まで実施し、4回目相当で即停止。

### Step 6: Proceed
- `Proceed=Go` 条件:
  - `A2A3_OPEN_ALLOWED==true` かつ `validatorPass==true` かつ `pendingApprovalCount==0`
- `Proceed=Conditional` 条件:
  - `A2A3_OPEN_ALLOWED==false` かつ `heldCount>0` かつ `unresolvedApprovalsAreHeldOnly==true`
- `Proceed=NoGo` 条件:
  - 上記以外すべて（特に pending bypass / undefined conflict / scope外編集要求）
- `NoGo` 時は以下3点を必須出力:
  1. 原因
  2. 影響I/F
  3. 人間判断が必要な論点
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
- No-Go: ドリフト、Pending bypass、未定義競合、Self-Correction 3回超過、指定外差分。
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

## Stream C execution record（2026-04-30 / Critical Governance Contract Audit）

### Phase 1: Read Gate（Plan -> Execute -> Verify -> Proceed）
- Plan:
  - 対象: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` と本Issue。
  - AC: 固定キー（`freezeContractId/schemaVersion/overridePolicy/safeMode境界/decisionQueueTransition`）差分0。
  - DoD: 未確定項目の一覧化と不足有無判定を記録。
- Execute:
  - 契約項目・固定値・未確定点を再読監査し、差分なしを確認。
- Verify:
  - 固定キー差分 `0`、未確定項目は `held` 1件（`HIL-RS-02-GOV-EXCEPTION-01`）のみ。
- Proceed:
  - Phase 2進行可。

### Phase 2: ADR判定（Plan -> Execute -> Verify -> Proceed）
- Plan:
  - 運用解釈で吸収不能な差分があるかを判定し、必要時のみADR草案を準備。
- Execute:
  - 判定結果: 新規ADR不要（既存A1契約とADR-0026/0027/0028の範囲で吸収可能）。
- Verify:
  - `context/decision/consequences` は既存記録と矛盾なし。
- Proceed:
  - Phase 3進行可。

### Phase 3: Contract Freeze（Plan -> Execute -> Verify -> Proceed）
- Plan:
  - 凍結スナップショットに必須要素（ID / schemaVersion / API signature / validation rule / rollback条件）を固定。
- Execute:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` に `Frozen Contract Snapshot v1.2 (2026-04-30)` を追加。
- Verify:
  - 必須5要素が全て明示され、`THIS_VERSION_IS_FROZEN_FOR_ALL_DOWNSTREAM_LANES` 宣言を確認。
- Proceed:
  - Phase 4進行可。

### Phase 4: Verify（Plan -> Execute -> Verify -> Proceed）
- Plan:
  - 契約整合（重複・矛盾・未定義項目）を検証し、失敗時は最大3回まで自己修正。
- Execute:
  - docs-check と差分健全性チェックを実施。
- Verify:
  - self-correction `0/3`、重複/矛盾/未定義の新規発生なし。
- Proceed:
  - Phase 5進行可。

### Phase 5: Proceed（固定リンク集 / read-only handoff）
- A2/A3向け固定参照（read-only）:
  1. `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
  2. `01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`
  3. `01_Plans/issues/issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`
  4. `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- 判定: `Go`（A1契約凍結の参照利用のみ許可。再定義は禁止）。

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

## Stream C serial execution update（2026-04-30 / contract-governance only）

### Phase 1: Read同期（差分表）
| Key | Expected (A1 SSOT) | Observed | Result |
| --- | --- | --- | --- |
| `freezeContractId` | `HIL-RS-02-A1-CONTRACT-FREEZE-v1` | `HIL-RS-02-A1-CONTRACT-FREEZE-v1` | Match |
| `schemaVersion` | `1.0.0` | `1.0.0` | Match |
| `overridePolicy` | `human_dual_control_only` | `human_dual_control_only` | Match |
| `contractLinkLocked` | `true` | `true` | Match |
| `sharedResourceFreeze` | `true` | `true` | Match |
| `safeModeDefault` | `ON` | `ON` | Match |
| `safeModeBoundary` | `SAFE_MODE_STRICT_ON` | `SAFE_MODE_STRICT_ON` | Match |
| `decisionQueueTransition` | `Pending -> Approved \| Pending -> Rejected` | `Pending -> Approved \| Pending -> Rejected` | Match |

- 差分判定: `0`（契約未固定項目なし）。
- 未確定項目: `Approval Record: Pending`, `HIL-RS-02-GOV-EXCEPTION-01(held)`。

### Phase 2: ADR/Decision明文化（未確定フラグ維持）
- Context: A2/A3公開判定の誤開放を防ぐため、A1 SSOT契約からの派生定義を禁止する。
- Decision: Gate判定・freeze keys・NoGo return pathを再定義せず参照専用で固定する。
- Consequences: `Approval Record` が揃うまで **Needs-decision** を維持し、確定扱いを禁止する。

### Phase 3: 契約固定（A2/A3向け固定参照表）
> **Change Prohibited Declaration**: 以下の固定参照表は A2/A3 で再定義・改名・追加を禁止する。

| Category | Fixed Reference | Consumer Rule |
| --- | --- | --- |
| Contract ID | `HIL-RS-02-A1-CONTRACT-FREEZE-v1` | 参照のみ（上書き禁止） |
| Snapshot ID | `SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1` | 参照のみ（派生ID生成禁止） |
| Schema | `schemaVersion=1.0.0` | 改版要求はA1 CDCへ差戻し |
| Policy | `overridePolicy=human_dual_control_only` | 緩和禁止 |
| Safety | `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON` | 後退禁止 |
| Queue | `Pending -> Approved \| Pending -> Rejected` | bypass禁止 |
| Unlock | `a1Status=="Done" && pendingDecisionQueueCount==0` | 未充足時Open禁止 |
| NoGo return path | `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` | 変更禁止 |

### Phase 4: 引き渡し（固定値セット + 禁止事項）
- 固定値セット: `freezeContractId`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`, `unlockRule`。
- 下流禁止事項:
  1. `Pending` を経由しない状態遷移。
  2. A1未完了での A2/A3 `Draft -> Open`。
  3. `safeModeDefault=ON` / `SAFE_MODE_STRICT_ON` の緩和。
  4. `NoGo return path` の変更。
- Proceed判定: **Conditional / Needs-decision 維持**（承認記録未入力のため）。

## Stream C execution runbook log（2026-04-27 / Critical Path replay）

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

## Stream C fixed-serial protocol replay（2026-04-27 / Plan→Execute→Verify→Proceed）

- Issue order position: `3/4 HIL-RS-02 A1`
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

## Stream C execution log（2026-04-28 / governance hardening replay）

### Phase 1: Read（状態同期）
- 対象4ファイルを再読し、`Status / Priority / Scope / Dependencies / Approval Record / held` を同期。
- 結果: `Status=Open` / `Priority=P1` / `Scope=planning only` / `Dependencies=A1 -> A2 -> A3` / `Approval Record=Pending` / `held` 維持。
- 事前想定との差分: なし。

### Phase 2: ADR/CDC（実装前必須）
- Context: governance hardening は Pending bypass 防止とNoGo差戻し先固定が中核。
- Decision: `overridePolicy=human_dual_control_only`・`sharedResourceFreeze=true`・`contractLinkLocked=true`・`NoGo return path=A1 issue` を固定維持。
- Consequences: 承認未充足のまま確定化は禁止、`held` 維持。

### Phase 3: Plan（AC/DoD先行）
- Scope: 統治契約の禁止遷移と判定式整合。
- Non-goals: 契約緩和、pending bypass例外化、allowlist外編集。
- Acceptance Criteria:
  1. 固定キー差分 `0`。
  2. `NoGo return path` 改変なし。
  3. `Pending bypass` 禁止が維持される。
- Definition of Done:
  1. 順序ログ完備（Plan→Execute→Verify→Proceed）。
  2. self-correction `<=3`。
  3. 未承認事項の確定化なし。
- Validation Plan:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Stop Conditions: self-correction>=4、未承認確定化、NoGo return path改変、safeMode境界後退。

### Phase 4: Execute
- 実施内容: 本Issueへの運用ログ追記のみ。
- 非実施: 禁止遷移の緩和、NoGo return path変更、A2/A3先行Open。

### Phase 5: Verify
- Validation Plan に従い docs-check を実行。
- self-correction: `0/3`。

### Phase 6: Proceed / Stop
- 判定: **Conditional**。
- 理由: 承認記録未充足（`approved_by` / `approved_at` / `evidence` 未入力）。
- 再開条件: 人間承認完了後にProceedGateを再評価。


## Stream C fixed-serial execution log（2026-04-28 / HIL-RS critical contract governance）

### Phase 1: Read
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

### Phase 1: Read（Status / AC / Dependency contradiction list）
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


## Stream C serial execution log（2026-04-28 / 固定順 Phase 2）

### Fixed Phase
- Phase 2: `HIL-RS-02 A1 hardening`（本Issue）

### Read Sync
- 対象4Issueを再読し、`Status / Scope / Dependencies / 固定キー` を同期確認。
- 判定: ドリフトなし（`safeModeDefault=ON` / `SAFE_MODE_STRICT_ON` / `human_dual_control_only` 維持）。

### Plan
- 統治契約の固定のみを対象化し、A2/A3依存は `mock I/F signature` 参照に限定。
- 未承認事項の確定化を禁止（`pending/held` 維持）。

### ADR合意ゲート（必須）
- Context: Governance hardeningはNoGo path一意性とPending bypass防止が主目的。
- Decision: `NoGo return path` はA1 issue固定、`decisionQueueTransition` は `Pending -> Approved | Pending -> Rejected` のみ許可。
- Consequences: A1未完了でのA2/A3 Open要求は即NoGo。
- Approval Record: `Pending`（`approved_by` / `approved_at` / `evidence` 未入力）。

### Execute
- 実施: 統治条件の再掲・整合確認ログのみ。
- 非実施: 契約値再定義、SafeMode緩和、実装確定。

### Verify
- 自己検証: fail-safe条件（4回目相当self-correction、未承認確定化、未定義競合）未検知。
- self-correction: `0/3`。

### Proceed
- 判定: `Conditional`。
- 根拠: Approval RecordがPendingのため、Phase 3への進行は「条件付き（承認後）」。


## Stream C execution note（2026-04-29）
- Contract baseline re-read completed.
- `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeDefault` / `safeModeBoundary` のドリフトは未検知。
- `Approval Record` 未充足のため、状態は **Pending維持**。

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

## Stream C critical-path execution log（2026-04-29 / Contract Freeze & Handover Packet refresh）

### Phase 1: Read & Inventory
- 再読対象: `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `issue-HIL-RS-02-A1-governance-contract-hardening.md` / `issue-CE0-contract-freeze.md` / `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`。
- I/F未確定棚卸し結果:
  - 未確定（人間承認待ち）: `Approval Record`（`approved_by` / `approved_at` / `evidence`）。
  - 固定済み: `freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `NoGo return path`。
- AC/DoD不足判定: 新規不足なし（既存 `AC-D1..D3 / DoD-D1..D3` を継続）。

### Phase 2: ADR/CDC
- Context: 既存契約値は固定済みだが、下流Stream B/C向け引き渡し物を「read-only契約パケット」として明示化する必要がある。
- Decision: 下流参照を `HIL-RS-02-A1-CONTRACT-FREEZE-v1` に統一し、今回ランで `Contract Snapshot ID` を発行して handover packet を固定する。
- Consequences: Stream B/C は snapshot参照のみ許可され、契約値の再定義・派生定義・ID改名は禁止となる。

### Phase 3: Contract Freeze
- Contract snapshot ID（版）: `SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1-2026-04-29`。
- Freeze対象（再確認）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Compatibility条件:
  - 後方互換は `schemaVersion=1.0.0` 同値時のみ `compatible=true`。
  - enum追加・判定式派生・NoGo return path変更は `compatible=false` とし停止。

### Phase 4: Handover Packet（Stream B/C向け固定資料）
- Packet ID: `HANDOVER-HIL-RS-02-A1-2026-04-29`。
- I/F定義（read-only）:
  1. `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF`（再定義禁止）
  2. `A2A3_OPEN_ALLOWED` 判定式（本Issue記載のcanonical式を唯一参照）
  3. `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（固定）
- Non-goals:
  - 実装コード変更
  - A2/A3側での契約値補完・拡張
  - pending事項の確定化
- 禁止変更:
  - `safeModeDefault` / `safeModeBoundary` 後退
  - `overridePolicy` 緩和
  - `Pending bypass`
  - `freezeContractId` 改名・再採番
- 変更凍結宣言: **`HIL-RS-02 A1 contract is frozen as of 2026-04-29 (UTC)`**。

### Verify
- self-correction counter: `0/3`。
- docs-check実行（validator / unittest / diff check）を通過した場合のみ `Conditional` 以上を維持。

### Proceed
- 判定: **Conditional**（`Approval Record: Pending` が残存するため）。
- 失敗条件 / 影響I/F / 要人間判断:
  - failure_condition: 承認未完了のまま `Draft/Open` 変更要求が発生した場合。
  - impacted_interfaces: `A1-CRITIQUE-IF`, `A1-REDIFF-IF`, `A1-ATTR-IF`, `A1-ERROR-IF`。
  - human_decision_required: `approved_by` / `approved_at` / `evidence` の確定入力。

## Stream C execution snapshot（2026-04-29 / serial-phase sync）

### Phase 1: Read & Snapshot
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

## Stream C fixed-key verification log（2026-04-29 / serial）

### Read
- 再読対象（allowlist）: `ADR-0026` / `ADR-0027` / `issue-HIL-RS-01-A1` / `issue-HIL-RS-02-A1`。
- 固定キー照合結果: `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeDefault` / `safeModeBoundary` / `decisionQueueTransition` すべて一致（diff=`0`）。

### Plan/Execute/Verify/Proceed
- Plan: AC/DoD追加不足なし、既存ドラフト継続。
- Execute: 契約値更新なし（ログ追記のみ）。
- Verify: self-correction `0/3`。
- Proceed: **Conditional**（`Approval Record: Pending` 継続）。


## Stream C governance hardening checkpoint (2026-04-29)
- Contract freeze keys（`freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeDefault` / `safeModeBoundary`）の固定を再確認。
- Verify phaseでは self-correction `0/3` から開始し、3回超過時は停止する運用を再固定。
- NoGo return path の一意固定（A1）を維持する。


## Phase 4 Final Gate Record（Go / Conditional / No-Go）
- Gate date: `2026-04-30`
- Judgment: `No-Go`
- Reason:
  1. `Approval Record` が `Pending` のため、承認なし実装確定を禁止するルールにより停止。
  2. 未承認事項（`HIL-RS-02-GOV-EXCEPTION-01` held）が残存。
  3. A2/A3は `mock/contract-only` 継続は可能だが、Open/実装移行を許可する最終Go条件は未充足。
- Impact on downstream streams:
  - A2: `A1-CRITIQUE-IF / A1-REDIFF-IF / A1-ATTR-IF / A1-ERROR-IF` を read-only mock 契約として利用可。
  - A3: 運用文書の下書き・参照同期は可、ただし `A2A3_OPEN_ALLOWED=true` を前提にする実装確定は禁止。
- Human decisions required:
  1. Approval Record の承認可否（dual-control）
  2. held項目 `HIL-RS-02-GOV-EXCEPTION-01` の解消方針（Approve/Reject）
  3. 承認後に `Go` へ遷移させる日付・責任者の確定


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


## Stream G execution log（2026-05-02 / independent lane）

### Phase 1 Read
- 最新同期を開始時に実施し、`Status=Open` / `Scope=planning only` / `Dependencies=A1 -> A2 -> A3` を再確認。
- ガバナンス要件と停止条件（`dual-control`、`Pending bypass禁止`、`NoGo return path固定`、`safeMode境界固定`）を抽出。

### Phase 2 CDC
- Context: governance hardening で塞ぐべきリスクを `誤Open` / `責務混在` / `override境界逸脱` / `固定遷移ドリフト` に限定。
- Decision:
  - 2者承認と責務分離（`overridePolicy=human_dual_control_only`）を固定。
  - `freezeContractId` / `contractIds` / `decisionQueueTransition` / `safeMode*` を固定値として再定義禁止。
  - `NoGo return path` は A1 SSOT へ固定し、A1以外への差戻しを禁止。
- Consequences:
  - 運用負荷は増えるが、監査証跡と逸脱検知性を優先する。

### Phase 3 Plan
- AC案（固定化）:
  1. 契約ID固定（`HIL-RS-02-A1-CONTRACT-FREEZE-v1`）。
  2. 承認条件固定（`Approval Record: Pending` 残存時は Execute禁止）。
  3. 逸脱時停止固定（`pendingBypassDetected || undefinedConflictDetected` で NoGo）。
- DoD案:
  - A1 hardening と delivery plan の判定式整合が取れている。
  - Verify証跡（validator / unittest / diff check）が残る。

### Phase 4 Execute
- A1 hardening 観点を先行適用し、契約固定キーと停止条件を再掲。
- 実装コード変更は行わず、issue契約整備の範囲に限定。

### Phase 5 Verify
- AC/DoD整合を自己検証し、語彙ドリフト（`dual-control`、`safeModeBoundary`、`decisionQueueTransition`）不一致なし。
- Self-Correction: `0/3`（再試行なし）。

### Phase 6 Proceed
- 判定: **Needs-decision**。
- 理由: `Approval Record: Pending` が残存し、`held`（`HIL-RS-02-GOV-EXCEPTION-01`）解消前のため。
- 不足承認項目:
  1. `approved_by`
  2. `approved_at`
  3. `evidence`（ADR-0027 D5/D6整合、A1 contract freeze一致、AC/DoD合意）

## Stream A contract fixation sync（2026-05-02 / A1 critical path）

### Phase 1: Read同期（Plan → Execute → Verify → Proceed）
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


## Stream A governance/interface freeze sync（2026-05-03 / Critical Path）

### Phase 1: Read同期
- Status / Scope / Dependencies を再抽出し、`Open` / `planning only` / `A1 -> A2 -> A3` を確認。
- 固定キー再読: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`。
- 差分判定: 固定キー `diff=0`（想定差分なし）。

### Phase 2: ADR/CDC（Context / Decision / Consequences）
- Context: A2/A3のOpen化条件とPending bypass禁止をA1契約凍結に従属させる必要がある。
- Decision: `A2A3_OPEN_ALLOWED` を唯一判定式として維持し、`Pending -> Approved | Pending -> Rejected` 以外の遷移を禁止。`safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を固定。
- Consequences: `Approval Record` 未充足中は Execute を契約同期（docs）のみに限定し、A2/A3の確定遷移は実施しない。

### Phase 3: Plan（AC/DoD補完）
- 対象ファイル: 本ファイル（contract governance / delivery plan の契約I/F同期）
- 非対象ファイル: allowlist外すべて（実装コード、他stream成果物、README/dashboard）
- AC:
  1. 固定キー集合を閉じた契約として維持（unknown keyは許容しない）。
  2. `A2A3_OPEN_ALLOWED` と `NoGo return path` の一意性を維持。
  3. Pending bypass禁止・SafeMode境界後退禁止を明文化。
- DoD:
  1. Plan→Execute→Verify→Proceed の順序ログを残す。
  2. self-correction を `<=3` で管理。
  3. 未承認事項は `Needs-decision/held` のまま維持。

### Phase 4: Execute（契約I/Fのみ）
- 契約語彙を `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeMode*` / `decisionQueueTransition` に統一。
- 禁止遷移（Pending bypass、A1未完了でのA2/A3 Open、NoGo return path変更）を再固定。

### Phase 5: Verify
- docs-check / diff整合 / 用語整合を実行対象として確認。
- self-correction count: `0/3`（追加修復なし）。

### Phase 6: Proceed判定
- 判定: `Conditional`。
- 理由: `Approval Record`（`approved_by` / `approved_at` / `evidence`）未充足、および `HIL-RS-02-GOV-EXCEPTION-01=held` が継続。
- No-Go条件（継続監視）: 固定キー矛盾、allowlist外編集要求、self-correction 4回目相当、未定義競合。
