# Issue Plan: QA-UNIT-01 ユニットテスト拡充（欠陥検知能力ベース）

- Type: Process
- Status: Draft (Plan-Refined / Execution Hold)
- Priority: P0
- Owner: Stream F（QA専任）
- Scope: `01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`（計画文書更新のみ）
- Out of Scope: 実装コード変更 / テストコード追加 / CI設定変更
- Expected verification level: `unit`

## Phase 1: Read Baseline（AC/DoD抽出 + 資産ギャップ）

### AC/DoD抽出（現行）
- AC-01: Layer棚卸し表（unit/integration/e2e）が更新済み。
- AC-02: Priority別検証深度（P0/P1/P2）が明記済み。
- AC-03: flakyゼロ方針と再試行上限（3回）が明記済み。
- AC-04: 対象ごとに期待値と失敗時挙動が定義済み。
- DoD-01: coverage数値依存ではなくリスク起点で判定可能。
- DoD-02: 実装前に unit 強化タスク分解が第三者再利用可能。
- DoD-03: 保留条件（依存未解決/承認待ち/環境制約）を明記。

### 既存テスト資産ギャップ（単体〜E2E対応）
| Layer | 現行カバレッジ（把握） | ギャップ（不足） | Expected verification level 連動 |
|---|---|---|---|
| Unit | safeMode/validation系の基本観点あり | 失敗系、境界値、回帰点の欠陥クラス定義が不足 | unit: P0=4観点 / P1=3観点 / P2=2観点 |
| Integration | API契約/永続化の断面は散在 | contract drift検知の責務分離（入力拒否/永続化失敗/復旧）不足 | integration: P0は失敗時挙動まで必須 |
| E2E | smoke中心 | unit失敗をユーザージャーニーへ追跡するマッピング不足 | e2e: P1/P2は代表フローで確認 |

## Phase 2: Plan（品質戦略）

### ADR明文化（Context / Decision / Consequences）
#### Context
coverage数値のみでは Done 判定が曖昧で、欠陥再発を抑止できない。

#### Decision
1. Done 判定は「検知可能欠陥クラス」の充足で行う。
2. flaky許容はゼロ（passは単回成功ではなく再現性成功）。
3. 再試行は最大3回。4回目相当は即 Stop（Fail-safe）。
4. unit→integration→e2e の段階ゲートを通過しない限り上位ゲートへ進まない。

#### Consequences
- 利点: 高リスク欠陥の見逃し抑止。
- 制約: 計画策定時に失敗時挙動まで先に明文化が必要。

### 段階ゲート定義（unit / integration / e2e）
| Gate | Entry | Exit（合格条件） | 失敗分類 |
|---|---|---|---|
| G1 Unit | 対象欠陥クラス定義済み | P0/P1/P2観点数充足 + 期待値/失敗時挙動定義完了 | test defect / product defect / environment limitation |
| G2 Integration | G1合格 | 契約境界 + 永続化断面の失敗時挙動を定義済み | 同上 |
| G3 E2E Traceability | G2合格 | unit失敗を代表ジャーニーへ逆引き可能 | 同上 |

### flakyリスク項目（明示）
- 非決定的待機（time-based wait）依存。
- テストデータ初期化不足による順序依存。
- 外部依存（compose/network/port競合）による環境揺らぎ。
- 失敗分類未実装により「再試行で隠蔽」される運用リスク。

## Phase 3: Execute（テスト拡張計画）

| Priority | 対象モジュール群 | 期待値 | 失敗時挙動 |
|---|---|---|---|
| P0 | safeMode判定 / 入力validation / diff適用 | 誤許可・誤拒否・不整合受理を検知 | fail-fast + 原因分類可能 |
| P1 | backend request validation / service failure handling | 契約違反拒否・失敗握り潰し防止 | errorを成功扱いしない |
| P2 | 契約未凍結境界（mock-first） | 仕様確定後に即テスト化可能 | Hold記録（未確定の明示） |

> 注: 本issueは docs-only のため、実テスト追加は別実行タスクで実施する。

## Phase 4: Verify（自己検証ルール）
- 検証失敗時は最大3回まで自己修復（再実行/待機調整/fixture確認）。
- 4回目相当は停止し、`test defect / product defect / environment limitation` のいずれかへ分類して記録する。
- 推測で期待値や閾値を書き換えない（Fail-safe）。

## Phase 5: Proceed（品質判定）

### Acceptance Criteria
- AC-01: Layer棚卸し表（unit/integration/e2e）が更新済み。
- AC-02: Priority別検証深度（P0/P1/P2）が明記済み。
- AC-03: flakyゼロ方針と再試行上限（3回）が明記済み。
- AC-04: 対象ごとに期待値と失敗時挙動が定義済み。
- AC-05: unit/integration/e2e 段階ゲートが定義済み。
- AC-06: 失敗分類（3分類）と停止条件（4回目相当Stop）が明記済み。

### Definition of Done
- DoD-01: coverage数値依存ではなくリスク起点で判定可能。
- DoD-02: 実装前に unit 強化タスク分解が第三者再利用可能。
- DoD-03: 保留条件（依存未解決/承認待ち/環境制約）を明記。
- DoD-04: blocker発生時の再開条件（何が揃えば再開可能か）が文書化済み。

### blockers / 再開条件
- blocker: 契約未凍結、実行環境制約、上流承認待ち。
- 再開条件: 対象契約凍結、実行環境復旧、承認記録の付与。
- 未達時: `Execution: Hold` を維持。
