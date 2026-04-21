# Issue Draft: FB-P0 baseline / Stream A critical-path planning baseline

- Type: Process
- Status: Open（critical path active）
- Priority: P0
- Owner: Stream A（Critical Path: P0/P1 Contract & Governance）
- Scope: `01_Plans/issues/` の対象7Issueの計画・契約整合のみ
- Editable files:
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  - `01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`
  - `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
  - `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- Non-editable files: 上記以外すべて
- Related ADR/Spec: `ADR-0001`, `ADR-0019`, `ADR-0026`, `ADR-0027`, `ADR-0028`
- Verification level: `docs-check`

---

## Phase 1: Read（再読・差分ログ）

### Extracted baseline
- Status: `Open`
- Priority: `P0`
- Scope: 対象7Issueの契約/統治文書
- Related ADR/Spec: 上記5ADR

### Delta log（事前想定との差分）
1. Issue名に `stream-c` が残存しており、実運用（Stream A）と命名が不一致。
2. 既存文書群に「A1完了前A2/A3 Open禁止」の表現ゆれがあった。
3. A3文書の参照専用制約（read-only reference only）は維持すべきで一致。

## Phase 2: ADR Consensus（必須）

### Context
- クリティカルパスでは、A1契約凍結を唯一ゲートとしてA2/A3を統治する必要がある。

### Decision
- 次の契約値をSSOTとして固定する。
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
- A1未完了でA2/A3 Openは禁止。
- NoGo時差戻し先はA1契約Issueに固定。

### held（未承認事項）
- `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持（A2先行Done解釈は未承認）。

## Phase 3: Plan（AC/DoD点検）

### AC
1. 固定キー差分0。
2. `A1 -> A2 -> A3` の依存順序固定。
3. `Pending bypass` 禁止。

### DoD
1. NoGo return path が A1 で一意。
2. 未承認事項は `held` で固定。
3. 指定外ファイル差分0。

## Phase 4: Execute
- 対象7Issueの語彙・判定式・停止条件を統一。
- 実装コードや他ストリームIssueは未変更。

## Phase 5: Verify
- `docs-check` と `git diff --check` で検証。
- 失敗時 self-correction は最大3回。

## Phase 6: Proceed / Stop
- Proceed条件: AC/DoD充足。
- Stop条件: 前提崩れ / 未定義競合 / 承認なき契約確定 / self-correction 3回超過。
