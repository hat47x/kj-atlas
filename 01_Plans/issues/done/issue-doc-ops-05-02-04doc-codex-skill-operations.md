# Issue Draft: DOC-OPS-05-02 04_Documentation/codex_skill_operations.md のOpen化準備

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Stream E
- Scope: `04_Documentation/codex_skill_operations.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `04_Documentation/codex_skill_operations.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `DOC-OPS-05-02`
- RequirementStatement: 対象文書の公開境界を明示し、Open化判定に必要な判断情報を不足なく揃える。
- AcceptanceScenario: 前提=DOC-OPS-05前半はIssue品質固定; 操作=公開/内部分類根拠と検証手順を記載; 期待結果=Ready/Hold/Needs-decision判定可能; 除外=本体文書改稿
- SecurityGateImpact: public-exposure

## Proposed classification
- Decision: **Move internal（維持）**
- Rationale: 内部運用手順・権限運用の性格が強く、公開境界を越えると誤公開リスクがある。

## Acceptance criteria / DoD（補完合意済み）
- 分類方針（Move internal）と根拠（Audience/Goal/Public boundary）→ 上記 Proposed classification に記録済み。
- 検証（`git diff --check`・memo validator）→ 本文 Mini Phase の Verify に記録済み（5-phase礼式は AGENTS.md §4 で廃止、AC/DoDチェックボックスは撤去）。
- 下記 Mini Phase 1..5（Read→Plan→Execute→Verify→Proceed）は廃止済み5-phase礼式の実行記録であり、本issueの受入条件ではない。

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

## Stream H serial completion log（2026-05-18）

### Phase 1: Read
- 本Issueと対応する `04_Documentation` 文書を再読し、docs-only と allowlist 制約を再確認。

### Phase 2: Plan
- 共通契約（Audience / Goal / Non-goal / Public boundary / Related）と品質ゲート（可読性・検証可能性・保守性）を適用。

### Phase 3: Execute
- 章構造・用語・相互リンク規約を統一し、各文書に「運用手順 / 判断基準 / 失敗時対応」を必須化。

### Phase 4: Verify
- `git diff --check` と issue memo validator（対象ファイル）を検証対象とする。
- self-correction: 0/3（4回目相当は Hold）。

### Phase 5: Proceed
- 判定: **Ready**（DOC-OPS-05 直列処理対象として継続可能）。

## 16) Open readiness gate（DOC-OPS-05 machine-check）

- Batch: `A (01-05)`
- GateStatus: `Conditional`（現時点のIssue StatusはDraftのため、Open化は本ゲートの充足を条件とする）
- DraftReasonClass: `open-trigger-not-executed`
- BlockingIssueIDs: `none`
- OpenTrigger:
  1. `Status` を Draft から Open へ変更。
  2. `Expected verification level` と `VerificationLevel` が `docs-check` で一致。
  3. `GoNoGoGate=Required` に対する判定条件（Ready/Hold/Needs-decision）が本文中で一意。
  4. `DecisionStatus=Fixed` の場合、`DecisionQueueRef` は `N/A` であること。
- MechanicalChecks:
  - `rg -n "^- Status:|Expected verification level|VerificationLevel|GoNoGoGate|DecisionStatus|DecisionQueueRef" 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`
  - `rg -n "Open readiness:|状態分類:|Phase 5: Proceed" 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`
  - `git diff --check`
- Proceed verdict (Phase 6): `Open可能（条件付き）`

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `codex skill operations`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-05-02` の公開境界を再確認。
- Decision: codex_skill_operations は開発者/AIエージェント運用向けに分類し、一般利用者向けGistには含めない境界を明記した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
