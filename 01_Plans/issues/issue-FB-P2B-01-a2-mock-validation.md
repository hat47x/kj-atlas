# Issue Draft: FB-P2B-01-A2 Similar-card候補提示 / モック検証

- Type: Feature request
- Status: Open
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-01`
- RequirementStatement: A1契約に基づく候補group提示をmockで検証可能状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1契約がFixedである。
  - 操作: mock candidate groupsを投入し、表示/再読込の期待値を検証する。
  - 期待結果: 非自動確定かつ再読込復元の契約がテスト化される。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- A1契約を実装前に検証しないと、A3で「表示できるが復元できない」等の結合欠陥が顕在化する。

## 2) 背景 / Context

- Backlog基準: `FB-P2B-01` / AC-2B-1。
- A2では mock 検証のみ実施し、実装判断はA3に限定する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 実装前に結合失敗を潰し、レビュー負荷を低減する。
- 安全（THREAT_MODEL / SafeMode）: 候補提示で自動確定を禁止し、人手判断を維持する。
- 企業・行政要件（enterprise_architecture）: 判断ログ復元の検証可能性を確保。
- 後方互換（schemas）: A1フィールド欠損時の扱いをA2でテスト条件化する。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（本issue memo）。
- A2検証契約:
  - mock入力: `CandidateListViewModel` with 2 groups / 1 target card each。
  - 期待表示: group順序と `targetCardId` が一致。
  - 非自動確定: 候補提示のみで merge state は未確定のまま。
  - 再読込復元: 同一 `snapshotVersion` を再投入すると同一group構造が再現される。
- 非目標: 候補計算アルゴリズム・永続層実装。

## 5) 受入条件 / Acceptance criteria

- [x] 非自動確定（候補提示のみ）を契約として明記。
- [x] 再読込復元の期待値（snapshotVersion一致時の復元）を明記。
- [x] A1契約の逸脱禁止を明記。
- [x] `integration` 検証レベルと計画が整合。
- [x] 編集対象が本ファイルのみ。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: mock入力データセット条件を定義。
- [x] T2: 非自動確定の判定条件を定義。
- [x] T3: 再読込復元の一致条件を定義。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: A2を省略しA3へ直行 → 却下（契約未検証）。
- 代替案B: A2で実装を開始 → 却下（フェーズ境界違反）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 再読込復元条件が曖昧で、A3で解釈分岐が発生。
- 影響範囲: `FB-P2B-01` の結合テスト計画全体。
- ロールバック手順: A2をOpen維持し、A1契約への差し戻しを記録。

## 10) Additional context

- Fail-safe: 未定義競合・前提崩れ・自己修復3回超過時は停止。
