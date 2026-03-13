# Issue Draft: FB-P2A-01-A1 Island階層モデル導入 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Draft (起票用)
- Priority: P0
- Owner: Stream C
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

## Context / Decision / Consequences

- Context:
  - A2/A3で契約の再解釈が起こると、階層整合（親参照・循環禁止）の責務境界が崩れる。
- Decision:
  - `IslandHierarchyContractV1` をA1の単一正本として固定し、A2/A3は参照専用とする。
- Consequences:
  - A2はモック妥当性検証に集中できる。
  - A3は `schema -> domain model -> persistence roundtrip` へ直列接続できる。

## ADR要否判定（Phase 1要件）

- 判定: **現時点はADR追加不要**。
- Reason:
  - 新規アーキテクチャ方針ではなく、`ADR-0007` DoD具体化のためのI/F固定である。
  - 既存 `schemas.md` の拡張範囲に収まる。
- ADR追加トリガ:
  - 階層モデルの循環許容など、既存価値判断（ADR-0001）と衝突する仕様変更が必要になった場合。

## Acceptance criteria

- [ ] A1でRequired fields / Invariants / ContractLinksが固定される。
- [ ] A2/A3は本契約を変更せず参照のみで進行できる。
- [ ] SafeMode・share/export既定挙動を変更しないと明記される。
- [ ] 契約リンク不整合がない（A1→A2→A3）。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-01-a1-interface-contract.md`
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`
- 前回コミット差分競合がある場合は、契約リンク整合を優先して修正する。

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Expected:
  - issue memoの命名とメタ項目が検証を通過する。

## Fail-safe

- 自己修復が3回連続で失敗、または契約リンク不整合を検出した場合は更新を停止し、指示待ちに遷移する。
