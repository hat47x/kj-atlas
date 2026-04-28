# Issue Draft: DOC-OPS-05-06 04_Documentation/e2e_testing.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream E
- Scope: `04_Documentation/e2e_testing.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/e2e_testing.md`, `04_Documentation/operations.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-06`
- RequirementStatement: E2E運用文書の公開改善方針を維持しつつ、Open化判定に必要な情報を不足なく固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: E2E運用方針はADR-0019を正本として維持。
  - 操作: 公開改善（Improve external）方針、検証、Proceed判定を明記。
  - 期待結果: Open化審査で追加確認なしに着手可否が判断できる。
  - 除外: `04_Documentation/e2e_testing.md` の本文改稿。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- 既存メモが長文化し、Improve external方針とOpen readiness判定が埋もれている。
- 5Phase記録が重複し、監査時に最終状態を取り出しにくい。

## 2) 背景 / Context

- e2e_testingは対外運用説明の主要導線であり、公開品質改善が必要。
- ただし本Issueはメモ整備限定であり、実文書改稿は後続Issueで行う。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 公開品質改善タスクの着手判断を早める。
- 安全（THREAT_MODEL / SafeMode）: 公開運用情報の誤記載リスクを低減。
- 企業・行政要件（enterprise_architecture）: 運用手順の説明責務を保持。
- 後方互換（schemas）: 実装・データ互換への影響なし。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs（Issue memo only）
- 分類方針: **Improve external（維持）**
- 非目標: 対象文書本体の編集、shared resources更新、他Issue編集。

## 5) 受入条件 / Acceptance criteria

- [ ] Improve external 判定と根拠（公開runbook品質向上）が明記される。
- [ ] GoNoGoGate=Required の判定条件（ADR-0019整合、公開境界）が明記される。
- [ ] Validation plan が `docs-check` と一致する。
- [ ] Proceed判定（三値）が記録される。
- [ ] 5Phase実行記録が1セットで維持される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 重複ログを整理し、最終判定情報を単一化。
- [ ] T2 AC/DoD不足を補完してOpen化基準を固定。
- [ ] T3 Verify結果を記録。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check`
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - 体裁崩れなし。
  - active memo検証に副作用なし。
- 未実施時の理由・代替検証:
  - N/A

## 8) リスクとロールバック / Risks & rollback

- 失敗モード: 判定根拠が過度に簡略化される。
- ロールバック: 当該メモのみrevertし、根拠節を復元。

## 9) Phase execution record（Stream E）

### Phase 1 Read
- 対象ファイル再読を実施し、長文化による可読性低下を確認。

### Phase 2 Plan
- 主責務を「Open化審査に必要な最終値の固定」に設定。

### Phase 3 Execute
- 重複する履歴節を整理し、判定・検証・Proceedを再編。
- 指定外ファイルは未編集。

### Phase 4 Verify
- `git diff --check` を実行。
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- Open readiness: **Ready**
- Blocker: なし
- Needs decision: なし（DecisionStatus=Fixed）
