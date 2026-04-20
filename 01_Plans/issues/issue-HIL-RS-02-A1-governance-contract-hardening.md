# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0027`, `ADR-0026`, `ADR-0028`, `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`
- Expected verification level: `docs-check`

## 1) Objective

A1 契約凍結を統治判定式として固定し、A2/A3 の誤Open化を防止する。

## 2) Hardening Rules（固定）

- Dependency order: `A1 -> A2 -> A3`
- Unlock rule（唯一）:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Decision Queue（唯一）:
  - `Pending -> Approved` または `Pending -> Rejected`
- Freeze keys:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
- Return path（唯一）:
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 3) ADR CDC（必要時のみ）

- Context:
  - 判定規約が複数化すると HIL-RS-02 の統治が崩れる。
- Decision:
  - Stream A は統治規約を本 issue に固定し、下流は read-only 参照のみ。
- Consequences:
  - 契約差分要求は A1 へ集約し、A2/A3 で局所上書きしない。

## 4) Acceptance Criteria / DoD

- [x] Unlock rule が唯一条件として明文化されている。
- [x] Decision Queue 遷移が唯一化されている。
- [x] 固定識別子と固定値が明文化されている。
- [x] `safeModeDefault=ON` と安全境界後退禁止が明文化されている。
- [x] Verify 失敗3回上限と停止条件が明文化されている。

## 5) Serial Phase Protocol（強制）

各Phaseで必ず **Plan -> Execute -> Verify -> Proceed** を実施する。

1. Read
   - Plan: 再読対象を固定。
   - Execute: 契約ID/凍結値/遷移を照合。
   - Verify: 不一致=0件。
   - Proceed: 差分は CDC 論点へ。
2. Plan
   - Plan: AC/DoD不足を抽出。
   - Execute: ドラフト提案化。
   - Verify: 未承認は `Pending` 維持。
   - Proceed: 合意済みのみ次へ。
3. ADR CDC（必要時）
   - Plan: 方針変更要否判定。
   - Execute: CDC 記録（承認待ち）。
   - Verify: 承認前確定化なし。
   - Proceed: 承認済みのみ Execute。
4. Execute
   - Plan: 契約文言正規化対象を固定。
   - Execute: 曖昧語を削除し統一式へ。
   - Verify: 依存逆転/未定義競合=0件。
   - Proceed: Verify pass で次へ。
5. Verify & Proceed
   - Plan: 検証コマンド固定。
   - Execute: docs-check 実施。
   - Verify: `validatorPass=true`。
   - Proceed: 固定I/Fを read-only handoff。

## 6) Open化条件

- `a1Status=="Done"`
- `pendingDecisionQueueCount==0`
- `contractLinkLocked==true`
- `sharedResourceFreeze==true`
- `validatorPass==true`

## 7) Go / No-Go（固定）

- `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `NoGo = !Go`

## 8) Fail-safe

- 即停止:
  1. Self-Correction 3回超過
  2. 未承認確定化
  3. 固定識別子不一致
  4. 担当外編集要求
- 停止時報告:
  - 失敗条件 / 影響範囲 / 要承認事項

## 9) Fixed Values Handoff（変更禁止）

| Key | Frozen Value |
| --- | --- |
| freezeContractId | `HIL-RS-02-A1-CONTRACT-FREEZE-v1` |
| contractIds | `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF` |
| schemaVersion | `1.0.0` |
| overridePolicy | `human_dual_control_only` |
| contractLinkLocked | `true` |
| sharedResourceFreeze | `true` |
| safeModeDefault | `ON` |
