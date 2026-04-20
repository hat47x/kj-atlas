# Issue Draft: FB-P2C-01-A1 Polygon auto-fit / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (A1 contract freeze for Stream C lock lane)
- Source Issue: N/A
- Priority: P0
- Owner: Stream C（FB Stream F lock lane 専任）
- Scope: `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md` のみ
- Related Backlog: `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`
- Expected verification level: `docs-check`

## Stream C execution boundary（hard lock）

- Editable files:
  - `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `issue-FB-P2C-01-a1-interface-contract.md`
- Prohibited edits: 上記以外すべて（FB-P2A / HIL / CE / 共有統合ファイル / 実装コードを含む）。
- Fixed phase order:
  1) Phase 1 Read（依存・優先度確認）
  2) Phase 2 Plan（I/F固定）
  3) Phase 3 ADR CDC（必要時のみ）
  4) Phase 4 Execute（mock前提）
  5) Phase 5 Verify/Proceed（下流へread-only handoff）
- Dependency cut policy:
  - 外部ストリーム待ち禁止。
  - 必要I/Fは本Issue内でfreezeし、mock可能形を出力。
- Fail-safe:
  - 全Phaseで `Plan → Execute → Verify → Proceed` を適用。
  - Verify自己修復は最大3回。
  - **未承認確定 / 契約競合 / 3回超過 / 指定外ファイル差分発生** で即停止。

---

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2C-02`
- RequirementStatement: `Polygon auto-fit` をインターフェース先行（型/契約）で固定し、A2/A3へ安全に引き渡す。
- PriorityClass: Must
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: `DQ-FB-P2C-01`（GateDecision: approved）

---

## Phase 1) Read

### Plan
- A1契約の単一正本化とA2/A3 read-only導線を確認する。

### Execute
- 既存契約の必須要素（Contract ID / tie-break順序 / Required fields / Invariants）を読み取り固定。

### Verify
- 必須要素の欠落なし。

### Proceed
- Phase 2へ進行。

---

## Phase 2) Plan（I/F固定）

### Plan
- A1契約の固定値を明文化し、AC/DoD不足時のドラフト提案を行う。

### Execute
- AC/DoDドラフト（不足時提案）:
  1. Contract ID 一意固定。
  2. tie-break順序固定。
  3. Required fields / Invariants 固定。
  4. A2/A3 read-only handoff固定。
- A1契約境界（A2/A3参照専用）:
  - `ReferenceContractID=CTR-FB-P2C-01-A1-TIEBREAK-V1`
  - `DeterministicOrder=padding>self_intersection>area_delta>vertex_count`
  - `ReplayKeys=inputHash,seed,outputPolygonHash,paddingViolationCount,appliedTieBreakOrder`
  - `MutationPolicy=prohibited`（A2/A3での契約値変更禁止）

### Verify
- AC/DoDが検証可能で曖昧語を含まない。

### Proceed
- Phase 3へ進行。

---

## Phase 3) ADR CDC（必要時のみ）

### Plan
- 契約が既存ADRと衝突する場合のみCDC補強を行う。

### Execute
- 衝突なし: `CDC変更不要` を明記。
- 衝突あり: Context / Decision / Consequences を最小差分で記録。

### Verify
- CDC欠落なし。

### Proceed
- Phase 4へ進行。

---

## A1 Contract freeze（CDC本体）

### Context
- `FB-P2C-01` のDoD「同一入力で同一polygon」を満たすには、tie-break順序の非決定性排除が必要。
- A2/A3はA1契約を単一正本としてread-only参照し、契約値変更を行わない必要がある。

### Decision
- Contract ID: `CTR-FB-P2C-01-A1-TIEBREAK-V1`
- Deterministic tie-break order（機械可読）:
  - `padding>self_intersection>area_delta>vertex_count`
- Required fields:
  - `inputHash`
  - `seed`
  - `outputPolygonHash`
  - `paddingViolationCount`
  - `appliedTieBreakOrder`
- Invariants:
  1. 同一 `inputHash + seed` で同一 `outputPolygonHash`。
  2. `appliedTieBreakOrder` は固定順序と完全一致。
  3. `paddingViolationCount == 0` を必須。
- Must-not:
  - A2/A3による順序入替・項目追加・項目削除。
  - 未承認状態での契約更新。

### Consequences
- A2はmock-validationを外部待ちなしで進行できる。
- A3はimplementation-ready判定を契約準拠で実施できる。
- 契約変更要求はA1へ差し戻し、直接更新を禁止する。

---

## Approval record（A1 Gate）

- GateDecision: `approved`
- Approval basis: `DQ-FB-P2C-01`（deterministic tie-break order 承認）
- Effective mode: `A2/A3 read-only reference`

---

## Phase 4) Execute（mock-first handoff）

### Plan
- A2/A3が実装前に検証可能な最小I/Fを固定する。

### Execute
#### A2 mock-validation handoff
- ReferenceContractID: `CTR-FB-P2C-01-A1-TIEBREAK-V1`
- Mock I/F: `PolygonAutoFitStub.v1`
- Stub schema:
  - input: `islandId`, `targetCardIds[]`, `padding`, `seed`
  - output: `polygon`, `vertexCount`, `areaDelta`, `appliedTieBreakOrder`, `outputPolygonHash`, `paddingViolationCount`
- Pass criteria:
  - 同一入力同一ハッシュ再現
  - tie-break順序一致
  - `paddingViolationCount == 0`

#### A3 implementation-ready handoff
- ReferenceContractID: `CTR-FB-P2C-01-A1-TIEBREAK-V1`（read-only）
- Implementation constraints:
  - A1の`Required fields`と`Invariants`を変更しない。
  - 逸脱検知時は実装継続せずA1へ差し戻し。
- Stop triggers:
  1. tie-break順序不一致
  2. `paddingViolationCount > 0`
  3. `outputPolygonHash` の非決定的変動

### Verify
- mock-first条件でA2/A3開始可。
- 契約更新を伴わずに検証可能。
- 決定論順序の変更はStop triggerとしてA1差し戻し対象。

### Proceed
- Phase 5へ進行。

---

## Phase 5) Verify / Proceed

### Verify checklist
- [x] Contract ID 固定
- [x] CDC（Context/Decision/Consequences）固定
- [x] 承認状態（GateDecision=approved）明示
- [x] A2/A3 handoff（mock-first, read-only）固定
- [x] フェイルセーフ停止条件明示

### Proceed
- **A2 Proceed: 可（mock-validationのみ）**
- **A3 Proceed: 可（implementation-ready contract参照のみ）**
- 契約更新要求はA1差し戻しのみ可。

---

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - `ok: validated <N> active issue memos`
