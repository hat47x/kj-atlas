# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0027`, `ADR-0026`, `ADR-0028`, `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`
- Expected verification level: `docs-check`

## 1) Objective

A1 契約凍結を統治判定式として固定し、A2/A3 の誤Open化を防止する。

## 2) Contract Hardening Baseline（read-only）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Return path（唯一）: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 3) Serial Phase Management（強制）

- 各 Phase で `Plan -> Execute -> Verify -> Proceed` を適用する。

> 各 Phase 開始時に対象4ファイル（`issue-HIL-RS-01` / `issue-HIL-RS-01-A1` / `issue-HIL-RS-02` / 本書）を再読し、差分時は Plan 更新を優先する。

### Phase 1 Read（2026-04-21）

- Check: `Status / Priority / AC / Dependencies`
- Result: 差分なし（`DiffCount=0`）

### Phase 2 Plan（追記案 + 合意 / 判定軸明示）

- 追記案（合意済み）:
  - 判定軸（固定）: `a2a3Unlock / decisionQueueTransition / safeModeDefault`
  - AC に `decisionQueueTransition` 固定参照を追加。
  - DoD に「A1以外へ差し戻さない」を追加。
  - Verify に「依存矛盾ゼロ」を追加。

### Phase 3 Execute

- Executed:
  - 契約ID、凍結キー、unlockRule、Decision Queue を単一語彙で整備。
  - Stop Conditions を4ファイルで一致化。

### Phase 4 Verify

- Verification:
  - fixed keys diff = 0
  - dependency contradiction = 0
  - NoGo return path consistency = OK

### Phase 5 Proceed（handoff）

- handoff 固定値一覧: `freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`
- handoff 禁止遷移: `A1!=Done で A2/A3 Open` / `Pending bypass` / `NoGo時のA1以外差し戻し`
- handoff 差し戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 次担当者向け:
  - A2/A3 は本 hardening 契約を read-only 参照。
  - `Pending/held` を承認前に確定化しない。
  - NoGo 時は A1 契約ファイルへ差し戻す。

## 4) Acceptance Criteria / DoD

### Acceptance Criteria

- `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` の差分が 0 件。
- Return path が A1 に唯一固定される。

### DoD

- Go/No-Go 判定式が全節で一貫。
- 未承認事項が `Pending/held` で維持。
- Verify失敗時の自己修復上限が3回。

## 5) Go / No-Go（固定）

- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `A1未完了時A2/A3 Open禁止 = (a1Status!="Done") => Open禁止`
- `NoGo = !A2A3StartAllowed`

## 6) ADR Rule

- ADR追加/改訂が必要な場合は、実装前に `Context / Decision / Consequences` を Draft 起案。
- 承認が明示されるまで確定扱い禁止。
- 現時点判定: 契約整合化のみのため新規 ADR 起案なし。

## 7) Stop Conditions / Fail-safe

- Self-Correction 3回超過
- 前提崩壊
- 未定義競合
- 指定外ファイル編集要求または検知
