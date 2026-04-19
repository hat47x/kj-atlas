# Issue Draft: FB-P0 (2A/2B/2C) Stream C planning baseline

- Type: Process
- Status: Open (Audit Hold: Stream C contract freeze)
- Source Issue: N/A
- Priority: P0
- Owner: Stream C（P2C契約 + baseline計画のみ）
- Scope: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ
- Editable files (hard lock):
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
- Non-editable files: 上記以外すべて
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`
- Expected verification level: `docs-check`

---

## Baseline objective（Stream C）

- 目的: **P2C A1契約をStream C内でfreeze** し、A2/A3が外部待ちなしでmock前提進行できる引き渡し仕様を固定する。
- 非目標:
  - `03_Implement/**` の変更
  - 他Issue・共有統合ファイルの変更
  - 他ストリーム判断待ちでの進行停止（依存切断方針に反する）
- 依存切断原則:
  - 外部ストリーム待ち禁止。
  - 必要I/Fは本ストリームで固定し、mock可能な形で出力する。
- フェイルセーフ:
  - 未承認確定 / 契約競合 / Verify自己修復3回超過のいずれかで即停止。

---

## Phase 1) Read同期

### Plan
- 編集境界（2ファイルのみ）と実施Phase順序を固定する。
- P2C A1契約対象とVerify観点（ContractID / Required fields / Invariants / Handoff）を同期する。

### Execute
- 編集許可2ファイルのみ対象であることを確認。
- 実施順序を `1) Read同期 -> 2) baseline前提固定 -> 3) A1契約固定 -> 4) A2/A3引き渡し仕様化 -> 5) Verify/Proceed` に固定。

### Verify
- 編集境界逸脱なし。
- Phase順序の逆転なし。

### Proceed
- Phase 2へ進行。

---

## Phase 2) baseline前提の固定（Scope / Non-goal）

### Scope（固定）
- Stream Cは **P2C契約とbaseline計画のみ** を扱う。
- 成果物は docs-check で検証可能な契約文書に限定する。

### Non-goal（固定）
- 実装着手（A3実コード編集）、実行基盤更新、他ストリーム計画更新を行わない。
- 未承認事項を `Fixed` として扱わない。

### Verify
- Scope/Non-goalがA1契約文書と矛盾しないこと。

### Proceed
- Phase 3へ進行。

---

## Phase 3) A1契約固定（CDC→承認）

### Plan
- A1契約は CDC（Context / Decision / Consequences）形式で固定し、承認済み状態を明記する。

### Execute
- ContractID・必須キー・invariants・禁止遷移をA1文書へ固定。
- 承認ゲートを `DecisionStatus=Fixed` + `GateDecision=approved` で明示。
- 契約更新要求のルートを「A1差し戻しのみ」に固定。

### Verify
- CDC要素欠落なし。
- 契約ID衝突なし。
- 未承認項目をApproved扱いしていない。

### Proceed
- Phase 4へ進行。

---

## Phase 4) A2/A3への引き渡し仕様化（モック前提）

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

## Phase 5) Verify / Proceed

### Final checks

| 観点 | 判定 | 備考 |
| --- | --- | --- |
| 編集境界（2ファイルのみ） | Pass | Stream C独立性を維持 |
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
