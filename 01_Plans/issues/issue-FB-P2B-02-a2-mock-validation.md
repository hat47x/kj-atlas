# Issue Draft: FB-P2B-02-A2 Manual assisted mergeフロー / モック検証

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
- RequirementStatement: A1のdecision log契約をmock検証し、非自動確定・再読込復元を担保する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1契約がFixedである。
  - 操作: 4アクションをmock appendし、restoreで復元検証する。
  - 期待結果: 自動確定なしで決定履歴が再読込で復元される。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- decision logは保存できても復元時に欠落しやすく、手動判断フローが破綻するリスクがある。

## 2) 背景 / Context

- Backlog基準: `FB-P2B-02` / AC-2B-2, AC-2B-5。
- A2ではmockで契約整合を検証し、実装変更は行わない。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 人間判断の追跡可能性を実装前に検証可能化。
- 安全（THREAT_MODEL / SafeMode）: 自動決定を発火させない契約を維持。
- 企業・行政要件（enterprise_architecture）: decisionログ監査再現性を担保。
- 後方互換（schemas）: snapshotVersion基準で復元互換を評価。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（本issue memo）。
- A2検証契約:
  - mock append順序: `accept -> partial -> reject -> defer`。
  - 非自動確定: append時に representative確定イベントを発生させない。
  - 再読込復元: 同一 `snapshotVersion` で `restore` が同順序同内容を返す。
  - 異常系: `action` がenum外の場合は復元対象外として扱う（契約違反）。
- 非目標: decision log store実装。

## 5) 受入条件 / Acceptance criteria

- [x] 非自動確定の判定条件が明記されている。
- [x] 再読込復元の一致条件（同順序同内容）が明記されている。
- [x] enum外actionの扱いが定義されている。
- [x] `integration` 検証レベル宣言と整合している。
- [x] 編集対象が本ファイルのみ。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: mock append/restoreシナリオを定義。
- [x] T2: 非自動確定を検証する否定条件を定義。
- [x] T3: 異常系（enum外）を検証条件に追加。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: 正常系のみ検証 → 却下（契約逸脱の早期検出不可）。
- 代替案B: A2で実装試験へ進む → 却下（フェーズ越境）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: restore順序不整合によりレビュー履歴が再現不能。
- 影響範囲: `FB-P2B-02` の監査性。
- ロールバック手順: A2契約を再定義しA3着手を停止。

## 10) Additional context

- 自己修復上限3回超過時はfail-safeで停止する。
