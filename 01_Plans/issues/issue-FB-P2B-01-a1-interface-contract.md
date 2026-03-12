# Issue Draft: FB-P2B-01-A1 Similar-card候補提示 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-01`
- RequirementStatement: `Similar-card候補提示` の候補group構造と境界I/Fを固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: `FB-P2B-01` を A1→A2→A3 で分割実行する。
  - 操作: A1で候補group構造・契約型・I/O境界のみを定義する。
  - 期待結果: A2/A3が参照すべき単一契約が固定される。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- `FB-P2B-01` のDoD（candidate group 一覧と対象Card確認）を達成するための最小契約が未固定だと、A2/A3で再定義競合が起こる。

## 2) 背景 / Context

- Backlog基準: `FB-P2B-01` / AC-2B-1 / DoD: candidate group 一覧と対象Cardを確認できる。
- Stream C担当境界: FB-P2B系 issue memo のみ編集。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 先に契約固定し、後続検証の判断揺れを排除する。
- 安全（THREAT_MODEL / SafeMode）: SafeMode既定やshare/export方針は不変更。
- 企業・行政要件（enterprise_architecture）: 監査可能なI/F定義を先行固定する。
- 後方互換（schemas）: 破壊変更の可能性をA1段階で明示してA3へ伝播する。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（本issue memo）。
- 固定契約（A1成果物）:
  - `SimilarCandidateGroup`:
    - `groupId: string`
    - `targetCardId: string`
    - `candidateCardIds: string[]`
    - `scoreSummary: { min: number; max: number; avg: number }`
    - `reasonCodes: string[]`
    - `snapshotVersion: string`
  - `CandidateListViewModel`:
    - `generatedAt: string`
    - `groups: SimilarCandidateGroup[]`
    - `totalGroupCount: number`
- 非目標: 候補抽出ロジック実装、UI描画、永続化実装。

## 5) 受入条件 / Acceptance criteria

- [x] A2/A3が参照する候補groupの必須フィールドが固定されている。
- [x] 入出力境界（候補計算→UI表示）を1契約として明示している。
- [x] セキュリティ境界（SafeMode/share/export）を変更しない。
- [x] `docs-check` の検証レベル宣言と整合している。
- [x] 編集対象が本ファイルのみに限定されている。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: candidate group構造のキーと型を固定。
- [x] T2: A2への引き渡し条件（mock入力/期待出力）を定義。
- [x] T3: A3への契約逸脱禁止条件を明記。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: A1でUIまで定義 → 却下（A1実装禁止に抵触）。
- 代替案B: A2で契約同時定義 → 却下（契約揺れリスク増）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: A2で追加フィールド要求が発生し契約が揺れる。
- 影響範囲: `FB-P2B-01` 全体の再検証増加。
- ロールバック手順: A1へ差し戻し、Context/Decision/Consequences を先に追記して再固定。

## 10) Additional context

- フェーズ運用: Read → Plan → Execute → Verify（自己修復3回まで）→ Proceed。
- ADR要否発生時は本IssueでDecisionを確定せず停止する。
