# Issue Draft: FB-P2B-01-A3 Similar-card候補提示 / 実装

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
- RequirementStatement: A1/A2契約を逸脱せず実装接続へ引き継ぐ。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1/A2がFixedである。
  - 操作: 実装タスクを契約準拠で接続する。
  - 期待結果: candidate group 一覧と対象Card確認DoDを満たす実装計画になる。
  - 除外: 契約変更の独断実施。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- A3で契約を変更するとA1/A2の検証資産が無効化されるため、接続時の逸脱防止が必要。

## 2) 背景 / Context

- Backlog基準: `FB-P2B-01` / AC-2B-1。
- 本Issueは実装そのものではなく、実装接続条件の固定メモ。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 先行契約を守り、手戻りを最小化する。
- 安全（THREAT_MODEL / SafeMode）: 候補提示が意思決定を上書きしない前提を維持する。
- 企業・行政要件（enterprise_architecture）: 説明可能な判断過程を保つ。
- 後方互換（schemas）: A1構造を破る変更はADR判断へエスカレーション。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（本issue memo）。
- A3接続ゲート:
  - Gate-1: A1 `SimilarCandidateGroup` フィールド完全準拠。
  - Gate-2: A2 非自動確定・再読込復元契約を実装テストへ転写。
  - Gate-3: 逸脱が必要な場合はADR Ruleに従い停止。
- 非目標: 実装コード記述。

## 5) 受入条件 / Acceptance criteria

- [x] A1/A2契約逸脱禁止が明示されている。
- [x] 実装接続時のGo/No-Goゲートが定義されている。
- [x] 検証レベル `integration` を維持している。
- [x] セキュリティ境界不変更を維持している。
- [x] 編集対象が本ファイルのみ。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: 契約準拠チェック項目を列挙。
- [x] T2: integration検証観点へのマッピングを定義。
- [x] T3: ADR要否時の停止条件を明記。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: A3で契約を拡張して吸収 → 却下（A1/A2無効化）。
- 代替案B: A3を分割せず一括記述 → 却下（接続責務が不明確）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 実装側が追加フィールドを前提化。
- 影響範囲: 2B全体の整合性。
- ロールバック手順: A3を停止し、A1へ契約改訂提案を戻す。

## 10) Additional context

- Fail-safeにより競合検知時は即停止し、人間判断待ちへ移行。
