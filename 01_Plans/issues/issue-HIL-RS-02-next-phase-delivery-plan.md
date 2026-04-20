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


## 2.1) Phase 1 Read 差分確認（2026-04-20固定）

- 対象: `issue-HIL-RS-02` / `issue-HIL-RS-02-A1` / `issue-HIL-RS-01-A1`
- 固定キー差分:
  - `schemaVersion`: 差分なし（`1.0.0`）
  - `overridePolicy`: 差分なし（`human_dual_control_only`）
  - `contractLinkLocked`: 差分なし（`true`）
  - `sharedResourceFreeze`: 差分なし（`true`）
  - `safeModeDefault`: 差分なし（`ON`）
- 判定: `DiffCount=0`（Proceed可）

## 3) ADR CDC（必要時のみ）

- Context:
  - HIL-RS-02 は A1 契約を運用へ接続するフェーズ。
- Decision:
  - 依存は状態遷移で固定し、A2/A3 で契約値を変更しない。
- Consequences:
  - 契約差分は A1 へ集約。未承認事項は `Pending` 維持。

### 3.1) ADR合意ステータス（承認待ち）

- ApprovalStatus: `Pending (Human approval required)`
- ApprovalScope: `CDC Context/Decision/Consequences`
- Pre-approval lock: `承認前は確定扱い禁止（運用はread-only継続）`

## 4) Acceptance Criteria / DoD

- [x] CDC が明文化されている。
- [x] 依存順序 `A1 -> A2 -> A3` が固定されている。
- [x] `contractLinkLocked / sharedResourceFreeze / validatorPass` が判定条件として固定されている。
- [x] SafeMode既定ONと安全境界後退禁止が明示されている。
- [x] Proceed条件と停止条件が明示されている。

## 5) Serial Phase Protocol（強制）

各Phaseで必ず **Plan -> Execute -> Verify -> Proceed** を実施する。

### Phase 1 Read
- Plan: 対象4ファイルの依存・固定値・unlockRule照合項目を固定。
- Execute: `A1 -> A2 -> A3`、`a2a3Unlock`、固定キー群を再読照合。
- Verify: 不一致 `DiffCount=0`。
- Proceed: 差分は即停止し Phase 2 CDC へ。

### Phase 2 ADR CDC（必要時）
- Plan: 方針差分の有無を判定し、必要時のみ CDC を起票。
- Execute: `Context / Decision / Consequences` を `Pending/held` で記録。
- Verify: 承認前の確定化（契約値変更）が0件。
- Proceed: 承認済みのみ Phase 3 へ。

### Phase 3 Plan
- Plan: AC/DoD 不足（Go/No-Go、停止条件、差し戻し条件）をドラフト化。
- Execute: 合意済みドラフトを契約語彙に正規化して反映。
- Verify: 固定キーと矛盾がない。
- Proceed: 合意済みのみ Phase 4 へ。

### Phase 4 Execute
- Plan: 凍結対象キーを再確定。
- Execute: `contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault` を本文全体で統一。
- Verify: 依存逆転/語彙ドリフト=0件。
- Proceed: 一致時のみ Phase 5 へ。

### Phase 5 Verify
- Plan: docs-check（validator / `rg` / `git diff --check`）を固定。
- Execute: docs-check 実施、失敗時Self-Correction最大3回。
- Verify: `validatorPass=true`、frozen keys不一致0件。
- Proceed: 3回超過・未定義競合・前提崩壊で即停止。

### Phase 6 Proceed
- Plan: 「凍結I/Fスナップショット（read-only handoff）」を確定。
- Execute: freezeContractId・fixed keys・Go/No-Go・NoGo時差し戻し先を出力。
- Verify: A1契約（Stream A）と一致。
- Proceed: 一致時のみ handoff 完了。

## 6) Proceed Gate（固定）

1. `a1Status=="Done"`
2. `pendingDecisionQueueCount==0`
3. `contractLinkLocked==true`
4. `sharedResourceFreeze==true`
5. `validatorPass==true`

## 7) A2/A3 Start Rule（固定）

- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `NoGo = !A2A3StartAllowed`
- `NoGo` 時は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ差し戻す。

## 8) Fail-safe

- 即停止:
  - Self-Correction 3回超過
  - 未定義競合
  - 前提崩壊
  - 担当外編集要求
- 停止時報告:
  - 失敗条件 / 影響I/F / 要承認事項

## 9) Next Step 固定I/F一覧

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`


## 10) Phase 5 Proceed Handoff（read-only）

- Handoff mode: `read-only`
- Frozen values:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
- No-Go conditions（いずれか1つでも該当で停止）:
  - `a1Status!="Done"`
  - `pendingDecisionQueueCount>0`
  - `contractLinkLocked!=true`
  - `sharedResourceFreeze!=true`
  - `validatorPass!=true`
