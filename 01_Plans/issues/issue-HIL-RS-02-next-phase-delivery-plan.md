# Issue Draft: HIL-RS-02 次フェーズ実行計画（Stream E 単独完結版）

- Type: Process
- Status: Open
- Source Issue: N/A
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Owner: Stream E Agent（delivery plan self-contained）
- Scope: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md` のみ
- Dependencies (contract-only): `ADR-0026`, `ADR-0027`, `ADR-0028`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`

## Stream E Serial Protocol（固定）
- Serial phases: **Read → ADR(C/D/C) → Plan → Execute → Verify → Stop/Proceed**
- Mandatory per-phase discipline: **各Phase開始時に対象ファイルを再読する**。
- AC/DoD不足時: **不足案をドラフト提示し、合意後に次Phaseへ進む**。
- Self-correction limit: `<=3`（4回目相当は即停止）。
- Hard stop: `safeMode` 後退要求 / 契約ID再定義要求 / pending bypass 要求を検知した時点で停止。

## 0. Fixed Guardrails（変更禁止）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## Phase 1. Read

### Re-read target
- `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`

### Context
- 本タスクは単一ファイル編集のみ許可される。

### Decision
- 差分確認観点を `Fixed Guardrails / Stop条件 / Self-correction / Proceed条件` に固定する。

### Consequences
- 越境編集と外部進捗推測を防止できる。

### Verify
- allowlist外の編集対象が存在しないこと。

---

## Phase 2. ADR（C/D/C）

### Re-read target
- `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`

### Context
- delivery plan が冗長化すると停止条件と判定条件が曖昧化し、運用逸脱リスクが上がる。

### Decision
- D1: Stream E の責務を `Gate判定ログ整備 / AC-DoD照合 / 停止条件固定` に限定する。
- D2: 外部進捗や他ストリーム状態を入力に使わない。
- D3: 不確定事項は `Hold` として保持し、推測確定を禁止する。

### Consequences
- 単独完結で再開可能な計画を維持できる。

### Verify
- C/D/C が欠落なく記述され、相互矛盾がないこと。

---

## Phase 3. Plan（AC/DoD）

### Re-read target
- `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`

### AC（Acceptance Criteria）
- AC-1: 6フェーズ（Read/ADR/Plan/Execute/Verify/Stop-Proceed）が順序通り定義されている。
- AC-2: 各Phaseに「Re-read target」が明記されている。
- AC-3: Self-correction上限（<=3）と hard stop 条件が固定されている。
- AC-4: Proceed判定が `Ready | Hold | No-Go` で定義されている。

### DoD（Definition of Done）
- DoD-1: 本ファイルのみ更新（allowlist遵守）。
- DoD-2: Fixed Guardrails に後退がない。
- DoD-3: safeMode後退・契約ID再定義・pending bypass 要求を許容しない記述が残る。
- DoD-4: docs-check手順が明示されている。

### AC/DoD不足時ドラフト提案（合意用）
- Draft-AC-5: Gate判定ログに理由（Reason）を必須化する。
- Draft-DoD-5: Stop時報告テンプレに `last_safe_phase` を必須化する。

---

## Phase 4. Execute

### Re-read target
- `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`

### Gate判定ログ
- GATE-01 `A1-GOV-GATE-V1`: **Conditional**
- GATE-02 `A2-PROPOSAL-ENVELOPE-V1`: **Ready-By-Contract**
- GATE-03 `A3-DOC-SYNC-CHECK-V1`: **Ready-By-Contract**

### Stop conditions
- S1: `self_correction_attempt >= 4`
- S2: pending bypass 要求を検知
- S3: 固定ガードレール改変要求を検知
- S4: allowlist外編集要求を検知

### Self-correction counter
- `0/3` で開始し、再試行ごとに `+1`。

---

## Phase 5. Verify

### Re-read target
- `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`

### docs-check commands
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Verify criteria
- AC-1〜AC-4 を満たす。
- DoD-1〜DoD-4 を満たす。
- self-correction が `<=3` である。

---

## Phase 6. Stop/Proceed

### Re-read target
- `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`

### Proceed decision model
- **Ready**: 固定キー整合 / hard stop 非該当 / AC-DoD充足。
- **Hold**: 前提不足があるが hard stop 非該当。
- **No-Go**: S1〜S4 のいずれかを満たす。

### Current decision
- **Hold**（契約前提の確認継続）。

### Stop report template
- `stop_reason`: `S1|S2|S3|S4`
- `last_safe_phase`: `Read|ADR|Plan|Execute|Verify`
- `guardrail_diff`: `none|detected`
- `next_action`: `NoGo return pathへ差戻し`
