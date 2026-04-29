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

### AC/DoD不足ドラフト提案（事前合意ログ）

- Gap認識: ACは存在するが、DoD（完了判定）の明文化が不足。
- Draft提案（実編集前）:
  - DoD-1: ACチェック項目が全て確認済みであること。
  - DoD-2: Validation plan記載コマンドを実行し、差分体裁とIssue memo整合が維持されること。
  - DoD-3: 5Phase直列ログに「Phase開始時Read同期」を明示し、自己修復回数が3回以内であること。
  - DoD-4: 編集対象が `01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md` のみに限定されること。
- 合意: 本Issueメモ内で上記DoDを採用し、以降のExecute/Verifyに適用する（Status: Agreed）。

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
- Read同期: 対象ファイルおよび上位基準（`AGENTS.md` / `01_Plans/documentation_quality.md`）を再読。
- 対象ファイル再読を実施し、判定情報の分散を確認。

### Phase 2 Plan
- Read同期: Phase 1の読取結果とRequirement meta I/Fを再確認。
- 主責務を「Open化可否判定の明確化」に固定。
- AC/DoD不足を検出し、ドラフト提案→合意ログを先行記録。

### Phase 3 Execute
- Read同期: 合意済みDoDを再確認してから編集開始。
- メモ品質固定のみを実施（本文改稿禁止）。
- 重複ログを統合し、判定・検証・Proceedを単一セクションへ再編。
- 指定外ファイルは未編集。

### Phase 4 Verify
- Read同期: Validation planとDoDを照合して検証コマンドを確定。
- `git diff --check` を実行。
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- Read同期: AC/DoD/Verify結果を最終突合。
- Open readiness: **Ready**
- Blocker: なし
- Needs decision: なし（DecisionStatus=Fixed）


## Stream E phase run（2026-04-29）

### 1) Read（Draft gate条件抽出）
- Draft gate条件を再確認: `Status=Draft` / `DecisionStatus=Fixed` / `VerificationLevel=docs-check`。

### 2) Context / Decision / Consequences
- Context: `documentation_quality.md` は内部品質規約の正本。
- Decision: 分類は **Move internal 維持**。
- Consequences: 対外公開より内部統制の一貫性を優先。

### 3) AC/DoD・Open化条件の明文化
- Open化条件: 外部向け品質基準へ再編集し、内部運用規約の機微を分離できた場合のみ再審査。
- DoD: 三値Proceed + Verify結果の併記を必須とする。

### 4) Plan→Execute→Verify（自己修復）
- Plan/Execute: 本Issueメモのみ更新。
- Verify: docs-check方針維持、自己修復 0/3。

### 5) Proceed
- 判定: **Hold**（Open化不可）。
- 理由: 文書の性質が内部運用品質ゲートに固定されている。
