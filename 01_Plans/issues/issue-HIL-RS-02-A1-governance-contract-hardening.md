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

## 3) Serial Phase Protocol（強制）

各Phaseは **開始時に対象5ファイルを再読** し、`Plan -> Execute -> Verify -> Proceed` を順に実施する。

### Phase 1: Read & Baseline（2026-04-21）
- Plan: `Status / Priority / Dependencies / AC / DoD` を比較軸として固定。
- Execute: 5ファイルの契約値・依存順序・停止条件を照合。
- Verify: `DiffCount=0`。
- Proceed: 差分検知時は Plan 更新を優先。

### Phase 2: Plan（合意済み）
- Plan: 判定軸を `a2a3Unlock / decisionQueueTransition / safeModeDefault` に固定。
- Execute: ACへDecision Queue固定遷移、DoDへA1以外差戻し禁止、Verifyへ依存矛盾ゼロを明記。
- Verify: NoGo return path が A1 で一意。
- Proceed: CDC必要時は Phase 3。

### Phase 3: ADR CDC Gate
- Plan: ADR変更の必要性判定。
- Execute: 契約整合のみのため ADR変更なし。
- Verify: 承認待ちCDCなし。
- Proceed: Phase 4。

### Phase 4: Execute
- Plan: 契約ID・凍結キー・停止条件の統一対象を再固定。
- Execute: Go/NoGo式と禁止遷移を5ファイルで一致化。
- Verify: fixed keys diff=0、dependency contradiction=0。
- Proceed: Phase 5。

### Phase 5: Verify
- Plan: AC/DoD自己検証手順を固定。
- Execute: docs-check + diff check。
- Verify: self-correction最大3回。
- Proceed: Pass時のみ Phase 6。

### Phase 6: Proceed（handoff）
- handoff固定値: `freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`
- handoff禁止遷移: `A1!=Done で A2/A3 Open` / `Pending bypass` / `NoGo時のA1以外差し戻し`
- handoff差戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

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
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 6) ADR Rule

- ADR追加/改訂が必要な場合は、実装前に `Context / Decision / Consequences` を Draft 起案。
- 承認が明示されるまで確定扱い禁止。
- 現時点判定: 契約整合化のみのため新規 ADR 起案なし。

## 7) Stop Conditions / Fail-safe

- 固定値ドリフト検出
- `Pending bypass` 要求
- Self-Correction 3回超過
- 前提崩壊 / 未定義競合
- 指定外ファイル編集要求または検知
