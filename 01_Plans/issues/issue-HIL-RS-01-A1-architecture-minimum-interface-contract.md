# Issue Draft: HIL-RS-01 A1 Architecture最小I/F契約固定

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Dependencies: `ADR-0026`, `ADR-0027`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Expected verification level: `docs-check`

## 1) Objective

Critique/再提案差分/レビュー帰属の最小I/FをA1で固定し、A2/A3は参照専用とする。

## 2) Contract Freeze Keys（must match）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- SSOT: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`

## 3) CDC（Phase 2 ADR）

- Context:
  - 本A1は `ADR-0026` / `ADR-0027` の契約先行を具現化する作業。
- Decision:
  - 上位ADR改定を伴う変更要求は承認完了まで停止。
- Consequences:
  - A2/A3の契約変更は禁止。変更要求はA1へ差し戻し。

## 4) Acceptance Criteria

- [x] 契約ID・schemaVersion・overridePolicy・freeze flagsが固定。
- [x] Decision Queue 遷移が `Pending -> Approved|Rejected` のみ。
- [x] A2/A3 開始条件が `A1 Done && Pending=0` のみ。
- [x] SafeMode/share-export/human_dual_control_only 後退禁止が明示。
- [x] A2/A3 での契約本文変更禁止が明示。

## 5) Stream A Serial Phases（Plan → Execute → Verify → Proceed）

### Phase 1 Read
- Plan: 対象5ファイルの `Status/Priority/Scope/Dependencies` を再抽出。
- Execute: 契約凍結キーを比較。
- Verify: 差分ゼロを確認。
- Proceed: 差分なしでPhase 2へ。

### Phase 2 ADR CDC
- Plan: Context/Decision/Consequencesを固定。
- Execute: 上位ADR改定要否を判定。
- Verify: 未承認決定を確定しない。
- Proceed: 改定不要ならPhase 3。

### Phase 3 Plan
- Plan: AC/DoD不足を補完。
- Execute: A1 gate・Decision Queue遷移・停止条件を固定。
- Verify: `A1 Done && Pending=0` 以外の解放条件が無い。
- Proceed: Phase 4。

### Phase 4 Execute
- Plan: SSOTへ契約固定を反映。
- Execute: 凍結キー、禁止事項、差し戻し経路を明文化。
- Verify: 契約再定義が入っていない。
- Proceed: Phase 5。

### Phase 5 Verify
- Plan: docs-check実施。
- Execute: validator / unittest / rg / diff-check。
- Verify: Self-Correctionは最大3回。
- Proceed: 成功でPhase 6。

### Phase 6 Proceed
- Plan: 未確定事項のみDecision Queueへ戻す。
- Execute: Pending管理を更新し、契約再定義はしない。
- Verify: 未承認確定化なし。
- Proceed: A1契約固定完了。

## 6) Fail-safe

即停止条件:
- 修復3回超過
- 未承認決定の確定化
- 未定義競合

停止報告テンプレート:
1. 失敗条件
2. 競合ファイル
3. 必要承認者
4. Yes/No質問
