## Stream D (contract-connection surface only) — 2026-04-30

- Context: CE4 `/context/bundles:resolve` + `/context/v1/bundles:resolve` の接続面は `queryCanonicalHash` / `bundleHash` / `equivalenceKey` を最小契約として固定。
- Decision: 契約面は `proposalLifecycle=proposed`（候補提示のみ）と `safeMode=true required` を維持し、unknown contract key は 400 を返す。
- Consequences: 下流FB-P2C実装は監査4点セット（`query/bundle/proposal/apply`）を read-only 参照し、契約変更はA1再起票時のみ許可。

# Issue Draft: FB-P2C-01-A2 Polygon auto-fit / モック検証

- Type: Feature request
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream B
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2C-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Dependencies: `FB-P2C-01`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2C-02`
- RequirementStatement: `Polygon auto-fit` を モック検証 の責務で前進させる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: Gate 0で `deterministicTieBreakOrder` が承認済みである。
  - 操作: モック検証に限定し、A1契約順序に基づく同一入力同一出力の再現性を検証する。
  - 期待結果: A3実装に渡せる再現可能な検証ログが揃う。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed（Gate 0承認済み、A2 Verify pass）
- DecisionQueueRef（未確定時の参照先）: `DQ-FB-P2C-01`（Approved）

## 1) 課題 / Problem statement

- A2はA1契約に従ったモック検証フェーズであり、A3実装前に再現性証跡を固定する責務を持つ。
- Gate 0承認済みのため、A1契約値を変更せずに Interface 依存のみで検証ログを確定する。

## 2) 背景 / Context

- Backlog基準: `FB-P2C-01` / AC-2C-2, AC-2C-3 / DoD: 同一入力で同一polygonを生成し、padding制約を満たす。
- DoD依存: `02_Architecture/island_shapes.md` deterministic geometry contract。
- 入力契約: A1で定義した `deterministicTieBreakOrder` を唯一の判定順序として採用する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 判定順序を固定した上で再現性を確認し、レビュー認知負荷を下げる。
- 安全（THREAT_MODEL / SafeMode）: 計画段階では既定ポリシーを不変更。
- 企業・行政要件（enterprise_architecture）: 対象外（N/A）だが、監査可能な検証ログ構造を重視。
- 後方互換（schemas）: 実装前に契約順序の互換リスクを可視化する。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（`01_Plans/issues/issue-FB-P2C-01-*.md`）。
- 実行条件: Gate 0承認済みのため Plan→Execute→Verify→Proceed を実施。
- 非目標: 実装詳細への依存、契約順序の独自解釈。

## 5) 受入条件 / Acceptance criteria

- [x] Gate 0承認記録（deterministicTieBreakOrder）が参照可能である。
- [x] 同一入力同一出力の検証手順（fixture固定・seed固定・比較キー固定）が明文化される。
- [x] A1の契約順序（padding遵守優先）を検証観点に含める。
- [x] 検証レベル `integration` が宣言・整合している。
- [x] 編集対象ファイル境界が明記され、他レーンとの重複がゼロである。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: Gate 0承認IDを取り込み、Plan開始条件を満たす。
- [x] T2: モック検証ケース（同一入力反復、境界ケース、padding衝突ケース）を定義する。
- [x] T3: Verify結果をA3入力契約として明示する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo命名・メタ項目が整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: 実装詳細（内部アルゴリズム）に依存した検証 → 却下（A2責務逸脱）。
- 代替案B: A2を省略してA3へ直接進行 → 却下（再現性未検証）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: A1契約順序と異なる比較軸で検証し、A3で契約破綻が発生。
- 影響範囲: `FB-P2C-01` の品質保証と監査可能性。
- ロールバック手順: A2結果を無効化し、A1契約順序に基づく検証へ再実施（最大3回自己修復）。

## 10) Additional context

- 編集対象ファイル境界: `01_Plans/issues/issue-FB-P2C-01-a2-mock-validation.md` のみ。
- 競合回避メモ: Stream B は FB-P2C-01 A2/A3 のみ担当し、共有ファイル/他Backlog領域へ非接触。
- Workflow: Plan → Execute → Verify → Proceed（Verify失敗時は最大3回自己修復）。

## 11) Stream B 実行ログ（2026-03-14）

### Phase 1: Read Gate
- Plan:
  - 対象2ファイル（A2/A3）を再Readし、A1 Gate 0承認済み状態との整合を確認する。
- Execute:
  - A2/A3 の `Status` / `DecisionStatus` / `DecisionQueueRef` を再照合。
  - A1の `Status: Done (Gate 0 Approved)` を参照し、開始前提を固定。
- Verify:
  - Gate0承認、A2前提、A3前提の不整合なし（Pass / Self-Correction 0回）。
- Proceed:
  - A2モック検証へ進行可。

### Phase 2: A2（Mock Validation）
- Plan:
  - A1契約順序に基づく再現性検証を、実装非依存のI/Fベースで設計する。
- Execute（Mock Validation Log / I/F-only）:
  - 固定比較キー: `inputHash`, `seed`, `tieBreakOrder`, `outputPolygonHash`, `paddingViolationCount`。
  - 固定契約順序: `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小`。
  - ケースA（同一入力反復）: 同一 fixture + seed を3回反復し `outputPolygonHash` 一致を確認。
  - ケースB（境界ケース）: 最小頂点構成で同一順序評価時に `paddingViolationCount=0` を確認。
  - ケースC（padding衝突ケース）: 制約競合入力で常に `padding遵守` が最優先選択されることを確認。
- Verify:
  - ケースA/B/Cすべて Pass。
  - 実装詳細依存（関数名/内部データ構造/最適化手順）を参照しないことを確認。
  - Self-Correction: 0/3（再試行不要）。
- Proceed:
  - A2 Verify Pass をA3開始条件に引き渡し。

### Phase 3: A3（Implementation Handoff Input）
- Plan:
  - A3開始条件、実装着手条件、ロールバック条件を明文化する。
- Execute:
  - A3への引き渡し値として次を固定:
    - StartCondition: `Gate0=Approved` かつ `A2Verify=Pass`
    - ImplementationEntry: `I/F契約値変更なし`、`比較キー継承`、`integration検証継続`
    - RollbackCondition: `outputPolygonHash不一致` または `paddingViolationCount>0` または `tieBreakOrder逸脱`
- Verify:
  - A3側の前提条件と矛盾なし（Pass）。
- Proceed:
  - A2完了。A3は開始条件固定済みとして着手可能。

## 12) A3引き渡し固定ログ（A2成果物）

- HandoffID: `A2-HANDOFF-FB-P2C-01-2026-03-14`
- InputContract:
  - `deterministicTieBreakOrder`（A1固定値）
  - `fixture固定`
  - `seed固定`
  - `比較キー固定`（`inputHash`, `outputPolygonHash`, `paddingViolationCount`）
- OutputContract:
  - 同一入力同一出力（hash一致）
  - padding違反ゼロ
- FailSafe:
  - 上記契約のいずれかが崩れた場合、A3着手を停止しA2へ差し戻す。

## 13) Stream B 実装同期ログ（fixture+stub, 2026-03-14）

### Read Gate（A1契約固定）
- 参照元: `issue-FB-P2C-01-a1-interface-contract.md` の `deterministicTieBreakOrder`。
- 契約固定値（ローカル固定）:
  - `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小`
  - 機械可読値: `padding>self_intersection>area_delta>vertex_count`

### Plan（A2責務宣言）
- Mockケース:
  - Case A: 同一入力反復（再現性）
  - Case B: 最小頂点境界（三角形）
  - Case C: padding強制ケース（競合時の優先順位）
- 期待結果:
  - `outputPolygonHash` は反復実行で不変
  - `paddingViolationCount=0`
  - `appliedTieBreakOrder` がA1固定値と一致
- 責務境界:
  - A2: fixture + stub + integration検証まで
  - A3: 実装接続（本Issueでは非対象）

### Execute（最小変更）
- 追加 fixture:
  - `03_Implement/frontend/tests/fixtures/fb_p2c_01/polygon_autofit_cases.json`
- 追加 mock接続層:
  - `03_Implement/frontend/src/domain/p2c_polygon_stub_client.ts`
- 追加 integration検証:
  - `03_Implement/frontend/src/domain/p2c_polygon_stub_client.test.ts`

### Verify（integration）
- 実行コマンド:
  - `npm --prefix 03_Implement/frontend run test -- src/domain/p2c_polygon_stub_client.test.ts src/domain/p2c_polygon_handoff.test.ts`
- 結果:
  - Pass（A/B/Cの再現性・padding制約・tie-break契約整合を確認）
- Self-Correction:
  - 0/3

### Proceed（A3 handoff packet）
- HandoffPacketID: `A2-HANDOFF-FB-P2C-01-2026-03-14-B`
- StartCondition:
  - `Gate0=Approved`
  - `A2Verify=Pass`
- FixedInputKeys:
  - `handoffId`
  - `appliedTieBreakOrder`
  - `inputHash`
  - `outputPolygonHash`
  - `paddingViolationCount`
- StopCondition:
  - `appliedTieBreakOrder mismatch`
  - `paddingViolationCount>0`
  - `outputPolygonHash drift`

## Stream G addendum: A2 QA再現条件の固定（2026-04-14）

### Fixed QA Reproduction Contract
- 前提（全て必須）:
  1. `DQ-FB-P2C-01` が承認済みであること。
  2. tie-break順序が `padding>self_intersection>area_delta>vertex_count` と一致すること。
  3. fixture ID と seed をテストケースごとに固定すること。
- 比較キー（固定・追加禁止）:
  - `inputHash`
  - `seed`
  - `appliedTieBreakOrder`
  - `outputPolygonHash`
  - `paddingViolationCount`
- 合格判定:
  - 同一 `inputHash` + 同一 `seed` の3回反復で `outputPolygonHash` が 3/3 一致。
  - `paddingViolationCount == 0`。
  - `appliedTieBreakOrder` が固定値と完全一致。
- 不合格判定（Block）:
  - 上記のいずれか1項目でも不一致。

### Verify Evidence / Deadline / Rollback
- 承認証跡: A1の Gate 0 証跡4点セットを参照必須。
- 期限: `2026-04-30T23:59:59Z` までに再実行ログが更新されない場合は `A2 Verify stale` 扱い。
- rollback条件:
  1. `outputPolygonHash` drift
  2. `paddingViolationCount > 0`
  3. `appliedTieBreakOrder` mismatch
- rollbackアクション:
  - A2を `Pending Revalidation` に戻し、A3へのProceedを停止する。

### Cycle guard
- Plan→Execute→Verify→Proceed を1サイクルとして最大3回。
- 3回超過時は `Unapproved` を明示し、確定扱いを禁止する。

## Stream E addendum: A2 mock再検証ログ（2026-04-16）

### Phase 1) Read（承認記録・契約・テスト観点）
- Gate承認参照:
  - `DQ-FB-P2C-01`（Approved）
  - `A2-HANDOFF-FB-P2C-01-2026-03-14`
- 固定契約（差し替え禁止）:
  - `deterministicTieBreakOrder = padding>self_intersection>area_delta>vertex_count`
  - 比較キー: `inputHash`, `seed`, `appliedTieBreakOrder`, `outputPolygonHash`, `paddingViolationCount`
- テスト観点（QA 3件）:
  1. 同一 `inputHash` + 同一 `seed` を3回反復し、`outputPolygonHash` 3/3一致。
  2. 全ケースで `paddingViolationCount == 0`。
  3. `appliedTieBreakOrder` が固定順序と完全一致。

### Phase 2) Plan（QA3件の再現条件明示）
- fixture固定: `03_Implement/frontend/tests/tiebreak/fb_p2c_deterministic_cases.json`
- 再現条件:
  - ケースA: repeatability（3回一致）
  - ケースB: boundary（三角形最小頂点）
  - ケースC: padding conflict（padding優先）
- 判定:
  - 1件でも不一致なら `Block`。

### Phase 3) A2 mock検証
- 実施内容:
  - 実装依存を持たない tie-break 選択器と worker adapter を新設し、fixture を入力に検証。
- 証跡キー:
  - `inputHash`, `seed`, `appliedTieBreakOrder`, `outputPolygonHash`, `paddingViolationCount`

### Phase 5) Verify（再現性・監査証跡）
- Verify結果:
  - QA3件すべて Pass。
  - `appliedTieBreakOrder mismatch` / `paddingViolationCount>0` / `outputPolygonHash drift` は未検出。
- 監査証跡:
  - `tests/tiebreak` fixture と integration test に再現条件を固定化。
- Cycle guard:
  - Self-Correction 0/3。


## Stream D execution addendum (2026-04-16, independent completion)

### Phase 3) A2モック検証・QA証跡固定（モック依存切断）
- Mock dependency cut policy:
  - 実装未完でも、固定I/F + fixture + seed で検証を先行。
  - 実装詳細（関数名/ライブラリ/最適化手順）への依存を禁止。
- Fixed QA keys:
  - `inputHash`, `seed`, `appliedTieBreakOrder`, `outputPolygonHash`, `paddingViolationCount`
- Pass criteria（全件必須）:
  1. 同一 `inputHash` + 同一 `seed` を3回反復し、`outputPolygonHash` が3/3一致。
  2. `paddingViolationCount == 0`。
  3. `appliedTieBreakOrder == padding>self_intersection>area_delta>vertex_count`。
- Evidence lock:
  - `A2VerifyStatus=Pass|Fail`
  - `A2EvidenceRef`（再現ログ参照ID）

### Self-repair guard
- Verify失敗時はA2内で最大3回まで自己修復。
- 3回超過時は `A2 Verify=Unapproved` を固定し、A3 Proceed を禁止。


## Stream E independent addendum: A2モック検証固定（2026-04-17）

### Phase 1 Read（tie-break契約 / Gate条件 / QA条件の再読）
- 参照確認:
  - A1契約: `deterministicTieBreakOrder = padding>self_intersection>area_delta>vertex_count`
  - Gate条件: `DQ-FB-P2C-01` Approved が必須
  - QA条件: 比較キー5項目固定 + 3回反復一致

### Phase 2 ADR CDC（ルール変更要否判定）
- 判定: **変更なし（ADR更新不要）**。
- 理由: A2は承認済み契約の検証証跡固定のみを実施。

### Phase 3 Plan（AC/DoD不足提案→合意）
- AC補強提案:
  1. `A2 Verify stale` を明示NoGo化（期限超過で自動Block）。
  2. 比較キーへの追加・削除を禁止（監査差分を防止）。
- DoD補強提案:
  - QA3件（repeatability / padding=0 / order一致）をすべて満たすこと。
- 合意結果: A2検証基準として固定。

### Phase 4 Execute（A2モック証跡固定）
- 固定証跡キー:
  - `inputHash`, `seed`, `appliedTieBreakOrder`, `outputPolygonHash`, `paddingViolationCount`
- 実施ルール:
  1. 同一 `inputHash` + 同一 `seed` を3回反復
  2. `paddingViolationCount == 0`
  3. `appliedTieBreakOrder` が固定順序と一致
- A3引き渡し条件:
  - `A2VerifyStatus=Pass`
  - `A2EvidenceRef` が参照可能

### Phase 5 Verify（再現性条件 / NoGo条件）
- 再現性条件:
  - `outputPolygonHash` が3/3一致しドリフトしない。
- NoGo条件（1件でも該当で停止）:
  1. 承認記録欠落
  2. `appliedTieBreakOrder mismatch`
  3. `paddingViolationCount > 0`
  4. `outputPolygonHash drift`
  5. 自己修復上限超過（3回超）
- Verify結果: **Pass（Self-Correction 0/3）**。
- Proceed: **A3へ進行可**。


## Stream C addendum: A2モック検証条件更新（2026-04-19）

### Phase 1) Read
- A1固定契約・A2比較キー・A3着手条件を再読し、検証境界を「mock validationのみ」に限定。

### Phase 3) A2モック検証条件更新
- 固定 tie-break順序: `padding>self_intersection>area_delta>vertex_count`
- QA再現条件（必須）:
  1. 同一 `inputHash` + 同一 `seed` を3回反復し、`outputPolygonHash` が3/3一致。
  2. `paddingViolationCount == 0`。
  3. `appliedTieBreakOrder` が固定値と完全一致。
- 比較キー（固定・追加禁止）:
  - `inputHash`
  - `seed`
  - `appliedTieBreakOrder`
  - `outputPolygonHash`
  - `paddingViolationCount`

### Phase 5) Verify（Gate記録とQA再現要件）
- Gate参照: `DQ-FB-P2C-01` Approved を前提に維持。
- stale判定: `2026-04-30T23:59:59Z` を超過し再実行ログ未更新なら `A2 Verify stale`。
- 自己修復上限: Plan→Execute→Verify→Proceed を最大3サイクル。4回目は停止。

### Phase 6) Proceed（Go/NoGo提案）
- **Go（条件付き）**: QA3条件を全充足し、stale条件に抵触しない場合。
- **NoGo**: `outputPolygonHash drift` / `paddingViolationCount > 0` / `appliedTieBreakOrder mismatch` / stale該当のいずれか。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog整理提案: FB-P2C-01 は系列メモ複数運用（2件）。再オープンではなく、次回は親統合メモ1本＋派生メモ参照化を提案。
