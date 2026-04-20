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

## 2) Fixed Contract Snapshot（read-only）

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`

## 3) ADR CDC（必要時のみ）

- Context:
  - A1 が曖昧だと A2/A3 の Open 判定が不安定化する。
- Decision:
  - Stream A は A1 契約識別子と遷移条件のみ固定し、下流は read-only 参照とする。
- Consequences:
  - 変更要求は `A1-CDC-only` へ差し戻し、A2/A3 で局所修正しない。

## 4) State Transition Contract（固定）

- Unlock rule（唯一）:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Decision Queue:
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

1. Read
   - Plan: 対象 issue 再読対象を固定。
   - Execute: 契約ID / Gate式 / 固定値を照合。
   - Verify: 不一致=0件。
   - Proceed: 不一致時は CDC 承認待ちへ。
2. Plan
   - Plan: AC/DoD不足を抽出。
   - Execute: ドラフト提案を記録。
   - Verify: `agreementStatus=agreed` まで確定しない。
   - Proceed: 合意済みのみ Execute へ。
3. ADR CDC（必要時）
   - Plan: 方針変更有無を判定。
   - Execute: CDC を承認待ちで記録。
   - Verify: 承認前の確定化なし。
   - Proceed: 承認後のみ Phase 4。
4. Execute
   - Plan: 正規化対象（契約文言・依存順・停止条件）を固定。
   - Execute: 曖昧語を削除し式を固定。
   - Verify: 依存逆転=0。
   - Proceed: Verify pass で次へ。
5. Verify & Proceed
   - Plan: 検証コマンド固定。
   - Execute: docs-check 実施。
   - Verify: `validatorPass=true`。
   - Proceed: 固定I/Fを read-only handoff する。

## 7) Go / No-Go（固定）

- `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `NoGo = !Go`

## 8) Fail-safe

- 即停止: Self-Correction 3回超過 / 未定義競合 / 前提崩壊 / 担当外編集要求。
- 停止時報告:
  1. 失敗条件
  2. 影響契約ID
  3. 要承認事項

## 9) Downstream Fixed I/F（変更禁止）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
