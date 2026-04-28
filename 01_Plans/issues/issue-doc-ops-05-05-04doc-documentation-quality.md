# Issue Draft: DOC-OPS-05-05 01_Plans/documentation_quality.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `01_Plans/documentation_quality.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `04_Documentation/release.md`
- Expected verification level: `docs-check`

## Execution protocol（DOC-OPS-05-Set1 固定）

- 各Issue開始時は **必ず Phase 1 (Read) を再実行** してから着手する。
- 実行順序は **Phase 1 Read → Phase 1.5 ADR/CDC → Phase 2 Plan → Phase 3 Execute → Phase 4 Verify → Phase 5 Proceed** の直列固定。
- Verify 失敗時の自己修復は **最大3回**。4回目相当は **即停止（Hold）** とする。

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-05`
- RequirementStatement: `01_Plans/documentation_quality.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## Contract profile（DOC-OPS-05-05 固定）

- freeze_mode: `contract-only`
- downstream_policy: `read-only reference`
- quality_gate_contract: `QG-definition-clarification-only`
- scope_guard: `01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md` 以外は編集禁止

## 1) 課題 / Problem statement

- `01_Plans/documentation_quality.md` が、対外公開文書として維持すべきか、内部文書へ移すべきか未整理。
- 現状のままだと `04_Documentation/` に内部向け情報が残るか、逆に公開候補文書の改善優先度が見えない。
- AIエージェントが外部向け資料を作る際の配置判断が曖昧なままになる。

## 2) 背景 / Context

- 公開文書ではなく内部品質基準として扱うべき内容。
- `01_Plans/minimal-context-triage.md` 導入により、低情報価値の一覧再読ではなく、必要な対象だけを追う運用へ寄せたい。
- `01_Plans/documentation_quality.md` は対外文書作成の内部品質基準として扱う。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 外部読者へ公開する文書と内部運用文書の混在を減らし、判断コストを下げる。
- 安全（THREAT_MODEL / SafeMode）: 公開境界の曖昧さを減らし、内部情報の対外露出を防ぐ。
- 企業・行政要件（enterprise_architecture）: 役割・運用責務を外部説明可能な形へ整理しやすくする。
- 後方互換（schemas）: 文書配置の見直しで実装互換性は変えない。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs
- 推奨アクション: **Move internal**
- 実施方針: `01_Plans/documentation_quality.md` を内部正本として固定し、公開側には導線のみを残す。
- 非目標: このIssue単体で対象文書の全文改稿や実装仕様変更は行わない。

## 5) 受入条件 / Acceptance criteria

