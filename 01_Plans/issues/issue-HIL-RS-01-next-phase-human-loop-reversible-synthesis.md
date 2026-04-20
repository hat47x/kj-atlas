# Issue Draft: HIL-RS-01 次フェーズ計画（Human-in-the-loop 可逆統合）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0026`, `ADR-0027`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0001`, `00_Prompt/domain.md`
- Expected verification level: `docs-check`

## 1) Goal

HIL-RS-01 を **契約先行の計画正本** として固定し、A1/A2/A3 依存を実装待ちではなく状態遷移契約で管理する。

## 2) Contract Freeze（mock-first / read-only）

- snapshotId=`MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- freezeContractId=`HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Dependency order: `A1 -> A2 -> A3`
- unlockRule=`a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Contract IDs:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `A1-ERROR-IF`
- Fixed values:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
- Fixed decision criteria:
  - `contractLinkLocked`
  - `sharedResourceFreeze`
  - `validatorPass`

## 3) ADR CDC（方針変更が必要な場合のみ承認待ち）

- Context:
  - HIL-RS-01 は `ADR-0026/0027/0028` の下位計画であり、契約逸脱を抑止する。
- Decision:
  - A1/A2/A3 依存は `state-transition contract` で固定し、下流で契約値を再定義しない。
- Consequences:
  - 契約差分要求は常に `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ差し戻す。

## 4) State Transition Contract（固定）

- Allowed:
  - `A1: Draft -> Open -> In Progress -> Done`
  - `A2/A3: Draft -> Open` は `A1==Done && pendingDecisionQueueCount==0` のときのみ
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Forbidden:
  - `Pending` bypass
  - `A1!=Done` での `A2/A3 Draft -> Open`
  - A2/A3 側での契約ID・固定値再定義

## 5) Acceptance Criteria / DoD

- [x] CDC（Context/Decision/Consequences）が明文化されている。
- [x] 依存順序 `A1 -> A2 -> A3` が固定されている。
- [x] 判定条件 `contractLinkLocked / sharedResourceFreeze / validatorPass` が固定されている。
- [x] `safeModeDefault=ON` と `human_dual_control_only` 後退禁止が明示されている。
- [x] Proceed 条件と停止条件が明文化されている。

## 6) Serial Phase Protocol（強制）

各Phaseで必ず **Plan -> Execute -> Verify -> Proceed** を実施する。

### Phase 1: Read
- Plan: 対象4ファイル（HIL-RS-01 / HIL-RS-01-A1 / HIL-RS-02 / HIL-RS-02-A1）の照合項目を固定。
- Execute: `A1 -> A2 -> A3`、`unlockRule`、固定キー（`contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`）を再読照合。
- Verify: 差分件数 `DiffCount=0`。
- Proceed: 差分があれば即停止し Phase 2 へ論点送付。

### Phase 2: ADR CDC（必要時のみ）
- Plan: 方針差分の有無を判定し、必要時のみ `Context / Decision / Consequences` を起票。
- Execute: CDC は `Pending/held` として記録し、承認前は確定禁止。
- Verify: 承認前に固定値・依存順・Go/No-Go の確定化が行われていない。
- Proceed: 承認済みのみ Phase 3 へ。未承認は `held` 継続。

### Phase 3: Plan
- Plan: AC/DoD の不足項目（受入条件、停止条件、差し戻し条件）をドラフト化。
- Execute: 追加提案を本文へ反映し、既存契約語彙へ正規化。
- Verify: AC/DoD が固定キーと矛盾しない。
- Proceed: 合意済みドラフトのみ Phase 4 へ。

### Phase 4: Execute
- Plan: 契約凍結対象（`contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`）を再固定。
- Execute: 契約本文と handoff 節へ同一値を反映し、read-only 参照前提を明文化。
- Verify: `A1 -> A2 -> A3` と `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)` の逆転・重複定義が0件。
- Proceed: 一致確認後のみ Phase 5 へ。

### Phase 5: Verify
- Plan: docs-check 実行手順を固定（validator / 語彙照合 / diff整合）。
- Execute: docs-check を実施し、失敗時は Self-Correction を最大3回まで実行。
- Verify: `validatorPass=true` かつ fixed keys 不一致0件。
- Proceed: 3回超過・未定義競合・前提崩壊時は即停止。

### Phase 6: Proceed
- Plan: 他ストリーム向けの「凍結I/Fスナップショット（read-only handoff）」を確定。
- Execute: freezeContractId・固定キー・unlockRule・Go/No-Go を出力。
- Verify: A1 frozen keys と完全一致。
- Proceed: 成功時のみ handoff 完了。失敗時は停止報告へ移行。

## 7) Gate / Proceed 条件

- `A1==Done`
- `pendingDecisionQueueCount==0`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `validatorPass=true`

## 8) Fail-safe

- 即停止条件:
  1. Self-Correction が3回超過
  2. 未定義競合
  3. 前提崩壊
  4. 担当外ファイル編集要求
- 停止時報告テンプレ:
  - 失敗条件
  - 影響範囲
  - 要承認事項

## 9) Next Step 固定I/F（read-only handoff）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
