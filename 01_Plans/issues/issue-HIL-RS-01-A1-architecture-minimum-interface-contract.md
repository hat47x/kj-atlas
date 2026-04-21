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

## 2) Frozen Minimum Interface Contract

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

## 3) Serial Phase Management（強制）

- 各 Phase で `Plan -> Execute -> Verify -> Proceed` を適用する。

> 各 Phase 開始時に対象4ファイル（`issue-HIL-RS-01` / 本書 / `issue-HIL-RS-02` / `issue-HIL-RS-02-A1`）を再読し、差分があれば Plan 更新後に実行する。

### Phase 1 Read（2026-04-21）

- Check: `Status / Priority / AC / Dependencies`
- Result: 差分なし（`DiffCount=0`）

### Phase 2 Plan（追記案 + 合意 / 判定軸明示）

- 追記案（合意済み）:
  - 判定軸（固定）: `a2a3Unlock / decisionQueueTransition / safeModeDefault`
  - AC に `decisionQueueTransition` の固定参照を追加。
  - DoD に「A1が唯一差し戻し先」を追加。
  - Verify に「依存矛盾ゼロ」を追加。

### Phase 3 Execute

- Executed:
  - 契約ID・固定値・unlockRule を単一正本として再固定。
  - Stop Conditions を4ファイルで同語彙へ統一。
  - Decision Queue 参照を一意化。

### Phase 4 Verify

- AC/DoD 整合結果:
  - fixed keys diff = 0
  - dependency contradiction = 0
  - NoGo return path = A1（本書）で統一

### Phase 5 Proceed（handoff）

- handoff 固定値一覧: `freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`
- handoff 禁止遷移: `A1!=Done で A2/A3 Open` / `Pending bypass` / `NoGo時のA1以外差し戻し`
- handoff 差し戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 次担当者向け:
  - A2/A3 は read-only 参照のみ。
  - 契約差分要求は本書へ集約（A2/A3 で局所修正禁止）。
  - `Pending/held` bypass 禁止。

## 4) Acceptance Criteria / DoD

### Acceptance Criteria

- `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` が対象4ファイルで一致。
- `A1 -> A2 -> A3` と `a2a3Unlock` が唯一条件として定義される。

### DoD

- A1 が唯一の差し戻し先である。
- Go/No-Go 判定式が他ファイルと一致する。
- Verify 失敗時 Self-Correction は最大3回。

## 5) ADR Rule

- 追加/改訂が必要な場合のみ `Context / Decision / Consequences` を Draft 化。
- 承認明示まで確定禁止（`Pending/held`）。
- 現時点判定: 既存契約整合化のみのため新規 ADR なし。

## 6) Go / No-Go（固定）

- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `A1未完了時A2/A3 Open禁止 = (a1Status!="Done") => Open禁止`
- `NoGo = !A2A3StartAllowed`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 7) Stop Conditions / Fail-safe

- Self-Correction 3回超過
- 前提崩壊
- 未定義競合
- 指定外ファイル編集要求または検知
