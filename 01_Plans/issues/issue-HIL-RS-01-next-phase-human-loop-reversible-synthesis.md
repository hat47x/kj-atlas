# Issue Draft: HIL-RS-01 次フェーズ計画（Human-in-the-loop可逆統合）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Dependencies: `ADR-0026`, `ADR-0027`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0001`, `00_Prompt/domain.md`
- Expected verification level: `docs-check`

## 1) Goal

HIL-RS-01 の A1（契約固定）を単一契約として凍結し、A2/A3 を **A1 Done かつ Pending=0 のときのみ** 解放する。

## 2) Fixed Contract Baseline

- Freeze Pack ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Contract IDs（固定）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `A1-ERROR-IF`
- Fixed values:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- SSOT:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`

## 3) CDC（Phase 2 ADR）

- Context:
  - 本issueは `ADR-0026` / `ADR-0027` の下位具体化であり、上位方針を変更しない。
- Decision:
  - 上位ADR改定が必要な要求は **承認待ち停止** とし、未承認で確定しない。
- Consequences:
  - A2/A3 は read-only 参照のみ。契約変更要求はA1へ差し戻す。

## 4) Acceptance Criteria / DoD

- [x] A1契約値（Contract IDs / schemaVersion / overridePolicy / freeze flags / SSOT）が単一化されている。
- [x] A2/A3 開始条件が `A1 Done && pendingDecisionQueueCount==0` に固定されている。
- [x] Decision Queue 遷移が `Pending -> Approved|Rejected` のみ。
- [x] SafeMode既定ON / share-export漏えい防止 / human_dual_control_only の後退禁止が明示されている。
- [x] 契約再定義をA2/A3で実施しないことが明示されている。

## 5) Stream A Workflow（Plan → Execute → Verify → Proceed）

### Phase 1 Read
- Plan: 対象5ファイルを再読し、`Status/Priority/Scope/Dependencies` の差分を抽出。
- Execute: 5ファイルから固定キーを抽出。
- Verify: ベースライン不一致がないことを確認。
- Proceed: 差分なしならPhase 2へ。差分ありは即停止。

### Phase 2 ADR CDC
- Plan: CDC を明文化。
- Execute: Context / Decision / Consequences を固定。
- Verify: 上位ADR改定要否を判定。
- Proceed: 改定必要なら承認待ち停止、不要ならPhase 3へ。

### Phase 3 Plan
- Plan: AC/DoD不足を補完。
- Execute: Gate条件とDecision Queue遷移制約を明示。
- Verify: `A1 Done && Pending=0` 以外の解放条件が存在しない。
- Proceed: Phase 4へ。

### Phase 4 Execute
- Plan: 契約凍結をSSOTへ反映。
- Execute: A1 gate固定、A2/A3 read-only化、差し戻し導線一本化。
- Verify: 契約ID再定義・安全後退・未承認確定化がない。
- Proceed: Phase 5へ。

### Phase 5 Verify
- Plan: docs-checkを実施。
- Execute: validator / unittest / rg / diff-check。
- Verify: 失敗時Self-Correction最大3回。
- Proceed: 成功でPhase 6へ、3回超過は停止報告。

### Phase 6 Proceed
- Plan: 未確定事項をDecision Queueへ戻す。
- Execute: Pending項目を更新し、契約再定義は行わない。
- Verify: 未承認決定の確定化がない。
- Proceed: Stream A A1固定完了として終了。

## 6) Fail-safe（即停止条件）

- 3回修復超過
- 未承認決定の確定化
- 未定義競合検出

停止時は必ず以下を提出する。
1. 失敗条件
2. 競合ファイル
3. 必要承認者
4. Yes/No質問
