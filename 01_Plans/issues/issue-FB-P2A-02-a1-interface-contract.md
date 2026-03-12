# Issue Draft: FB-P2A-02-A1 Collapse/Expand操作 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Draft (起票用)
- Priority: P0
- Owner: Stream B
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/architecture.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: `Collapse/Expand操作` の境界I/F（型・必須項目・契約リンク）を先行固定する。
- Phase: `A1 Interface First`
- PriorityClass: Must
- GoNoGoGate: Required
- SecurityGateImpact: N/A（計画のみ）
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Contract definition（A1成果物）

- InterfaceName: `IslandVisibilityContractV1`
- ContractLinks:
  - Upstream: `ADR-0007 FB-P2A-02`
  - Downstream-A2: `issue-FB-P2A-02-a2-mock-validation.md`
  - Downstream-A3: `issue-FB-P2A-02-a3-implementation.md`
- Required fields:
  - `island.id: string`
  - `island.isCollapsed: boolean`
  - `view.hiddenDescendantIslandIds: string[]`
  - `view.hiddenCardIds: string[]`
- Invariants:
  - `isCollapsed=true` の親配下は描画・ヒットテスト対象外。
  - `isCollapsed=false` で直近状態から復帰可能。
  - collapse/expand操作はdocument構造を破壊しない（view stateのみ変更）。

## ADR要否判定（Phase 1要件）

- 判定: **現時点はADR追加不要**。
- Reason:
  - 既存 `ADR-0007` のAC-2A-2/3を具体化するI/F定義であり、方針変更ではない。
- ADR追加トリガ:
  - collapse状態を永続仕様へ昇格する等、architecture層の責務分離を変える場合。

## Acceptance criteria

- [ ] Required fields / Invariants / ContractLinksが固定される。
- [ ] A2/A3は本契約の参照のみで進行可能。
- [ ] SafeMode既定やshare/export既定挙動を変更しない。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- 自己修復が3回連続で失敗、または契約リンク不整合を検出した場合は停止して指示待ち。
