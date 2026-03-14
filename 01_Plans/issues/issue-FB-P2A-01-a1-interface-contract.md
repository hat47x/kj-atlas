# Issue Draft: FB-P2A-01-A1 Island階層モデル導入 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Ready (A1 Contract Fixed)
- Priority: P0
- Owner: Stream B
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

## A1 contract audit（Stream B / Phase 2）

- 契約項目確定:
  - InterfaceName=`IslandHierarchyContractV1`
  - Required fields / Invariants / ContractLinks を固定対象として継続維持。
- I/F境界確定:
  - A2へは `contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence` を受け渡す。
  - A3は上記I/Fを受信専用で扱い、A1契約本文を再定義しない。
- 非目標（Non-goals）:
  - 永続スキーマ昇格判断、UI仕様追加、03_Implement配下の実装変更は本Issueの対象外。
  - SafeMode/share-export既定値の変更は対象外。

## ADR起票要否（Phase 2判定）

- 判定: **起票不要（No ADR proposal）**
- Context:
  - 既存 `ADR-0007` のDoD具体化であり、新規設計方針の導入ではない。
- Decision:
  - A1契約はIssue内固定で管理し、ADR改定は行わない。
- Consequences:
  - A2/A3は契約固定前提で直列進行可能。
  - 価値判断変更が発生した場合のみADR追加トリガへ遷移する。

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

### Stop report template（競合/前提崩れ時）

1) 失敗再現手順
2) 競合ファイル
3) 必要承認者
4) 解決のYes/No質問

- 自己修復が3回連続で失敗、または契約リンク不整合を検出した場合は更新を停止し、指示待ちに遷移する。


## Decision Queue整理（Stream A view）

| QueueID | Topic | Status | Decision | Proceed Impact |
|---|---|---|---|---|
| DQ-FB-P2A-01-001 | ContractID固定 (`CTR-2A-01-ISLAND-HIERARCHY-V1`) | Closed | A1で固定 | A2可 |
| DQ-FB-P2A-01-002 | A2/A3で契約変更禁止 | Closed | 逸脱はA1差し戻し | A3可 |
| DQ-FB-P2A-01-003 | SafeMode後退禁止の適用確認 | Closed | 契約境界で後退禁止 | A2/A3可 |

## Proceed判定（A2/A3）

- 可否: **可**
- 根拠: 契約IDと必須フィールドが固定、Decision Queueの未処理項目なし。
- 残リスク: tie時ソートキーの名称揺れ（実装詳細）。A1契約変更なしでA2/A3注記で吸収。



## Stream A固定シグネチャ / 検証キー（A2/A3引き渡し）

- Fixed signature:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Verification keys:
  - `ContractID`（または `InterfaceName`）
  - `schemaVersion`（定義がある契約）
  - 必須フィールド一覧
- Rule:
  - A2/A3は上記キーの一致確認のみ実施し、契約本文は改訂しない。
