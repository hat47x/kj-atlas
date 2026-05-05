# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening（Stream E）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Owner: Stream E（HIL A1 governance/interface contract）
- Scope: 本ファイルのみ（docs-only）
- Dependency: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（A1最小I/F固定済み前提）
- Expected verification level: docs-check
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`

## Serial Phases（固定）
1. Phase 1 Read（A1固定値再確認）
2. Phase 2 Plan（hardening計画）
3. Phase 3 ADR/CDC（Context / Decision / Consequences）
4. Phase 4 Execute（統治契約の強化明文化）
5. Phase 5 Verify
6. Phase 6 Proceed

## Fail-safe（即停止条件）
- 承認不足
- 前提崩れ
- 競合発生
- 3回超修復

---

## Phase 1 Read
### Context
- RS-02 A1は、A1最小I/Fに対する統治面（承認・責務分離・例外境界）のhardeningを担う。

### Decision
- `HIL-RS-02-A1-CONTRACT-FREEZE-v1` の再定義を禁止。
- `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を維持。

### Consequences
- A1凍結値と不一致があれば即NoGo。
- 別レーン（A2/A3/delivery-plan）は編集対象外。

---

## Phase 2 Plan（hardening計画）
- Goal: 統治契約をhardeningし、A2/A3がread-only参照可能な固定境界を提供する。
- Non-goal: A2/A3実装、A3運用文書同期の実行。
- Planned checks: SoD整合、承認遷移固定、freeze key一致、NoGo差戻し。

## Phase 3 ADR/CDC
### Context
- 失敗モードは主に `Pending bypass` と `承認責務の混線`。

### Decision
- SoD（Separation of Duties）を固定:
  - Requester: Stream D agent
  - Approver-A: Architecture Owner
  - Approver-B: Governance reviewer
  - Executor: Platform Operator
- 兼務禁止:
  - `requester != approver_a`
  - `requester != approver_b`
  - `approver_a != approver_b`
  - `executor != approver_a && executor != approver_b`
- 承認遷移固定:
  - 許可: `Pending -> Approved | Pending -> Rejected`
  - 禁止: `Draft -> Approved`, `Pending -> Execute`, `Rejected -> Execute`
- Execute前提:
  - `Approval Record: Pending == 0`
  - `approval_evidence_required` 充足
  - `A2A3_OPEN_ALLOWED=true`

### Consequences
- 承認未了時は `Hold` 維持。
- 例外時も `overridePolicy=human_dual_control_only` 以外を許可しない。

---

## Phase 4 Execute（hardening contract）
### Approval Record（必須）
- required_fields: `approved_by`, `approved_at`, `evidence`
- required_approvers: `Architecture Owner` + `Governance reviewer`
- state_default: `Pending`

### Hard Gate
- `pendingDecisionQueueCount > 0` -> `decision=Hold` / `executeAllowed=false`
- freeze key mismatch -> `decision=NoGo`
- NoGo return: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Needs-decision
- Approver-A/Bの実名アサインと証跡URI命名規約は人間判断待ち（未確定扱い）。

### Protected Immutable Set
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

## Phase 5 Verify
- A1固定値との一致: pass
- 承認/実行責務分離: pass
- fail-safe停止条件: pass

## Phase 6 Proceed
- Proceed条件: hardening定義がA1契約と矛盾せず、別レーン非干渉を維持
- Stop条件: fail-safe 4条件のいずれか該当
