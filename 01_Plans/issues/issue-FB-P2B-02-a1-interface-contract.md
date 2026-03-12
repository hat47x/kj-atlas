# Issue Draft: FB-P2B-02-A1 Manual assisted mergeフロー / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-02`
- RequirementStatement: decision log 永続化I/FをA1で固定する（実装禁止）。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: `FB-P2B-02` を A1→A2→A3 で実行する。
  - 操作: decision log の型・保存I/F・読込I/Fのみ定義する。
  - 期待結果: A2/A3が同一の永続化契約を参照できる。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- `採用/部分採用/却下/後で` の意思決定を永続化するI/F未固定だと、再読込復元の整合を保証できない。

## 2) 背景 / Context

- Backlog基準: `FB-P2B-02` / AC-2B-2, AC-2B-5。
- DoD: 決定が保存でき、自動確定しない。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 判断ログの再現性を先に固定する。
- 安全（THREAT_MODEL / SafeMode）: 自動確定禁止を契約で担保。
- 企業・行政要件（enterprise_architecture）: 監査可能な意思決定履歴を保つ。
- 後方互換（schemas）: decision enum拡張時の影響点をA1で可視化。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（本issue memo）。
- 固定契約（A1成果物）:
  - `MergeDecisionRecord`:
    - `decisionId: string`
    - `groupId: string`
    - `action: "accept" | "partial" | "reject" | "defer"`
    - `selectedCardIds: string[]`
    - `note: string`
    - `decidedBy: string`
    - `decidedAt: string`
    - `snapshotVersion: string`
  - `DecisionLogStoreContract`:
    - `append(record: MergeDecisionRecord): void`
    - `listByGroup(groupId: string): MergeDecisionRecord[]`
    - `restore(snapshotVersion: string): MergeDecisionRecord[]`
- 非目標: append/list実装、DB/API変更。

## 5) 受入条件 / Acceptance criteria

- [x] decision log永続化I/Fが型付きで固定されている。
- [x] 4アクション（accept/partial/reject/defer）が契約上必須化されている。
- [x] 自動確定禁止が契約レベルで明記されている。
- [x] `docs-check` レベルと整合している。
- [x] 編集対象が本ファイルのみ。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: decision record最小スキーマを固定。
- [x] T2: 永続化I/F（append/list/restore）を固定。
- [x] T3: A2/A3への受け渡し条件を明文化。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: action enumをA3で確定 → 却下（A2検証不能）。
- 代替案B: 永続化I/Fを省略 → 却下（再読込契約が未固定）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: enumや必須項目の解釈ズレ。
- 影響範囲: `FB-P2B-02` のmock検証と実装接続。
- ロールバック手順: A1契約を再固定し、A2/A3を保留。

## 10) Additional context

- ADR要否が発生したら Context/Decision/Consequences を記録後に停止する。
