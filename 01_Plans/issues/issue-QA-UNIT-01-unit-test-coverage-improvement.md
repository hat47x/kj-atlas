# Issue Plan: QA-UNIT-01 ユニットテスト拡充（欠陥検知能力ベース）

- Type: Process
- Status: Draft (Plan-Refined / Execution Hold)
- Priority: P2
- Owner: Stream K（QA Unit計画専任）
- Scope: `01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`（計画文書更新のみ）
- Out of Scope: 実装コード変更 / テストコード追加 / CI設定変更 / 他Issue・ADR編集
- Dependencies（前提条件として明示のみ）:
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Start Gate: 依存未解除時は docs-only を維持
- Expected verification level: `unit`

## Phase 1 Read（不足点の同期）

- 「coverage向上」の語だけでは、欠陥検知能力（defect detection power）の達成可否を判定できない。
- 高リスク優先順位（P1/P2/P3）は提示されているが、停止条件・再開条件と接続されていない。
- 実行可否のゲート（依存前提、自己修復上限、allowlist逸脱時停止）が運用文として固定されていない。

## Phase 2 ADR（Context / Decision / Consequences）

### Context
- 本Issueは unit計画の品質を「網羅率の高さ」ではなく「欠陥を早期に検知できるか」で評価する必要がある。
- 依存Issueが未解除の間は実行フェーズに入れないため、計画文書のみで再現可能な判定軸が必要。

### Decision
1. 評価軸は coverage閾値ではなく、欠陥クラス検知能力（正常系/異常系/境界値/回帰点）を必須とする。
2. 停止条件を固定する（self-correction > 3、依存前提崩れ、allowlist外編集要求）。
3. 再開条件を固定する（停止原因の解消証跡 + docs-only統制維持 + AC/DoD再判定）。

### Consequences
- 利点: coverage偏重による見かけ上の品質を回避し、重大欠陥の見逃しリスクを下げられる。
- コスト: 判定に必要な観点整理（欠陥クラス定義、トリアージ順序）が増える。
- 制約: 依存未解除の間は Execution Ready に遷移しない。

## Phase 3 Plan（AC/DoD補完）

## Requirement meta I/F
- RequirementID: `QA-UNIT-01`
- RequirementStatement: 網羅率の数字ではなく、欠陥検知能力を基準にユニットテスト計画を拡充する。
- PriorityClass: Should
- VerificationLevel: unit
- SecurityGateImpact: SafeMode
- DecisionStatus: Hold-for-Dependency-Gate（execution only）

### 3.1 Acceptance Criteria（補完後）
- AC-01: P1/P2/P3の優先順位と対象候補が固定されている。
- AC-02: 対象ごとに「正常系/異常系/境界値/回帰点」の4観点が記載されている。
- AC-03: 完了条件がcoverage固定閾値に依存せず、欠陥検知能力で定義されている。
- AC-04: 先行可能領域と契約待ち領域が分離されている。
- AC-05: 実行前提コマンドと失敗時トリアージ順序が明示されている。
- AC-06: 依存未解除時 docs-only 統制文が保持されている。
- AC-07: 停止条件と再開条件がYes/No判定可能な文で固定されている。

### 3.2 Definition of Done（補完後）
- DoD-01: 追加テスト採用基準（検知できる欠陥クラス）が明文化される。
- DoD-02: 再現性条件（同一入力→同一結果、flake抑制方針）が定義される。
- DoD-03: 保守性条件（命名規約、fixture最小化、過剰モック回避）が定義される。
- DoD-04: 失敗時修復ポリシー（self-correction最大3回、4回目相当で停止）が明示される。
- DoD-05: 依存解除前は execution を開始しないことが明記される。
- DoD-06: 再開時に停止原因の解消証跡を確認してからProceed判定する。

### 3.3 高リスク優先順位（欠陥検知能力指標つき）
- P1: Frontend safeMode判定 / validation / diff適用可否
  - 指標: 「誤許可」「誤拒否」「不整合差分受理」の再発を検知可能であること。
- P2: Backend request validation / service failure handling
  - 指標: 「契約違反受理」「失敗握り潰し」の再発を検知可能であること。
- P3: 契約未凍結の連携境界（mock-firstで観点のみ保持）
  - 指標: 契約凍結後に即時テスト具体化できる観点粒度が保持されること。

### 3.4 テスト観点表（unit計画）

| Priority | 対象 | 正常系 | 異常系 | 境界値 | 回帰点 |
|---|---|---|---|---|---|
| P1 | safeMode判定 | 許可条件で許可 | 条件不足で拒否 | 閾値境界で安定 | safeMode緩和の再発検知 |
| P1 | 入力validation | 正常入力通過 | 不正入力fail-fast | 空/最小/最大で安定 | validation抜け再発検知 |
| P1 | diff適用判定 | 正常差分適用 | 不整合差分拒否 | 境界件数で安定 | 誤適用再発検知 |
| P2 | request validation | 契約入力受理 | 契約違反拒否 | 欠落/過剰項目境界 | 契約逸脱再発検知 |
| P2 | service失敗系 | 正常復帰パス | 失敗時に誤成功しない | 最小データで挙動一定 | 失敗握り潰し再発検知 |

## Phase 4 Execute（docs-only）

### 4.1 Draft/Ready条件
- Draft維持条件: AC/DoDまたは観点表、停止/再開条件のいずれかが未充足。
- Ready（Planning）条件: AC/DoD/観点表/停止条件/再開条件が揃い、docs-only統制が明記される。
- Ready（Execution）条件: 上記に加え、依存解除証跡が確認済み。

### 4.2 実行前提とトリアージ
- Frontend: `npm run test -- --coverage --runInBand`
- Backend: `pytest -q --maxfail=1`
- Backend coverage補助: `pytest --cov=src --cov-report=term-missing`

失敗時トリアージ順序:
1. 前提不備（依存・fixture・環境差分）
2. 契約不整合（仕様と期待値ズレ）
3. 実装回帰（直近変更の影響）
4. テスト設計不良（brittle/assertion不足/過剰モック）

## Phase 5 Verify（unit計画としての再現性確認）

- チェック1: AC/DoDがYes/Noで判定可能。
- チェック2: coverage値依存ではなく欠陥検知能力で説明可能。
- チェック3: 優先順位と観点表から実装時ケース分解が可能。
- チェック4: 停止条件とself-correction上限が明文化される。
- チェック5: 再開条件（解消証跡確認）が明文化される。

自己点検結果（2026-05-10 UTC）
- Planning Ready: Yes
- Execution Ready: No（依存前提未解除のため）
- self-correction count: 0 / 3

## Phase 6 Proceed（Proceed / Hold / Stop）

- Proceed条件: 依存解除証跡が揃い、停止原因が存在せず、AC/DoD再判定が全てYes。
- Hold条件: 依存解除待ち、または契約未確定でP3が観点保持状態のまま。
- Stop条件:
  1. self-correction が3回を超える。
  2. 依存前提が崩れる。
  3. allowlist外編集要求が発生する。

