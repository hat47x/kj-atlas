# Issue Plan: HIL-RS-01 次フェーズ実行計画（Human-in-the-loop / Reversible Synthesis, Stream D）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream D（HIL governance contract）
- Scope: 本ファイルのみ（docs-only）
- Dependencies:
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `issue-HIL-RS-02-A1-governance-contract-hardening.md`

## Serial Phases（固定）
1. Phase 1 Read
2. Phase 2 ADR（Context / Decision / Consequences）
3. Phase 3 Plan（AC / DoD）
4. Phase 4 Execute
5. Phase 5 Verify
6. Phase 6 Proceed

## Constraints（固定）
- `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` は固定参照のみ。
- `Pending` bypass禁止。
- mock契約参照で独立遂行（外部レーン完了待ち前提を置かない）。

## Phase 1 Read
- 親計画はA1契約（最小I/F + hardening）の参照ノードであり、再定義ノードではない。

## Phase 2 ADR（C/D/C）
### Context
- 親計画で契約値を再定義すると下流レーンの整合が崩れる。

### Decision
- 親計画側は以下を参照のみ:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 解放ゲート参照:
  - `a1Status=="Done" && pendingDecisionQueueCount==0`

### Consequences
- 親計画は gate条件を再定義しない。
- 矛盾時は Proceedせず Hold/NoGo。

## Phase 3 Plan（AC / DoD）
### Acceptance Criteria
- AC-1: A1最小I/F固定値とのドリフト0。
- AC-2: hardening（SoD/承認遷移固定）の参照整合。
- AC-3: `NoGo return path` 一意固定。
- AC-4: A2/A3非干渉（編集・判定代行なし）。

### Definition of Done
- DoD-1: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし。
- DoD-2: `overridePolicy` 後退なし。
- DoD-3: `Pending` 残存時は `Hold/NoGo` のみ。
- DoD-4: 外部レーン完了待ちを前提にしない独立遂行条件を維持。

## Phase 4 Execute
- A1先行固定 → hardening固定 → 親計画整合反映の順序だけを実施。

## Phase 5 Verify
- 固定値整合: pass
- hardening整合: pass
- bypass禁止: pass

## Phase 6 Proceed
- Proceed: 上記順序・固定参照・非干渉が維持された場合のみ。
