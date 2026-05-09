# Issue Ready: QA-UNIT-01 ユニットテスト拡充（欠陥検知能力ベース）

- Type: Process
- Status: Ready (Execution Plan Fixed)
- Source Issue: N/A
- Priority: P2
- Owner: Stream I（QA-UNIT-01 Draft Ready化）
- Dependencies:
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`（P0収束）
  - `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`（検証スコープ同期）
- Scope: `01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`（本作業は計画文書更新のみ）
- Out of Scope: 実装コード変更 / テストコード追加 / CI設定変更 / 他Issue・ADR編集
- Start Gate (fixed): FB-P0収束完了 + HIL-RS-02計画同期完了まで execution は Hold（docs-only）
- Related ADR/Spec: `ADR-0001-value-to-requirements`, `ADR-0019-e2e-verification-policy-and-compose-runbook`
- Expected verification level: `unit`

## Requirement meta I/F（共通キー）

- RequirementID: `QA-UNIT-01`
- RequirementStatement: 主要ドメインロジックのユニットテストを、**網羅率の数値目標ではなく欠陥検知能力**を基準として拡充する。
- PriorityClass: Should
- AcceptanceScenario:
  - 前提: 既存unit基盤（Vitest/Pytest）が実行可能
  - 操作: 高リスク領域に対して設計済みテストケースを追加
  - 期待結果: 正常系/異常系/境界値の失敗検知が再現可能
  - 除外: E2E追加・機能改修・閾値先行導入
- GoNoGoGate: Optional
- SecurityGateImpact: SafeMode
- VerificationLevel: unit
- DecisionStatus: Hold-for-Dependency-Gate（execution only）
- DecisionQueueRef: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`
- DependencyLockPolicy: Dependency未解除時は docs-only。テスト実装・閾値導入・CI変更を開始しない。

## 1) 課題 / Problem statement（曖昧目標の明確化）

従来の「coverage向上」は、以下の曖昧さを残していた。

- coverage率が上がっても、欠陥を検知できるとは限らない。
- 変更頻度の高い領域（safeMode/validation/diff）で、異常系や境界値の回帰検知が不足しうる。
- テスト失敗時の切り分け順序が不明瞭で、レビューがデバッグ作業へ流れやすい。

本Issueはこの曖昧さを解消し、実装前に「何を検知できれば十分か」を固定する。

## 2) Context

- ADR-0019: 結合品質の前段として unit 検証の積み上げを重視。
- ADR-0001: 可逆性・説明可能性・レビュー追跡性を品質判断の軸に置く。
- 現行基盤: Frontend（Vitest）/ Backend（Pytest）は存在し、追加設計を段階投入可能。

## 3) Decision（Ready化の中核）

### 3.1 リスクベース優先順位（対象モジュール候補）

P1（最優先: 安全境界 / 回帰影響大）
1. Frontend `safe_mode` 相当ポリシー判定ロジック
2. Frontend import/export 前段の validation ロジック
3. Frontend diff/patch 適用可否判定ロジック

P2（高優先: 仕様逸脱検知）
4. Backend request validation / schema整合チェック
5. Backend service層の失敗系ハンドリング（不正入力・前提不成立）

P3（依存確定後）
6. 依存契約が未凍結の連携境界（mock先行で設計のみ保持）

### 3.2 欠陥検知能力で定義するカバレッジ目標

本Issueでは coverage数値そのものを完了条件にしない。代わりに以下を必須化する。

- 正常系: 期待出力・状態遷移が仕様どおりである。
- 異常系: 不正入力・契約違反を fail-fast で拒否し、誤った成功を返さない。
- 境界値: 空入力/最小値/最大値/閾値境界で挙動が安定し、意図しない丸め・通過がない。
- 回帰点: 既知不具合クラス（safeMode緩和、validation抜け、diff誤適用）を再発時に必ず検知する。

### 3.3 先行可能設計と契約待ち設計の分離

