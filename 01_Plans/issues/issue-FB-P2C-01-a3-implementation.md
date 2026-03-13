# Issue Draft: FB-P2C-01-A3 Polygon auto-fit / 実装

- Type: Feature request
- Status: Blocked (A2完了待ち)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream A
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
- DecisionStatus（Fixed / Pending）: Pending（A2 Verify完了まで開始不可）
- DecisionQueueRef（未確定時の参照先）: A2 Verify結果 + Gate 0承認記録

## 1) 課題 / Problem statement

- A3は実装接続フェーズだが、A2検証を通っていない状態で進めると契約逸脱（特にpadding優先順序）が発生する。
- そのため本Issueは **A2完了までBlock** とし、契約順序の改変を禁止する。

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
- 実行条件: Gate 0承認 + A2 Verify pass の両方をProceed条件に設定。
- 非目標: 契約順序の再定義、A2未完了での実装着手。

## 5) 受入条件 / Acceptance criteria

- [ ] Gate 0承認記録とA2 Verify結果の両方が参照可能である。
- [ ] 実装接続時の契約順序（padding遵守優先）が明文化される。
- [ ] A2からの入力契約（fixture/比較キー/許容差分）を継承する。
- [ ] 検証レベル `integration` が宣言・整合している。
- [ ] 編集対象ファイル境界が明記され、他レーンとの重複がゼロである。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: A2 Verify pass を受領し、Plan開始条件を満たす。
- [ ] T2: 契約順序逸脱禁止（padding遵守優先）を実装受入条件に固定する。
- [ ] T3: 実装フェーズへの引き渡しメモ（入力/出力/失敗時ロールバック）を確定する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo命名・メタ項目が整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - A2未完了の間は Execute/Verify に進まない（Fail-safe）。

## 8) 代替案 / Alternatives considered

- 代替案A: A2未完了で実装に進む → 却下（契約順序逸脱リスク）。
- 代替案B: 実装側で独自tie-break最適化を許可 → 却下（決定論喪失）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 契約順序違反により同一入力同一出力を満たせない。
- 影響範囲: `FB-P2C-01` のDoD未達。
- ロールバック手順: A3をBlocked維持し、A2またはA1へ差し戻す。

## 10) Additional context

- 編集対象ファイル境界: `01_Plans/issues/issue-FB-P2C-01-a3-implementation.md` のみ。
- 競合回避メモ: Stream A は FB-P2C系のみ担当し、共有ファイル/FB-P2A/P2B/HIL領域へ非接触。
- Workflow: Plan → Execute → Verify → Proceed（Verify失敗時は最大3回自己修復）。

## 11) Stream A Phase status（2026-03-13 実行ログ）

### Phase 1: A1 Interface Contract / Phase 2: Gate 0 判定 参照同期
- Read同期（必須3ファイル再読込）: 実施済み。
- 直前コミット想定との差分記録: 3ファイルとも差分なし（開始時点）。
- Verify: A3開始条件が `Gate 0承認 + A2 Verify pass` であることを再確認。

### Phase 3: A2 Mock Validation 依存確認
- Read同期（必須3ファイル再読込）: 実施済み。
- 直前コミット想定との差分記録: 依存条件に差分なし。
- Proceed判定: A2 Verify pass 未受領のためA3は進行不可。

### Phase 4: A3 Implementation Planning Link
- Plan: A2 Verify通過後にのみ実装接続条件を確定。
- Execute: 未実施（A2 Blocked継続）。
- Verify: 未実施（Fail-safe準拠）。
- Proceed判定: 停止。

### Phase 5: Verify & Report
- フェイルセーフ判定: `Gate 0承認ログ不在` に起因する連鎖Block。
- Blocking ID: `BLK-FB-P2C-01-GATE0-MISSING`
- 参照元:
  - A2 `Status: Blocked (Gate 0待ち)`
  - 本ファイル `Status: Blocked (A2完了待ち)`
- 解消に必要な承認者: Human Decision Gate 0 承認権限者（承認後、A2 Verify実施担当）。
