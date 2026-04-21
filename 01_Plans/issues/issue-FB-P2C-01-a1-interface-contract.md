# Issue Draft: FB-P2C-01 A1 interface contract freeze（Stream A critical path）

- Type: Feature request
- Status: Open（A1 contract freeze active）
- Priority: P0
- Owner: Stream A（Critical Path）
- Scope: A1最小I/F契約の固定（Contract ID / Signature / Deterministic Rule）
- Editable files: 対象7Issueのみ
- Related ADR/Spec: `ADR-0001`, `ADR-0026`, `ADR-0027`
- Verification level: `docs-check`

---

## Phase 1: Read
- Status: `Open`
- Priority: `P0`
- Scope: A1契約固定のみ
- Related ADR/Spec: `ADR-0001/0026/0027`
- Delta log: 既存の契約3点は有効。Stream B表記をStream A運用へ補正。

## Phase 2: ADR Consensus

### Context
- A1はA2/A3の開始可否を決める唯一ゲートであり、契約値の多重正本化を防止する必要がある。

### Decision
- Contract ID: `CTR-FB-P2C-01-A1-TIEBREAK-V1`
- Signature: `PolygonAutoFitContract.v1(input) -> output`
- Type:
  - input: `inputHash:string`, `seed:string`, `candidatePolygonHash:string`, `paddingViolationCount:number`
  - output: `outputPolygonHash:string`, `appliedTieBreakOrder:string`
- Deterministic Rule: `padding > self_intersection > area_delta > vertex_count`
- MutationPolicy: `read-only`

### Consequences
- A2/A3は契約変更禁止（参照のみ）。
- 下流実装仕様は本Issueで確定しない。

### held
- 実装アルゴリズム詳細、最適化詳細、下流テスト詳細は `held`。

## Phase 3: Plan
### AC
1. Contract ID固定。
2. Signature単一表記。
3. Deterministic Rule固定順序。
4. MutationPolicy=read-only。

### DoD
1. handoff最小セットのみ。
2. 指定外ファイル差分0。

## Phase 4: Execute
- Handoff snapshot（read-only）:
  - `SnapshotID=SNAP-FB-P2C-A1-CTR-V1`
  - `ContractID=CTR-FB-P2C-01-A1-TIEBREAK-V1`
  - `Signature=PolygonAutoFitContract.v1(input)->output`
  - `DeterministicRule=padding>self_intersection>area_delta>vertex_count`
  - `MutationPolicy=read-only`

## Phase 5: Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `git diff --check`

## Phase 6: Proceed / Stop
- Proceed: AC/DoD全充足。
- Stop: 未承認確定、契約競合、self-correction 3回超過、指定外差分。
