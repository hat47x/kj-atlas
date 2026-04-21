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

> 各 Phase 開始時に対象4ファイル（`issue-HIL-RS-01` / `issue-HIL-RS-01-A1` / 本書 / `issue-HIL-RS-02-A1`）を再読し、差分検知時は Plan 更新を先行する。

### Phase 1 Read（2026-04-21）

- Check: `Status / Priority / AC / Dependencies`
- Result: 差分なし（`DiffCount=0`）

### Phase 2 Plan（追記案 + 合意）

- 追記案（合意済み）:
  - AC に Decision Queue 固定参照を追加。
  - DoD に「NoGo時のA1差し戻し固定」を追加。
  - Verify に「依存矛盾ゼロ」の明記を追加。

### Phase 3 Execute

- Executed:
  - 契約ID・凍結キー・unlockRule を統一。
  - 停止条件を4ファイルで一致化。
  - Decision Queue 参照を固定語彙化。

### Phase 4 Verify

- Verification:
  - AC diff check = 0
  - DoD consistency check = OK
  - 文書整合（依存矛盾）= 0

### Phase 5 Proceed（handoff）

- 次担当者向け:
  - A2/A3 は read-only 参照のみ。
  - NoGo時は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ差し戻し。
  - `Pending/held` を承認前に解除しない。

## 4) Acceptance Criteria / DoD

### Acceptance Criteria

- `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` の差分が 0 件。
- A2/A3 開放条件が `A1 Done + pendingDecisionQueueCount==0` で固定。
- Decision Queue が `Pending -> Approved | Pending -> Rejected` に固定。

### DoD

- Go/No-Go 判定式が単一化される。
- 差し戻し先が A1 に固定される。
- 未承認事項は `Pending/held` のまま維持される。

## 5) A2/A3 Start Rule（固定）

- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `NoGo = !A2A3StartAllowed`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 6) ADR Rule

- ADR追加/改訂が必要な場合のみ、実装前に `Context / Decision / Consequences` を Draft 起案。
- 人間承認が明示されるまで確定扱い禁止。
- 現時点判定: 契約整合化のみのため新規 ADR 起案なし。

## 7) Stop Conditions / Fail-safe

- 固定値ドリフト検出
- Pending bypass 要求
- Self-Correction 3回超過
- 指定外ファイル編集要求または検知
