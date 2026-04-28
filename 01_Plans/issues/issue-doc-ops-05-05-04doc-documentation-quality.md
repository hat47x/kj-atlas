# Issue Draft: DOC-OPS-05-05 01_Plans/documentation_quality.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream E
- Scope: `01_Plans/documentation_quality.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `04_Documentation/release.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-05`
- RequirementStatement: 内部品質基準文書としての扱いを固定し、Open化審査に必要な判断情報を揃える。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: DOC-OPS-05前半のDraft品質均一化を行う。
  - 操作: 分類方針・品質ゲート・検証手順を明記する。
  - 期待結果: Open化可否を一読で判定できる。
  - 除外: `01_Plans/documentation_quality.md` 本体改稿。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- 過去ログ重畳により、最終判定（Move internal）が視認しづらい。
- Open化に必要な契約情報（Go/No-Go、Proceed判定）が分散している。

## 2) 背景 / Context

- `documentation_quality.md` は内部運用品質ゲート文書であり、公開文書本体ではない。
- 本Issueは「分類の是非」ではなく「Open化可能な記述品質の固定」を目的とする。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 文書ガバナンス判断を短時間化する。
- 安全（THREAT_MODEL / SafeMode）: 公開・内部境界の誤判定を防止する。
- 企業・行政要件（enterprise_architecture）: 内部統制文書の責務を保持する。
- 後方互換（schemas）: 実装非変更のため影響なし。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs（Issue memo only）
- 分類方針: **Move internal（維持）**
- 非目標: 本体ドキュメント変更、shared resources更新、他Issue編集。

## 5) 受入条件 / Acceptance criteria

- [ ] Move internal 判定と根拠が単一箇所で参照できる。
- [ ] GoNoGoGate=Required の判定条件（公開境界・品質責務分離）が明文化される。
- [ ] Validation plan が `docs-check` と一致する。
- [ ] Proceed判定（三値）が記録される。
- [ ] 5Phase実行記録が簡潔に維持される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 重複記録を整理し、最終判断情報を集約。
- [ ] T2 AC/DoDをOpen化判定向けに補強。
- [ ] T3 Verify実行結果を追記。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check`
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - Markdown体裁が維持される。
  - active issue memos整合に影響しない。
- 未実施時の理由・代替検証:
  - N/A

## 8) リスクとロールバック / Risks & rollback

- 失敗モード: 履歴削減で監査可能性を損なう。
- ロールバック: 対象メモのみrevertして必要最小限で再編集。

## 9) Phase execution record（Stream E）

### Phase 1 Read
- 対象ファイル再読を実施し、判定情報の分散を確認。

### Phase 2 Plan
- 主責務を「Open化可否判定の明確化」に固定。

### Phase 3 Execute
- 重複ログを統合し、判定・検証・Proceedを単一セクションへ再編。
- 指定外ファイルは未編集。

### Phase 4 Verify
- `git diff --check` を実行。
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- Open readiness: **Ready**
- Blocker: なし
- Needs decision: なし（DecisionStatus=Fixed）
