# Issue Draft: QA-UNIT-01 ユニットテストのカバレッジ向上

- Type: Process
- Status: Draft (起票用)
- Source Issue: N/A
- Priority: P2
- Owner: Stream G (planning only)
- Dependencies: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`（P0収束後に着手）, `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`（検証スコープ同期）
- Scope: `01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`（本フェーズは計画文書更新のみ / 実装禁止）
- Start Gate (fixed): FB-P0収束完了 + HIL-RS-02計画同期完了まで `Draft/Hold` を維持する。
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
- DecisionStatus: Hold-for-Dependency-Gate
- DecisionQueueRef: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`
- DependencyLockPolicy: FB-P0収束 + HIL-RS-02計画同期完了まで Draft/Holdを維持し、テスト実装・閾値導入・CI変更を開始しない。

## Stream G phase protocol（dependency-locked planning）

固定フェーズ: Read同期 → AC/DoD具体化 → 依存条件の明記 → Verify → Proceed

- Read同期: ADR-0001 / ADR-0019 / 本IssueメタI/Fを毎回再確認。
- AC/DoD具体化: coverage「改善」ではなく、非悪化 + 観点網羅 + 記録完全性で判定式化。
- 依存条件の明記: 解除条件を明文化し、解除前の作業上限を docs-only に固定。
- Verify: 実行ではなく「検証可能性（コマンド・指標・No-Go条件）」の整備状況を確認。
- Proceed: dependency-locked のため本フェーズは `Proceed=Not Allowed`。

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
- [ ] AC-M4: dependency lock 未解除時は、変更対象を計画文書のみに制限する統制文を保持する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 現状テストの薄いモジュール抽出方法と優先順位付けルールを固定する（計画）。
- [ ] T2: Frontend追加候補（safeMode/validation/diff）をケース粒度で列挙する（計画）。
- [ ] T3: Backend追加候補（validation/service）をケース粒度で列挙する（計画）。
- [ ] T4: Verifyで使う測定ログ様式（Before/After/Assertion count）を固定する（計画）。

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

## 11) Proceed gate（dependency lock）

- Proceed = Not Allowed（現状態固定）
- Proceed可能化条件（全て必須）
  1. FB-P0収束 Go
  2. HIL-RS-02 計画同期完了
  3. AC-M1〜M4 と V-UNIT-01〜03 の記録テンプレート確定
  4. 実装着手前レビューで `DecisionStatus` を Hold から Ready に更新


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
  - docs-check証跡（`git diff --check` / `validate_active_issue_memos.py`）を残し、実行不能時は阻害要因を記録する。
- Self-correction: `3/3`（これ以上の自己修復は **Stop**）。

### Phase 5 Proceed
- ProceedDecision: **Hold（通常）**
- Hold条件:
  1. 依存 `issue-FB-P0-2A2B2C-stream-c-planning-baseline` 未収束。
  2. `issue-HIL-RS-02-next-phase-delivery-plan` との検証スコープ同期未完了。
  3. AC-M1/M2/M3 または AC-P1/P2/P3 のいずれかが `pending/hold`。
- Open化判定（Ready条件）:
  - 依存2件が解消され、Ownerが確定し、`V-UNIT-01/02/03` の記録先が確定していること。
- Stop条件:
  - self-correction 4回目相当が必要、または unit/e2e 境界が解消不能な競合状態になった場合。
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


## Stream D QA pass（2026-05-06 / UNIT拡張計画独立推進）

### Phase 1: Read & ギャップ抽出
- Draft維持前提（依存解消前はOpen化しない）を再確認。
- ギャップ抽出:
  1. 回帰/境界/性能の優先順が明示的な番号付きで固定されていない。
  2. 実行手順と完了条件（誰が証跡を残すか）が分離している。
  3. 他レーン非干渉（E2E側との境界）確認が明文化不足。

### Phase 2: AC/DoDドラフト提示・合意（docs-only）
- AC追記ドラフト:
  - AC-DU1: 回帰優先として safeMode/validation/diff の3観点で失敗検知アサーションを必須化。
  - AC-DU2: 境界優先として security境界に触れるケースは「fail時の期待シグナル」を併記。
  - AC-DU3: 性能優先として unit実行時間のBefore/After比較を記録（悪化時は要因分析）。
