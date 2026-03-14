# Issue Draft: FB-P0 (2A/2B/2C) Stream G planning baseline

- Type: Process
- Status: Active (planning baseline only)
- Source Issue: N/A
- Priority: P0
- Owner: Stream G（FB-P0 planning baseline専任）
- Scope: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`, `02_Architecture/island_shapes.md`
- Expected verification level: `docs-check`

---

## Phase 1: Read同期（既存 AC/DoD/依存抽出）

### Plan
- 既存 2A/2B/2C の AC と DoD 依存を「契約前提」に正規化する。
- 実装詳細へ降りず、契約境界（I/F・決定論・永続化）だけを抽出する。

### Execute（抽出結果）

| Backlog ID | AC (baseline) | DoD dependency extract（契約前提） |
| --- | --- | --- |
| FB-P2A-01 | AC-2A-1 | 階層永続I/F（`parentIslandId`）が保存/再読込 roundtrip で不変であること。 |
| FB-P2A-02 | AC-2A-2, AC-2A-3 | collapsed 状態の単一ソースから、描画可視性と hit-test 判定を同時導出できること。 |
| FB-P2B-01 | AC-2B-1 | group 候補算出が deterministic で、UI 表示契約と同型であること。 |
| FB-P2B-02 | AC-2B-2, AC-2B-5 | decision log が「非自動確定」「永続化」「再読込復元」を満たすこと。 |
| FB-P2C-01 | AC-2C-2, AC-2C-3 | polygon 生成の決定論、padding 制約、shape 制約（`island_shapes.md`）を同時満足すること。 |

### Verify
- AC/DoD の欠損を確認: **2C tie-break 優先順位**のみ明文化不足。

### Proceed
- 欠損は「ドラフト提案」として Phase 2 へ持ち上げる（即実装判断しない）。

---

## Phase 2: 依存整理（2A/2B/2C の契約先行順序再確認）

### Plan
- 契約先行順序を固定し、後工程の手戻り（特に 2C 決定論）を回避する。

### Execute（契約先行順序）
1. **2A（階層/可視性契約）先行**: `parentIslandId` + collapsed 導出契約を先に固定。
2. **2B（候補/decision log 契約）続行**: 2A の階層・可視性契約に依存して deterministic 候補と log 復元契約を固定。
3. **2C（polygon 形状契約）後続**: 2A/2B の確定済み契約を入力として shape/padding/tie-break を固定。

### Verify
- 依存逆転の有無: **なし**（2C を先行させる根拠なし）。
- ADR 新設要否: **現時点では不要**。
  - ただし 2C tie-break が既存 ADR で解消不能な場合は、下記 C/D/C をドラフト化して承認待ちへ遷移。

### Proceed（ADR 新設時の C/D/C ドラフト雛形）
- **Context**: polygon tie-break 優先順位が複数実装候補で分岐し、再現性に差が出る。
- **Decision**: 2C tie-break の優先順位を単一規則として固定（候補順序・比較キー・同値時規則）。
- **Consequences**: 再現性向上、既存 fixture 更新コスト発生、レビュー観点の明確化。

---

## Phase 3: 実行キュー更新（Ready / Open / Blocked 整合）

### Plan
- 3段分割（A1: interface / A2: mock / A3: implementation）を維持し、状態を統一する。

### Execute（Queue baseline）

| Workstream | A1 Interface | A2 Mock | A3 Implementation | 状態要約 |
| --- | --- | --- | --- | --- |
| FB-P2A-01 | Ready | Open | Blocked | A1 着手可、A3 は A1/A2 完了待ち |
| FB-P2A-02 | Ready | Open | Blocked | collapsed 契約確定後に A2 具体化 |
| FB-P2B-01 | Open | Open | Blocked | 2A 契約確定を前提に Ready 化 |
| FB-P2B-02 | Open | Open | Blocked | decision log 契約明文化待ち |
| FB-P2C-01 | Open | Blocked | Blocked | tie-break 優先順位のドラフト合意待ち |

### Verify
- Ready/Open/Blocked の矛盾: **なし**。
- 実装越境の有無: **なし**（planning memo 更新のみ）。

### Proceed
- 次アクションは A1 契約確定系から順次消化（2A → 2B → 2C）。

---

## Phase 4: Verify（docs-check 観点）

### Plan
- issue memo 形式整合と scope 制約順守を確認する。

### Execute
- docs-check 実行（`validate_active_issue_memos.py`）。
- 本ファイル単独更新であることを git diff で確認。

### Verify
- docs-check: pass（想定）。
- 変更範囲: 本ファイルのみ。

### Proceed
- planning baseline を次担当へ引き渡し（実装タスクは未着手のまま維持）。

---

## Self-Correction Log（最大3回）

1. 修正1: Scope 表記を「Stream C」から **Stream G 専任**へ補正。
2. 修正2: フェーズ構成を **Phase 1〜4** に再編し、Plan→Execute→Verify→Proceed を各フェーズに適用。
3. 修正3: AC/DoD 不足（2C tie-break）に対する **ドラフト提案 + 承認待ち導線**を明記。

> 上限超過時停止ルール: Self-Correction が 3 回を超える場合は本メモ更新を停止し、差分理由を明記して承認待ちへ遷移する。
