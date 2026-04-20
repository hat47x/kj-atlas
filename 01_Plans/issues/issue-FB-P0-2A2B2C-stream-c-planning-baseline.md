# Issue Draft: FB-P0 (2A/2B/2C) Stream C planning baseline

- Type: Process
- Status: Open (Contract Freeze in progress)
- Source Issue: N/A
- Priority: P0
- Owner: Stream C（FB Stream F lock lane 専任）
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

- 目的: **FB-P0 baseline と FB-P2C A1契約のみを freeze** し、A2/A3が外部待ちなし・mock前提で進行できる引き渡し仕様を固定する。
- 非目標:
  - `03_Implement/**` の変更
  - 他Issue・共有統合ファイルの変更
  - 外部ストリーム待ちでの進行停止
- tie-break契約ガード:
  - 決定論順序の変更禁止
  - A2/A3はA1契約を **read-only参照**
- フェイルセーフ:
  - `Plan → Execute → Verify → Proceed` を全Phaseで適用
  - Verify自己修復は最大3回
  - **未承認確定 / 契約競合 / 自己修復3回超過 / 指定外ファイル差分発生** で即停止

---

## Phase 1) Read（依存・優先度確認）

### Plan
- 編集境界（2ファイルのみ）とPhase順序を固定する。
- A1契約の評価観点（Contract ID / Required fields / Invariants / Handoff）を確認する。

### Execute
- 編集許可ファイルが2件のみであることを確認。
- 実行順序を `Read → Plan(I/F固定) → ADR CDC(必要時) → Execute(mock前提) → Verify/Proceed` に固定。

### Verify
- 指定外ファイル差分なし。
- Phase順序の逆転なし。

### Proceed
- Phase 2へ進行。

---

## Phase 2) Plan（I/F固定）

### Plan
- Stream Cが固定する契約境界（A1 tie-break契約・A2/A3 read-only導線）を定義する。
- AC/DoDが不足する場合のドラフト提案を先に作成する。

### Execute
- Scope固定: **FB-P0 baseline + FB-P2C-01 A1契約のみ**。
- Non-goal固定: 実装着手・他ストリーム依存・未承認項目のFixed化を禁止。
- AC/DoDドラフト（不足時提案）:
  1. A1 Contract ID が一意固定されている。
  2. tie-break順序が機械可読で固定されている。
  3. A2/A3 handoffがread-onlyで固定されている。
  4. 停止条件が文書化されている。

### Verify
- Scope/Non-goalとA1契約の整合が取れている。
- AC/DoDドラフトが検証可能な文言になっている。

### Proceed
- Phase 3へ進行。

---

## Phase 3) ADR CDC（必要時のみ）

### Plan
- A1契約が既存ADR/Specと衝突する場合のみCDC更新を行う。

### Execute
- 衝突なしの場合: `CDC変更不要` を明示。
- 衝突ありの場合: Context / Decision / Consequences を最小差分で補強。

### Verify
- CDC要素欠落なし。
- Contract ID衝突なし。

### Proceed
- Phase 4へ進行。

---

## Phase 4) Execute（mock前提）

### Plan
- A2/A3が外部依存なしで開始できる最低限I/Fを固定する。

### Execute
- Handoff最小セット:
  - `ReferenceContractID`: `CTR-FB-P2C-01-A1-TIEBREAK-V1`
  - `MockInterface`: `PolygonAutoFitStub.v1`
  - `DeterministicOrder`: `padding>self_intersection>area_delta>vertex_count`
  - `ReplayKeys`: `inputHash`, `seed`, `outputPolygonHash`, `paddingViolationCount`, `appliedTieBreakOrder`
- A2条件（mock-validation）:
  - 同一 `inputHash + seed` で同一 `outputPolygonHash` を再現。
- A3条件（implementation-ready contract）:
  - A1順序・ReplayKeys・停止条件をread-only参照（契約値変更禁止）。

### Verify
- mock前提でA2/A3開始可。
- 実装詳細への依存持ち込みなし。

### Proceed
- Phase 5へ進行。

---

## Phase 5) Verify / Proceed（下流へread-only handoff）

### Final checks

| 観点 | 判定 | 備考 |
| --- | --- | --- |
| 編集境界（2ファイルのみ） | Pass | Stream C lock lane遵守 |
| Scope/Non-goal固定 | Pass | baseline凍結完了 |
| A1契約（CDC/承認） | Pass | Contract ID + Gate明記 |
| A2/A3引き渡し（mock前提） | Pass | read-only handoff固定 |
| フェイルセーフ | Pass | 未承認/競合/3回超過/指定外差分で停止 |

### Proceed decision
- **Proceed = 可（条件付き）**
  - 条件: A2/A3はA1契約をread-only参照し、契約変更要求はA1へ差し戻す。
- **Stop条件（再掲）**
  1. 未承認確定
  2. 契約競合
  3. Verify自己修復3回超過
  4. 指定外ファイル差分発生

---

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - `ok: validated <N> active issue memos`
