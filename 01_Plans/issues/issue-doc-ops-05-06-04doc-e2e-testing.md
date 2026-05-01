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

## Proposed classification
- Decision: **Improve external（維持）**
- Rationale: 対外導線の主要文書であり、公開品質改善の価値が高い。

## Acceptance criteria / DoD（補完合意済み）
- [ ] AC1 Improve external 判定と根拠を明記。
- [ ] AC2 GoNoGoGate=Required（ADR-0019整合、公開境界）を明文化。
- [ ] AC3 Validation plan は `docs-check` と一致。
- [ ] AC4 Proceed 三値を記録。
- [ ] DoD1 Verify結果併記。
- [ ] DoD2 Self-correction 最大3回、超過時は Hold。

## Mini Phase（single cycle）
### 1) Read
- 本Issueを再読し、docs-only・単一ファイル編集制約を確認。

### 2) Plan
- 重複実行記録を整理し、分類/条件/Proceedを1セット化する計画を確定。

### 3) Execute
- 本Issueメモのみ更新。AC/DoD不足補完を本文に反映。

### 4) Verify
- `git diff --check`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-correction: 0/3

### 5) Proceed
- 判定: **Conditional**
- 根拠: Improve external 方針、GoNoGo条件、Verify手順は再現可能。
- Blocker: 依存 `DOC-OPS-05` の Open gate未確定。


## Stream H DOC-OPS-05 serial update（2026-04-30）

### Phase 1 Read同期
- Read Order（00→02）と本Issue、対象Docを再読し、docs-only制約を確認。

### Phase 2 章ごとのAC定義
- AC固定: Audience / Goal / Non-goal / Public boundary / Related / GoNoGoGate / VerificationLevel(docs-check)。

### Phase 3 章単位更新（直列）
- 本Issueに対応する章のみを更新対象として直列処理し、未承認事項の確定化は行わない。

### Phase 4 docs-check / link-check
- `git diff --check` と `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md` を実行対象とする。
- 自己修復回数: 0/3（4回目相当はHold停止）。

### Phase 5 issue更新
- 判定: **Ready**（停止条件非該当、docs-only維持）。

## Stream E execution log（2026-05-01 / DOC-OPS-05-06 Draft解消）

### Phase 1: Draft issueのAC/DoD明文化
- Assumption: `Improve external` 判定は維持し、本文改稿より先にOpen判定ゲートを可逆的に固定する。
- AC補強: `ADR-0019整合` / `GoNoGoGate=Required` / `docs-check再現性` をOpen必須条件として扱う。

### Phase 2: Plan（不足メタ提案）
- 提案1: `Improve external` のOpen責務者（最終判定ロール）を明示する。
- 提案2: `ADR-0019整合` の判定証跡（どの節を根拠にするか）を固定する。
- 提案3: 依存 `DOC-OPS-05` 未解消時の既定判定を `Hold` に統一する。

### Phase 3: 用語・役割・導線・固定値(D1-D4)整合チェック
- canonical語彙: `Security Officer / System Owner / Platform Operator`。
- 状態語彙: `DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed` + `StoppedForClarification`。
- D1-D4: `4h / 2h / 代理承認なし / 48h + 15m/60m` を再定義せず参照固定。

### Phase 4: issueステータス更新案（Draft→Open条件）
- 提案: **Open候補（条件付き）**。
- Open条件案:
  1. `e2e_testing.md` の分類ヘッダ（Improve external）と本Issue判定の一致。
  2. 4観点（用語・役割・導線・D1-D4）でdrift=0。
  3. `validate_active_issue_memos.py` と `git diff --check` がpass。

### Phase 5: AC/DoD判定
- 判定: **Conditional**（記録要件は充足、依存未解消のためOpen化保留）。
- Self-correction: 0/3。

## Stream E Proceed判定（2026-05-01）
- Open化可否: **Hold**
- Stopper:
  1. 依存 `DOC-OPS-05` の gate確定待ち。
  2. Open最終判定ロール（誰がOpen宣言するか）の明文化待ち。
