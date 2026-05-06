# Issue Draft: HIL-RS-02 Next-Phase Delivery Plan（Stream C 完遂版）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream C Agent（delivery + ops sync independent completion）
- Scope: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`, `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`, `01_Plans/adr/ADR-0027-hil-rs-02-next-phase-execution-plan.md`
- Out of scope: allowlist以外のIssue/ADR編集、`03_Implement/**`、`04_Documentation/**`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Dependencies (read-only): `ADR-0026`, `ADR-0028`, `issue-HIL-RS-02-A1-governance-contract-hardening.md`
- Expected verification level: `docs-check`

## Fixed Guardrails（変更禁止）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## Stream C Serial Protocol（固定）
- Serial phases: **Phase 1 Read → Phase 2 ADR整合（C/D/C）→ Phase 3 Delivery具体化 → Phase 4 運用同期条件定義 → Phase 5 Verify**
- Mandatory discipline per phase: **Plan → Execute → Verify → Proceed**
- Self-correction limit: `<=3`（4回目相当は即停止）
- Hard stop: safeMode後退要求 / 契約ID再定義要求 / pending bypass / allowlist外編集要求

## Phase 1: Read（現状・未決事項確認）
### Plan
- 対象3ファイルの再読と、未決事項を `Approval pending` / `dependency pending` / `drift risk` に分類する。

### Execute
- 未決事項を次で固定:
  1. `Approval Record` の未充足（`approved_by`, `approved_at`, `evidence`）
  2. `A1 Done` 未達時は A3 Open不可
  3. 固定キー差分検知時は即 `No-Go`

### Verify
- 3分類がPhase 2以降の判定式に反映されること。

### Proceed
- **Proceed=Yes**（未決事項は管理可能）

## Phase 2: ADR整合（Context / Decision / Consequences）
### Plan
- ADR-0027 と issue 2件の C/D/C 記述粒度を揃える。

### Execute
- C: A1依存下でA2/A3の先行確定は統治ドリフトを生む。
- D: Stream Cは「契約参照固定 + delivery里程標固定 + docs sync条件固定」に限定。
- Csq: A1完了前は Conditional 維持、Open化先行を禁止。

### Verify
- Context/Decision/Consequences が3ファイルで欠落なく整合すること。

### Proceed
- **Proceed=Yes（Approval Pending注記を維持）**

## Phase 3: Delivery計画具体化（里程標・受入条件）
### Plan
- 里程標（M1-M3）と AC/DoD を実行可能粒度で確定する。

### Execute
- M1: 契約固定値・依存式の一致確認
- M2: Gate判定（Go / Conditional / No-Go）の文書固定
- M3: Verify証跡（validator/unittest/diff）記録

### Acceptance Criteria
- AC-1: 5フェーズが順序固定されている。
- AC-2: 各フェーズに Plan/Execute/Verify/Proceed がある。
- AC-3: `Go / Conditional / No-Go` の判定式が明記される。
- AC-4: hard stop と self-correction 上限が明記される。
- AC-5: `Reason` を含む gate log が必須化される。

### Definition of Done
- DoD-1: allowlist 3ファイルのみ更新。
- DoD-2: Fixed Guardrails に後退がない。
- DoD-3: A1未完時のA3 Open禁止が維持される。
- DoD-4: docs-checkコマンドと成功条件が明示される。

### Verify
- AC/DoD が Phase 5 の検証項目へ反映されること。

### Proceed
- **Proceed=Yes**

## Phase 4: 運用文書同期条件の定義（リンク・責務分離）
### Plan
- DOC-OPS-02 固定順序と責務分離語彙を同期条件として定義する。

### Execute
- Sync order（read-only reference）:
  `02_Architecture/strict_mode_exception_approval_flow.md`
  → `02_Architecture/enterprise_architecture.md`
  → `04_Documentation/operations.md` / `04_Documentation/security.md`
  → `01_Plans/*` → `AGENTS.md`
- Role vocabulary固定:
  - `Security Officer`（承認責務）
  - `System Owner`（最終決裁責務）
  - `Platform Operator`（実行責務）
- Separation rule:
  - 2者承認と実行責務を同一主体に集約しない。

### Verify
- リンク導線、役割語彙、D1-D4固定値が矛盾しないこと。

### Proceed
- **Proceed=Conditional**（A1完了待ちのため Open化は保留）

## Phase 5: Verify（AC/DoD・競合ゼロ確認）
### Plan
- 機械検証 + 差分健全性 + 競合ゼロ確認を実施する。

### Execute（docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Verify
- AC-1〜AC-5 / DoD-1〜DoD-4 を満たす。
- self-correction が `<=3`。
- allowlist外差分 `0`。

### Proceed
- Ready: A1 Done かつ pendingDecisionQueueCount=0 かつ固定キー一致
- Conditional: A1未完だが固定キー一致
- No-Go: hard stop 条件発火
- **Current decision: Conditional（A1依存未解消のため）**
