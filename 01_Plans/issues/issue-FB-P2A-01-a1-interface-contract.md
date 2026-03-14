# Issue Draft: FB-P2A-01-A1 Island階層モデル導入 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Ready (A1 Contract Fixed)
- Priority: P0
- Owner: Stream E
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: `Island階層モデル導入` の境界I/F（型・必須項目・契約リンク）を先行固定する。
- Phase: `A1 Interface First`
- PriorityClass（Must / Should / Could）: Must
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed

## Contract definition（A1成果物）

- ContractFreeze:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`


- InterfaceName: `IslandHierarchyContractV1`
- ContractLinks:
  - Upstream: `ADR-0007 FB-P2A-01`
  - Downstream-A2: `issue-FB-P2A-01-a2-mock-validation.md`
  - Downstream-A3: `issue-FB-P2A-01-a3-implementation.md`
- Required fields:
  - `island.id: string`
  - `island.parentIslandId: string | null`（rootはnull）
  - `island.childIslandIds: string[]`（重複禁止、循環参照禁止）
  - `document.schemaVersion: string`（契約適用範囲を識別）
- Invariants:
  - `parentIslandId` が存在する場合、参照先islandは同一document内に存在。
  - 親子関係は有向非巡回（DAG）を維持。
  - save/load roundtripで階層情報が不変。

## Phase execution log（A1）

### Read sync（Phase開始時）

- `issue-FB-P2A-01-a1-interface-contract.md`
- `issue-FB-P2A-01-a2-mock-validation.md`
- `issue-FB-P2A-01-a3-implementation.md`

### Plan

- `IslandHierarchyContractV1` の固定対象（Required fields / Invariants / ContractLinks）を確定する。
- A2/A3で契約変更を禁止する freeze 条件を明記する。

### Execute

- Required fields と Invariants をA1成果物として記述し、A2/A3リンクを固定。
- SafeMode・share/export既定挙動に非影響であることを明記。

### Verify

- ContractLinks が A1→A2→A3 で到達可能であることを確認。
- A2/A3で参照する固定契約名が `IslandHierarchyContractV1` で一致することを確認。

### Proceed

- A2へ引き渡す固定契約として `IslandHierarchyContractV1` を採用し、A1を完了状態とする。

## ADR change handling

- ADR change involved: **No**（本タスクは既存 `ADR-0007` の具体化であり、新規ADR改定は不要）
- C/D/C + approval: **N/A**

## ADR要否判定（Phase 1要件）

- 判定: **現時点はADR追加不要**。
- Reason:
  - 新規アーキテクチャ方針ではなく、`ADR-0007` DoD具体化のためのI/F固定である。
  - 既存 `schemas.md` の拡張範囲に収まる。
- ADR追加トリガ:
  - 階層モデルの循環許容など、既存価値判断（ADR-0001）と衝突する仕様変更が必要になった場合。

## Acceptance criteria

- [x] A1でRequired fields / Invariants / ContractLinksが固定される。
- [x] A2/A3は本契約を変更せず参照のみで進行できる。
- [x] SafeMode・share/export既定挙動を変更しないと明記される。
- [x] 契約リンク不整合がない（A1→A2→A3）。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-01-a1-interface-contract.md`
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`
- 前回コミット差分競合がある場合は、契約リンク整合を優先して修正する。

## Handoff（A2/A3参照専用）

- Fixed links:
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`
- 変更禁止項目:
  - `InterfaceName=IslandHierarchyContractV1`
  - Required fields / Invariants / ContractLinks
  - `contractLinkLocked=true` / `sharedResourceFreeze=true`
- 逸脱要求はA1へ差し戻し。

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Expected:
  - issue memoの命名とメタ項目が検証を通過する。

## Fail-safe

- 自己修復が3回連続で失敗、または契約リンク不整合を検出した場合は更新を停止し、指示待ちに遷移する。
