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
- Dependencies: `DOC-OPS-05`
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

## Proposed classification
- Decision: **Move internal（維持）**
- Rationale: 内部統制向け品質規約のため、公開文書本体とは責務が異なる。

## Acceptance criteria / DoD（補完合意済み）
- [ ] AC1 Move internal 判定と根拠を単一箇所化。
- [ ] AC2 GoNoGoGate=Required の判定条件（公開境界・責務分離）を明文化。
- [ ] AC3 Validation plan は `docs-check` と一致。
- [ ] AC4 Proceed 三値を記録。
- [ ] DoD1 AC確認・Verify結果併記で完了判定。
- [ ] DoD2 Self-correction 最大3回、超過時は Hold。

## Mini Phase（single cycle）
### 1) Read
- 本Issueと `Requirement meta I/F` を再読し、判定情報分散を確認。

### 2) Plan
- 判定情報の集約、AC/DoD不足の補完、5Phase直列記録化を計画。

### 3) Execute
- 本Issueメモのみ更新。指定外ファイルは未編集。

### 4) Verify
- `git diff --check`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-correction: 0/3

### 5) Proceed
- 判定: **Hold**
- 根拠: 内部運用品質ゲート文書として公開境界のGo条件を満たさない。
- Blocker: なし（分類確定済み）。

## Stream E execution log（2026-05-01 / DOC-OPS-05-05 Draft解消）

### Phase 1: Draft issueのAC/DoD明文化
- Assumption: `01_Plans/documentation_quality.md` 本体改稿は本IssueのScope外であり、Open化判定に必要な運用メタ情報の固定を優先する。
- AC/DoD判定軸を `Move internal` 前提で再固定（公開導線化を非目標として明記）。

### Phase 2: 04_Documentation対象章の更新
- 本Issueは `01_Plans/documentation_quality.md` 対応のため、04_Documentation本文更新は **非対象**（docs-only境界を維持）。

### Phase 3: 用語・役割・導線・固定値(D1-D4)整合チェック
- 本Issue単体ではAUTH-OPS-03固定値を新規定義せず、`04_Documentation/security.md` / `operations.md` 側の既存定義を参照のみ。
- 判定: drift未検知（再定義なし）。

### Phase 4: issueステータス更新案（Draft→Open条件）
- 提案: **Draft維持**。
- Open条件案:
  1. DOC-OPS-05全体で `Move internal` 実体移設先が合意済み。
  2. 実体移設PRの受け皿（directory/policy）が確定。
  3. Verify結果（validator + diff check）を再掲。

### Phase 5: AC/DoD判定
- 判定: **Conditional**（Draft解消準備は完了、ただしOpen条件(1)(2)未充足）。
- Self-correction: 0/3。
