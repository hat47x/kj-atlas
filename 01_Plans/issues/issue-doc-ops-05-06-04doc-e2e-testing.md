# Issue Draft: DOC-OPS-05-06 04_Documentation/e2e_testing.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream F (Doc-Ops Draft)
- Scope: `04_Documentation/e2e_testing.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/e2e_testing.md`, `01_Plans/documentation_quality.md`
- Dependencies: `01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`, `01_Plans/issues/issue-doc-ops-05-07-04doc-e2e-verification-log-2026-03-03.md`
- Dependency status: `未確定（DOC-OPS-05 Open gate 判定待ち）`

## Requirement meta I/F
- RequirementID: `DOC-OPS-05-06`
- RequirementStatement: E2E運用文書の公開改善方針を維持しつつ、Open化判定情報を固定する。
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Classification（Fixed）
- Decision: **Improve external**
- Basis: E2E検証導線を利用者に提示する公開導線文書である。

## Phase Run（Plan→Execute→Verify→Proceed）
### Phase 1: Read（Draft理由・不足情報確認）
- Draft理由を「依存確定証跡不足」に統一。
- 不足情報は Approval Record 5項目に整理。

### Phase 2: AC/DoD補完提案→合意（提案整備）
- AC提案:
  - AC-1: Improve external の根拠と公開境界を単体再読可能化。
  - AC-2: docs-check pass + self-correction `<=3` 記録。
  - AC-3: Approval Record（日時/承認者/対象/判断/evidence）記録。
- DoD提案:
  - DoD-1: 3Issueで Gate/Validation/Proceed の語彙・構造一致。
  - DoD-2: 依存未確定は **Hold**、4回目相当は **Stop**。

### Phase 3: Open化に必要な前提・証跡定義
- 前提:
  1. ADR-0019との整合維持。
  2. DOC-OPS-05 依存確定。
  3. docs-only 制約維持。
- 証跡:
  - `git diff --check -- 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`

### Phase 4: 相互リンク・用語統一・完了条件整備
- 05/05/07との相互リンクを固定。
- 判定語彙を `Go/NoGo`, `Proceed/Hold/Stop` に統一。
- 完了条件は「依存確定 + AC/DoD充足 + docs-check pass」。

### Phase 5: Verify（Draft脱却判定、非競合確認）
- Draft脱却判定: **Hold**（依存未確定）。
- 非競合確認: 3Issue間で Gate定義・Stop条件の競合なし。
- Self-correction: `1/3`。

## Validation
- docs-check: **必須**
- unit/integration/e2e: **期待レベル定義のみ（非目標）**

## Non-goals
- `03_Implement/**` の実装変更
- `04_Documentation/e2e_testing.md` 本文改稿
- unit/integration/e2e 実行結果の新規作成

## Proceed tri-state
- ProceedDecision: **Hold**
- Reason: `DOC-OPS-05` 依存確定証跡待ち。


## Stream F draft整備 pass（2026-05-06 / DOC-OPS-05-06）

### Phase 1 Read同期
- 対象限定を確認: 本対応はIssueメモ整備のみ。`04_Documentation/e2e_testing.md` 本文改稿は非実施。
- 依存状態を確認: DOC-OPS-05 Open gate証跡未確定のため、Open化判定は保留。

### Phase 2 ADR要素（C/D/C）
- Context: E2E運用導線は公開対象だが、判定証跡が不足した状態でOpen化すると運用境界が曖昧になる。
- Decision: Classificationを `Improve external` 固定、判定要件を `Approval Record` 5項目で明文化する。
- Consequences: 公開文書としての改善方針を維持しつつ、依存未確定時は安全側（Hold）で停止できる。

### Phase 3 Plan→Execute
- Plan: AC/DoDに「再読可能性」「self-correction上限」「依存未確定時停止」を保持する。
- Execute: 用語を `Go/NoGo` と `Proceed/Hold/Stop` に統一し、3Issue横断整合を維持する。

### Phase 4 Verify→Proceed
- Verify: docs-check基準の整合確認を実施。
- Proceed: 依存証跡未確定のため `Hold` 継続。
- Self-correction: `2/3`（上限内）。


## Stream F unblock criteria update（2026-05-06 / execution readiness）

### Read
- 停止要因は `DOC-OPS-05依存証跡未確定` と `3Issue横断の語彙整合未確認`。

### AC/DoD解除条件（Open化条件）
- [ ] U1: `Classification: Improve external` の根拠段落に公開境界（含む/含まない）を1段落で追記。
- [ ] U2: 05/05/07との相互リンクが存在し、各Issueの Proceed 判定日時が記録されている。
- [ ] U3: `Dependency status` が更新され、Hold解除の根拠を明記。

### Validation plan（コマンド）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `rg -n "Classification|Dependency status|ProceedDecision|Related Backlog" 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `git diff --check -- 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`

### Proceed
- 判定: **Hold維持**。
- Open化条件: U1〜U3完了時に Draft解除可。
- Proceed判定日: `2026-05-06`（依存更新時に再判定）。
- Stop条件: self-correction が4回目相当に到達、または05/05/07間でProceed語彙が不一致の場合は停止。


