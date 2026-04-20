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

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- Freeze Pack ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Dependency order: `A1 -> A2 -> A3`
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
  - `DecisionQueue: Pending -> Approved | Rejected`
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

### Phase 1: Read & Lock
- Plan: 対象5 issue を再読し差分候補を列挙。
- Execute: `Status / Dependencies / Scope / fixed keys` を照合。
- Verify: 固定値不一致=0件を確認。
- Proceed: 不一致があれば即停止して Phase 3 CDC 承認待ちへ。

### Phase 2: Contract Freeze（mock-first）
- Plan: I/F固定対象（contractIds / schemaVersion / gate条件）を確定。
- Execute: 実装詳細は追加せず、他ストリーム非依存の最小契約のみ固定。
- Verify: read-only 契約として矛盾がない。
- Proceed: 凍結完了時のみ Phase 3 へ。

### Phase 3: ADR CDC（必要時のみ）
- Plan: 方針変更の必要性判定。
- Execute: `Context/Decision/Consequences` を承認待ちで明文化。
- Verify: 承認前に確定文言へ進んでいないことを確認。
- Proceed: 承認済みのみ Phase 4 へ。

### Phase 4: Plan -> Execute -> Verify
- Plan: AC/DoD 不足提案と停止条件を固定。
- Execute: 契約文言・依存順・停止条件を正規化。
- Verify: 依存逆転=0、未定義語彙=0、`validatorPass=true`。
- Proceed: Verify pass 時のみ Phase 5 へ。

### Phase 5: Proceed / Stopper
- Plan: 次工程へ渡す固定I/F一覧を確定。
- Execute: read-only handoff を出力。
- Verify: A1 frozen keys と一致。
- Proceed: 失敗・競合時は即停止し指示待ち。

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
