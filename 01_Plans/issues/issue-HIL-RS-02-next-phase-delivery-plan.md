# Issue Draft: HIL-RS-02 次フェーズ実行計画

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0027`, `ADR-0026`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `00_Prompt/domain.md`
- Expected verification level: `docs-check`

## 1) Objective

HIL-RS-02 を、A1 契約凍結を前提にした実行計画として固定する。

## 2) Governance Baseline（read-only snapshot）

- snapshotId=`MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- freezeContractId=`HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Dependency order: `A1 -> A2 -> A3`
- unlockRule=`a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- decisionQueueTransition=`Pending -> Approved | Pending -> Rejected`
- Forbidden transitions:
  - Pending bypass
  - A1未完了での A2/A3 Open
- Fixed identifiers:
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`

## 3) ADR CDC（必要時のみ）

- Context:
  - HIL-RS-02 は A1 契約を運用へ接続するフェーズ。
- Decision:
  - 依存は状態遷移で固定し、A2/A3 で契約値を変更しない。
- Consequences:
  - 契約差分は A1 へ集約。未承認事項は `Pending` 維持。

## 4) Acceptance Criteria / DoD

- [x] CDC が明文化されている。
- [x] 依存順序 `A1 -> A2 -> A3` が固定されている。
- [x] `contractLinkLocked / sharedResourceFreeze / validatorPass` が判定条件として固定されている。
- [x] SafeMode既定ONと安全境界後退禁止が明示されている。
- [x] Proceed条件と停止条件が明示されている。

## 5) Serial Phase Protocol（強制）

各Phaseで必ず **Plan -> Execute -> Verify -> Proceed** を実施する。

### Phase 1 Read & Lock
- Plan: 対象 issue の依存・固定値照合項目を定義。
- Execute: `Status / Dependencies / Scope / identifiers` を再読。
- Verify: 不一致=0件。
- Proceed: 差分は Phase 3 CDC で論点化。

### Phase 2 Contract Freeze（mock-first）
- Plan: I/F固定対象（contractIds / schemaVersion / gate条件）を固定。
- Execute: 実装詳細なしで最小契約のみ維持。
- Verify: 他ストリーム非依存で参照可能。
- Proceed: 凍結確認後に Phase 3 へ。

### Phase 3 ADR CDC（必要時）
- Plan: 方針変更要否を判定。
- Execute: CDC を承認待ちで記録。
- Verify: 承認前の確定記述なし。
- Proceed: 承認済みのみ Phase 4 へ。

### Phase 4 Plan -> Execute -> Verify
- Plan: AC/DoD 不足提案と停止条件を固定。
- Execute: 契約文言・依存順・停止条件を正規化。
- Verify: 依存逆転/語彙ドリフト=0件、`validatorPass=true`。
- Proceed: Verify pass で次へ。

### Phase 5 Proceed / Stopper
- Plan: 固定I/Fを次工程へ渡す。
- Execute: read-only handoff を発行。
- Verify: frozen keys 一致。
- Proceed: 失敗時は即停止し指示待ち。

## 6) Proceed Gate（固定）

1. `a1Status=="Done"`
2. `pendingDecisionQueueCount==0`
3. `contractLinkLocked==true`
4. `sharedResourceFreeze==true`
5. `validatorPass==true`

## 7) A2/A3 Start Rule（固定）

- `StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = StartAllowed`
- `NoGo = !StartAllowed`
- `NoGo` 時は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ差し戻す。

## 8) Fail-safe

- 即停止:
  - Self-Correction 3回超過
  - 未定義競合
  - 前提崩壊
  - 担当外編集要求
- 停止時報告:
  - 失敗条件 / 影響範囲 / 要承認事項

## 9) Next Step 固定I/F一覧

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