## Stream K alignment pass（2026-05-06 / DOC-OPS-05-06 E2E Draft hardening）

### Phase 1: Read（現状・依存・不足抽出）
- 現状: `04_Documentation/e2e_testing.md` は公開向けE2E方針の正本であり、Issue 05-06 は Open化判定情報の固定を担う。
- 依存: `05-05`（内部品質基準）と `05-07`（検証ログ配置）の Proceed 判定整合が前提。いずれも現時点は `Hold`。
- 不足: 「対象シナリオ範囲」「環境前提」「成功/失敗判定」「ログ必須項目」の記述が Draft内で散在し、着手ゲートとして単体再読性が不足。

### Phase 2: ADR（C/D/C）
- Context: E2E方針の境界が曖昧なまま着手すると、再現性と監査可能性（pass/fail根拠）が崩れる。
- Decision: 本Draftで **Scenario Scope / Environment Preconditions / Judgement Axes** を固定し、判定不能時は `Hold` で停止する。
- Consequences: 05-05/05-07と矛盾しない共通ゲート（docs-check必須、self-correction上限3、4回目相当Stop）を維持したまま、Open化可否の再判定が可能になる。

### Phase 3: Plan（AC/DoD明確化）
- AC（受入条件）
  - AC-1: 対象シナリオを `Smoke / Core Flow / Security-Safety Flow` の3区分で明示。
  - AC-2: 環境前提を `Compose優先 / SQLite代替 / 実行不能時blocked記録` の3段階で明示。
  - AC-3: 成功/失敗判定を `pass/fail/blocked` + 必須ログ4項目（実行コマンド・成否・未実施理由・再開条件）で明示。
  - AC-4: 05-05/05-07との判定語彙（`Go/NoGo`, `Proceed/Hold/Stop`）一致を確認。
- DoD（完了条件）
  - DoD-1: 本Issue単体で着手基準（範囲/前提/判定軸/停止条件）が再読可能。
  - DoD-2: `Dependency status` と `ProceedDecision` が依存Issueの最新状態と矛盾しない。
  - DoD-3: docs-check計画（validator / rg / diff-check）が記載され、検証可能性が担保される。

### Phase 4: Execute（本Draft本文のみ更新）
- 実施範囲を `01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md` のみに限定。
- 05-05/05-07本文、および `04_Documentation/e2e_testing.md`・実装コードは非編集を維持。

### Phase 5: Verify（依存整合・判定軸検証・用語一貫）
- 依存整合: 05-05/05-07が `Hold` 維持のため、本Issueの Proceed も `Hold` を維持する。
- 判定軸検証可能性: AC-1〜AC-4 を `docs-check` で機械確認できるコマンドを保持する。
- 用語一貫性: `Go/NoGo`, `Proceed/Hold/Stop`, `pass/fail/blocked`, `self-correction <=3` を固定。
- Self-correction: `3/3`（次回追加修正が必要な場合は Stop 条件を適用）。

### Phase 6: Proceed（Open化可否・未解決論点・次手順）
- ProceedDecision: **Hold**
- Open化可否: **Not ready**（依存確定証跡とApproval Record確定待ち）。
- 未解決論点:
  1. `DOC-OPS-05` Open gate の最終承認記録（日時/承認者/evidence link）。
  2. 05-05/05-07のProceed再判定日との同期。
  3. blocked発生時の再開条件テンプレートの運用先確定（Issue内記録かverification log集約か）。
- 次手順:
  1. 依存Issue（05-05/05-07）の `Dependency status` 更新を確認。
  2. Approval Record 5項目を本Issueへ追記。
  3. docs-check実行結果を添えて Draft解除可否を再判定。

## Stream H Ready化 pass（2026-05-06 / DOC-OPS-05-06）

### 1) Ready gate（Open判定前の必須条件）
- [ ] RG-0506-1: AC-1〜AC-4 が `done/pending/hold` で判定記録済み。
- [ ] RG-0506-2: DoD-1〜DoD-3 が `done/pending/hold` で判定記録済み。
- [ ] RG-0506-3: Approval Record 5項目が記録済み。
- [ ] RG-0506-4: 05-05/05-07 の `ProceedDecision` と再判定日が同期済み。

### 2) 品質ゲート定義（docs-check）
- Gate-E1: `validate_active_issue_memos.py` pass。
- Gate-E2: `Classification/Dependency status/ProceedDecision` の必須キー存在確認。
- Gate-E3: `git diff --check` pass。

### 3) E2E導線の固定
- 方針境界:
  - Compose優先 / SQLite代替 / blocked記録 を維持。
  - 実行不能時は `pass/fail/blocked` の tri-state で記録する。
- 本IssueはDraft整備のため、`04_Documentation/e2e_testing.md` 本文更新は非目標を維持。

### 4) Proceed
- ProceedDecision: **Hold（Ready gate定義完了、依存確定待ち）**
- Ready化状態: **判定基準はReady、Draft解除は未実施**