- DoD追記ドラフト:
  1. frontend/backend別の追加件数・coverage差分・失敗シグナルを1表で管理する。
  2. Verifyで `V-UNIT-01/02/03` 未記録があれば即No-Go。

### Phase 3: テスト観点の優先順位付け（回帰/境界/性能）
1. 回帰: safeMode/validation/diff の回帰検知アサーション充足。
2. 境界: fail-closed/拒否系の期待挙動を明示し、曖昧なpass条件を禁止。
3. 性能: coverage取得込みのunit実行時間を比較し、顕著悪化時に分割実行案を添付。

### Phase 4: 実行手順と完了定義の明文化
- 実行手順（実装フェーズ適用）:
  1. `cd 03_Implement/frontend && npm test -- --runInBand`
  2. `cd 03_Implement/backend && pytest -q`
  3. `cd 03_Implement/frontend && npm run test -- --coverage --runInBand`
  4. `cd 03_Implement/backend && pytest --cov=src --cov-report=term-missing`
  5. `python 01_Plans/issues/validate_active_issue_memos.py`
- 完了定義:
  - V-UNIT-01/02/03 記録完了。
  - coverage差分非負（対象モジュール）を満たす。
  - self-correction は `<=3`、超過見込みでStop。

### Phase 5: Verify（他レーン非干渉確認）
- 非干渉チェック:
  - 本更新は `issue-QA-UNIT-01` の計画本文のみ。
  - 実装コード・E2E仕様・他Issueは未編集。
  - unit/e2e境界を跨ぐ要求は Hold 扱いで停止。
- Fail-safe:
  - 不整合・依存崩壊時は停止して指示待ち。
  - 自己修復は3回まで。4回目相当でStop。


## Stream F alignment pass（2026-05-06 / QA-UNIT-01）

### Plan→Execute→Verify→Proceed（docs-only）
- Plan: Draft整備に限定し、QA-UNIT-01のAC/DoD/Verify指標をOpen判定用に再読可能化する。
- Execute: `Expected verification level: unit` を維持し、e2e拡張や実装変更を非目標として固定する。
- Verify: 依存未解決（FB-P0収束前/検証スコープ未同期）では `Status: Draft` と `Proceed: Hold` を継続する。
- Proceed: 依存解決・Owner確定・指標記録導線の3条件が揃うまで進めない。

### ADR要素（C/D/C）
- Context: Draft段階で実装に踏み込むと、unit/e2e境界の混線と再作業が発生する。
- Decision: 本Issueは提案文書の品質整備に限定し、実装着手は承認後に分離する。
- Consequences: QA-UNIT実装時の着手条件と停止条件が明確化され、過剰実装リスクを低減する。


## Stream F unblock criteria update（2026-05-06 / execution readiness）

### Phase 1 Read（停止要因の確定）
- 停止要因を `FB-P0収束待ち` と `QA-E2Eスコープ同期待ち` の2点に固定する。

### Phase 2 AC/DoD補完（解除条件）
- Open化解除条件（全件必須）:
  - [ ] U1: `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` が `Status: Ready-for-Implementation` 以上である。
  - [ ] U2: 本Issueの Owner が個人または実行チーム名で確定している。
  - [ ] U3: Frontend/Backendの対象モジュール一覧と risk tag（safeMode/validation/diff）が記録済み。
  - [ ] U4: AC-M1/M2/M3 と AC-P1/P2/P3 の判定欄（done/pending/hold）が全て埋まっている。

