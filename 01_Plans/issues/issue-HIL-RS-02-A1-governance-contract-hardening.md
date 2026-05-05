# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening（Stream B）

- Type: Process
- Status: Open（Approval Pending）
- Priority: P1
- Owner: Stream B（HIL Governance）
- Scope: 本ファイルのみ（docs-only）
- Dependency: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## Serial Phases（固定）
1. Phase 1 Read
2. Phase 2 ADR（Context / Decision / Consequences）
3. Phase 3 Plan（AC / DoD）
4. Phase 4 Execute
5. Phase 5 Verify
6. Phase 6 Proceed/Stop

## Constraints（固定）
- `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` は固定参照のみ。
- `Pending` bypass禁止。
- mock契約参照で独立遂行し、外部レーン完了待ちを前提化しない。

## Phase 1 Read
- 対象ファイル最新状態を再読し、SoD・Pending遷移・固定キーを確認する。
- RS-02 A1は最小I/Fへの統治hardening層であり、A1 SSOTとの差分を持ち込まない。

## Phase 2 ADR（Context / Decision / Consequences）
### Context
- 主要リスクは `Pending bypass` と承認責務混線。
- 固定キー不一致時に実行継続すると統治契約が破綻する。
- 本件は承認待ち論点を含むため、承認前に `Execute` へ進めない。

### Decision
- SoD固定:
  - Requester: Stream B agent
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
- 保護固定集合:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- 承認待ち明文化:
  - `Status=Open（Approval Pending）` の間は `executeAllowed=false` を維持する。

### Consequences
- 未承認時は `Hold` 維持。
- 例外時も `overridePolicy=human_dual_control_only` 以外を許可しない。
- 固定キー不一致は `NoGo` とし、A1 SSOTへ return する。

## Phase 3 Plan（AC / DoD）
### Acceptance Criteria
- AC-1: A1固定値と完全一致。
- AC-2: SoD（承認/実行責務分離）が明示。
- AC-3: `Pending` bypass禁止が明示。
- AC-4: `NoGo return path` がA1 SSOTへ固定。
- AC-5: 承認待ち状態（Approval Pending）では実行不可が明示。

### Definition of Done
- DoD-1: `Approval Record` 必須項目（`approved_by`, `approved_at`, `evidence`）を要求。
- DoD-2: `pendingDecisionQueueCount > 0` で `executeAllowed=false`。
- DoD-3: freeze key mismatchで `decision=NoGo`。
- DoD-4: 外部レーン完了待ちを前提にしない。
- DoD-5: `Pending -> Approved/Rejected` 以外の遷移を許容しない。

## Phase 4 Execute
- Hard Gate:
  - `pendingDecisionQueueCount > 0` -> `decision=Hold` / `executeAllowed=false`
  - freeze key mismatch -> `decision=NoGo`
  - `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 実行遷移制約:
  - 承認遷移は `Pending -> Approved` または `Pending -> Rejected` のみ。
  - `Approved` 以外の状態で `Execute` へ遷移しない。

## Phase 5 Verify
- 検証基準: AC/DoDを逐次照合する。
- 自己修復: 失敗時は最大3回まで修正・再検証し、超過時は `Stop`。
- 検証結果（現時点）:
  - A1固定値一致: pass
  - SoD整合: pass
  - bypass禁止: pass
  - NoGo return path固定: pass

## Phase 6 Proceed/Stop
- Proceed条件:
  - hardening定義がA1契約と矛盾せず、別レーン非干渉を維持。
  - 承認が `Approved` に遷移し、AC/DoDを全て満たす。
- Stop条件:
  - 試行回数超過（自己修復3回超過）
  - 役割競合（SoD違反）
  - 前提崩壊（固定キー不一致、A1 SSOT不整合）
  - 上記発生時は推測実行せず `Hold/NoGo` で停止する。
