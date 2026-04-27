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
- 実行順序は **Phase 1 Read → Phase 2 Plan → Phase 3 Execute → Phase 4 Verify → Phase 5 Proceed** の直列固定。
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

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 対象文書の Audience / Goal / Non-goal を確認する。
- [ ] T2 内部移設か対外改善かを判定し、根拠を本文へ追記する。
- [ ] T3 次の実行単位（移設先作成 or 公開改善PR）を明記する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 期待結果:
  - 分類根拠と次アクションが差分として確認できる。
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

## 11) 5-phase execution record（2026-04-27）

### Phase 1: Read
- 本Issueを再読し、`Scope`・`VerificationLevel=docs-check`・`DecisionStatus=Fixed` を確認。
- docs-only 境界を確認し、実装コード・他Issueファイル非変更を固定。

### Phase 2: Plan（AC/DoD不足のAIドラフト提案）
- ACドラフト提案:
  - AC-P1: 分類根拠として Audience / Goal / Public boundary を本文で必須追跡。
  - AC-P2: GoNoGoGate=Required の Go / No-Go 判定条件を本文で再現可能化。
  - AC-P3: `Expected verification level` と `Validation plan` のコマンド一致を必須化。
- DoDドラフト提案:
  - DoD-P1: Read → Plan → Execute → Verify → Proceed を単一セクションで記録。
  - DoD-P2: Proceed判定を `Ready / Hold / Needs-decision` の三値で明記。
  - DoD-P3: Verify不一致は最大3回自己修復、4回目相当は停止。
- 合意記録: **本Issue内で上記提案を採用し、Phase 3で反映する。**

### Phase 3: Execute
- AC/DoDドラフト提案を本Issue本文へ反映（本節を含む）。
- 分類方針は `Move internal` を維持（再判定なし）。

### Phase 4: Verify
- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 自己修復回数: 0/3（4回目停止条件は未発動）。

### Phase 5: Proceed
- 判定: **Ready**
- 判定理由: `DecisionStatus=Fixed`、`VerificationLevel=docs-check`、分類方針 `Move internal`、3回上限ポリシー記載を満たす。

## Authoring Checklist（人間/生成AI 共通）
- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。
