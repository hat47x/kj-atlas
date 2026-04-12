# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner (Stream B planning)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0027`, `ADR-0026`, `ADR-0028`, `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`
- Expected verification level: `docs-check`

## 1) Objective

A1契約凍結をガバナンス判定式として固定し、A2/A3の誤Open化を防止する。

## 2) Hardening Rules（状態遷移契約）

- Unlock rule（唯一）:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Decision Queue（唯一）:
  - `Pending -> Approved | Rejected`
- Freeze keys（Mock snapshot固定識別子）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Return path（唯一）:
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 3) ADR CDC（Phase 2）

- Context:
  - A1の判定規約が複数化すると、HIL-RS-02の統治が崩れる。
- Decision:
  - Stream Bはガバナンス規約をissue本文へ固定し、設計/運用文書の実体編集は行わない。
- Consequences:
  - A2/A3はread-only参照となり、契約差分要求はA1に集約される。

## 4) Acceptance Criteria / DoD

- [x] Unlock ruleが唯一条件として明文化。
- [x] Decision Queue遷移が唯一化。
- [x] 固定識別子が明文化。
- [x] 安全境界後退禁止が明文化。
- [x] Verify失敗3回上限と停止条件が明文化。

## 5) Serial Phases（Read -> CDC -> Plan -> Execute -> Verify -> Proceed）

- Phase開始ごとに対象5 issueを再Readする。
- Executeはissue本文のみ同期する（契約識別子、遷移、禁止事項）。
- Verifyは `validate_active_issue_memos.py` / `rg` / `git diff`。
- 失敗時は自己修復最大3回。超過時は停止。

## 6) Open化条件

- `a1Status=="Done"`
- `pendingDecisionQueueCount==0`
- 固定識別子一致
- 未承認決定の確定化がない

## 7) Fail-safe

- 3回修復超過 / 未承認確定化 / 不一致競合で停止。
