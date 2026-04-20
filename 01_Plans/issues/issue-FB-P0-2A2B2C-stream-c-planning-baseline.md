# Issue Draft: FB-P0 (2A/2B/2C) Stream F planning baseline

- Type: Process
- Status: Open (Audit Hold: Stream F contract freeze)
- Source Issue: N/A
- Priority: P0
- Owner: Stream F（FB-P0 baseline + FB-P2C A1契約固定のみ）
- Scope: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ
- Editable files (hard lock):
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
- Non-editable files: 上記以外すべて（FB-P2A / HIL / CE / 共有統合ファイル / 実装コードを含む）
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`
- Expected verification level: `docs-check`

---

## Baseline objective（Stream F）

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
  - 未承認確定 / 契約競合 / Verify自己修復3回超過のいずれかで致命停止。

---

## Phase 1) Read（依存・優先度確認）

### Plan
- 編集境界（2ファイルのみ）と実施Phase順序を固定する。
- P2C A1契約対象とVerify観点（ContractID / Required fields / Invariants / Handoff）を同期する。

### Execute
- 編集許可2ファイルのみ対象であることを確認。
- 実施順序を `1) Read -> 2) Plan -> 3) ADR CDC（必要時のみ） -> 4) Execute（mock前提） -> 5) Verify/Proceed` に固定。

### Verify
- 編集境界逸脱なし。
- Phase順序の逆転なし。

### Proceed
- Phase 2へ進行。

---

## Phase 2) Plan（I/F固定）

### Scope（固定）
- Stream Fは **FB-P0 baseline と FB-P2C A1契約固定のみ** を扱う。
- 成果物は docs-check で検証可能な契約文書に限定する。

### Non-goal（固定）
- 実装着手（A3実コード編集）、実行基盤更新、他ストリーム計画更新を行わない。
- 未承認事項を `Fixed` として扱わない。

### Verify
- Scope/Non-goalがA1契約文書と矛盾しないこと。

### Proceed
- Phase 3へ進行。

---

## Phase 3) ADR CDC（必要時のみ）

### Plan
- A1契約が既存ADR/Specと矛盾する場合のみ、CDC（Context / Decision / Consequences）を補強する。

### Execute
- 契約差分が必要な場合のみCDC節を更新し、不要時は「変更不要」を明記して先に進む。

### Verify
- CDC要素欠落なし。
- 契約ID衝突なし。

### Proceed
- Phase 4へ進行。

---

## Phase 4) Execute（モック前提を明示）

### Plan
- A2/A3が外部依存なしで開始できるよう、mock I/F・比較キー・停止条件を固定する。

### Execute
- Handoff最小セット:
  - `ReferenceContractID`: `CTR-FB-P2C-01-A1-TIEBREAK-V1`
  - `MockInterface`: `PolygonAutoFitStub.v1`
  - `DeterministicOrder`: `padding>self_intersection>area_delta>vertex_count`
  - `ReplayKeys`: `inputHash`, `seed`, `outputPolygonHash`, `paddingViolationCount`
- A2条件（mock-validation）:
  - 同一入力で同一`outputPolygonHash`を再現できること。
- A3条件（implementation-ready contract）:
  - A1順序・ReplayKeys・停止条件をread-only参照すること（契約値変更禁止）。

### Verify
- mock前提でA2/A3開始可。
- 実装詳細への依存持ち込みなし。

### Proceed
- Phase 5へ進行。

---

## Phase 5) Verify / Proceed（下流へ read-only handoff）

### Final checks

| 観点 | 判定 | 備考 |
| --- | --- | --- |
| 編集境界（2ファイルのみ） | Pass | Stream F独立性を維持 |
| Scope/Non-goal固定 | Pass | baseline前提を凍結 |
| A1契約（CDC→承認） | Pass | ContractID + Gate明記 |
| A2/A3引き渡し（mock前提） | Pass | ReferenceContractID固定 |
| フェイルセーフ | Pass | 未承認/競合/自己修復3回超過で停止 |

### Proceed decision
- **Proceed = 可（条件付き）**
  - 条件: A2/A3はA1契約をread-onlyで参照し、契約変更要求はA1へ差し戻す。
- **Stop条件（再掲）**
  1. 未承認確定
  2. 契約競合
  3. Verify自己修復3回超過

---

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - `ok: validated <N> active issue memos`
