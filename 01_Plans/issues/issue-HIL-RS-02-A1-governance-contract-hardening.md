# Issue Draft: HIL-RS-02 A1 Governance/Contract hardening

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Related Backlog: `HIL-RS-02`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `02_Architecture/review_attribution.md`
- Expected verification level: `docs-check`

## 1) 背景

- HIL-RS-02でA2/A3を安全に開始するため、A1で契約変更差し戻し導線と未確定管理を強化する必要がある。

## 2) 目的

- A2/A3開始条件（契約固定・責務分離・停止条件）を明文化し、未確定事項の誤確定を防ぐ。

## 3) スコープ

- A1契約参照先、変更差し戻し手順、Decision Queue更新基準の文書化。

## 4) 非スコープ

- 実装コード変更。
- schemaVersionの再定義。

## 5) 受入条件

- AC-1: A1開始/停止/再開条件が文書化される。
- AC-2: human_dual_control_only と SafeMode維持が明示される。
- AC-3: A2/A3は「A1完了までDraft維持」と明記される。

## 6) 検証方法

- `rg -n "SafeMode|human_dual_control_only|A1→A2→A3" 01_Plans/issues/issue-HIL-RS-02-*.md 01_Plans/adr/ADR-0027-hil-rs-02-next-phase-execution-plan.md`
- `python 01_Plans/issues/validate_active_issue_memos.py`

## 7) 依存関係

- `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 8) リスク

- A1定義が曖昧なままA2/A3をOpen化すると、契約逸脱が発生する。

## 9) 着手順

1. A1開始条件固定
2. 停止/再開条件固定
3. A2/A3 Draft境界反映
