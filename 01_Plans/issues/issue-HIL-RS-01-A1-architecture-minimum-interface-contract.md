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

## 2) Frozen Minimum Interface Contract（SSOT）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

## 3) Serial Phase Protocol（強制）

各Phaseは **開始時に対象5ファイルを再読** し、`Plan -> Execute -> Verify -> Proceed` を順に実施する。

### Phase 1: Read & Baseline（2026-04-21）
- Plan: `Status / Priority / Dependencies / AC / DoD` の比較軸を固定。
- Execute: 5ファイルで契約値・語彙・停止条件を照合。
- Verify: `DiffCount=0`。
- Proceed: 差分ありなら Plan 更新を先行。

### Phase 2: Plan（合意済み）
- Plan: 判定軸を `a2a3Unlock / decisionQueueTransition / safeModeDefault` に固定。
- Execute: AC/DoDへ `NoGo時A1差戻し` と `依存矛盾ゼロ` を補完。
- Verify: A1が唯一ゲートとして参照される。
- Proceed: CDC必要時は Phase 3。

### Phase 3: ADR CDC Gate
- Plan: ADR改訂要否を判定。
- Execute: 契約整合のみのため ADR変更なし。
- Verify: 承認待ち事項なし。
- Proceed: Phase 4。

### Phase 4: Execute
- Plan: Go/NoGo判定式を単一化。
- Execute: unlockRule・decisionQueueTransition・NoGo return pathを5ファイルで一致化。
- Verify: fixed keys diff=0, dependency contradiction=0。
- Proceed: Phase 5。

### Phase 5: Verify
- Plan: AC/DoD自己検証。
- Execute: docs-check + diff check。
- Verify: 失敗時self-correction最大3回。
- Proceed: Pass時のみ Phase 6。

### Phase 6: Proceed（handoff）
- handoff固定値: `freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`
- handoff禁止遷移: `A1!=Done で A2/A3 Open` / `Pending bypass` / `NoGo時のA1以外差し戻し`
- handoff差戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 4) Acceptance Criteria / DoD

### Acceptance Criteria

- `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` が対象5ファイルで一致。
- `A1 -> A2 -> A3` と `a2a3Unlock` が唯一条件として定義される。

### DoD

- A1 が唯一の差し戻し先である。
- Go/No-Go 判定式が5ファイルで一致する。
- Verify失敗時 Self-Correction は最大3回。

## 5) Go / No-Go（固定）

- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `A1未完了時A2/A3 Open禁止 = (a1Status!="Done") => Open禁止`
- `NoGo = !A2A3StartAllowed`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 6) ADR Rule

- 追加/改訂が必要な場合のみ `Context / Decision / Consequences` を Draft 化。
- 承認明示まで確定禁止（`Pending/held`）。
- 現時点判定: 既存契約整合化のみのため新規 ADR なし。

## 7) Stop Conditions / Fail-safe

- 固定値ドリフト検出
- `Pending bypass` 要求
- Self-Correction 3回超過
- 前提崩壊 / 未定義競合
- 指定外ファイル編集要求または検知
