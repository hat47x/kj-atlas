# Issue Draft: HIL-RS-02 A3 Operations Documentation Sync（Contract Reference Only）

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: TBD
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Out of scope:
  - `03_Implement/**`
  - `04_Documentation/**`
  - `01_Plans/project-progress-dashboard.md`
  - `01_Plans/issues/README.md`
  - `01_Plans/issues/decision-pack-2026-03-human-judgement.md`
- Dependencies: `ADR-0027`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`

## 1) Objective

A3 を「契約参照専用」の計画メモとして確定し、A1 完了前の逸脱実行を防止する。

## 2) Fixed Contract Snapshot（read-only）

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- Freeze Pack: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Fixed identifiers:
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
- Fixed decision criteria:
  - `contractLinkLocked`
  - `sharedResourceFreeze`
  - `validatorPass`

## 3) ADR CDC（必要時のみ）

- Context:
  - A3 は A1 契約固定後に開放される下流計画であり、契約変更窓口ではない。
- Decision:
  - A3 は契約参照のみ許可し、契約差分要求は A1 へ差し戻す。
- Consequences:
  - A1 未完了または Queue 未解決時は `Draft/Open(hold)` を維持する。

## 4) Acceptance Criteria / DoD

- [x] A3 が contract reference only であることが明文化されている。
- [x] 依存順序 `A1 -> A2 -> A3` が明文化されている。
- [x] `contractLinkLocked / sharedResourceFreeze / validatorPass` 判定が固定されている。
- [x] `safeModeDefault=ON` 後退禁止が明文化されている。
- [x] Proceed 条件・停止条件・差戻し先が明文化されている。

## 5) Serial Phase Protocol（強制）

各Phaseで必ず **Plan -> Execute -> Verify -> Proceed** を実施する。

### Phase 1 Read
- Plan: 再読対象と照合項目を固定。
- Execute: A1/A2/A3 依存・固定値・禁止遷移を確認。
- Verify: 差分/競合=0件。
- Proceed: 差分があれば CDC 論点化。

### Phase 2 Plan
- Plan: AC/DoD不足を提案化。
- Execute: 合意前は `Pending` で保持。
- Verify: 未承認確定化なし。
- Proceed: 合意済みのみ次へ。

### Phase 3 ADR CDC（必要時）
- Plan: 方針変更要否を判定。
- Execute: CDC を承認待ち化。
- Verify: 承認前確定化なし。
- Proceed: 承認後のみ Execute。

### Phase 4 Execute
- Plan: 契約文言・依存順・停止条件の正規化範囲を固定。
- Execute: 曖昧語排除、差戻し導線を一意化。
- Verify: 禁止遷移/語彙ドリフト=0件。
- Proceed: Verify pass で次へ。

### Phase 5 Verify & Proceed
- Plan: 検証コマンド固定。
- Execute: docs-check 実施。
- Verify: `validatorPass=true`。
- Proceed: 固定I/F一覧を次工程へ出力。

## 6) Open/Proceed Gate（固定）

- `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `NoGo = !Go`
- `NoGo` 時は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ差し戻す。

## 7) Fail-safe

- 即停止:
  1. Self-Correction 3回超過
  2. 未定義競合
  3. 前提崩壊
  4. 担当外ファイル編集要求
- 停止時報告:
  - 失敗条件 / 影響範囲 / 要承認事項

## 8) Next Step 固定I/F（read-only handoff）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