### Phase 3 Validation plan（コマンド確定）
- 準備完了判定コマンド（docs-only）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`
  - `rg -n "^\- Status:|^\- Owner:|AC-M[123]|AC-P[123]|V-UNIT-0[123]" 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`
  - `git diff --check -- 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`

### Phase 4 Verify
- Verify合格条件: 上記3コマンドが成功し、U1〜U4が全てチェック済み。
- 失敗時: self-correction は最大3回、4回目相当は `Stop`。

### Phase 5 Proceed
- 判定: **Hold維持**（2026-05-06時点で依存証跡未添付）。
- Open化条件: U1〜U4完了時に `Status: Ready-for-Implementation` へ更新可。

## Stream I execution pass（2026-05-06 / QA-UNIT-01 Draft整備専任）

### Phase 1 Read（依存・着手条件の同期）
- 現在状態を再確認: `Status: Draft` / `Priority: P2` / `Expected verification level: unit` を維持する。
- 依存整合:
  - P0依存: `issue-FB-P0-2A2B2C-stream-c-planning-baseline` が `Open` 継続中のため、本Issueは **Open化しない**。
  - P1依存: `issue-HIL-RS-02-next-phase-delivery-plan` が `Draft` のため、検証スコープ同期完了までは **Hold** 維持。
- 非対象境界: 本レーンは Draft文書整備のみ。`03_Implement/**`・他Issue編集は禁止。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: 上流（P0/P1）の契約・運用ゲート未確定でQA実装を先行すると、unit/e2e境界の再試験コストが増大する。
- Decision: Draft段階では「対象範囲」「優先テスト軸」「ゲート条件」のみ固定し、実装着手判断は依存解消後に限定する。
- Consequences: 品質戦略を前倒しで提示しつつ、上流未確定事項との衝突を回避できる。

### Phase 3 Plan（AC / DoD 明確化）
- AC-I1（対象分類）:
  - Frontend: `src/domain` 系の safeMode / validation / diff。
  - Backend: validation / service 層。
  - いずれも「追加ケース数（最低1件）」を分類単位で記録する。
- AC-I2（最小改善目標）:
  - Coverageは対象モジュール単位で Before/After を比較し、**差分非負（悪化なし）** を最低条件とする。
- AC-I3（除外条件）:
  - e2eシナリオ拡張、実装リファクタ、新機能追加は本Issueの対象外として固定する。
- DoD-I1（着手条件）:
  - `issue-FB-P0-2A2B2C-stream-c-planning-baseline` が `Ready-for-Implementation` 以上。
  - `issue-HIL-RS-02-next-phase-delivery-plan` が unit検証境界と矛盾しない状態（Draft解除済みまたは同等の承認記録あり）。
- DoD-I2（完了判定式）:
  - `Done = (U1 && U2 && U3 && AC-M1..M3 done && AC-P1..P3 done && AC-I1..I3 done && V-UNIT-01..03 recorded && self-correction<=3)`。

### Phase 4 Execute（docs-only）
- 実施内容: Draft本文に着手条件・完了判定式・除外条件を明文化。
- 非実施内容: テストコード追加、実装コード変更、coverage実測値の新規確定。

### Phase 5 Verify（依存整合・優先度整合・非対象明記）
- Verify-V1: P0/P1依存が未解消なら `Proceed=Hold` を維持する記述になっている。
- Verify-V2: 優先軸は `safeMode -> validation -> diff` の順で回帰検知観点が残っている。
- Verify-V3: 非対象（e2e拡張/実装変更/他Issue編集）が明示されている。
- Verify-V4: self-correction上限は `<=3`、4回目相当は `Stop` を維持。

### Phase 6 Proceed（Open化可否 / 保留理由 / 次アクション）
- Open化可否: **不可（現時点）**。
- 保留理由:
  1. P0依存Issueが `Open` で収束未了。
  2. P1依存Issueが `Draft` でスコープ同期未了。
- 次アクション（依存解消後に再判定）:
  1. U1〜U4 + AC-M/P/I + V-UNIT 指標記録先の充足確認。
  2. 充足済みなら `Status: Ready-for-Implementation` への更新を審査。

## Stream H Ready化 pass（2026-05-06 / QA-UNIT-01）

### 1. Read同期
- `Expected verification level=unit` と `Non-goals=e2e拡張なし` の境界を再固定。
- 依存2件（FB-P0収束 / HIL-RS-02検証スコープ同期）が未解決のため、実装着手は不可。

### 2. Plan（AC/DoD不足補完）
- Open/Ready判定に使う不足項目を固定:
  - RQ-1: Owner（個人またはチーム）確定。
  - RQ-2: Frontend/Backend対象モジュール一覧の確定。
  - RQ-3: `V-UNIT-01/02/03` の記録先（CIログ or artifact path）確定。
  - RQ-4: No-Go時の再開条件（再実行コマンド / 停止理由テンプレ）確定。

### 3. Execute（Ready化の判定基準明示）
- Ready判定基準（全件必須）:
  - [ ] RG-UNIT-1: AC-M1/M2/M3 + AC-P1/P2/P3 の評価欄が `done/pending/hold` で埋まっている。
  - [ ] RG-UNIT-2: `Go/NoGo/Conditional(Hold)` の判定トリガーが再現可能な文章で記載されている。
  - [ ] RG-UNIT-3: `self-correction <=3` と 4回目相当Stop条件が明示されている。
  - [ ] RG-UNIT-4: unit実行コマンド4本と代替検証手段が矛盾なく併記されている。

### 4. Verify（品質ゲート定義・E2E導線）
- 品質ゲート:
  - Gate-Q1: `VerificationLevel=unit` と `GoNoGoGate=Optional` が整合。
  - Gate-Q2: SafeMode境界（safeMode/validation/diff）の回帰検知要件が3観点で定義済み。
  - Gate-Q3: docs-check証跡（validator/rg/diff-check）が記録可能。
- E2E導線の境界定義:
  - 本Issueは unit専任であり、E2E要求は `ADR-0019` と `DOC-OPS-05-06` 側へ委譲する。

### 5. Proceed
- ProceedDecision: **Hold（Ready gate定義完了、依存解消待ち）**
- Ready化状態: **判定基準はReady、着手状態はHold**

## Stream E Open化準備 pass（2026-05-07 / QA-UNIT-01）

### Phase 1 Start Re-read
- 対象再読: 本Issueを再読し、`Draft維持`・`Expected verification level: unit`・依存2件未解決を確認。
- 境界再確認: 本フェーズはP2 Draft整備のみで、実装/テスト追加は非実施。

### Phase 2 Plan（AC/DoD不足提案）
- AC/DoD不足提案（合意待ち）:
  - 提案A: AC-M1 の「追加ケース数」を frontend/backend別に `0可否` ルール付きで明記。
  - 提案B: DoDに「Owner未確定時はGo判定禁止」を明文化。
  - 提案C: Verify指標 V-UNIT-02 の記録フォーマット（Before/After/差分）を固定。
- 合意状態: 依存解決後に最終合意し反映する前提で提案保持。

### Phase 3 ADR明文化（C/D/C）
- Context: 依存未解決状態でQA-UNITをOpen化すると、unit/e2e境界と着手順が混線する。
- Decision: 本IssueはDraftのまま判定情報を整備し、依存解決前は `Hold` を固定する。
- Consequences: 実装先行を防ぎ、後続で再現可能なGo/NoGo判断を維持できる。

### Phase 4 Execute（docs-only）
- 実施: 本Issueメモへの追記のみ。
- 非実施: frontend/backendコード変更、unit test追加、coverage再計測。

### Phase 5 Verify
- 判定: `Hold` 維持（依存未確定）。
- self-correction: `1/3`（Stream E pass）。
- 失敗時方針: 3回まで修復、4回目相当で `Stop`。

### Phase 6 Proceed
- ProceedDecision: **Hold**
- Stop条件（再確認）:
  1. 依存2件の前提矛盾が解消不能。
  2. unit/e2e境界競合が解消不能。
  3. self-correction上限超過。


## Stream H dependency lock (2026-05-07 / planning freeze)

- 本Issueは QA計画確定専用とし、実装・テスト追加は実施しない。
- 依存固定（Go条件）:
  1. `issue-FB-P0-2A2B2C-stream-c-planning-baseline` の収束完了。
  2. `issue-HIL-RS-02-next-phase-delivery-plan` の計画同期完了（A1依存/Decision Queue条件を反映）。
  3. unit/e2e 境界が再確認され、QA-E2E-USE-01 と優先順位矛盾がない。
- 優先順位（固定）: FB-P0収束確認 → HIL-RS-02同期確認 → QA-UNIT実装着手判定。
- ProceedDecision（現時点）: **Hold**。
- Stopper: 上記依存のいずれか未解消、または依存証跡なしでOpen化要求が出た場合は即Stop。
