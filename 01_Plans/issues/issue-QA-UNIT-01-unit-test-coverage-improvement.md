# Issue Plan: QA-UNIT-01 ユニットテスト拡充（欠陥検知能力ベース）

- Type: Process
- Status: Draft (Plan-Refined / Execution Hold)
- Priority: P0
- Owner: Stream H（QA計画・検証境界）
- Scope: `01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`（計画文書更新のみ）
- Out of Scope: 実装コード変更 / テストコード追加 / CI設定変更
- Expected verification level: `unit`

## Phase 1: テスト資産棚卸し（unit/integration/e2e）

| Layer | 現行カバレッジ（把握） | 欠落 | Priority連動深度 |
|---|---|---|---|
| Unit | safeMode/validation系の観点は存在 | 失敗系・境界値・回帰点の定義が不足 | P0: 4観点必須 / P1: 3観点必須 / P2: 2観点必須 |
| Integration | API契約/永続化の断面は散在 | contract drift検知の責務分解不足 | P0: 必須（失敗時挙動含む） |
| E2E | smoke中心 | unit失敗を再現可能なマッピング不足 | P1/P2は代表フローのみ |

## Phase 2: ADR明文化（Context / Decision / Consequences）

### Context
coverage数値のみでは Done 判定が曖昧で、欠陥再発を抑止できない。

### Decision
1. Done 判定は「検知可能欠陥クラス」の充足で行う。
2. flaky許容はゼロ（passは単回成功ではなく再現性成功）。
3. 再試行は最大3回。4回目相当は即 Stop（Fail-safe）。

### Consequences
- 利点: 高リスク欠陥の見逃し抑止。
- 制約: 計画策定時に失敗時挙動まで先に明文化が必要。

## Phase 3: Unit強化計画（リスク起点）

| Priority | 対象モジュール群 | 期待値 | 失敗時挙動 |
|---|---|---|---|
| P0 | safeMode判定 / 入力validation / diff適用 | 誤許可・誤拒否・不整合受理を検知 | fail-fast + 原因分類可能 |
| P1 | backend request validation / service failure handling | 契約違反拒否・失敗握り潰し防止 | errorを成功扱いしない |
| P2 | 契約未凍結境界（mock-first） | 仕様確定後に即テスト化可能 | Hold記録（未確定の明示） |

## Phase 6 完了判定（AC/DoD）

### Acceptance Criteria
- AC-01: Layer棚卸し表（unit/integration/e2e）が更新済み。
- AC-02: Priority別検証深度（P0/P1/P2）が明記済み。
- AC-03: flakyゼロ方針と再試行上限（3回）が明記済み。
- AC-04: 対象ごとに期待値と失敗時挙動が定義済み。

### Definition of Done
- DoD-01: coverage数値依存ではなくリスク起点で判定可能。
- DoD-02: 実装前に unit 強化タスク分解が第三者再利用可能。
- DoD-03: 保留条件（依存未解決/承認待ち/環境制約）を明記。

### 保留条件
- 依存未解決、契約未凍結、実行環境制約が残る場合は `Execution: Hold` を維持する。
