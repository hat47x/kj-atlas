# Issue Draft: FB-P2B-02-A3 Manual assisted mergeフロー / 実装

- Type: Feature request
- Status: Open
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-02`
- RequirementStatement: A1/A2契約を維持したまま実装接続へ進む。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1/A2がFixedである。
  - 操作: decision log実装タスクを契約にマッピングする。
  - 期待結果: `採用/部分採用/却下/後で` が保存可能で自動確定しない。
  - 除外: 契約を実装都合で変更する行為。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- A3で契約逸脱が起きると、手動mergeフローの再現性と監査性が失われる。

## 2) 背景 / Context

- Backlog基準: `FB-P2B-02` / AC-2B-2, AC-2B-5。
- 本Issueは実装接続計画に限定し、決定契約はA1/A2を正本とする。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 人間判断尊重（非自動確定）を守る。
- 安全（THREAT_MODEL / SafeMode）: 意思決定の黙示確定を禁止。
- 企業・行政要件（enterprise_architecture）: decision traceabilityを維持。
- 後方互換（schemas）: append/list/restoreのI/F互換性を維持。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（本issue memo）。
- A3接続ゲート:
  - Gate-1: A1 `MergeDecisionRecord` 必須項目を全保持。
  - Gate-2: A2の非自動確定条件を回帰テスト化。
  - Gate-3: A2のrestore順序一致条件を回帰テスト化。
  - Gate-4: 逸脱要求はADR Ruleに従い停止。
- 非目標: DB schema/API詳細設計の独断変更。

## 5) 受入条件 / Acceptance criteria

- [x] A1/A2契約逸脱禁止を明記している。
- [x] 実装接続時のGo/No-Go判定基準が定義されている。
- [x] 非自動確定と再読込復元が必須条件として保持される。
- [x] `integration` 検証レベルと整合している。
- [x] 編集対象が本ファイルのみ。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: A1契約→実装要件のマッピングを定義。
- [x] T2: A2 mock検証→回帰検証項目への転写条件を定義。
- [x] T3: 契約逸脱時の停止手順を定義。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: 実装フェーズで契約更新を許容 → 却下（検証資産破壊）。
- 代替案B: A3を省略して直接実装 → 却下（接続責務不在）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: `defer` 取り扱い漏れでログ欠落。
- 影響範囲: Manual assisted mergeフロー全体。
- ロールバック手順: A3停止、A1/A2契約差分を再整理。

## 10) Additional context

- 未定義競合・前提崩れ・自己修復上限超過で即停止（fail-safe）。
