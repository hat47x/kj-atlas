# Issue Draft: FB-P0 (2A/2B/2C) Stream C planning baseline

- Type: Process
- Status: Draft (起票用)
- Source Issue: N/A
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Phase 1: Read/Baseline（再読込結果）

| Backlog ID | AC | DoD dependency extract |
| --- | --- | --- |
| FB-P2A-01 | AC-2A-1 | schemaに `parentIslandId` を持つ階層永続I/Fが必要。保存/再読込のroundtrip整合が前提。 |
| FB-P2A-02 | AC-2A-2, AC-2A-3 | 描画可視性とhit-test判定を同一collapsed状態から導出する契約が必要。 |
| FB-P2B-01 | AC-2B-1 | deterministicな候補group構造とUI表示契約が必要。 |
| FB-P2B-02 | AC-2B-2, AC-2B-5 | decision log永続化、非自動確定、再読込復元の契約が必要。 |
| FB-P2C-01 | AC-2C-2, AC-2C-3 | polygon生成決定論・padding制約・shape制約（`island_shapes.md`依存）が必要。 |

## Phase 2: ADR判定

- 判定結果: 原則は既存ADR（ADR-0007）で完結可能。
- 例外候補: `FB-P2C-01` の tie-break（決定論優先順位）は判断補強が必要なため A1 issue に Context/Decision/Consequences を明記し Pending 扱い。
- フェイルセーフ: HIL共有リソースを触る必要が出た時点で Stream D へ即時エスカレーション。

## Phase 3/4: 3段分割Issue起票（インターフェース→モック→実装）

- FB-P2A-01: `issue-FB-P2A-01-a1-interface-contract.md` / `issue-FB-P2A-01-a2-mock-validation.md` / `issue-FB-P2A-01-a3-implementation.md`
- FB-P2A-02: `issue-FB-P2A-02-a1-interface-contract.md` / `issue-FB-P2A-02-a2-mock-validation.md` / `issue-FB-P2A-02-a3-implementation.md`
- FB-P2B-01: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
- FB-P2B-02: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
- FB-P2C-01: `issue-FB-P2C-01-a1-interface-contract.md` / `issue-FB-P2C-01-a2-mock-validation.md` / `issue-FB-P2C-01-a3-implementation.md`

## Phase 5: Verify → Proceed

- docs-check: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- dependency table: 本メモ + 各Issueの「DoD依存」節を相互参照。
- conflict table: 下表で境界衝突ゼロを確認。

| Stream | 編集対象 |
| --- | --- |
| Stream C (this task) | `01_Plans/issues/issue-FB-P2*.md` 新規のみ |
| Other streams | 本タスク範囲外（実装/既存issue/README/dashboard） |

