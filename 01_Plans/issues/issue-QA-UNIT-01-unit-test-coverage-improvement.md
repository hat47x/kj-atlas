# Issue Plan: QA-UNIT-01 ユニットテスト拡充（欠陥検知能力ベース）

- Type: Process
- Status: Draft (Plan-Refined / Execution Hold)
- Priority: P2
- Owner: Stream D（QA計画整備専任）
- Scope: `01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`（計画文書更新のみ）
- Out of Scope: 実装コード変更 / テストコード追加 / CI設定変更 / 他Issue・ADR編集
- Dependencies（前提条件として明示のみ）:
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Start Gate: 依存未解除時は docs-only を維持
- Expected verification level: `unit`

## 1) Read同期（不足整理）

- coverage向上の語だけでは、欠陥検知力の判定ができない。
- 高リスク領域の優先度はあるが、Ready判定との接続が不足している。
- 実行時の停止条件と自己修復上限の運用文が不足している。

## 2) Plan（AC/DoD不足補完提案）

## Requirement meta I/F
- RequirementID: `QA-UNIT-01`
- RequirementStatement: 網羅率の数字ではなく、欠陥検知能力を基準にユニットテスト計画を拡充する。
- PriorityClass: Should
- VerificationLevel: unit
- SecurityGateImpact: SafeMode
- DecisionStatus: Hold-for-Dependency-Gate（execution only）

### 2.1 Acceptance Criteria（補完後）
- AC-01: P1/P2/P3の優先順位と対象候補が固定されている。
- AC-02: 正常系/異常系/境界値/回帰点の4観点が対象ごとに記載されている。
- AC-03: 完了条件がcoverage固定閾値に依存せず、欠陥検知能力で定義される。
- AC-04: 先行可能領域と契約待ち領域が分離されている。
- AC-05: 実行前提コマンドと失敗時トリアージ順序が明示されている。
- AC-06: 依存未解除時 docs-only 統制文が保持される。

### 2.2 Definition of Done（補完後）
- DoD-01: 追加テスト採用基準（検知できる欠陥クラス）が明文化される。
- DoD-02: 再現性条件（同一入力→同一結果、flake抑制方針）が定義される。
- DoD-03: 保守性条件（命名規約、fixture最小化、過剰モック回避）が定義される。
- DoD-04: 失敗時修復ポリシー（self-correction最大3回、4回目相当で停止）が明示される。
- DoD-05: 依存解除前は execution を開始しないことが明記される。

## 3) Execute（Draft/Ready条件の明文化 + テスト観点表）

### 3.1 Draft/Ready条件
- Draft維持条件: AC/DoDまたは観点表が未充足。
- Ready（Planning）条件: AC/DoD/観点表/停止条件が揃い、docs-only統制が明記される。
- Ready（Execution）条件: 上記に加え、依存解除証跡が確認済み。

### 3.2 リスクベース対象
- P1: Frontend safeMode判定 / validation / diff適用可否
- P2: Backend request validation / service failure handling
- P3: 契約未凍結の連携境界（mock-firstで観点のみ保持）

### 3.3 テスト観点表（unit計画）

| Priority | 対象 | 正常系 | 異常系 | 境界値 | 回帰点 |
|---|---|---|---|---|---|
| P1 | safeMode判定 | 許可条件で許可 | 条件不足で拒否 | 閾値境界で安定 | safeMode緩和の再発検知 |
| P1 | 入力validation | 正常入力通過 | 不正入力fail-fast | 空/最小/最大で安定 | validation抜け再発検知 |
| P1 | diff適用判定 | 正常差分適用 | 不整合差分拒否 | 境界件数で安定 | 誤適用再発検知 |
| P2 | request validation | 契約入力受理 | 契約違反拒否 | 欠落/過剰項目境界 | 契約逸脱再発検知 |
| P2 | service失敗系 | 正常復帰パス | 失敗時に誤成功しない | 最小データで挙動一定 | 失敗握り潰し再発検知 |

### 3.4 実行前提とトリアージ
- Frontend: `npm run test -- --coverage --runInBand`
- Backend: `pytest -q --maxfail=1`
- Backend coverage補助: `pytest --cov=src --cov-report=term-missing`

失敗時トリアージ順序:
1. 前提不備（依存・fixture・環境差分）
2. 契約不整合（仕様と期待値ズレ）
3. 実装回帰（直近変更の影響）
4. テスト設計不良（brittle/assertion不足/過剰モック）

## 4) Verify（検証手順の実行可能性自己点検）

- チェック1: AC/DoDがYes/Noで判定可能。
- チェック2: coverage値依存ではなく欠陥検知能力で説明可能。
- チェック3: 優先順位と観点表から実装時ケース分解が可能。
- チェック4: 停止条件とself-correction上限が明文化される。

自己点検結果（2026-05-09 UTC）
- Planning Ready: Yes
- Execution Ready: No（前提条件未確認のため）

## 5) Proceed / Stop

- Proceed条件: 依存解除証跡が揃った場合のみ execution に移行。
- Stop条件:
  1. 対象優先順位を確定できない。
  2. 契約未確定で観点定義が成立しない。
  3. スコープ外編集が必要。
  4. self-correction が3回を超える。

self-correction count: 0 / 3
