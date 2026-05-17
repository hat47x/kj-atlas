# Issue Draft: DOC-OPS-05-02 04_Documentation/codex_skill_operations.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Ready
- Source Issue: N/A
- Priority: P2
- Owner: Stream E
- Scope: `04_Documentation/codex_skill_operations.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `00_Prompt/codex_gsd_skill_ops.md`, `01_Plans/documentation_quality.md`, `04_Documentation/codex_skill_operations.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `DOC-OPS-05-02`
- RequirementStatement: 対象文書の公開境界を明示し、Open化判定に必要な判断情報を不足なく揃える。
- PriorityClass: Must
- AcceptanceScenario: 前提=DOC-OPS-05前半はIssue品質固定; 操作=公開/内部分類根拠と検証手順を記載; 期待結果=Ready/Hold/Needs-decision判定可能; 除外=本体文書改稿
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## Proposed classification
- Decision: **Move internal（維持）**
- Rationale: 内部運用手順・権限運用の性格が強く、公開境界を越えると誤公開リスクがある。

## Acceptance criteria / DoD（補完合意済み）
- [ ] AC1 分類方針（Move internal）と根拠（Audience/Goal/Public boundary）を単一箇所で参照可能。
- [ ] AC2 GoNoGoGate=Required の No-Go 条件（内部運用手順・非公開導線を含む場合）を明記。
- [ ] AC3 Validation plan は `docs-check` と一致。
- [ ] AC4 Proceed を `Ready/Hold/Needs-decision` 三値で記録。
- [ ] DoD1 Verifyは `git diff --check` と memo validator の成功を必須化。
- [ ] DoD2 Self-correction は最大3回、4回目相当は停止して Hold。

## Mini Phase（single cycle）
### 1) Read
- 本Issueを再読し、docs-only・当該ファイル限定編集を確認。

### 2) Plan
- 重複ログを除去し、分類/AC/DoD/Proceed を1系統に正規化する計画を確定。

### 3) Execute
- 本Issueメモ内のみ更新。AC/DoD補完提案を採用済みとして本文へ固定。

### 4) Verify
- `git diff --check`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-correction: 0/3

### 5) Proceed
- 判定: **Hold**
- 根拠: internal運用責務が主で public-exposure のGo条件を満たさない。
- Blocker: なし（分類は確定、公開化のみ保留）。


## Stream H DOC-OPS-05 serial update（2026-04-30）

### Phase 1 Read同期
- Read Order（00→02）と本Issue、対象Docを再読し、docs-only制約を確認。

### Phase 2 章ごとのAC定義
- AC固定: Audience / Goal / Non-goal / Public boundary / Related / GoNoGoGate / VerificationLevel(docs-check)。

### Phase 3 章単位更新（直列）
- 本Issueに対応する章のみを更新対象として直列処理し、未承認事項の確定化は行わない。

### Phase 4 docs-check / link-check
- `git diff --check` と `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md` を実行対象とする。
- 自己修復回数: 0/3（4回目相当はHold停止）。

### Phase 5 issue更新
- 判定: **Ready**（停止条件非該当、docs-only維持）。


## Stream F serial run（2026-05-01）

### Phase 1: Read同期
- 本Issueと `04_Documentation/codex_skill_operations.md` を再読し、allowlist（Issue+対応docの2ファイル）内での docs-only 更新に限定することを確認。

### Phase 2: ADR/CDC判定
- 判定: **新規決定なし**（DecisionStatus=Fixed を維持）。
- C/D/C: 既存の `Move internal` 判定を再利用し、未承認事項の確定化は行わない。

### Phase 3: Plan
- AC/DoD補完: `Proceed` 三値（Go/Hold/Needs-decision）と `docs-check` 実行ログの追跡性を強化。
- docs-check観点固定: `git diff --check` / issue memo validator / 用語整合（Move internal, Public boundary, GoNoGoGate）。

### Phase 4: Execute
- 本Issueに Stream F 実行ログを追記し、対応doc側にも同日の直列ログを追記（単一docのみ）。

### Phase 5: Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`
- `rg -n "Stream F serial run（2026-05-01）|Phase 1: Read同期|Phase 5: Verify|Move internal" 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md 04_Documentation/codex_skill_operations.md`
- `git diff --check`
- Self-Correction: 0/3

### Phase 6: Proceed
- 判定: **Go**
- 理由: allowlist内・単一doc更新・未承認事項の確定化なし・docs-check整合を満たす。


## Stream G normalization pass（2026-05-04）

### Phase 1: Read同期（Issue ↔ 04_Documentation 対応表）
| Issue | Target 04_Documentation | Current classification |
| --- | --- | --- |
| `issue-doc-ops-05-02-04doc-codex-skill-operations.md` | `04_Documentation/codex_skill_operations.md` | 既存本文の Decision / Proposed classification を継承 |

### Phase 2: Plan（AC / DoD 統一テンプレ）
- AC（統一）
  - 読者タスク完遂性: Audience / Goal / Non-goal が追跡可能。
  - 用語統一: 役割語彙と判定語彙（Move internal / Improve external / GoNoGo）を統一。
  - 参照導線: Related ADR/Spec と対象04文書の相互参照を明記。
- DoD（統一）
  - 相互参照が明記される。
  - 品質ゲート（`docs-check` + `git diff --check`）が明記される。
  - 更新責務（Issue整備担当 / 04_Documentation改稿担当の分離）が明記される。

### Phase 3: Execute（標準セクション）
- 目的: DOC-OPS-05対象Issueを、公開境界を崩さず運用できる品質に正規化する。
- 範囲: 本Issue本文（`01_Plans/issues`）のみ。
- 非対象: `04_Documentation/**` 本文改稿、`03_Implement/**`、shared統合3ファイル。
- 検証観点: メタ項目充足 / 優先度矛盾なし / リンク表記整合 / docs-check一致。
- 停止条件: scope逸脱検知、自己修復4回目相当、未承認確定化要求。
- 並行実行可能フラグ: **No (security-lane serial)**。

### Phase 4: Verify（重複・矛盾・リンク）
- 重複Issue: 既存DOC-OPS-05連番内で対象重複なし（本Issue固有対象）。
- 優先度矛盾: `Priority=P2` 系列で整合（高優先度との衝突なし）。
- リンク切れ: Related ADR/Spec は既存記載を継承し、解決不能リンクは本パスでは未検出。
- 自己修復: 0/3（本更新時点）。

### Phase 5: Proceed（04_Documentation改訂担当への引継ぎ）
- 引継ぎメモ: 本Issueは「本文改稿を行わず、品質ゲートと参照導線を固定」済み。
- 次担当依頼: `04_Documentation` 側で本Issueの分類（Move internal / Improve external）に従って本文改訂を実施。
- ゲート条件: 改訂後は `docs-check` を再実行し、Issue側の分類・用語・導線と一致確認すること。
