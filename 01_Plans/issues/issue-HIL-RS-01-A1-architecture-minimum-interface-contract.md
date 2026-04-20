# Issue Draft: HIL-RS-01 A1 Architecture 最小I/F契約固定

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0026`, `ADR-0027`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`
- Expected verification level: `docs-check`

## 1) Objective

A1 を A2/A3 の唯一ゲートとして固定し、契約値の多重正本化を防止する。

## 2) Contract Freeze（mock-first / read-only）

- snapshotId=`MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`

### 2.1) Phase 1 Read 差分確認（2026-04-20 固定）

- 対象: `issue-HIL-RS-01-A1` / `issue-HIL-RS-01` / `issue-HIL-RS-02` / `issue-HIL-RS-02-A1`
- A1固定値差分:
  - `schemaVersion`: 差分なし（`1.0.0`）
  - `contractLinkLocked`: 差分なし（`true`）
  - `sharedResourceFreeze`: 差分なし（`true`）
  - `safeModeDefault`: 差分なし（`ON`）
- 判定: `DiffCount=0`（Proceed可）

## 3) ADR CDC（必要時のみ）

- Context:
  - A1 が曖昧だと A2/A3 の Open 判定が不安定化する。
- Decision（Draft / held）:
  - Stream A は A1 契約識別子と遷移条件のみ固定し、下流は read-only 参照とする。
- Consequences:
  - 変更要求は `A1-CDC-only` へ差し戻し、A2/A3 で局所修正しない。

### 3.1) ADR合意ステータス（承認待ち）

- ApprovalStatus: `Pending (Human approval required)`
- ApprovalScope: `CDC Context/Decision/Consequences`
- Pre-approval lock: `承認前は確定扱い禁止（契約凍結値は変更禁止）`

## 4) State Transition Contract（固定）

- Dependency order（唯一）:
  - `A1 -> A2 -> A3`
- Unlock rule（唯一）:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Decision Queue（唯一）:
  - `Pending -> Approved` または `Pending -> Rejected`
- Prohibited:
  - `Pending` bypass
  - `a1Status!="Done"` での `A2/A3 Draft -> Open`
  - A2/A3 issue 内で固定識別子の再定義

## 5) Acceptance Criteria / DoD

- [x] CDC が明文化されている。
- [x] Unlock rule が一意である。
- [x] 固定識別子が Mock snapshot と一致している。
- [x] `safeModeDefault=ON` と安全境界後退禁止が明示されている。
- [x] Verify 失敗時の3回上限と停止条件が明示されている。

## 6) Serial Phase Protocol（強制）

各Phaseで必ず **Plan -> Execute -> Verify -> Proceed** を実施する。

1. Phase 1 Read
   - Plan: 対象5ファイル（`issue-HIL-RS-01` / `issue-HIL-RS-01-A1` / `issue-HIL-RS-02` / `issue-HIL-RS-02-A1` / `issue-HIL-RS-02-A3`）の照合項目（依存順序 / unlockRule / fixed keys）を固定。
   - Execute: `Status / Dependencies / Scope / fixed keys / unlockRule` を照合。
   - Verify: 不一致 `DiffCount=0`。
   - Proceed: 差分は即停止し Phase 2 Plan へ送る。
2. Phase 2 Plan
   - Plan: AC/DoD 不足（停止条件 / 差し戻し条件 / 検証条件）をドラフト化。
   - Execute: ドラフトを既存契約語彙へ正規化して追記。
   - Verify: 固定キーとの矛盾が0件。
   - Proceed: 合意済みのみ Phase 3。
3. Phase 3 ADR CDC（必要時）
   - Plan: 方針差分がある場合のみ `Context / Decision / Consequences` を起票。
   - Execute: 承認前は `Pending/held` として扱い、確定禁止を維持。
   - Verify: 承認前の契約再定義が0件。
   - Proceed: 承認済みのみ Phase 4。
4. Phase 4 Execute
   - Plan: `contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault` を再固定。
   - Execute: A1契約本文と Downstream snapshot を同一値へ統一。
   - Verify: `A1 -> A2 -> A3`・unlockRule の重複/逆転0件。
   - Proceed: 一致時のみ Phase 5。
5. Phase 5 Verify
   - Plan: docs-check（validator / 語彙照合 / diff整合）を定義。
   - Execute: docs-check 実施、失敗時Self-Correctionは最大3回。
   - Verify: `validatorPass=true` かつ frozen keys 不一致0件。
   - Proceed: 失敗3回超過時は即停止。
6. Phase 6 Proceed
   - Plan: 凍結I/Fスナップショット（read-only handoff）を確定。
   - Execute: freezeContractId・fixed keys・Go/No-Go を出力。
   - Verify: Downstream 変更禁止キーが一致。
   - Proceed: A2/A3 へ参照専用で引き渡す。



## 7) Go / No-Go（固定）

- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `NoGo = !A2A3StartAllowed`

## 8) Fail-safe

- 即停止: Self-Correction 3回超過 / 未定義競合 / 前提崩壊 / 担当外編集要求。
- 停止時報告:
  1. 失敗条件
  2. 影響I/F
  3. 要承認事項

## 9) Downstream Fixed I/F Snapshot（変更禁止）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
