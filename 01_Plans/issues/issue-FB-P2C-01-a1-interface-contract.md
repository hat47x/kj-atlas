# Issue Draft: FB-P2C-01-A1 Polygon auto-fit / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (Audit Hold: A1 contract freeze for Stream F)
- Source Issue: N/A
- Priority: P0
- Owner: Stream F（FB-P2C A1契約固定のみ）
- Scope: `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md` のみ
- Related Backlog: `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`
- Expected verification level: `docs-check`

## Stream F execution boundary（hard lock）

- Editable files:
  - `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `issue-FB-P2C-01-a1-interface-contract.md`
- Prohibited edits: 上記以外すべて（FB-P2A / HIL / CE / 共有統合ファイル / 実装コードを含む）。
- Fixed phase order:
  1) Phase 1 Read（依存・優先度確認）
  2) Phase 2 Plan（I/F固定）
  3) Phase 3 ADR CDC（必要時のみ）
  4) Phase 4 Execute（モック前提）
  5) Phase 5 Verify/Proceed（下流へread-only handoff）
- Dependency cut policy:
  - 外部ストリーム待ち禁止。
  - 必要I/Fは本Issue内でfreezeし、mock可能形を出力。
- Fail-safe:
  - 共通ルール `Plan → Execute → Verify → Proceed` を適用。
  - Verify自己修復は最大3回。未承認確定 / 契約競合 / 3回超過で停止。

---

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2C-02`
- RequirementStatement: `Polygon auto-fit` をインターフェース先行（型/契約）で固定し、A2/A3へ安全に引き渡す。
- PriorityClass: Must
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: `DQ-FB-P2C-01`（GateDecision: approved）

---

## A1 Contract freeze（CDC）

### Context
- `FB-P2C-01` のDoD「同一入力で同一polygon」を満たすには、tie-break順序の非決定性を排除する必要がある。
- A2/A3はA1契約を単一正本としてread-only参照し、契約値を変更しない運用が必要。

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

## Handoff spec for A2/A3（mock-first）

### A2 mock-validation handoff
- ReferenceContractID: `CTR-FB-P2C-01-A1-TIEBREAK-V1`
- Mock I/F: `PolygonAutoFitStub.v1`
- Stub schema:
  - input: `islandId`, `targetCardIds[]`, `padding`, `seed`
  - output: `polygon`, `vertexCount`, `areaDelta`, `appliedTieBreakOrder`, `outputPolygonHash`, `paddingViolationCount`
- Pass criteria:
  - 同一入力同一ハッシュ再現
  - tie-break順序一致
  - `paddingViolationCount == 0`

### A3 implementation-ready handoff
- ReferenceContractID: `CTR-FB-P2C-01-A1-TIEBREAK-V1`（read-only）
- Implementation constraints:
  - A1の`Required fields`と`Invariants`を変更しない。
  - 逸脱検知時は実装継続せずA1へ差し戻し。
- Stop triggers:
  1. tie-break順序不一致
  2. `paddingViolationCount > 0`
  3. `outputPolygonHash` の非決定的変動

---

## Verify / Proceed

- Verify checklist:
  - [x] Contract ID 固定
  - [x] CDC（Context/Decision/Consequences）固定
  - [x] 承認状態（GateDecision=approved）明示
  - [x] A2/A3 handoff（mock-first）固定
  - [x] フェイルセーフ停止条件明示

- Proceed:
  - **A2 Proceed: 可（mock-validationのみ）**
  - **A3 Proceed: 可（implementation-ready contract参照のみ）**
  - 契約更新要求はA1差し戻しのみ可。

---

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - `ok: validated <N> active issue memos`
