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

## 2) Contract Freeze（read-only, single source of truth）

- snapshotId=`MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- freezeContractId=`HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Dependency order: `A1 -> A2 -> A3`
- unlockRule=`a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- decisionQueueTransition=`Pending -> Approved | Pending -> Rejected`
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

## 3) Serial Phase Management（強制）

> 各 Phase 開始時に対象4ファイル（本書 / `issue-HIL-RS-01-A1` / `issue-HIL-RS-02` / `issue-HIL-RS-02-A1`）を再読し、差分があれば Plan を更新してから実行する。

### Phase 1 Read（2026-04-21）

- Check targets: `Status / Priority / Acceptance Criteria / Dependencies`
- Result: 差分なし（`DiffCount=0`）
- Proceed条件: 差分なしのみ Phase 2 へ

### Phase 2 Plan（AC/DoD不足の追記案 + 合意）

- 追記案（合意済み）:
  1. AC に `decisionQueueTransition` の固定参照を追加。
  2. DoD に「NoGo時の唯一差し戻し先=A1」を追加。
  3. Verifyに「依存矛盾ゼロ」を明文化。
- 合意ログ: 本タスク依頼をもって Stream A で実施合意済み。

### Phase 3 Execute（契約ID・停止条件・Decision Queue参照整備）

- Executed:
  - `freezeContractId` と `contractIds` を全節で固定。
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected` を統一参照化。
  - Stop Conditions を `固定値差分 / Pending bypass / Self-Correction 3回超過 / 担当外編集要求` に統一。

### Phase 4 Verify（AC/DoD整合検査）

- Verification checks:
  - AC: `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` の差分 0。
  - DoD: `A1 -> A2 -> A3` と `NoGo -> A1差し戻し` が整合。
  - 文書整合: 対象4ファイルで依存矛盾 0。

### Phase 5 Proceed（handoff）

- 次担当者向け handoff（read-only）:
  - A2/A3 は本書の契約値を再定義しない。
  - NoGo 条件が1つでも成立した場合は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` に差し戻す。
  - 未承認事項は `Pending/held` を維持し、確定扱い禁止。

## 4) Acceptance Criteria / DoD

### Acceptance Criteria

- `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` の差分が 0 件。
- A2/A3 開放条件が `A1==Done && pendingDecisionQueueCount==0` で固定。
- Decision Queue 参照が `Pending -> Approved | Pending -> Rejected` に固定。

### Definition of Done

- Serial workflow（Plan -> Execute -> Verify -> Proceed）を本書で固定。
- `safeModeDefault=ON` と `human_dual_control_only` 後退禁止が明文化。
- NoGo時の唯一差し戻し先が A1 契約ファイルである。

## 5) ADR Rule

- ADR追加/改訂が必要な場合は、実装前に `Context / Decision / Consequences` を Draft 起案する。
- 人間承認が明示されるまで ADR は確定扱いにしない（`Pending/held` 維持）。
- 現時点判定: 本更新は既存契約の整合化のみで、新規 ADR 起案は不要。

## 6) Stop Conditions / Fail-safe

- 即停止条件:
  1. Self-Correction 3回超過
  2. 前提崩壊
  3. 未定義競合
  4. 指定外ファイル編集要求または検知
- 停止時即時報告:
  - 失敗条件
  - 影響範囲
  - 人間に必要な判断

## 7) Next Step Fixed I/F（read-only）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