- 先に書けるユニットテスト設計（契約確定不要）
  - 純関数/同期ロジック（safeMode判定、入力検証、diffルール）
  - deterministicな入出力を持つユーティリティ
- 契約確定後に実装する設計（契約待ち）
  - API contract依存のエラーコード精査
  - 外部境界での型拡張・互換動作

契約待ちは mock-first でテスト観点のみ先行定義し、実装着手は gate解除後に限定する。

### 3.4 CI実行前提と失敗時修復ポリシー

CI前提（unitレベル）
- Frontend: `npm run test -- --coverage --runInBand`
- Backend: `pytest -q --maxfail=1` と `pytest --cov=src --cov-report=term-missing`

失敗時トリアージ順序（固定）
1. **前提不備**: 依存欠落・fixture破損・環境差分を確認
2. **契約不整合**: 期待仕様とテスト期待値のズレを確認
3. **実装回帰**: 直近変更点でロジック崩れを確認
4. **テスト設計不良**: brittle/assertion不足/過剰モックを修正

ルール
- 同一失敗の自己修復（self-correction）は最大3回。
- 4回目相当が必要なら停止し、ブロッカーを issue に記録して human judgement に移送する。

## 4) Acceptance Criteria（検証可能なAC）

- [ ] AC-01: リスクベース優先順位（P1/P2/P3）と対象候補が明示されている。
- [ ] AC-02: 正常系/異常系/境界値/回帰点の4観点が、対象ごとに確認可能な形で定義されている。
- [ ] AC-03: 欠陥検知能力ベースの完了条件が、coverage率の固定閾値に依存せず記述されている。
- [ ] AC-04: 「先行可能（mock不要）」と「契約確定後（mock先行設計）」が分離されている。
- [ ] AC-05: CI実行前提コマンドと失敗時トリアージ順序が明示されている。
- [ ] AC-06: Dependency lock未解除時は docs-only を維持する統制文が保持されている。

## 5) Definition of Done（DoD）

- [ ] DoD-01: 追加テスト判定基準（何を検知できれば採用か）が明文化されている。
- [ ] DoD-02: 回帰検知の再現性条件（同一入力で同一結果、flake回避方針）が定義されている。
- [ ] DoD-03: 保守性条件（命名規約、fixture最小化、過剰モック回避）が定義されている。
- [ ] DoD-04: 失敗時の修復ポリシー（最大3回・停止条件）が明示されている。
- [ ] DoD-05: 実行開始前の依存解除条件（FB-P0 + HIL-RS-02同期）が明示されている。

## 6) Task breakdown（Execution準備）

- [ ] T1: 高リスク領域ごとに「正常/異常/境界/回帰」観点マトリクスを作成する。
- [ ] T2: Frontend候補（safeMode/validation/diff）を case ID 単位で分解する。
- [ ] T3: Backend候補（validation/service failure）を case ID 単位で分解する。
- [ ] T4: mock先行領域と契約確定待ち領域を分離し、着手順を固定する。
- [ ] T5: Verifyログ様式（Before/After、検知欠陥クラス、再現手順）を固定する。

## 7) Validation plan（計画文書としての検証）

本フェーズは docs-only のため、以下を満たせば検証完了とする。

- 文書内に AC/DoD/Dependencies/Stop 条件が存在する。
- AC/DoD が「実行時にYes/No判定可能」な粒度で記述される。
- coverage率偏重を避け、欠陥検知能力が主判定になっている。

## 8) Consequences

- 実装フェーズ開始時に、対象優先度・観点・停止条件が既に固定され、手戻りを抑制できる。
- coverage数値を追うだけの形式的改善を避け、実害のある回帰を捕捉しやすくなる。
- dependency lock下でも docs-only で準備を進められ、再開可能性を維持できる。

## 9) Fail-safe / Stop conditions

以下のいずれかで停止し、必要最小限の確認事項のみ列挙する。

1. 対象モジュールの優先順位を確定できない。
2. 契約未確定で観点定義が成立しない。
3. スコープ外編集が必要になる。
4. self-correction が3回を超える。
