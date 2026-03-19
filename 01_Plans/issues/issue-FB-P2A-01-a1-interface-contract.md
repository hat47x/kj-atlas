# Issue Draft: FB-P2A-01-A1 Island階層モデル導入 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Ready (A1 Contract Fixed)
- Priority: P0
- Owner: Stream D
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

## Phase management（Stream D）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約点検（I/F固定と契約ドリフト検知）
- Phase 3: A2モック検証計画固定（M1..M4・責務分離）
- Phase 4: A3 handoff条件固定（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）

## Contract definition（A1成果物）

- ContractID: `CTR-2A-01-ISLAND-HIERARCHY-V1`
- InterfaceName: `IslandHierarchyContractV1`
- ContractFreeze:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- ContractLinks:
  - Upstream: `ADR-0007 FB-P2A-01`
  - Downstream-A2: `issue-FB-P2A-01-a2-mock-validation.md`
  - Downstream-A3: `issue-FB-P2A-01-a3-implementation.md`
- Required fields:
  - `document.schemaVersion: string`
  - `island.id: string`
  - `island.cardIds: string[]`
  - `island.parentIslandId?: string`（rootは未設定許容）
- Invariants:
  - `parentIslandId` が存在する場合、参照先 island は同一 document 内に存在する。
  - `parentIslandId` のみを正本とし、子一覧は派生情報としてA1契約に含めない。
  - self-parent を含む循環参照は許可しない。
  - import 正規化では不正な `parentIslandId` を `undefined` にフォールバックできる。
  - save/load roundtrip では有効な `parentIslandId` を欠落させず往復保持する。

## Context / Decision / Consequences（A1固定化）

### Context

- `02_Architecture/schemas.md` は FB-P2A-01 の単一正本として `parentIslandId?: string` を定義している。
- Stream D の担当範囲は P2A 専用 issue の契約固定・モック検証設計・実装引き渡し条件の文書化に限定される。
- 実装コードや共有ファイルを更新せずに、A2/A3 が同一契約を参照できる状態を先に作る必要がある。

### Decision

- ContractID を `CTR-2A-01-ISLAND-HIERARCHY-V1`、InterfaceName を `IslandHierarchyContractV1` として固定する。
- 階層表現は `parentIslandId` を正本に採用し、`childIslandIds` のような派生情報は A1 契約必須項目へ含めない。
- A2/A3 は A1 契約本文を変更せず、ContractID / InterfaceName / Required fields / Invariants の一致確認のみ行う。

### Consequences

- `02_Architecture/schemas.md` と矛盾しない最小契約で A2/A3 を直列進行できる。
- 子一覧キャッシュや UI 都合の派生表現は A3 実装検討の裁量として残るが、A1 契約破壊変更は禁止される。
- SafeMode / share-export / 実装コードには影響を持ち込まない。

## A1 contract audit（Stream D / Phase 2）

- 契約項目確定:
  - `ContractID=CTR-2A-01-ISLAND-HIERARCHY-V1`
  - `InterfaceName=IslandHierarchyContractV1`
  - Required fields / Invariants / ContractLinks を固定対象として継続維持。
- I/F境界確定:
  - A2へは `contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence` を受け渡す。
  - A3は上記I/Fを受信専用で扱い、A1契約本文を再定義しない。
- 非目標（Non-goals）:
  - 永続スキーマ昇格判断、UI仕様追加、03_Implement配下の実装変更は本Issueの対象外。
  - SafeMode/share-export既定値の変更は対象外。

## ADR起票要否（Phase 2判定）

- 判定: **起票不要（No ADR proposal）**
- Context:
  - 既存 `ADR-0007` と `02_Architecture/schemas.md` のDoD具体化であり、新規設計方針の導入ではない。
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

- `CTR-2A-01-ISLAND-HIERARCHY-V1` の固定対象（Required fields / Invariants / ContractLinks）を確定する。
- A2/A3で契約変更を禁止する freeze 条件を明記する。

### Execute

- Required fields と Invariants をA1成果物として記述し、A2/A3リンクを固定。
- SafeMode・share/export既定挙動に非影響であることを明記。

### Verify

- ContractLinks が A1→A2→A3 で到達可能であることを確認。
- A2/A3で参照する ContractID / InterfaceName が一致することを確認。

### Proceed

- A2へ引き渡す固定契約として `CTR-2A-01-ISLAND-HIERARCHY-V1` を採用し、A1を完了状態とする。

## Acceptance criteria

- [x] A1で ContractID / Required fields / Invariants / ContractLinks が固定される。
- [x] A2/A3は本契約を変更せず参照のみで進行できる。
- [x] `02_Architecture/schemas.md` と整合する（`parentIslandId` 正本、root未設定許容）。
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
  - `ContractID=CTR-2A-01-ISLAND-HIERARCHY-V1`
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

- self-correction上限: 3回。連続失敗時はProceed禁止で停止。
- 停止トリガ: Ready条件崩壊 / 依存逆転 / 未定義競合 / ContractID衝突を検出した場合は即時停止して報告。

## Decision Queue整理（Stream D）

| QueueID | Topic | Status | Decision | Proceed Impact |
|---|---|---|---|---|
| DQ-FB-P2A-01-001 | ContractID固定 (`CTR-2A-01-ISLAND-HIERARCHY-V1`) | Closed | A1で固定 | A2可 |
| DQ-FB-P2A-01-002 | A2/A3で契約変更禁止 | Closed | 逸脱はA1差し戻し | A3可 |
| DQ-FB-P2A-01-003 | `parentIslandId` 正本維持 | Closed | `childIslandIds` を必須契約から除外 | A2/A3可 |
| DQ-FB-P2A-01-004 | SafeMode後退禁止の適用確認 | Closed | 契約境界で後退禁止 | A2/A3可 |

## Proceed判定（A2/A3）

- 可否: **可**
- 根拠: ContractIDと必須フィールドが固定、Decision Queueの未処理項目なし。
- 残リスク: 派生子一覧の表現方式はA3検討対象だが、A1契約変更なしで扱う。

## Stream D固定シグネチャ / 検証キー（A2/A3引き渡し）

- Fixed signature:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Verification keys:
  - `contractId`
  - `contractVersion`（`IslandHierarchyContractV1`）
  - 必須フィールド一覧
- Rule:
  - A2/A3は上記キーの一致確認のみ実施し、契約本文は改訂しない。
