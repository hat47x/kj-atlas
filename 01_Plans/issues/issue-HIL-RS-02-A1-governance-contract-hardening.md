# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Dependencies: `ADR-0027`, `ADR-0026`, `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Expected verification level: `docs-check`

## 1) Objective

A1契約凍結を運用ガバナンスとして固定し、A2/A3解放の誤判定を防止する。

## 2) Hardening Rules

- Unlock rule（唯一）:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Freeze keys（必須一致）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- SSOT:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Return path（唯一）:
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 3) CDC（Phase 2 ADR）

- Context:
  - A1はHIL-RS-02のクリティカルパス。
- Decision:
  - 上位ADR改定を要する提案は承認待ち停止。
- Consequences:
  - A2/A3は契約値変更不可、read-only参照のみ。

## 4) Acceptance Criteria / DoD

- [x] A1 gateの唯一条件が明文化されている。
- [x] Decision Queue 許可遷移が `Pending -> Approved|Rejected` のみ。
- [x] 安全境界（SafeMode既定ON / share-export漏えい防止 / human_dual_control_only）後退禁止が明文化。
- [x] 契約変更要求の窓口がA1へ一本化されている。
- [x] docs-check検証方針（3回修復上限）が明文化されている。

## 5) Stream A Serial Workflow（Plan → Execute → Verify → Proceed）

### Phase 1 Read
- Plan: 対象5ファイルの差分抽出。
- Execute: Status/Priority/Scope/Dependencies/Gate keys照合。
- Verify: 不一致がない。
- Proceed: 一致時のみPhase 2。

### Phase 2 ADR CDC
- Plan: CDCを固定。
- Execute: 上位ADR改定要否判定。
- Verify: 未承認確定化なし。
- Proceed: 不要ならPhase 3。

### Phase 3 Plan
- Plan: AC/DoD不足補完。
- Execute: Unlock条件・停止条件・差し戻し導線を固定。
- Verify: Unlock経路が1つのみ。
- Proceed: Phase 4。

### Phase 4 Execute
- Plan: 契約統治ルールを固定。
- Execute: SSOT参照・freeze flags・禁止事項を明記。
- Verify: A2/A3で契約変更しない。
- Proceed: Phase 5。

### Phase 5 Verify
- Plan: docs-check実施。
- Execute: validator / unittest / rg / diff-check。
- Verify: Self-Correction最大3回。
- Proceed: 成功時のみPhase 6。

### Phase 6 Proceed
- Plan: 未確定事項をDecision Queueへ戻す。
- Execute: Pending管理を更新、契約再定義は行わない。
- Verify: 未承認確定化なし。
- Proceed: Governance hardening完了。

## 6) Fail-safe

即停止条件:
- 3回修復超過
- 未承認決定の確定化
- 未定義競合検出

停止報告:
1. 失敗条件
2. 競合ファイル
3. 必要承認者
4. Yes/No質問
