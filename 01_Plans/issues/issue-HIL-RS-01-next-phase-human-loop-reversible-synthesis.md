# Issue Plan: HIL-RS-01 次フェーズ実行計画（Human-in-the-loop / Reversible Synthesis）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Owner: Stream D（HIL A1 governance/interface contract）
- Scope: 本ファイルのみ（docs-only）
- Dependencies:
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（先行固定）
  - `issue-HIL-RS-02-A1-governance-contract-hardening.md`（hardening反映）
- Expected verification level: docs-check
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`

## Serial Phases（固定）
1. Phase 1 Read
2. Phase 2 ADR/CDC
3. Phase 3 Plan
4. Phase 4 Execute
5. Phase 5 Verify
6. Phase 6 Proceed

## Integration Order（厳守）
1. A1最小I/F契約を先に固定
2. A1 hardeningを次に固定
3. 最後に親計画issueへ整合反映

## Fail-safe（即停止条件）
- 承認不足
- 前提崩れ
- 競合発生
- 3回超修復

---

## Phase 1 Read
### Context
- 親計画は、A1契約（最小I/F + hardening）を参照する統合ノードである。

### Decision
- 本Issueは「整合反映」に限定し、A2/A3やdelivery-planを編集しない。

### Consequences
- 参照値に矛盾があれば Proceed せず Hold。

---

## Phase 2 ADR/CDC
### Context
- 親計画で契約値の再定義が起こると、下流レーンの整合が崩れる。

### Decision
- 親計画側は以下を **参照のみ** とする:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- A2/A3解放ゲート:
  - `a1Status=="Done" && pendingDecisionQueueCount==0`

### Consequences
- 親計画は gate条件を再定義せず、A1 SSOTへ差戻し可能性を維持する。

---

## Phase 3 Plan
- AC/DoDを「契約整合」「承認境界」「停止条件」に分割。
- 実装依存は非対象として分離。

## Phase 4 Execute（parent issue alignment）
### Acceptance Criteria
- AC-1: A1最小I/F固定値とのドリフト 0
- AC-2: A1 hardening（SoD / 承認遷移固定）を親計画に整合反映
- AC-3: `NoGo return path` 一意固定
- AC-4: A2/A3非干渉（編集・判定代行なし）

### Definition of Done
- DoD-1: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし
- DoD-2: `overridePolicy` 後退なし
- DoD-3: Self-correction `<=3`
- DoD-4: 承認不足時は `Hold/NoGo` のみ（Execute強行なし）

## Phase 5 Verify
- 固定値整合: pass
- hardening整合: pass
- fail-safe停止条件: pass

## Phase 6 Proceed
- Proceed: A1先行→hardening→親計画整合の順序が維持された場合のみ
- Stop: fail-safe 4条件のいずれか該当時
