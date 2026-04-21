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

HIL-RS-01 を **契約先行の計画正本** として固定し、A1/A2/A3 依存を状態遷移契約で管理する。

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

## 3) Serial Phase Protocol（強制）

各Phaseは **開始時に対象5ファイルを再読** し、必ず `Plan -> Execute -> Verify -> Proceed` を順に実施する。

- 対象5ファイル:
  - `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `issue-HIL-RS-02-next-phase-delivery-plan.md`
  - `issue-HIL-RS-02-A1-governance-contract-hardening.md`
  - `issue-HIL-RS-02-A3-operations-documentation-sync.md`

### Phase 1: Read & Baseline（2026-04-21）
- Plan: `Status / Priority / Dependencies / AC / DoD` を比較観点として固定。
- Execute: 対象5ファイルの固定キー・依存順序・停止条件を照合。
- Verify: `DiffCount=0`。
- Proceed: 差分がある場合は Plan を更新してから次へ進む。

### Phase 2: Plan（合意済み）
- Plan: `A1 -> A2 -> A3`、`unlockRule`、`decisionQueueTransition`、`NoGo return path` を単一正本へ収束。
- Execute: AC/DoD不足を補完（Decision Queue固定遷移、NoGo時A1差戻し、依存矛盾ゼロ）。
- Verify: 5ファイル全てで同語彙・同判定式を参照。
- Proceed: CDC必要時は Phase 3 へ。

### Phase 3: ADR CDC Gate
- Plan: ADR変更要否を判定。
- Execute: **契約整合のみ** のため ADR変更なし。
- Verify: `Context / Decision / Consequences` 新規起案不要。
- Proceed: Phase 4 へ。

### Phase 4: Execute
- Plan: 契約値・停止条件・語彙の統一対象を再固定。
- Execute: A1唯一ゲート、Decision Queue固定遷移、NoGo差戻し先A1を統一。
- Verify: 固定キー差分0・依存矛盾0。
- Proceed: Phase 5 へ。

### Phase 5: Verify
- Plan: AC/DoD検証手順を固定。
- Execute: docs-checkと差分検証を実施。
- Verify: 失敗時self-correction最大3回、4回目相当は停止。
- Proceed: Pass時のみ Phase 6 へ。

### Phase 6: Proceed（handoff）
- 固定値: `freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`
- 禁止遷移: `A1!=Done で A2/A3 Open` / `Pending bypass` / `NoGo時のA1以外差し戻し`
- NoGo return path: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 4) Acceptance Criteria / DoD

### Acceptance Criteria

- `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` の差分が 0 件。
- A2/A3 開放条件が `A1==Done && pendingDecisionQueueCount==0` で固定。
- Decision Queue 参照が `Pending -> Approved | Pending -> Rejected` に固定。

### Definition of Done

- Serial workflow（Plan -> Execute -> Verify -> Proceed）が5ファイルで一致。
- `safeModeDefault=ON` と `human_dual_control_only` 後退禁止が明文化。
- NoGo時の唯一差し戻し先が A1 契約ファイルである。

## 5) ADR Rule

- ADR追加/改訂が必要な場合は、実装前に `Context / Decision / Consequences` を Draft 起案する。
- 人間承認が明示されるまで ADR は確定扱いにしない（`Pending/held` 維持）。
- 現時点判定: 本更新は既存契約の整合化のみで、新規 ADR 起案は不要。

## 6) Stop Conditions / Fail-safe

- 即停止条件:
  1. 固定値ドリフト検出
  2. `Pending bypass` 要求
  3. Self-Correction 3回超過
  4. 前提崩壊 / 未定義競合
  5. 指定外ファイル編集要求または検知

## 7) Next Step Fixed I/F（read-only）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
