# Issue Draft: DOC-OPS-05-02 04_Documentation/codex_skill_operations.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream E
- Scope: `04_Documentation/codex_skill_operations.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `00_Prompt/codex_gsd_skill_ops.md`, `01_Plans/documentation_quality.md`, `04_Documentation/codex_skill_operations.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-02`
- RequirementStatement: 対象文書の公開境界を明示し、Open化判定に必要な判断情報を不足なく揃える。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: DOC-OPS-05はIssueメモ品質を先に固定する。
  - 操作: 公開/内部の分類根拠、Go/No-Go、検証手順を明記する。
  - 期待結果: Open化可否を `Ready/Hold/Needs-decision` で判定可能。
  - 除外: `04_Documentation` 本体の改稿・移設は実施しない。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- 既存Draftに重複した実行記録が累積し、Open化審査に必要な情報が読み取りにくい。
- 「分類方針」「検証計画」「Proceed判定」の最終値が1箇所に定義されていない。

## 2) 背景 / Context

- `codex_skill_operations.md` は内部運用色が強く、公開境界判断が必要。
- DOC-OPS-05前半は「IssueメモをOpen可能品質に揃える」ことが主目的。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 判断導線を短縮し、レビュー時間を削減する。
- 安全（THREAT_MODEL / SafeMode）: 公開境界の曖昧さを減らし誤公開を抑制する。
- 企業・行政要件（enterprise_architecture）: 運用文書の責務分離を明確化する。
- 後方互換（schemas）: 実装/スキーマ非変更のため互換影響なし。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs（Issue memo only）
- 分類方針: **Move internal（維持）**
- 非目標:
  - `04_Documentation` 本体更新
  - 共有リソース（README, dashboard, decision-pack）更新
  - 他Issue編集

## 5) 受入条件 / Acceptance criteria

- [ ] 分類方針（Move internal）と根拠（Audience/Goal/Public boundary）が明記される。
- [ ] GoNoGoGate=Required の判定条件が本文に記載される。
- [ ] VerificationLevel と Validation plan が `docs-check` で一致する。
- [ ] Proceed判定が `Ready/Hold/Needs-decision` の三値で記録される。
- [ ] 5Phase（Read→Plan→Execute→Verify→Proceed）記録が1セットに正規化される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 重複ログを整理し、最終判断値を単一化する。
- [ ] T2 AC/DoD不足を補い、Go/No-Go判定軸を明文化する。
- [ ] T3 docs-check結果とProceedを記録する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check`
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - 体裁崩れがない。
  - active memo 検証に副作用を出さない。
- 未実施時の理由・代替検証:
  - N/A

## 8) リスクとロールバック / Risks & rollback

- 失敗モード: 判定情報の削除し過ぎで根拠欠落。
- ロールバック: 当該メモを直前コミットへrevertし、必要項目のみ再追加。

## 9) Phase execution record（Stream E）

### Phase 1 Read
- 対象ファイル再読を実施し、重複記録の累積を確認。

### Phase 2 Plan
- 単一責務を「Open化判定可能なメモ整備」に固定。
- AC/DoD不足として Go/No-Go 判定条件と三値Proceed記録を補強。

### Phase 3 Execute
- 重複セクションを整理し、分類方針・検証・Proceedを1セットへ統合。
- 指定外ファイルは未編集。

### Phase 4 Verify
- `git diff --check` を実行。
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- Open readiness: **Ready**
- Blocker: なし
- Needs decision: なし（DecisionStatus=Fixed）
