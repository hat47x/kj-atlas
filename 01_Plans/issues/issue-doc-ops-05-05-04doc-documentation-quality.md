# Issue Draft: DOC-OPS-05-05 01_Plans/documentation_quality.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream J (DOC-OPS-05-05 Draft整備)
- Scope: `01_Plans/documentation_quality.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0023-doc-ops-04-readability-baseline.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `01_Plans/adr/ADR-0025-doc-ops-04-change-governance.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: `01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`, `01_Plans/issues/issue-doc-ops-05-07-04doc-e2e-verification-log-2026-03-03.md`
- Dependency status: `未確定（DOC-OPS-05 Open gate 判定待ち）`

## Requirement meta I/F
- RequirementID: `DOC-OPS-05-05`
- RequirementStatement: 内部品質基準文書としての扱いを固定し、Open化審査に必要な判断情報を揃える。
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Classification（Fixed）
- Decision: **Move internal**
- Basis: 内部審査用の品質統制基準であり、対外公開本文ではない。

## Phase Run（Plan→Execute→Verify→Proceed）

### Phase 1: Read同期（現状抽出と依存棚卸し）
- 現状:
  - 05-05 は `Move internal` 判定で統一済み。
  - Proceed は依存未確定のため `Hold` 継続が必要。
- 依存関係:
  - 05-06: 公開導線文書（Improve external）としての Open 判定要件。
  - 05-07: 検証ログ（Move internal）としての配置見直し判定要件。
- 棚卸し結果:
  - 3Issue 共通で `VerificationLevel: docs-check`、`ProceedDecision: Hold`、`self-correction <=3` を維持する必要がある。

### Phase 2: ADR（C/D/C）整合
- Context:
  - ADR-0023: 可読性基線（Audience / Goal / Non-goal / Outcome / 用語整合）を最低要件とする。
  - ADR-0024: docs-check を必須境界として扱い、CI拡張とは分離する。
  - ADR-0025: 変更統治・例外承認は責務分離し、停止条件を明示する。
- Decision:
  - 本Issueは品質ゲート目的・適用範囲・例外境界を **Issueメモ上で再読可能** に固定する。
  - 適用範囲は「Issueメモ整備のみ」。`04_Documentation/**` 本文改稿および実装変更は対象外。
  - 例外は「依存証跡未確定時の Hold 継続」のみを認め、Open化確定は行わない。
- Consequences:
  - 05-06/05-07との判定語彙不一致を抑止できる。
  - Open gate 判定時に必要な証跡欠落（Approval Record不足）を事前に検知できる。

### Phase 3: Plan（AC/DoD: 判定可能な品質評価軸）
- AC-1（可読性 / Readability）:
  - `Requirement meta I/F`、`Classification`、`Phase Run`、`Proceed tri-state` が1ファイル内で追跡可能。
- AC-2（一貫性 / Consistency）:
  - 05-06/05-07 と `Proceed/Hold/Stop`、`GoNoGoGate`、`VerificationLevel` の語彙が一致。
- AC-3（検証可能性 / Verifiability）:
  - docs-check 実施計画と `Approval Record` 5項目（日時/承認者/対象/判断/evidence）記録欄が存在。

- DoD-1:
  - 依存未確定時の判定を `ProceedDecision: Hold` で固定し、解除条件を明記。
- DoD-2:
  - `Self-Correction <=3` を明示し、4回目相当で停止（Stop）する。
- DoD-3:
  - Non-goals に「実装変更なし」「04_Documentation本文更新なし」を明記。

### Phase 4: Execute（本Issue Draft本文のみ更新）
- 実施内容:
  - Phase 1〜6 の直列フローを再編し、評価軸（可読性・一貫性・検証可能性）を AC/DoD に追加。
  - 05-06/05-07 と整合する判定語彙を固定。
  - Open候補化条件を `U1〜U3` として明文化。
- 非実施:
  - 05-06/05-07 への編集。
  - `04_Documentation/**` の本文更新。

### Phase 5: Verify（依存Issue整合とテスト可能性確認）
- 依存Issue整合:
  - 05-06/05-07 と `Dependency status: 未確定`、`ProceedDecision: Hold`、`docs-check必須` が矛盾しないこと。
- テスト可能性:
  - 下記 Validation plan で項目存在確認と体裁検証が可能。
- 判定:
  - **Hold維持**（依存証跡未確定のため）。

### Phase 6: Proceed（Open候補化条件と残課題）
- Open候補化条件:
  - U1: 05/06/07 で `ProceedDecision` 語彙が完全一致。
  - U2: 本Issueに `Approval Record` 5項目が記録済み。
  - U3: `Dependency status` が未確定以外へ更新され、根拠リンクが追記済み。
- 残課題:
  1. DOC-OPS-05 Open gate 判定証跡の確定待ち。
  2. 3Issue横断での再判定日時同期。
  3. Hold解除時の承認ログ追記責務者の明確化（ADR-0025責務境界に準拠）。

## Approval Record（Open化判定入力）
- 日時: `TBD`
- 承認者: `TBD`
- 対象: `DOC-OPS-05-05`
- 判断: `TBD (Go/NoGo)`
- Evidence: `TBD`

## Validation
- docs-check: **必須**
- unit/integration/e2e: **期待レベル定義のみ（非目標）**

### Validation plan（コマンド）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- `rg -n "Phase 1:|Phase 2:|Phase 3:|Readability|Consistency|Verifiability|Approval Record|ProceedDecision|Dependency status" 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- `git diff --check -- 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`

## Non-goals
- `03_Implement/**` の実装変更
- `04_Documentation/**` 本文改稿
- 05-06 / 05-07 Issue本文の編集
- unit/integration/e2e 実行結果の新規作成

## Proceed tri-state
- ProceedDecision: **Hold**
- Reason: `DOC-OPS-05` 依存確定証跡待ち。
- Proceed判定日: `2026-05-06`
- Stop条件: self-correction が4回目相当に到達、または05-06/05-07と矛盾し解消不能になった場合。