- [ ] `01_Plans/documentation_quality.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
- [ ] 分類の根拠として Audience / Goal / 公開境界の観点が記録される。
- [ ] 変更先候補（移設先または改善対象節）が明記される。
- [ ] 必要な検証（unit/integration/e2e/docs-check）が `Expected verification level` と一致する。
- [ ] `GoNoGoGate` の要否（Required/Optional/N/A）が明示され、Required時は判定基準が本文に記載される。
- [ ] セキュリティ境界に影響するIssueでは `SecurityGateImpact` を明示し、レビューゲート項目を記載する。
- [ ] 受入シナリオ最小テンプレ（前提/操作/期待結果/除外）は Process/実装系Issueで必須、Docs-onlyでは任意（推奨）。
- [ ] quality gate 定義は contract-only で明確化し、release 連携は read-only reference として整合確認する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 対象文書の Audience / Goal / Non-goal を確認する。
- [ ] T2 内部移設か対外改善かを判定し、根拠を本文へ追記する。
- [ ] T3 次の実行単位（移設先作成 or 公開改善PR）を明記する。
- [ ] T4 `04_Documentation/release.md` は read-only 参照のみで整合確認し、編集しない。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 期待結果:
  - 分類根拠と次アクションが差分として確認できる。
  - quality gate 定義の明確化が contract-only で記録され、release 参照が read-only であることが確認できる。
- 未実施時の理由・代替検証:
  - 本Issueは計画メモ作成のみのため、自動テストは不要。差分確認を代替検証とする。

## 8) 代替案 / Alternatives considered

- 代替案A: 04配下の全文書を一律に公開文書として扱う。
- 代替案B: 04配下の全文書を一律に内部文書へ移す。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 分類だけ作って実体変更が後続Issueに落ちない。
- 影響範囲: `04_Documentation/` の整理計画全体。
- ロールバック手順: 判定が不適切なら本IssueをDraftのまま更新し、推奨アクションを差し替える。

## 10) Additional context

- 本Issueは `01_Plans/documentation_quality.md` 専用の分類/改善トラッキングメモ。
- 実作業では `01_Plans/minimal-context-triage.md` と関連ADRだけを開き、一覧再読を前提にしない。

---

## 11) 6-phase execution record（2026-04-28）

### Phase 1: Read
- 本Issueを再読し、`Scope`・`VerificationLevel=docs-check`・`DecisionStatus=Fixed` を確認。
- docs-only 境界を確認し、実装コード・他Issueファイル非変更を固定。

### Phase 1.5: ADR/CDC
- `ADR-0024` の docs-check 境界（必須/CI拡張）を read-only 参照で再確認。
- `04_Documentation/release.md` の Mandatory（QG-1〜QG-6）連携記述を read-only 参照で確認。
- CDC（contract drift check）として、本Issueの更新を `contract-only` に固定し、対象外編集を禁止。

### Phase 2: Plan（AC/DoD固定）
- AC固定:
  - AC-P1: 分類根拠として Audience / Goal / Public boundary を本文で必須追跡。
  - AC-P2: GoNoGoGate=Required の Go / No-Go 判定条件を本文で再現可能化。
  - AC-P3: `Expected verification level` と `Validation plan` のコマンド一致を必須化。
  - AC-P4: quality gate 明確化は contract-only、release は read-only reference を必須化。
- DoD固定:
  - DoD-P1: Read → ADR/CDC → Plan → Execute → Verify → Proceed を単一セクションで記録。
  - DoD-P2: Proceed判定を `Ready / Hold / Needs-decision` の三値で明記。
  - DoD-P3: Verify不一致は最大3回自己修復、4回目相当は停止。

### Phase 3: Execute
- 実行プロンプト（DOC-OPS-05-05）に合わせ、Execution protocol と Contract profile を更新。
- 既存分類方針 `Move internal` を維持しつつ、release 連携を read-only 参照として明記。

### Phase 4: Verify
- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 自己修復回数: 0/3（4回目停止条件は未発動）。

### Phase 5: Proceed
- 判定: **Ready**
- 判定理由: `DecisionStatus=Fixed`、`VerificationLevel=docs-check`、分類方針 `Move internal`、`contract-only/read-only reference` 整合、3回上限ポリシー記載を満たす。

## Authoring Checklist（人間/生成AI 共通）
- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。

## Stream H Open化準備 run（2026-04-28）

### Phase 1 Read（issue + 対応docペア確認）
- 対応Issueと対象文書のペアを再読し、公開境界・分類・停止条件の整合を確認。

### Phase 2 Plan（Draft→Openゲート明文化）
- Open化ゲートを次の4点で固定。
  1. 必須メタ（Audience/Goal/Non-goal/Public boundary/Outcome または Requirement meta I/F）が追跡可能。
  2. AC/DoD/Validationが docs-check 前提で再現可能。
  3. 未承認事項の確定化を行わない（DecisionStatus=Fixed の範囲外は承認待ち）。
  4. self-repair は最大3回、4回目相当で停止。

### Phase 3 Execute（不足メタ/AC/Validation/Stop条件補完）
- 本セクションを追記し、Open化判定に必要な最小メタ（ゲート、検証、停止条件、Proceed判定）を明示。

### Phase 4 Verify（ゲート到達判定 + docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "Stream H Open化準備 run（2026-04-28）|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed|Open化可否" 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- `git diff --check`
- self-repair: 0/3（4回目相当は停止）。

### Phase 5 Proceed（Open化可否）
- Open化可否: **Yes**。
- 判定理由: Draft→Openの最小ゲート（メタ、AC/DoD、検証、停止条件）を満たし、docs-only境界を維持。
