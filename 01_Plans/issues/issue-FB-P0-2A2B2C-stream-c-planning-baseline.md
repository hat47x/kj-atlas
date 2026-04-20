# Issue Draft: FB-P0 (2A/2B/2C) Stream C planning baseline

- Type: Process
- Status: Open (Audit Hold: Stream C contract freeze pending A1 mock gate re-confirmation)
- Source Issue: N/A
- Priority: P0
- Owner: Stream C（FB-P0 baseline + FB-P2C A1契約固定のみ）
- Scope: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ
- Editable files (hard lock):
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
- Non-editable files: 上記以外すべて（FB-P2A / HIL / CE / 共有統合ファイル / 実装コードを含む）
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`
- Expected verification level: `docs-check`

---

## Baseline objective（Stream C）

- 目的: **FB-P0 baseline と FB-P2C A1契約のみをfreeze** し、A2/A3が外部待ちなしでmock前提進行できる引き渡し仕様を固定する。
- 非目標:
  - `03_Implement/**` の変更
  - 他Issue・共有統合ファイルの変更
  - 他ストリーム判断待ちでの進行停止（依存切断方針に反する）
- 依存切断原則:
  - 外部ストリーム待ち禁止。
  - 必要I/Fは本ストリームで固定し、mock可能な形で出力する。
- フェイルセーフ:
  - **Plan → Execute → Verify → Proceed** を順守し、Verify自己修復は最大3回。
  - 未承認確定 / 契約競合 / Verify自己修復3回超過 / 前提崩壊で致命停止。

---

## Phase 1) Read（Audit Hold理由の再確認）

### Plan
- Audit Hold理由を2ファイルで再確認し、解除に必要な不足情報を特定する。

### Execute
- Hold理由A（本ファイル）: A1 mock gate の再確認待ち。
- Hold理由B（A1契約ファイル）: 契約freezeは済みだが Go/NoGo 条件の機械可読化が未明確。

### Verify
- 2ファイル双方でHold理由を明示。
- 相互参照で理由の不整合がない。

### Proceed
- Phase 2へ進行。

---

## Phase 2) Mock Contract（A1契約ID / Go-NoGo固定）

### Plan
- A1契約をモック前提で固定し、Go/NoGo条件を判定可能な形式で記述する。

### Execute
- 固定値:
  - `ReferenceContractID`: `CTR-FB-P2C-01-A1-TIEBREAK-V1`
  - `MockInterface`: `PolygonAutoFitStub.v1`
  - `DeterministicOrder`: `padding>self_intersection>area_delta>vertex_count`
  - `ReplayKeys`: `inputHash`, `seed`, `outputPolygonHash`, `paddingViolationCount`, `appliedTieBreakOrder`
- Go条件（全件満たす）:
  1. `outputPolygonHash` が同一入力で再現
  2. `appliedTieBreakOrder` が固定順序と一致
  3. `paddingViolationCount == 0`
- NoGo条件（1件でも該当）:
  1. tie-break順序不一致
  2. `paddingViolationCount > 0`
  3. 非決定的な `outputPolygonHash` 変動

### Verify
- ContractID / Go / NoGo がA1契約ファイルと一致。

### Proceed
- Phase 3へ進行。

---

## Phase 3) ADR CDC（変更要否を明文化）

### Plan
- 既存ADR/Specとの差分有無を判定し、変更要否を明文化して承認待ち状態を定義する。

### Execute
- 判定: **ADR本文変更は不要**（A1契約は既存 `ADR-0001`, `ADR-0007`, `ADR-0019` と整合）。
- CDC記録:
  - Context: 決定論要件をA1契約で具体化する必要。
  - Decision: ContractID/Go-NoGoをissue内で固定。
  - Consequences: A2/A3はread-only参照で着手、契約変更はA1差し戻し。
- 承認待ちフラグ:
  - `CDCApprovalState: pending_review`
  - `CDCApprovalQueue: DQ-FB-P2C-01`

### Verify
- CDC三要素が欠落しない。
- 変更不要判定と承認待ちフラグを同時明示。

### Proceed
- Phase 4へ進行。

---

## Phase 4) Plan→Execute→Verify（AC/DoD機械可読化）

### Acceptance Criteria（machine-readable）

```yaml
acceptance_criteria:
  - id: AC-C1
    description: ContractID fixed and referenced by A2/A3
    check: "ReferenceContractID == 'CTR-FB-P2C-01-A1-TIEBREAK-V1'"
  - id: AC-C2
    description: Deterministic tie-break order fixed
    check: "DeterministicOrder == 'padding>self_intersection>area_delta>vertex_count'"
  - id: AC-C3
    description: Replay keys complete
    check: "ReplayKeys contains [inputHash, seed, outputPolygonHash, paddingViolationCount, appliedTieBreakOrder]"
  - id: AC-C4
    description: Go/NoGo conditions encoded
    check: "GoConditions and NoGoConditions are explicitly listed"
```

### Definition of Done（machine-readable）

```yaml
dod:
  docs_updated: true
  cross_file_consistency: true
  audit_hold_release_gate:
    condition: "all_acceptance_criteria_pass && CDCApprovalState != rejected"
    state: conditional_release_ready
```

### Verify
- AC/DoDをテキスト比較で検証可能。
- hold解除判定が機械可読化されている。

### Proceed
- Phase 5へ進行。

---

## Phase 5) Proceed（1行ルール）

- **解除条件が満たされた場合のみ次工程開始。**

---

## Final checks

| 観点 | 判定 | 備考 |
| --- | --- | --- |
| 編集境界（2ファイルのみ） | Pass | Stream C独立性を維持 |
| Audit Hold理由再確認 | Pass | 2ファイルで整合 |
| A1契約ID/Go-NoGo固定 | Pass | モック前提で凍結 |
| CDC変更要否 + 承認待ち明示 | Pass | pending_review を明記 |
| AC/DoD機械可読化 | Pass | hold解除判定を明文化 |
| フェイルセーフ | Pass | 3回失敗・競合・前提崩壊で停止 |

## Proceed decision
- **Proceed = 条件付き可**
  - 条件: `all_acceptance_criteria_pass` かつ `CDCApprovalState != rejected`。
- **Stop条件（再掲）**
  1. 未承認確定
  2. 契約競合
  3. Verify自己修復3回超過
  4. 前提崩壊

---

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - `ok: validated <N> active issue memos`
