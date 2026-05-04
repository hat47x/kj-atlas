# Issue Draft: DOC-OPS-05-06 04_Documentation/e2e_testing.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream G
- Scope: `04_Documentation/e2e_testing.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/e2e_testing.md`, `04_Documentation/operations.md`
- Dependencies: `DOC-OPS-05`
- Dependency status: `未確定（DOC-OPS-05 の Open gate 判定待ち）`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `DOC-OPS-05-06`
- RequirementStatement: E2E運用文書の公開改善方針を維持しつつ、Open化判定に必要な情報を固定する。
- PriorityClass: Must
- AcceptanceScenario: 前提=ADR-0019を正本維持; 操作=Improve external方針と検証/Proceedを明記; 期待結果=Open化着手可否が判断可能; 除外=本文改稿
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## Open gate判定情報（Fixed）
### Classification（Move internal / Improve external）
- Decision: **Improve external（固定）**
- Classification basis:
  1. Audience: 導入・運用担当者（外部利用者を含む）。
  2. Goal: E2E検証導線を対外に再現可能な形で提示すること。
  3. Public boundary: 対外公開導線の主文書に属する。
- Boundary note: 本Issueは本文改稿ではなく判定情報固定のみ。

### GoNoGoGate=Required（判定条件）
- Gate type: `Required`
- Go条件（全件必須）:
  1. Improve external 判定根拠（Audience/Goal/Public boundary）が明文化済み。
  2. `ADR-0019` との整合点（E2E方針・運用runbook参照）が記録済み。
  3. `docs-check` の再現コマンドと結果、自己修復回数（<=3）が併記済み。
  4. 依存 `DOC-OPS-05` のOpen gate確定。
- NoGo/Hold条件（いずれかで不成立）:
  - Go条件の欠落。
  - 依存 gate 未確定。
- Gate verdict: **NoGo（現時点）**

### Verification（docs-check）
- Planned checks:
  - `git diff --check -- 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- Result summary: pass
- Self-correction budget: `0/3`

### Proceed tri-state
- ProceedDecision: **Hold**
- Alternatives: `Proceed` / `Hold` / `Stop`
- Reason: Improve external 判定は固定済みだが、依存 `DOC-OPS-05` gate未確定。

## Acceptance criteria / DoD
- [x] AC1 Improve external 判定と分類根拠を明記。
- [x] AC2 GoNoGoGate=Required のGo/NoGo条件を明文化。
- [x] AC3 Validation plan が `docs-check` と一致。
- [x] AC4 Proceed 三値（Proceed/Hold/Stop）を記録。
- [x] DoD1 Verify結果とSelf-correction回数を併記。
- [x] DoD2 Self-correction 最大3回、超過時は Hold。

## Phase execution record（Stream G）
### Phase 1: Read
- 本Issue・`ADR-0019`・`e2e_testing.md` の関係を再読。

### Phase 2: ADR/CDC
- ADR整合: `ADR-0019` をE2E運用の正本として固定。
- CDC: docs-only / 単一ファイル編集を維持。

### Phase 3: Plan
- Open gate情報4要素の統合とRequired判定条件の明文化を計画。

### Phase 4: Execute
- 本Issueメモのみ更新し、Improve external根拠とGate条件を固定。

### Phase 5: Verify
- `git diff --check -- 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- Self-correction count: `0/3`
- Verify verdict: **Pass**

### Phase 6: Proceed
- Final decision: **Hold**
- Reason: 依存 `DOC-OPS-05` Open gate未確定のため。

## Stream F integration log（2026-05-03 / Draft Gate Management）

### Read
- `ADR-0019` 参照整合、Required Gate、依存状態を再読し、Open化前提未達を確認。

### CDC
- Context: Improve external 判定は固定済みだが、依存 gate が未確定。
- Decision: 判定情報の固定に限定し、本文改稿・実装変更を行わない。
- Consequences: Open化条件のみを明示し、依存確定まで Hold を維持。

### Plan
- Open化条件（未達時Hold）
  1. `DOC-OPS-05` Open gate 確定
  2. `ADR-0019` との整合記録維持
  3. `docs-check` 再実行で pass、self-correction `<=3`

### Execute
- メモ整備のみ（Docs/Plan範囲、実装コード変更禁止を維持）。

