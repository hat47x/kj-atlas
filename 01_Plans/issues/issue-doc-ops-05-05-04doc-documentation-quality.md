# Issue Draft: DOC-OPS-05-05 01_Plans/documentation_quality.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream I
- Scope: `01_Plans/documentation_quality.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `04_Documentation/release.md`
- Dependencies: `DOC-OPS-05`
- Dependency status: `未確定（DOC-OPS-05 の Open gate 判定待ち）`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `DOC-OPS-05-05`
- RequirementStatement: 内部品質基準文書としての扱いを固定し、Open化審査に必要な判断情報を揃える。
- PriorityClass: Must
- AcceptanceScenario: 前提=Draft品質均一化; 操作=分類方針/品質ゲート/検証手順を記載; 期待結果=Open可否を一読判定; 除外=本体改稿
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## Open gate判定情報（Fixed）
### Classification（Move internal / Improve external）
- Decision: **Move internal（固定）**
- Classification basis:
  1. Audience: 文書執筆者・レビュアー向け内部品質統制。
  2. Goal: 公開文書の品質担保ルールを内部で運用すること。
  3. Public boundary: 対外説明本文ではなく、内部審査の基準書。
- Boundary note: CE/HIL/FBおよび実装コード変更は対象外。

### GoNoGoGate=Required（判定条件）
- Gate type: `Required`
- Go条件（全件必須）:
  1. internal/public の責務分離（上記Classification basis）が明文化済み。
  2. Open判定に必要な4要素（Classification / Gate / Verification / Proceed）が本メモ単体で追跡可能。
  3. `docs-check` 手順・実行結果・自己修復回数（<=3）が併記されている。
  4. 依存 `DOC-OPS-05` のOpen gateが確定済み。
- NoGo/Hold条件（いずれかで不成立）:
  - Go条件の欠落。
  - 依存 gate 未確定。
- Gate verdict: **NoGo（現時点）**

### Verification（docs-check）
- Planned checks:
  - `git diff --check -- 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- Result summary: pass
- Self-correction budget: `0/3`

### Proceed tri-state
- ProceedDecision: **Hold**
- Alternatives: `Proceed` / `Hold` / `Stop`
- Reason: Move internal 判定は固定済みだが、依存 `DOC-OPS-05` gate が未確定。

## Acceptance criteria / DoD
- [x] AC1 Move internal 判定と分類根拠（Audience/Goal/Public boundary）を単一箇所化。
- [x] AC2 GoNoGoGate=Required のGo/NoGo条件を明文化。
- [x] AC3 Validation plan が `docs-check` と一致。
- [x] AC4 Proceed 三値（Proceed/Hold/Stop）を記録。
- [x] DoD1 Verify結果とSelf-correction回数を併記。
- [x] DoD2 Self-correction 最大3回、超過時は Hold。

## Phase execution record（Stream I / 2026-05-03）
### Phase 1: Read同期
- 本Issueを再読し、Open gate判定に必要な4要素（Classification/Gate/Verification/Proceed）の単独再読性を確認。
- 依存 `DOC-OPS-05` が未確定であることを再確認。

### Phase 2: ADR明文化（Context/Decision/Consequences）
- Context: Move internal 判定は固定済みだが、依存 gate は未確定でOpen化判断を確定できない。
- Decision: 判定情報を本Issue単体で再読完結できる構成として維持し、Proceedは Hold を維持する。
- Consequences: 依存未確定時の誤Proceedを防止し、fail-safe（Hold/Stop遷移）を保持する。

### Phase 3: Plan（AC/DoD不足補完）
- AC/DoDの狙いを Open gate 判定情報に直結させ、再読時の判定手順を固定。
- 不足補完方針: 「依存確定証跡」「docs-check結果」「self-correction<=3」を同一メモ内で追跡可能に維持。

### Phase 4: Execute（メモ整備のみ）
- 本Issueメモのみ整備（表現統一・判定理由明文化）。
- 実装コード/他ファイルの変更は実施しない。

### Phase 5: Verify（docs-check / self-correction<=3）
- `git diff --check -- 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- Self-correction count: `0/3`
- Verify verdict: **Pass**

### Phase 6: Proceed/Stop
- Final decision: **Hold**
- Reason: 依存 `DOC-OPS-05` Open gate が未確定であり、Fail-safeにより Proceed 不可。

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
