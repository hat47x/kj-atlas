# Issue Draft: FB-P0 (2A/2B/2C) Stream C planning baseline

- Type: Process
- Status: Active (Stream D planning orchestrator)
- Source Issue: N/A
- Priority: P0
- Owner: Stream D（FB-P2C-A3 + backend接続準備）
- Scope: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`, `02_Architecture/island_shapes.md`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

---

## Phase 1: Read Gate

### Plan
- Gate 0承認、A2 Verify pass、契約順序固定の有無を再確認する。
- Gate未承認・契約矛盾・競合検出時の即停止条件を先に固定する。

### Execute

| チェック項目 | 入力ソース | 判定 | 備考 |
| --- | --- | --- | --- |
| Gate 0承認 | `DQ-FB-P2C-01` | Pass | `approved` を確認 |
| A2 Verify | `A2-HANDOFF-FB-P2C-01-2026-03-14` | Pass | `verify=pass` を確認 |
| 契約順序固定 | A1/A2/A3 memo | Pass | tie-break順序の差分なし |
| 競合有無 | 編集境界定義 | Pass | 許可2ファイルのみ更新 |

### Verify
- Proceed 条件（Gate承認 + A2 pass + 契約順序固定）を満たす。
- Stop 条件（Gate未承認・契約矛盾・競合）には非該当。

### Proceed
- Phase 2（契約順序固定）へ進行。

---

## Phase 2: 契約順序固定

### Plan
- tie-break順序と禁止変更を固定し、例外条件のみADR承認待ちへ分離する。

### Execute
- 固定順序（変更禁止）:
  1. `padding遵守`
  2. `自己交差回避`
  3. `面積最小変動`
  4. `頂点数最小`
- 禁止変更:
  - 順序の追加
  - 順序の省略
  - 順序の並べ替え
- ADR移行条件（必要時のみ）:
  - 変更要求が上記禁止変更に該当した場合、`Context / Decision / Consequences` を備えたADR草案で承認待ちに遷移。

### Verify
- A1/A2契約と矛盾しない（Pass）。
- 新規上位方針の導入なし（Pass）。

### Proceed
- Phase 3（backend接続条件の分離）へ進行。

---

## Phase 3: backend接続条件の分離

### Plan
- API/Schema依存のみを明文化し、実装方式依存を排除した引き渡し境界を確定する。

### Execute

| 区分 | 依存先 | 必須キー | 用途 |
| --- | --- | --- | --- |
| API入力契約 | `02_Architecture/api.md` | `DocumentV1`, `inputHash` | 実装レーン入力の同一性保証 |
| Schema出力契約 | `02_Architecture/schemas.md` | `outputPolygonHash`, `paddingViolationCount` | A2比較キーとの照合 |
| 形状契約 | `02_Architecture/island_shapes.md` | `deterministicTieBreakOrder` | 決定順序の固定検証 |

- 分離原則:
  - 実装言語/ライブラリ/アルゴリズム詳細は別レーン責務。
  - 本レーンは契約キーの整合保証のみを担当。

### Verify
- 契約定義が architecture 参照のみで完結（Pass）。
- `03_Implement/**` 依存なし（Pass）。

### Proceed
- Phase 4（実装レーン引き渡し）へ進行。

---

## Phase 4: 実装レーン引き渡し

### Plan
- 入力契約/期待出力/失敗時ロールバックをテンプレ化し、実装レーンへ非曖昧に渡す。

### Execute
- **Input Contract Template**
  - `gateApprovalRef`
  - `a2VerifyRef`
  - `inputHash`
  - `deterministicTieBreakOrder`
- **Expected Output Template**
  - `outputPolygonHash`（同一入力同一出力）
  - `paddingViolationCount == 0`
  - `tieBreakOrderChanged == false`
- **Rollback Template**
  - Trigger: `outputPolygonHash不一致` / `paddingViolationCount>0` / `tieBreakOrderChanged=true`
  - Action: 実装停止 → A2比較キー再検証 → A2差戻し

### Verify
- テンプレが A3開始条件・停止条件を網羅（Pass）。
- 実装レーンが追加解釈なしで着手可能（Pass）。

### Proceed
- Stream D baseline を固定し、実装レーンへハンドオフする。

---

## ADRルール適用記録

- 判定: **ADR変更不要**。
- 理由: 本更新は既存契約の固定と引き渡し手順の明文化であり、上位設計の新規決定を追加していない。
- 追跡: 契約順序の変更要求が発生した場合のみ ADR 起票（Context/Decision/Consequences）を実施。

## Self-Correction Log（最大3回）

1. 修正1: Phase構成をユーザー指定の4段へ再編。
2. 修正2: backend接続条件を API/Schema依存のみに限定。
3. 修正3: Stop条件（Gate未承認・契約矛盾・競合検出）を明文化。

> 上限超過時停止ルール: Self-Correction が 3 回を超える場合は更新を停止し、競合一覧を提出する。
