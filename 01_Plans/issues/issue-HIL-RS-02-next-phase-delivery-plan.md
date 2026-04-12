# Issue Draft: HIL-RS-02 次フェーズ実行計画

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner (Stream B)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0027`, `ADR-0026`, `ADR-0028`, `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `00_Prompt/domain.md`
- Expected verification level: `docs-check`

## 1) Objective

議論→決定→文書化→同期サイクルを、A1契約固定を前提に **状態遷移契約で運用可能** な計画として固定する。

## 2) Governance Baseline（Mock Contract Snapshot参照）

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- A2/A3 Open条件: `A1 Done && pendingDecisionQueueCount==0`
- 許可遷移: `Pending -> Approved|Rejected`
- 禁止遷移: Pending bypass / A1未完了でのA2/A3 Open
- 固定識別子:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

## 3) ADR CDC（Phase 2）

- Context:
  - HIL-RS-02はA1契約を運用へ接続するフェーズ。
- Decision:
  - 依存は状態遷移として記述し、A1/A2/A3の実装待ちで計画を停止しない。
- Consequences:
  - 契約差分はA1へ集約。A2/A3では契約値を変更しない。

## 4) Acceptance Criteria / DoD

- [x] CDCが明文化されている。
- [x] Gate条件が機械判定可能な式で示されている。
- [x] Decision Queueの許可/禁止遷移が明示されている。
- [x] 安全境界（SafeMode/share-export/human_dual_control_only）後退禁止が明示されている。
- [x] Proceed（Open化）条件と停止条件が明示されている。

## 5) Serial Phases（各Phase開始時に対象再Read）

### Phase 1 Read
- 対象5 issueのStatus/Dependencies/識別子を再確認。

### Phase 2 ADR CDC
- Context/Decision/Consequencesを確認。上位ADR改定必要時は停止。

### Phase 3 Plan
- AC/DoD不足を補完し、遷移契約を固定。

### Phase 4 Execute
- issue本文に契約・禁止遷移・差し戻し先を同期。

### Phase 5 Verify
- validator + rg + diff確認。自己修復は最大3回。

### Phase 6 Proceed
- Open化条件を満たす項目のみ進行。未確定はDecision Queueへ戻す。

## 6) Open化条件（明文化）

1. `A1 Done`
2. `pendingDecisionQueueCount==0`
3. Mock snapshot固定識別子が一致
4. 安全境界の後退要求がない

## 7) Fail-safe

- 停止トリガー: 3回修復超過 / 未承認確定化 / 識別子不一致。