### Verify（max3）
- Verify attempt: `1/3`
- 判定: Pass（判定情報は整合、依存未確定のため Proceed不可）。

### Proceed
- Decision: **Hold**。

## Draft gate解消条件（Open化判定・合意形成専用 / 2026-05-03）

### Phase 1〜6 適合チェック（厳守）
- Phase 1 Read: 上位根拠（関連ADR/Spec）再読ログが当日付で記録されている。
- Phase 2 ADR/CDC: `Context / Decision / Consequences` が本Issue内で更新されている。
- Phase 3 Plan: AC/DoD/依存関係/停止条件が明文化されている。
- Phase 4 Execute: **メモ整備のみ** を実施し、実装変更（`03_Implement/**`）が 0 件である。
- Phase 5 Verify: docs-check 実行結果と self-correction 回数（`<=3`）が記録されている。
- Phase 6 Proceed/Stop: Open可否を `Proceed / Hold / Stop` の三値で記録している。

### Open化 AC（全件必須）
- [ ] AC-Open-1: 依存ステータスが `確定` であり、承認証跡（日時・承認者・対象・判断）が追跡可能。
- [ ] AC-Open-2: 本Issueの Go 条件と NoGo/Hold 条件が矛盾なく併記されている。
- [ ] AC-Open-3: docs-check 結果が最新化され、self-correction が `3回以内`。
- [ ] AC-Open-4: 実装禁止（proposal-only / docs-only / mock I/Fのみ など当該契約）を維持したまま判断情報が完結している。

### Open化 DoD（完了定義）
- [ ] DoD-Open-1: Open判定に必要な入力（AC/DoD/Dependency/Verification）が本Issue単体で再読可能。
- [ ] DoD-Open-2: 未承認・依存未確定・検証未達のいずれかで **自動的に Hold/Stop** へ遷移する fail-safe が残っている。
- [ ] DoD-Open-3: 次工程への引継ぎ文が「実装禁止解除条件」を1文で含む。

### 停止報告（Open化不可時）
- 判定: **Hold（Open化不可）**
- 停止理由: 依存または承認証跡が未確定のため、Draft gate を解消できない。
- 必須アクション（合意形成のみ）:
  1. 依存判定者が `Dependency status=確定` を記録。
  2. 承認ログ最小項目（日時・承認者・対象・判断）を補完。
  3. docs-check を再実行し、self-correction 回数を更新。
- 再開条件: 上記 1〜3 が揃った時点で Phase 6 を再判定する。

---

## Stream H execution log（2026-05-03 / DOC-OPS-05 Draft昇格直列化）

### Phase 1: Read & Sync（05→06→07）
- 05/06/07の3Issueを再読し、06のDraft gate要因を分解:
  1. `DOC-OPS-05` 依存確定証跡不足
  2. 上流Issue（05）のProceed確定待ち
  3. docs-check最新実行結果の維持

### Phase 2: Plan（06のAC/DoD補強）
- 06は中間ノードとして、以下の直列前提を追加:
  - `UpstreamDecisionKey: DOC-OPS-05-05/ProceedDecision`
  - `UpstreamRequiredValue: Proceed`
  - `DownstreamNotice: DOC-OPS-05-07 は 06 のProceed判定後に再判定`
- 検証観点:
  - 品質基準: `01_Plans/documentation_quality.md` の内部品質基準と矛盾しないこと。
  - E2E方針: `ADR-0019` の正本性を維持すること。
  - 検証ログ要件: 実行コマンド・結果・self-correction回数を記録すること。

### Phase 3: Execute（本Issue更新）
- 直列依存キーを本Issueに明示し、単独判定から鎖状判定へ更新。
- 本文改稿・実装変更は未実施（メモ整備のみ）。

### Phase 4: Verify（整合）
- 3Issue間で Proceed 三値運用（Proceed/Hold/Stop）と fail-safe 条件が一致していることを確認。
- Self-correction count: `0/3`
- Verify verdict: **Pass**

### Phase 5: Proceed判定（本Issue）
- Open昇格可否: **Hold**
- 阻害要因:
  1. `Dependency status=未確定`
  2. 上流 `DOC-OPS-05-05/ProceedDecision != Proceed`
- 解消条件:
  1. 05のProceed確定記録を反映。
  2. `DOC-OPS-05`依存確定証跡を記録。
  3. docs-check再実行後、07へ判定引継ぎ。
