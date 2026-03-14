# Issue Draft: FB-P2C-01-A3 Polygon auto-fit / 実装ハンドオフ

- Type: Feature request
- Status: Ready (Stream B / Awaiting implementation execution lane)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream B
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2C-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2C-02`
- RequirementStatement: `Polygon auto-fit` を 実装 の責務で前進させる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: Gate 0承認済みかつA2で同一入力同一出力の検証を完了している。
  - 操作: A1/A2契約を順守して実装フェーズへ接続する。
  - 期待結果: 契約順序逸脱なしで実装作業へ移行できる。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed（Gate 0承認 + A2 Verify pass を受領）
- DecisionQueueRef（未確定時の参照先）: `DQ-FB-P2C-01` + `A2-HANDOFF-FB-P2C-01-2026-03-14`

## 1) 課題 / Problem statement

- A3は実装接続フェーズであり、A2検証結果を満たす条件でのみ着手可能とする必要がある。
- 契約順序（特にpadding優先）が曖昧なまま実装するとDoD未達に直結するため、着手/停止条件を固定する。

## 2) 背景 / Context

- Backlog基準: `FB-P2C-01` / AC-2C-2, AC-2C-3 / DoD: 同一入力で同一polygonを生成し、padding制約を満たす。
- DoD依存: `02_Architecture/island_shapes.md` deterministic geometry contract。
- 実装拘束: `deterministicTieBreakOrder` は `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小` を固定順として継承する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 検証済み契約を実装に接続し、再作業コストを抑制する。
- 安全（THREAT_MODEL / SafeMode）: 計画段階では既定ポリシーを不変更。
- 企業・行政要件（enterprise_architecture）: 対象外（N/A）だが、契約順序固定により説明責任を担保。
- 後方互換（schemas）: 実装前に契約順序の変更禁止を明示し互換破壊を予防。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（`01_Plans/issues/issue-FB-P2C-01-*.md`）。
- 実行条件: `Gate 0承認 + A2 Verify pass` の両方を満たす場合のみProceed。
- 非目標: 契約順序の再定義、A2未完了での実装着手。

## 5) 受入条件 / Acceptance criteria

- [x] Gate 0承認記録とA2 Verify結果の両方が参照可能である。
- [x] 実装接続時の契約順序（padding遵守優先）が明文化される。
- [x] A2からの入力契約（fixture/比較キー/許容差分）を継承する。
- [x] 検証レベル `integration` が宣言・整合している。
- [x] 編集対象ファイル境界が明記され、他レーンとの重複がゼロである。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: A2 Verify pass を受領し、Plan開始条件を満たす。
- [x] T2: 契約順序逸脱禁止（padding遵守優先）を実装受入条件に固定する。
- [x] T3: 実装フェーズへの引き渡しメモ（入力/出力/失敗時ロールバック）を確定する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo命名・メタ項目が整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: A2未完了で実装に進む → 却下（契約順序逸脱リスク）。
- 代替案B: 実装側で独自tie-break最適化を許可 → 却下（決定論喪失）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 契約順序違反により同一入力同一出力を満たせない。
- 影響範囲: `FB-P2C-01` のDoD未達。
- ロールバック手順:
  1. 実装着手を停止する（Fail-fast）。
  2. A2の比較キーで逸脱点を再検証する。
  3. `outputPolygonHash不一致` / `paddingViolationCount>0` / `tieBreakOrder逸脱` のいずれかを検出した時点でA2へ差し戻す。

## 10) Additional context

- 編集対象ファイル境界: `01_Plans/issues/issue-FB-P2C-01-a3-implementation.md` のみ。
- 競合回避メモ: Stream B は FB-P2C-01 A2/A3 のみ担当し、共有ファイル/FB-P2A/P2B/HIL領域へ非接触。
- Workflow: Plan → Execute → Verify → Proceed（Verify失敗時は最大3回自己修復）。

## 11) Stream B 実行ログ（2026-03-14）

### Phase 1: Read Gate
- Plan:
  - A2/A3を再Readし、Gate0承認・A2前提・A3前提の一致を確認。
- Execute:
  - A1承認状態、A2更新内容、A3開始条件を三点照合。
- Verify:
  - 前提不整合なし（Pass / Self-Correction 0回）。
- Proceed:
  - A3開始条件定義フェーズへ進行。

### Phase 2: A2依存受領
- Plan:
  - A2検証ログの受領可否を判定する。
- Execute:
  - `A2-HANDOFF-FB-P2C-01-2026-03-14` を参照し、input/output契約を取り込む。
- Verify:
  - A2 Verify Pass を確認（Pass）。
- Proceed:
  - 実装ハンドオフ条件の固定へ進行。

### Phase 3: A3（Implementation Handoff）
- Plan:
  - 実装着手条件とロールバック条件を固定し、開始判定を明文化する。
- Execute:
  - **実装着手条件（Start Conditions）**
    1. `GateDecision=approved`（`DQ-FB-P2C-01`）
    2. `A2Verify=pass`（`A2-HANDOFF-FB-P2C-01-2026-03-14`）
    3. `deterministicTieBreakOrder` の順序固定を維持
    4. A2比較キー（`inputHash`, `outputPolygonHash`, `paddingViolationCount`）を実装検証へ継承
  - **ロールバック条件（Rollback Triggers）**
    1. 同一入力で `outputPolygonHash` 不一致
    2. `paddingViolationCount > 0`
    3. tie-break順序の追加/省略/並べ替えの検出
    4. A2で未定義の実装依存判定軸が受入基準に混入
- Verify:
  - 開始条件とロールバック条件がA1/A2契約と整合（Pass）。
- Proceed:
  - A3 planning handoff 完了。実装レーンへ引き渡し可能。

## 12) ADRルール適用記録

- 判定: ADR変更は不要。
- 理由:
  - 本更新はA1で承認済みの `deterministicTieBreakOrder` を再利用し、Context/Decision/Consequences の新規追加を要しない。
  - 契約値変更や上位方針変更を伴わないため、実装前ADR改訂トリガーは発生しない。


## 13) Stream D 実行ログ（2026-03-14）

### Phase 1: Read同期（A1/A2契約再確認）
- Plan:
  - A1/A2/A3の契約順序（`padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小`）とGate状態を再確認する。
- Execute:
  - Read Orderに従って上位文書を再読し、A2 Verify pass・A3開始条件を照合。
- Verify:
  - 前提不整合なし（Pass / Self-Correction 0回）。
- Proceed:
  - A2モック検証結果の実装境界（自己交差ガード）反映へ進行。

### Phase 2: A2モック検証（幾何契約・境界条件）
- Plan:
  - 自己交差polygonを有効polygonとして扱わない境界条件を実装対象へ反映する。
- Execute:
  - `canvas` / `export` で polygon採用判定に自己交差チェックを追加。
  - `IslandView.bounds` / `canvas_svg` のテストに自己交差フォールバックケースを追加。
- Verify:
  - 対象テストで境界条件の期待挙動を確認（Pass）。
- Proceed:
  - 回帰確認フェーズへ進行。

### Phase 3: A3実装（auto-fit本体への安全接続）
- Plan:
  - 既存auto-fit結果の表示/出力で、不正polygonをrectフォールバックに統一する。
- Execute:
  - `IslandView.tsx`: polygon bounds/hit対象の前提に自己交差禁止を導入。
  - `canvas_svg.ts`: SVG exportのpolygon描画条件に自己交差禁止を導入。
- Verify:
  - 正常polygonの描画互換を維持しつつ、自己交差polygonはrect経路へ遷移（Pass）。
- Proceed:
  - Verify（回帰）へ進行。

### Phase 4: Verify（回帰/安全境界）
- 実行:
  - `pnpm -s vitest run src/canvas/IslandView.bounds.test.ts src/export/canvas_svg.test.ts src/domain/stream_d_p2c_mock_validation.test.ts`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 結果:
  - すべてPass（Self-Correction: 2回、上限3回以内）。

### Phase 5: Proceed（監査ログ整理）
- 実施内容:
  - 本節へ実行ログを追記し、Plan→Execute→Verify→Proceedのトレースを固定。
  - 失敗→修復履歴（import名不一致、テスト文字列エスケープ）を明示し監査可能化。

## 14) Stream F 実行ログ（2026-03-14）

### Phase 1: Read同期（Gate0/A2 Verify/tie-break固定順）
- Plan:
  - A2/A3ハンドオフと実装差分を再照合し、固定順序逸脱がないことを確認する。
- Execute:
  - `deterministicTieBreakOrder` と比較キー（`inputHash`, `outputPolygonHash`, `paddingViolationCount`）の継承要件を確認。
- Verify:
  - Gate0承認 + A2 Verify pass の前提一致を確認（Pass）。
- Proceed:
  - polygon auto-fit 実装接続へ進行。

### Phase 2: 実装接続（A2ハンドオフ準拠）
- Plan:
  - canvas edge描画経路を `geometry/shape` 統一参照に接続し、不正polygonのフォールバックを固定化する。
- Execute:
  - `EdgeLayer.tsx` に `getRenderableIslandPolygonPoints` を追加し、
    - `getIslandPolygonPoints`（geometry優先）
    - `isSelfIntersectingPolygon`（自己交差排除）
    を通過したpolygonのみ centroid/anchor 計算へ利用するよう接続。
- Verify:
  - polygon妥当時は既存挙動維持、自己交差時はrect中心フォールバックへ遷移（Pass）。
- Proceed:
  - deterministic geometry 回帰テスト追加へ進行。

### Phase 3: Verify（同一入力同一出力 / padding順守）
- Plan:
  - 既存A2由来テストと新規回帰テストで、決定論と境界フォールバックを同時検証する。
- Execute:
  - `EdgeLayer.polygon_anchor.test.ts` を追加し、
    1. geometry優先の決定論
    2. 自己交差polygonの空配列フォールバック
    を検証。
- Verify:
  - 対象vitestと issue memo validator がPass（Self-Correction 0回）。
- Proceed:
  - 実装逸脱なしでA3を継続可能。

### Phase 4: Proceed（逸脱時差戻し条件の維持）
- `outputPolygonHash不一致` / `paddingViolationCount>0` / `tieBreakOrder逸脱` を検出した場合はA2へ差戻し、の運用を継続。
