# Issue Draft: FB-P2A-01-A1 Island階層モデル導入 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Closed (Stream A serial phase complete: A1 fixed on 2026-04-18)
- Priority: P0
- Owner: Stream A（Critical Path / FB-P2A planning memo exclusive）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: none（A1 contract root）
- Unblocks: `issue-FB-P2A-01-a2-mock-validation.md` / `issue-FB-P2A-01-a3-implementation.md`
- Gate/Blocker: Ready when ContractID・Required fields・Invariants・ContractLinks・Local Contract Annex are Fixed; Blocked when contract drift or `DecisionStatus=Pending`.

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: `Island階層モデル導入` の境界I/F（型・必須項目・契約リンク）を先行固定し、A2/A3参照専用の Local Contract Annex を確立する。
- Phase: `A1 Interface First`
- PriorityClass（Must / Should / Could）: Must
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed

## Local Contract Annex（Stream A SSOT）

> 以降A2/A3は外部I/Fを直接参照せず、本Annexを唯一の参照源（SSOT）として使用する。

### Annex identifier
- AnnexID: `LCA-FB-P2A-01-A1-V1`
- ContractID: `CTR-2A-01-ISLAND-HIERARCHY-V1`
- InterfaceName: `IslandHierarchyContractV1`

### External I/F mapping（A1内で写像済み）

- Source reference（read-only origin）:
  - `02_Architecture/schemas.md` の `parentIslandId?: string` 制約
- Annex mapping（A2/A3が利用する値）:
  - `document.schemaVersion: string`
  - `island.id: string`
  - `island.cardIds: string[]`
  - `island.parentIslandId?: string`（rootは未設定許容）

### Invariants

1. `parentIslandId` が存在する場合、参照先 island は同一 document 内に存在する。
2. `parentIslandId` のみを正本とし、子一覧は派生情報として契約必須項目へ含めない。
3. self-parent を含む循環参照は許可しない。
4. import 正規化では不正な `parentIslandId` を `undefined` にフォールバックできる。
5. save/load roundtrip では有効な `parentIslandId` を欠落させず往復保持する。

### Contract links
- Downstream-A2: `issue-FB-P2A-01-a2-mock-validation.md`（Annex参照のみ）
- Downstream-A3: `issue-FB-P2A-01-a3-implementation.md`（Annex参照のみ）

## Phase management（Stream A / FB-P2A serial lock）

## Phase 3 Plan result（agreement record）

- agreementStatus: `agreed`
- agreedAt: `2026-04-18`
- Agreement scope: AC/DoD gaps are closed and Stream A serial order (`A1 -> A2 -> A3`) is locked.
- Note: no undefined conflict found; no external lane file edits required.

## Phase 4 Execute result（strict serial）

1. A1: `ContractID / Required fields / Invariants / ContractLinks` fixed（done）
2. A2: mock ledger (`M1..M4`) fixed under A1 Annex freeze（done）
3. A3: implementation handoff contract and rollback conditions fixed（done）

## Phase 5 Verify result

- docs-check target: `01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- verificationFocus: AC/DoD consistency, dependency alignment, contract drift absence
- selfCorrectionCount: `0/3`（no retry needed）

## Phase 6 Proceed decision

- proceedDecision: `ready-to-transition`
- nextStatusProposal: `FB-P2A-01 planning serial complete (Stream A)`
- stopConditionCheck: clear（no blocker）


- Phase 1 Read: A1/A2/A3 3点を再読し、Status/AC/DoD/依存を抽出する。
- Phase 2 ADR CDC: 方針変更がある場合のみ CDC を起票し、承認記録完了まで停止する。
- Phase 3 Plan: AC/DoD不足ドラフトを作成し、`agreementStatus=agreed` まで進行しない。
- Phase 4 Execute: A1契約固定 → A2 mock検証 → A3実装計画確定を直列実行する。
- Phase 5 Verify: docs-check + 契約リンク整合 + 自己修復上限3回を確認する。
- Phase 6 Proceed: 完了条件を満たす場合のみ次ステータス提案、未達時は停止レポートを残す。

## Phase 1 Read result（差分抽出）

### 抽出（Status/AC/DoD/依存）
- Status: A1/A2/A3 いずれも Open（Audit Hold系）
- AC: 3ファイルとも契約固定・直列実行・GoNoGo明記あり
- DoD: 明示不足（A1はDoD見出し未定義、A2/A3もDoD節が不足）
- 依存: A1 -> A2 -> A3 の直列依存は定義済み

### 事前想定との差分
1. Ownerが Stream B 表記で、今回指示の Stream A 専属条件と不一致。
2. A1/A2/A3が外部I/F（例: architecture配下）を直接参照しうる記述が残っていた。
3. DoDの明文化が不足し、完了判定がAC中心に偏っていた。

## Phase 2 ADR CDC（判定）

- 判定: **起票不要（No ADR proposal）**
- Context: 既存方針の運用明確化であり、新規アーキテクチャ決定は含まない。
- Decision: A1に Local Contract Annex を追加し、A2/A3はAnnex参照限定とする。
- Consequences: 外部ストリーム非依存でA1→A2→A3の直列進行が可能。

## Acceptance criteria

- [x] ContractID / Required fields / Invariants / ContractLinks が固定される。
- [x] Local Contract Annex（`LCA-FB-P2A-01-A1-V1`）をA2/A3の唯一参照源として定義する。
- [x] A2/A3はA1契約本文を変更せず参照のみで進行できる。
- [x] SafeMode・share/export既定挙動に影響しないことを明記する。
- [x] A1→A2→A3の契約リンク不整合がない。

## Definition of Done (DoD)

- [x] `DecisionStatus=Fixed` と `AnnexID` が同時に記録されている。
- [x] A2/A3が参照する契約値（ContractID / InterfaceName / Invariants）がA1内で一意に取得できる。
- [x] 外部I/F参照はA1の External I/F mapping に写像済みで、A2/A3本文から直接参照されない。
- [x] docs-check 実行計画とFail-safe（self-correction<=3）が記録されている。

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。
- 停止トリガ: 3回超過 / 契約ドリフト / 未定義競合 / 前提崩壊 / 指定外ファイル編集要求。
- 停止時対応: 推測継続を禁止し、停止理由・再開条件・未達項目を記録する。

## Handoff（A2/A3参照専用）

- Fixed links:
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`
- 変更禁止項目:
  - `AnnexID=LCA-FB-P2A-01-A1-V1`
  - `ContractID=CTR-2A-01-ISLAND-HIERARCHY-V1`
  - `InterfaceName=IslandHierarchyContractV1`
  - Required fields / Invariants / ContractLinks
- 逸脱要求はA1へ差し戻し。
