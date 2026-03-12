# Issue Draft: FB-P2A-02-A3 Collapse/Expand操作 / 実装

- Type: Feature request
- Status: Draft (起票用)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: `Collapse/Expand操作` を 実装 の責務で前進させる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: `FB-P2A-02` のDoDを満たすための計画段階である。
  - 操作: 実装 に限定して成果物を作成する。
  - 期待結果: 下流段階へ引き渡せる判断材料が揃う。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- ADR-0007のP0 `FB-P2A-02` はDoDが定義済みだが、着手順と境界I/Fが未分解のままでは他レーンと衝突しやすい。
- 本Issueは3段分割のうち **実装 専用** とし、責務を単一化する。

## 2) 背景 / Context

- Backlog基準: `FB-P2A-02` / AC-2A-2, AC-2A-3 / DoD: collapseで子要素が描画/ヒットテスト対象外になり、expandで復帰する。
- DoD依存: 02_Architecture/architecture.md view-state boundary, frontend canvas hit-test contract

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 仕様評価前に判断境界を固定し、レビュー認知負荷を下げる。
- 安全（THREAT_MODEL / SafeMode）: 計画段階では既定ポリシーを不変更。
- 企業・行政要件（enterprise_architecture）: 本Issueでは対象外（N/A）だが、契約明文化により後続監査性を確保。
- 後方互換（schemas）: 互換破壊の有無を段階ごとに明記して実装段階へ引き継ぐ。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（`01_Plans/issues/issue-FB-*.md`）。
- 変更の最小単位: 1 Issue = 1段階 = 1検証責務。
- 非目標: 実コード変更、README/ダッシュボード更新、リリース判断。

## 5) 受入条件 / Acceptance criteria

- [ ] `FB-P2A-02` の実装責務と次段引き継ぎ条件が明文化される。
- [ ] AC/DoDギャップがあれば補完ドラフトを記録する。
- [ ] セキュリティ境界を変更しないことを明記する。
- [ ] 検証レベル `integration` が宣言・整合している。
- [ ] 編集対象ファイル境界が明記され、他レーンとの重複がゼロである。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: `FB-P2A-02` のDoD依存を段階責務へ分解する。
- [ ] T2: 実装 のAC補完ドラフト（不足時）を作成する。
- [ ] T3: 次段Issue（A1→A2→A3）の入出力契約を明示する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo命名・メタ項目が整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: 1Issueに3段を混在 → 却下（責務混線）。
- 代替案B: いきなり実装Issueのみ作成 → 却下（契約未固定）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 段階間契約が曖昧で再作業が発生。
- 影響範囲: `FB-P2A-02` の着手順遅延。
- ロールバック手順: 当該IssueをDraft維持し、上流ADR判断に戻す。

## 10) Additional context

- 編集対象ファイル境界: `01_Plans/issues/issue-FB-P2A-02-a3-implementation.md` のみ。
- 競合回避メモ: Stream Cは `issue-FB-P2*-*.md` 新規作成のみを担当し、既存issue/実装ファイルへ非接触。
