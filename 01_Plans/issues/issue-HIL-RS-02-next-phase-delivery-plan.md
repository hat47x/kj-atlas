# Issue Draft: HIL-RS-02 次フェーズ実行計画

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Dependencies: `ADR-0027`, `ADR-0026`, `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `00_Prompt/domain.md`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

## 1) Objective

議論→決定→文書化→同期のサイクルを、A1契約固定を前提に実行する。

## 2) Governance Baseline

- A2/A3公開条件: `A1 Done && pendingDecisionQueueCount==0` のみ。
- 許可遷移: `Pending -> Approved|Rejected`。
- 禁止遷移: Pending bypass、A1完了前 `Draft -> Open`。
- 固定契約キー:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

## 3) CDC（Phase 2 ADR）

- Context:
  - HIL-RS-02はA1先行固定の運用フェーズ。
- Decision:
  - 上位ADR改定が必要なら停止し承認待ち。
- Consequences:
  - A2/A3はread-only参照、契約変更要求はA1へ戻す。

## 4) Acceptance Criteria

- [x] A1 gate条件が機械判定可能である。
- [x] Decision Queue遷移制約が明示されている。
- [x] SafeMode/share-export/human_dual_control_only後退禁止が明示されている。
- [x] 契約変更要求の差し戻し先がA1に一本化されている。
- [x] Stream Aは `01_Plans/` と `02_Architecture/` のみ編集する。

## 5) Stream A Serial Workflow（Plan → Execute → Verify → Proceed）

### Phase 1 Read
- Plan: 対象5ファイルを再読し差分抽出。
- Execute: Status/Priority/Scope/Dependencies/Gate keys比較。
- Verify: ベースライン一致。
- Proceed: 一致時のみPhase 2。

### Phase 2 ADR CDC
- Plan: CDCを固定。
- Execute: 上位ADR改定要否判定。
- Verify: 未承認決定の確定化禁止。
- Proceed: 改定不要時のみPhase 3。

### Phase 3 Plan
- Plan: AC/DoD不足補完。
- Execute: Gateと停止条件を固定。
- Verify: `A1 Done && Pending=0` 以外の解放経路なし。
- Proceed: Phase 4。

### Phase 4 Execute
- Plan: A1 gateを運用文として固定。
- Execute: 差し戻し導線（A1一本化）を明文化。
- Verify: 契約再定義なし。
- Proceed: Phase 5。

### Phase 5 Verify
- Plan: docs-check実行。
- Execute: validator / unittest / rg / diff-check。
- Verify: Self-Correction最大3回。
- Proceed: 成功時のみPhase 6。

### Phase 6 Proceed
- Plan: 未確定事項をDecision Queueへ戻す。
- Execute: Pending項目を更新し契約再定義はしない。
- Verify: 未承認確定化なし。
- Proceed: Stream A計画固定完了。

## 6) Fail-safe

停止トリガー:
- 修復3回超過
- 未承認決定の確定化
- 未定義競合

停止時報告:
1. 失敗条件
2. 競合ファイル
3. 必要承認者
4. Yes/No質問
