# Issue Draft: QA-UNIT-01 ユニットテストのカバレッジ向上

- Type: Process
- Status: Draft (起票用)
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Dependencies: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`（P0収束後に着手）, `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`（検証スコープ同期）
- Scope: `03_Implement/frontend`, `03_Implement/backend`, `03_Implement/*/tests`
- Related Backlog: `N/A`
- Related ADR/Spec: `ADR-0001-value-to-requirements`, `ADR-0019-e2e-verification-policy-and-compose-runbook`
- Expected verification level: `unit`

## Requirement meta I/F（共通キー）

- RequirementID: `QA-UNIT-01`
- RequirementStatement: 主要ドメインロジックに対するユニットテストを拡充し、回帰検知能力を向上させる。
- PriorityClass: Should
- AcceptanceScenario: 前提=既存テスト基盤が実行可能 / 操作=不足領域へunit test追加 / 期待結果=追加テストが安定通過し回帰検知観点をカバー / 除外=e2eシナリオ拡張
- GoNoGoGate: Optional
- SecurityGateImpact: SafeMode
- VerificationLevel: unit
- DecisionStatus: Pending
- DecisionQueueRef: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`

## 1) 課題 / Problem statement

- テストは存在するが、変更頻度の高いロジックで回帰検知の粒度にばらつきがある。
- 仕様変更時に「どこまで壊れていないか」の判断が属人的になりやすい。
- 結果として実装レビュー時に仕様評価よりデバッグに時間を使いやすい。

## 2) 背景 / Context

- ADR-0019で「結合前に下位検証を積み上げる」方針が示されている。
- ADR-0001の価値整合（可逆性・人間レビュー追跡）を維持するため、局所的な振る舞い保証が必要。
- Frontend/Backendともにunit test基盤は存在し、未カバー領域を優先拡張できる。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 変更の安全な反復を支える品質基盤として妥当。
- 安全（THREAT_MODEL / SafeMode）: SafeMode境界を持つロジックの回帰検知強化に有効。
- 企業・行政要件（enterprise_architecture）: 監査時に挙動説明可能性を補強。
- 後方互換（schemas）: スキーマ改変は伴わず互換リスクは低い。

## 4) 提案する解決策 / Proposed solution

- 変更対象（Docs / Frontend / Backend / Schema）: Frontend + Backend テストコード、必要最小限のテスト用fixture。
- 変更の最小単位（再開可能な粒度）:
  1. カバレッジ計測コマンドの基準化
  2. 高優先ロジックからunit test追加
  3. 失敗時の回帰パターンをテスト名で明示
- 非目標（何をこのIssueでやらないか）:
  - e2eシナリオ追加
  - 大規模リファクタ
  - 新機能追加

## 5) 受入条件 / Acceptance criteria

- [ ] 優先対象ロジック（safeMode/validation/diff等）の不足ケースにunit testが追加される。
- [ ] 追加テストがローカルCI相当コマンドで安定通過する。
- [ ] テスト追加に伴う既存仕様との矛盾がない。
- [ ] 必要な検証（unit）が `Expected verification level` と一致する。
- [ ] `GoNoGoGate` の要否（Optional）が明示されている。
- [ ] セキュリティ境界に影響する観点（SafeMode関連）を含むテスト観点が列挙される。
- [ ] AC-M1: 測定対象モジュール一覧（Frontend/Backend）を明記し、各モジュールで「追加ケース数（最低1件）」を定量記録する。
- [ ] AC-M2: `pytest --cov` / `vitest --coverage`（または同等）で **statement coverageの差分（Before/After）** を保存し、対象モジュールで非負（悪化なし）を必須化する。
- [ ] AC-M3: 回帰検知の実効性指標として、safeMode/validation/diffの3観点それぞれで「失敗を検知できるアサーション」を1件以上持つことを必須化する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 現状テストの薄いモジュールを抽出し、優先順位を決める。
- [ ] T2: Frontendのドメインロジックにunit testを追加する。
- [ ] T3: Backendのバリデーション/サービス層にunit testを追加する。
- [ ] T4: 追加テストを実行し、失敗時は最小修正で再検証する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && npm test -- --runInBand`
  - `cd 03_Implement/backend && pytest -q`
  - `cd 03_Implement/frontend && npm run test -- --coverage --runInBand`
  - `cd 03_Implement/backend && pytest --cov=src --cov-report=term-missing`
- 期待結果:
  - 追加したunit testを含めて全件pass。
  - Coverage指標（statement/branchのうち収集可能なもの）がBefore比で悪化しない。
  - 対象3観点（safeMode/validation/diff）で回帰検知アサーション件数が0でない。
- 未実施時の理由・代替検証:
  - 依存不足で実行不可の場合は、対象テストファイルの静的レビュー結果と実行阻害要因を記録する。

### 7.1 Verify時の測定可能指標（必須）

- 指標V-UNIT-01: 追加unit test件数（frontend/backend別）。
- 指標V-UNIT-02: 対象モジュールのcoverage差分（Before/After、%）。
- 指標V-UNIT-03: 安全境界観点別アサーション件数（safeMode/validation/diff）。
- 判定ルール:
  - 3指標のうち1つでも未記録なら **No-Go**。
  - Verifyの自己修復（self-correction）は最大3回。4回目が必要な場合は **Stop**。

## 8) 代替案 / Alternatives considered

- 代替案A: 先にe2e中心で補う（却下: 原因切り分け粒度が粗い）。
- 代替案B: カバレッジ閾値のみ導入（却下: 実質的なケース不足が残る）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: brittle test増加による保守コスト上昇。
- 影響範囲: CI時間、テストfixture管理。
- ロールバック手順: 問題のある追加テストをコミット単位でrevertし、観点を再分割して再起票。

## 10) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件（トレードオフ閾値）: カバレッジ閾値を品質ゲート（必須）へ昇格する場合。


## Stream H Draft Reframe（2026-05-04 / proposal-only）

### Phase 1 Read
- 最新メタ確認: 本Issueは `Status=Draft` の提案段階として扱う。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: QA-UNIT-01 は品質向上の価値が高い一方、Draft段階で実装着手すると範囲逸脱が生じる。
- Decision: 本Issueは「Open化のための提案整理」に限定し、実装タスクは承認後に切り出す。
- Consequences: 受入条件と優先順位を先に固定でき、着手時の再調整コストを削減できる。

### Phase 3 Plan（Go / No-Go gate）
- Go: Owner確定、対象モジュール優先順、unit検証コマンド、承認記録が揃う。
- No-Go: Owner未定、検証レベル不一致、実装先行要求。
- Conditional(Hold): 提案記述は整ったが承認待ち。

### Phase 4 Execute（proposal-only整備）
- 実施: AC/DoD/Validationの提案粒度を揃える。
- 非実施: テスト追加、コード変更、カバレッジ閾値の強制導入。

### Phase 5 Verify（最大3回修復）
- 観点: Proposal範囲の明示、実装指示の排除、Gate条件の明確性。
- 失敗時: 3回まで修復、超過時は `held`。

### Phase 6 Stopper
- 依存未確定、承認不足、競合疑義（unit/e2e境界混線）を検知した場合は停止して照会する。


## Stream G execution pass（2026-05-04 / QA-UNIT P2）

### Phase Start Re-read
- 対象再読: `issue-QA-UNIT-01-unit-test-coverage-improvement.md` を再読し、docs-only境界・Open gate・self-correction上限を確認。

### Plan → Execute → Verify → Proceed
- Plan: Open判定に必要な品質ゲート（AC/DoD/Validation/Stop）を欠落なく保持。
- Execute: 単体テスト改善計画の判断材料を整備し、実装変更・実行結果の新規確定は行わない。
- Verify: docs-check前提で表記整合と依存記述の一貫性を検証。
- Proceed: 依存証跡未確定のため **Hold継続**。

### ADR task C / D / Csq
- Context: QA-UNITはカバレッジ改善の優先順位付けを誤ると、低効果の工数消費が発生する。
- Decision: DraftをOpen判定可能品質へ整備し、実装前に評価軸と停止条件を固定する。
- Consequences: 後続実装時の判断基準が明確になり、過剰実装や誤優先度を抑制できる。


## Stream F readiness pass（2026-05-05 / QA-UNIT issue readiness）

### Phase 1 Read（前提確認）
- FB-P0収束後に着手する依存前提を維持する（`issue-FB-P0-2A2B2C-stream-c-planning-baseline` 完了前はDraft維持）。
- 本Issueは実装前の準備フェーズであり、frontend/backend/testsの分解定義を先に固定する。

### Phase 2 Plan（対象分解）
- Frontend対象: `03_Implement/frontend/src/domain`（safeMode/diff/validation関連ロジック）と `03_Implement/frontend/tests`。
- Backend対象: `03_Implement/backend/src/kj_atlas_api` のvalidation/service層と `03_Implement/backend/tests`。
- Tests対象: `03_Implement/*/tests` に限定し、実装コード変更は「テスト成立に必要な最小差分」のみ許容する。

### Phase 3 Execute（AC/DoDドラフト提示）
- AC補強ドラフト（合意取得待ち）:
  - AC-F1: frontend/backendで対象モジュール一覧・追加ケース数・未対応理由を同一フォーマットで記録する。
  - AC-F2: Before/Afterのcoverage差分ログを保存し、悪化時はNo-Go。
  - AC-F3: safeMode/validation/diffで回帰検知アサーションを最低1件ずつ保持する。
- DoDドラフト（合意取得待ち）:
  1. unitコマンド実行結果（または代替検証ログ）を残す。
  2. 停止条件（self-correction上限3回・依存未解決時停止）を満たす。
  3. FB-P0依存が未解決ならStatusをDraftのまま据え置く。

### Phase 4 Verify（整合チェック）
- 想定コマンド・代替検証・停止条件の3点が矛盾しないことを確認する。
- self-correctionは最大3回。4回目相当の修復が必要な場合は `held` で停止する。

### Phase 5 Proceed（Fail-safe）
- 依存（FB-P0収束、検証スコープ同期）が未解決の場合はOpen化せずDraft維持で停止する。
- 依存解決後のみ、Owner確定とGo判定を実施する。


## QA-UNIT-01 Draft整備 pass（2026-05-06 / QA-UNIT-01）

### Phase 1 Read
- 対象限定を確認: 本対応は `issue-QA-UNIT-01-unit-test-coverage-improvement.md` のみ編集し、実装コード・他Issueは非編集。
- 依存関係を確認: `issue-FB-P0-2A2B2C-stream-c-planning-baseline` 収束前は Open 化しない。
- 検証レベルを確認: 本Issueの `Expected verification level=unit` を維持し、e2e拡張は非目標。

### Phase 2 Plan（AC/DoD不足補完）
- 補完方針: 既存ACを維持したまま、Open判定時に不足しやすい「測定単位」「停止条件」「証跡保存先」を明文化する。
- 追加AC（Draft）:
  - AC-P1: 対象モジュールごとに `risk tag`（safeMode / validation / diff）を付与し、どの境界を守るテストかを追跡可能にする。
  - AC-P2: 追加テストは「期待挙動」と「回帰シグナル（壊れたときに何で検知するか）」をテストケース単位で記録する。
  - AC-P3: Coverage差分は frontend/backend を別集計で保存し、片系のみ悪化時も No-Go とする。
- DoD補完（Draft）:
  1. AC-M1/M2/M3 と AC-P1/P2/P3 の全項目について、`done / pending / hold` を判定付きで記録する。
  2. Verify指標 `V-UNIT-01/02/03` の記録先（CIログまたは成果物パス）を残す。
  3. self-correction は最大3回、4回目相当は `Stop` とし、未解決理由をIssue本文へ追記する。
  4. 依存未解決（FB-P0未収束 / 検証スコープ未同期）の場合は `Status: Draft` を維持する。

### Phase 3 Execute（計画文書整備のみ）
- 本フェーズでは計画文書のみ更新し、テストコード追加・実装変更・coverage値の新規確定は行わない。
- Open判定に必要な追記チェックリスト（Draft）:
  - [ ] Owner確定（個人またはチーム）
  - [ ] 対象モジュール一覧確定（frontend/backend別）
  - [ ] Before/After計測コマンド確定（環境差分時の代替手順含む）
  - [ ] No-Go時の停止・再開条件確定（self-correction上限含む）

### Phase 4 Verify
- 文書検証観点（docs-only）:
  - AC/DoD/Validation/Stop条件が相互参照で矛盾しない。
  - `Expected verification level=unit` と非目標（e2e拡張なし）が整合している。
  - Go/No-Go/Conditional(Hold) の判定条件が再現可能な表現になっている。
- 検証結果記録ルール:
  - Verifyで未記録項目が1つでも残る場合は Open 化せず Draft 継続。

### Phase 5 Proceed
- Proceed条件:
  1. 依存Issueの前提解消（FB-P0収束 + 検証スコープ同期）。
  2. Owner確定。
  3. AC/DoD/Verify指標の記録導線が埋まっている。
- Proceed不可条件（Fail-safe）:
  - 競合兆候（unit/e2e境界混線、依存差し込み、対象外ファイル編集要求）を検知した場合は `Hold` へ遷移し停止。
