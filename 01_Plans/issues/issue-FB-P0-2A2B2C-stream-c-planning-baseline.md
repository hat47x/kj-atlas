# Issue Draft: FB-P0 baseline / Stream B contract-freeze lane

- Type: Process
- Status: Open（P0 contract freeze active）
- Source Issue: N/A
- Priority: P0
- Owner: Stream B（FB-P0 baseline / FB-P2C-A1 契約固定専任）
- Scope: `FB-P0 baseline` と `FB-P2C-01 A1契約固定` の文書化に限定
- Editable files (hard lock):
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
- Non-editable files: 上記以外すべて（実装コード・共有統合ファイルを含む）
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`
- Expected verification level: `docs-check`

---

## Baseline objective（Stream B / P0）

- 目的: `FB-P0 baseline` と `FB-P2C-01 A1` の **契約固定（Contract Freeze）** を行い、A2/A3へ read-only handoff する。
- 非目標:
  - `03_Implement/**` の変更
  - 他Issue・他ストリーム成果物の変更
  - 下流実装仕様（アルゴリズム詳細、内部データ構造）の記述
- 固定対象（A2/A3へ渡す最小セット）:
  1. `Contract ID`
  2. `Signature`
  3. `Deterministic Rule`

---

## Phase 1) Read（Status/Priority/Scope/Related ADR 整合チェック）

### Plan
- P0契約タスクとしての整合性を再点検する。

### Execute
- 不整合抽出:
  1. **Issue名の lane 表記** が `stream-c` だが、Owner/Boundary は Stream B 固定であり、命名と運用境界が不一致。
  2. Scope は2ファイル固定だが、本文中に下流向け実装条件へ読める記述があり、P0契約固定タスク境界を越えうる。
  3. Related ADR は妥当（`ADR-0001/0007/0019`）だが、A1契約凍結の観点では「契約固定以外を扱わない」補足が必要。

### Verify
- P0契約固定に不要な実装依存の除外方針を定義済み。

### Proceed
- Phase 2へ進行。

---

## Phase 2) Plan（A1契約固定の明文化）

### Plan
- A1契約を `signature + type + order rule` に限定して確定する。

### Execute
- Contract ID: `CTR-FB-P2C-01-A1-TIEBREAK-V1`
- Signature（契約署名）:
  - `PolygonAutoFitContract.v1(input) -> output`
- Type（契約型）:
  - `input`: `inputHash:string`, `seed:string`, `candidatePolygonHash:string`, `paddingViolationCount:number`
  - `output`: `outputPolygonHash:string`, `appliedTieBreakOrder:string`
- Deterministic Rule（固定順序）:
  - `padding > self_intersection > area_delta > vertex_count`
- Dependency cut policy:
  - 実装依存は mock I/F（fixture/stub）前提で切断し、契約値の固定以外は扱わない。

### Verify
- 契約値が検証可能な固定値である。
- 実装詳細（下流仕様）を書いていない。

### Proceed
- Phase 3へ進行。

---

## Phase 3) Execute（A2/A3 handoff内容の最小化）

### Plan
- A2/A3へ渡す情報を契約3点のみに制限する。

### Execute
- Handoff payload（read-only）:
  - `ContractID=CTR-FB-P2C-01-A1-TIEBREAK-V1`
  - `Signature=PolygonAutoFitContract.v1(input)->output`
  - `DeterministicRule=padding>self_intersection>area_delta>vertex_count`
- 明示禁止:
  - 下流実装仕様の記述
  - 項目追加/削除
  - 順序変更

### Verify
- A2/A3 handoff が `contract ID / signature / deterministic rule` のみで構成される。

### Proceed
- Phase 4へ進行。

---

## Phase 4) Verify（AC/DoD・語彙・競合確認）

### AC/DoD checks
1. A1 Contract ID が一意固定されている。
2. Signature が単一表記で固定されている。
3. Deterministic Rule が機械可読順序で固定されている。
4. A2/A3 handoff が read-only である。
5. 編集境界外ファイル差分が 0 件である。

### Terminology normalization
- 固定語彙: `Contract ID`, `Signature`, `Deterministic Rule`, `read-only handoff`。

### Conflict check
- 競合ファイル: `0`（編集許可2ファイル以外は未変更）。

### Self-repair policy
- Verify失敗時は最大3回まで自己修正し、4回目相当で停止。

### Proceed
- Phase 5へ進行。

---

## Phase 5) Proceed（Go/No-Go）

### Go condition
- AC/DoD 1〜5 をすべて満たし、契約3点セットが固定済み。

### No-Go / Stop condition
1. 未承認確定の発生
2. 契約競合の発生
3. Verify自己修正が3回を超過
4. 指定外ファイル差分の発生

### Pending（確定しない論点）
- 実装アルゴリズム詳細
- 実行時最適化戦略
- 下流テストケース詳細

> 上記 Pending は本Stream BのP0契約固定範囲外のため、ここでは確定しない。

---

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - `ok: validated <N> active issue memos`
