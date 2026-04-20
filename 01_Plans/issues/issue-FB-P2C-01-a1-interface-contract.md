# Issue Draft: FB-P2C-01 A1 interface contract freeze（Stream B）

- Type: Feature request
- Status: Open（A1 contract freeze active）
- Source Issue: N/A
- Priority: P0
- Owner: Stream B（FB-P0 baseline / FB-P2C-A1 契約固定専任）
- Scope: `FB-P2C-01 A1` の契約固定（Contract ID / Signature / Deterministic Rule）
- Editable files (hard lock):
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
- Prohibited edits: 上記以外すべて（実装コード・共有統合ファイルを含む）
- Related Backlog: `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`
- Expected verification level: `docs-check`

---

## Requirement meta I/F

- RequirementID: `RQ-2C-02`
- RequirementStatement: Polygon auto-fit のA1契約を固定し、A2/A3へ read-only handoff する。
- PriorityClass: Must
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: `DQ-FB-P2C-01`（GateDecision: approved）

---

## Phase 1) Read（Status/Priority/Scope/Related ADR 再確認）

### Plan
- P0契約タスクとしての境界妥当性を確認する。

### Execute
- `Status=P0契約固定進行中`、`Priority=P0`、`Scope=契約固定のみ` を確認。
- Related ADR は `ADR-0001/0007` を参照し、契約固定以外（実装設計）は対象外とする。

### Verify
- 契約固定タスクの境界が明確。

### Proceed
- Phase 2へ進行。

---

## Phase 2) Plan（A1契約固定）

### Plan
- A1契約を signature/型/順序規則として固定する。

### Execute
- Contract ID: `CTR-FB-P2C-01-A1-TIEBREAK-V1`
- Signature:
  - `PolygonAutoFitContract.v1(input) -> output`
- Type definition:
  - `input`:
    - `inputHash: string`
    - `seed: string`
    - `candidatePolygonHash: string`
    - `paddingViolationCount: number`
  - `output`:
    - `outputPolygonHash: string`
    - `appliedTieBreakOrder: string`
- Deterministic Rule:
  - `padding > self_intersection > area_delta > vertex_count`
- MutationPolicy:
  - `read-only`（A2/A3は契約値を変更しない）
- Dependency cut:
  - 下流実装依存は fixture/stub を前提に切断し、実装方式は契約対象外とする。

### Verify
- 契約固定3要素（ID/Signature/Rule）が明示されている。
- 型はI/F境界に限定され、実装仕様を含まない。

### Proceed
- Phase 3へ進行。

---

## Phase 3) Execute（A2/A3 read-only handoff）

### Plan
- A2/A3に渡す情報を最小契約に固定する。

### Execute
- Handoff snapshot:
  - `SnapshotID=SNAP-FB-P2C-A1-CTR-V1`
  - `ContractID=CTR-FB-P2C-01-A1-TIEBREAK-V1`
  - `Signature=PolygonAutoFitContract.v1(input)->output`
  - `DeterministicRule=padding>self_intersection>area_delta>vertex_count`
  - `MutationPolicy=read-only`
  - `Consumers=A2,A3`
- 下流越境禁止:
  - アルゴリズム記述
  - 内部実装データ構造
  - 性能最適化仕様

### Verify
- A2/A3向け情報が契約最小セットのみで構成される。

### Proceed
- Phase 4へ進行。

---

## Phase 4) Verify（AC/DoD・語彙統一・競合確認）

### AC/DoD
1. Contract ID が一意固定されている。
2. Signature が単一固定されている。
3. Deterministic Rule が固定順序で明示されている。
4. MutationPolicy が read-only である。
5. 編集境界外差分が 0 件である。

### Vocabulary
- 固定語彙: `Contract ID`, `Signature`, `Deterministic Rule`, `MutationPolicy`, `read-only handoff`。

### Conflict check
- 編集許可外ファイルの差分なし。

### Self-repair policy
- 検証失敗時は最大3回まで自己修正し、4回目相当で停止。

### Proceed
- Phase 5へ進行。

---

## Phase 5) Proceed（Go/No-Go）

### Go
- AC/DoD 1〜5 を満たし、A2/A3 handoff の契約最小セットが固定済み。

### No-Go
1. 契約競合
2. 未承認確定
3. 自己修正3回超過
4. 指定外ファイル差分

### Pending（保留のまま維持）
- 実装アルゴリズム選定
- 実行時最適化
- 下流テスト詳細

> Pending は本A1契約固定の範囲外のため未確定のまま保持する。

---

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - `ok: validated <N> active issue memos`
