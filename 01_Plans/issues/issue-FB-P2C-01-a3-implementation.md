# Issue Draft: FB-P2C-01-A3 Polygon auto-fit / 実装ハンドオフ

- Type: Feature request
- Status: Done (Stream C / P2C-A3 implementation)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` + `03_Implement/frontend/src/domain/**`（P2C-A3実装）
- Related Backlog: `FB-P2C-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/island_shapes.md`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2C-02`
- RequirementStatement: `Polygon auto-fit` の A3 を、契約順序固定 + backend接続準備で前進させる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: Gate 0承認済みかつA2で同一入力同一出力の検証を完了している。
  - 操作: A1/A2契約を順守し、API/Schema依存だけを分離したハンドオフテンプレへ接続する。
  - 期待結果: 契約順序逸脱なしで実装レーンが着手可能になる。
  - 除外: A1/A2契約本文の変更、shared resource 3ファイル、運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed（Gate 0承認 + A2 Verify pass を受領）
- DecisionQueueRef（未確定時の参照先）: `DQ-FB-P2C-01` + `A2-HANDOFF-FB-P2C-01-2026-03-14`

## 1) 課題 / Problem statement

- A3は実装接続フェーズであり、A2検証結果を満たす条件でのみ着手可能とする必要がある。
- 契約順序（特にpadding優先）が曖昧なまま実装するとDoD未達に直結するため、着手/停止条件を固定する。
- backend接続準備は API/Schema 依存だけを切り出し、実装レーンへ委譲可能な粒度に分離する。

## 2) 背景 / Context

- Backlog基準: `FB-P2C-01` / AC-2C-2, AC-2C-3 / DoD: 同一入力で同一polygonを生成し、padding制約を満たす。
- DoD依存: `02_Architecture/island_shapes.md` deterministic geometry contract。
- API依存: `02_Architecture/api.md` の DocumentV1 I/F 契約。
- Schema依存: `02_Architecture/schemas.md` の polygon表現・互換条件。
- 実装拘束: `deterministicTieBreakOrder` は `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小` を固定順として継承する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 検証済み契約を実装に接続し、再作業コストを抑制する。
- 安全（THREAT_MODEL / SafeMode）: 計画段階では既定ポリシーを不変更。
- 企業・行政要件（enterprise_architecture）: 対象外（N/A）だが、契約順序固定により説明責任を担保。
- 後方互換（schemas）: 実装前に契約順序の変更禁止を明示し互換破壊を予防。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（`01_Plans/issues/issue-FB-P2C-01-*.md`）。
- 実行条件: `Gate 0承認 + A2 Verify pass` の両方を満たす場合のみProceed。
- 非目標: 契約順序の再定義、A2未完了での実装着手、`03_Implement/**` への直接変更。

## 5) 受入条件 / Acceptance criteria

- [x] Gate 0承認記録とA2 Verify結果の両方が参照可能である。
- [x] 実装接続時の契約順序（padding遵守優先）が明文化される。
- [x] API/Schema依存のみを分離した入力契約が明文化される。
- [x] 実装レーン向けの期待出力/失敗時ロールバックテンプレが定義される。
- [x] 編集対象ファイル境界が明記され、他レーンとの重複がゼロである。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: Gate 0承認・A2 Verify pass・契約順序固定の再確認。
- [x] T2: tie-break順序と禁止変更を固定（必要時はADR起票待ち条件を明文化）。
- [x] T3: backend接続条件を API/Schema 依存に限定して分離。
- [x] T4: 実装レーン引き渡しテンプレ（入力契約/期待出力/失敗時ロールバック）を確定。

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
- 代替案C: backend接続条件をコード依存で定義 → 却下（レーン独立性を破壊）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 契約順序違反により同一入力同一出力を満たせない。
- 影響範囲: `FB-P2C-01` のDoD未達。
- ロールバック手順:
  1. 実装着手を停止する（Fail-fast）。
  2. A2の比較キーで逸脱点を再検証する。
  3. `outputPolygonHash不一致` / `paddingViolationCount>0` / `tieBreakOrder逸脱` のいずれかを検出した時点でA2へ差し戻す。

## 10) Additional context

- 編集対象ファイル境界: `01_Plans/issues/issue-FB-P2C-01-a3-implementation.md` のみ。
- 競合回避メモ: Stream D は計画メモ更新のみに限定し、共有統合/HIL/FB-P2A/B/`03_Implement/**` へ非接触。
- Workflow: Plan → Execute → Verify → Proceed（Verify失敗時は最大3回自己修復）。
- 停止条件: Gate未承認・契約矛盾・競合検出時は即停止。

## 11) Stream D 実行ログ（2026-03-14）

### Phase 1: Read Gate
- Plan:
  - Gate 0承認、A2 Verify pass、契約順序固定の有無を再確認する。
- Execute:
  - `DQ-FB-P2C-01` と `A2-HANDOFF-FB-P2C-01-2026-03-14` を照合。
- Verify:
  - `GateDecision=approved` / `A2Verify=pass` / `deterministicTieBreakOrder固定` を確認（Pass）。
- Proceed:
  - 契約順序固定フェーズへ進行。

### Phase 2: 契約順序固定
- Plan:
  - tie-break順序と禁止変更を固定し、逸脱時の処理を定義する。
- Execute:
  - 固定順序を `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小` として明文化。
  - 禁止変更を `追加/省略/並べ替え` の3種に固定。
  - ADR例外条件: 上記3種のいずれかが必要になった場合のみ `Context/Decision/Consequences` 形式で承認待ちに遷移。
- Verify:
  - 契約矛盾なし（Pass）。
- Proceed:
  - backend接続条件の分離へ進行。

### Phase 3: backend接続条件の分離
- Plan:
  - 実装依存を排除し、API/Schema依存だけを引き渡し可能な形へ整理する。
- Execute:
  - 入力契約（API）: `DocumentV1.cards/islands` を受領し、`inputHash` を比較キーとして保持。
  - 出力契約（Schema）: polygon結果は `outputPolygonHash` と `paddingViolationCount` で評価。
  - 境界条件: 実装方式・ライブラリ選定は別レーン責務として除外。
- Verify:
  - `02_Architecture/api.md` / `02_Architecture/schemas.md` 依存のみで閉じることを確認（Pass）。
- Proceed:
  - 実装レーン引き渡しへ進行。

### Phase 4: 実装レーン引き渡し
- Plan:
  - 入力契約/期待出力/失敗時ロールバックをテンプレ化する。
- Execute:
  - **Input Contract Template**
    - `gateApprovalRef`
    - `a2VerifyRef`
    - `inputHash`
    - `deterministicTieBreakOrder`
  - **Expected Output Template**
    - `outputPolygonHash`
    - `paddingViolationCount == 0`
    - `tieBreakOrderChanged == false`
  - **Rollback Template**
    - Trigger: `outputPolygonHash不一致` または `paddingViolationCount>0` または `tieBreakOrderChanged=true`
    - Action: 実装停止 → A2比較キー再検証 → A2差戻し
- Verify:
  - テンプレ適用時に契約逸脱を即時検知できる構成を確認（Pass）。
- Proceed:
  - Stream D planning handoff 完了。

## 12) ADRルール適用記録

- 判定: ADR変更は不要。
- 理由:
  - 本更新は承認済み契約の固定と引き渡し様式の明文化であり、新しい上位方針を追加していない。
  - 契約順序変更要求が発生した場合のみ ADR 起票へ移行する。

## 13) Self-Correction Log（最大3回）

1. 修正1: Stream D専属範囲に合わせて `03_Implement/**` 参照を除外した。
2. 修正2: Phase構成を指定の4段（Read Gate / 契約順序固定 / backend接続条件分離 / 実装レーン引き渡し）へ統一した。
3. 修正3: 停止条件（Gate未承認・契約矛盾・競合検出）を明示した。

> 上限超過時停止ルール: Self-Correction が 3 回を超える場合は更新を停止し、競合一覧を提出する。


## 14) Stream C 実装ログ（P2C-A3 implementation）

### Phase 1: Read Gate
- Plan:
  - A1/A2成果物を再読し、`deterministicTieBreakOrder` の不変条件を確認する。
- Execute:
  - A1/A2/A3 memoと既存実装を照合し、tie-breakキー名ドリフト（`minimum_*` と `*_minimization`）を検出。
- Verify:
  - Gate 0承認 + A2 Verify pass + 契約順序固定を再確認（Pass）。
- Proceed:
  - 契約変更なしでA3実装に進行。

### Phase 2: Plan
- 実装差分:
  1. tie-breakキー名をA1/A2契約語彙（`area_delta_minimization`, `vertex_count_minimization`）へ統一。
  2. `polygon_pad.ts` の評価順序を `merge/p2c_tie_break_contract.ts` 参照へ一本化し、重複定義を排除。
  3. 既存unitテストを契約語彙へ更新して回帰検証を追加。
- AC/DoD:
  - 同一入力同一出力（deterministic）
  - `paddingViolationCount == 0`
  - tie-break順序の追加/省略/並べ替え禁止
- 検証コマンド:
  - `npm test -- --run src/domain/geometry/polygon_pad.test.ts src/domain/p2c_polygon_handoff.test.ts src/domain/merge/p2c_tie_break_contract.test.ts src/domain/stream_d_p2c_mock_validation.test.ts`

### Phase 3: Execute
- 契約参照専用で以下を実施:
  - `merge/p2c_tie_break_contract.ts` をA1/A2契約語彙へ整合。
  - `polygon_pad.ts` は tie-break順序定数を契約モジュールから参照し、候補比較をスコア辞書ベースで固定順評価へ置換。
  - `p2c_polygon_handoff.ts` は同一契約定数を再利用し、A2→A3ハンドオフ判定で単一定義を使用。

### Phase 4: Verify（失敗時自己修復 最大3回）
- 1回目実行で全テストPass。自己修復は **0回**。
- 実行結果:
  - 4 test files / 15 tests passed。

### Phase 5: Proceed
- A3完了判定:
  - 契約順序は不変のまま実装へ接続完了。
  - キー名ドリフトを除去し、A2比較キーとA3実装キーを整合。
- ロールバック手順:
  1. `03_Implement/frontend/src/domain/geometry/polygon_pad.ts`
  2. `03_Implement/frontend/src/domain/merge/p2c_tie_break_contract.ts`
  3. `03_Implement/frontend/src/domain/p2c_polygon_handoff.ts`
  4. 関連テスト3ファイル
  - 上記を本コミット以前へ戻し、`npm test -- --run ...` の再実行でA2整合状態へ復帰する。

## Stream G addendum: A3 proceed/block判定基準の固定（2026-04-14）

### Proceed criteria（全件必須）
1. Gate証跡4点セット（`Approver(s)` / `ApprovedAt` / `DecisionStatement` / `GateDecision`）が参照可能。
2. A2で `A2 Verify Pass` が記録され、再現性キーが欠損していない。
3. tie-break順序が `padding>self_intersection>area_delta>vertex_count` から変更されていない。
4. 失敗時 rollback 導線（A2差し戻し）が有効なまま維持されている。

### Block criteria（1件でも該当で停止）
- `GateDecision != approved`
- `A2 Verify stale` または `A2 Verify fail`
- `appliedTieBreakOrder mismatch`
- `paddingViolationCount > 0`
- `outputPolygonHash drift`
- 承認証跡の期限切れ（`2026-04-30T23:59:59Z` を超過し再確認なし）

### Verify Evidence / Rollback
- Verify証跡:
  - `gateApprovalRef`
  - `a2VerifyRef`
  - `inputHash`
  - `outputPolygonHash`
  - `paddingViolationCount`
- rollback条件:
  1. Block criteria に1件でも該当
  2. 契約語彙（tie-break key名）にドリフトを検知
- rollbackアクション:
  - A3を即時停止し、A2比較キーで再検証後、必要ならA1再承認へエスカレーション。

### Cycle guard
- Plan→Execute→Verify→Proceed の自己修復は最大3回。
- 3回超過時は `Proceed=No` を固定し、未承認事項の確定扱いを禁止する。

## Stream E addendum: FB-P2C deterministic tie-break A3実装（2026-04-16）

### Phase 1) Read（承認記録・契約・テスト観点）
- Read結果:
  - Gate承認は維持（`DQ-FB-P2C-01` Approved）。
  - A2 handoff参照（`A2-HANDOFF-FB-P2C-01-2026-03-14`）に矛盾なし。
  - 契約語彙は `padding>self_intersection>area_delta>vertex_count` に固定。

### Phase 2) Plan（QA3件の再現条件明示）
- A3実装の受入条件:
  1. tie-break順序を単一定義化（差し替え禁止）。
  2. worker経由でも同一証跡キーを返却。
  3. QA3件（repeatability / padding=0 / order一致）がintegrationで再現可能。
- 停止条件:
  - Gate未承認、契約差し替え要求、自己修復3回超過で停止。

### Phase 4) A3実装
- 追加対象（Stream E専任範囲内）:
  - `src/domain/tiebreak/deterministic_tie_break.ts`
  - `src/worker/tiebreak/deterministic_tiebreak_worker_adapter.ts`
  - `tests/tiebreak/deterministic_tie_break.integration.test.ts`
  - `tests/tiebreak/fb_p2c_deterministic_cases.json`
- 実装方針:
  - tie-break順序定数を domain に固定。
  - worker adapter は証跡キー（5項目）を返却。
  - fixture固定で deterministic 判定をintegration化。

### Phase 5) Verify（再現性・監査証跡）
- Verifyで確認するBlock条件:
  - `appliedTieBreakOrder mismatch`
  - `paddingViolationCount > 0`
  - `outputPolygonHash drift`
- 結果:
  - 全条件を満たし `Proceed=Yes`。
  - Self-Correction 0/3（上限未到達）。
