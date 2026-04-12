# Issue Draft: 0019 Phase6 Feedback Loop Operations

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Stream G
- Scope: `01_Plans/issues/` + `04_Documentation/operations.md`
- Related ADR/Spec: `ADR-0019`, `ADR-0024`, `04_Documentation/operations.md`
- Expected verification level: `docs-check`

## 1) Problem statement

公開ドキュメント更新時に、feedback分類（Gate C）とKPI判定（Gate D）と公開可否判定（Gate E）の実行順序・証跡形式・公開判定導線が統一されず、監査再現性が低下していた。

## 2) Phase 1 Read（状態同期）

- Status / Priority / Scope は `In Progress / P1 / issues+operations` を維持。
- Gate依存は `C→D→E` を固定し、Gate C 完了前に Gate D を開始しない。
- evidence形式は `Date / Gate / Command / Result / Decision / Next action` を6項目必須で固定。
- KPI閾値（しきい値）は「承認済み台帳の値のみ採用」とし、未承認変更を禁止。
- 2026-04-12 の Read同期で、Gate依存（C→D→E）とKPI監査スコアカード入力契約を Stream G 観点で再確認。

## 3) Phase 2 ADR CDC（新規ADR要否判定）

### Context

- Gate C→D→E が運用ごとに入れ替わると、同一差分でも監査結果が再現できない。
- Gate D の入力項目が揺れると、Gate E の Go/Conditional/No-Go 判定根拠が比較不能になる。

### Decision

- 既存ADR（`ADR-0019`, `ADR-0024`）の運用具体化で対応可能なため、**新規ADRは作成しない**。
- 順序は Gate C（分類完了）→ Gate D（KPI評価）→ Gate E（公開判定）に固定する。
- Gate D 必須入力を `測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク` に固定する。
- Gate E Proceed 条件を次で固定する。
  - Go: 記録確定後に次工程へ進行。
  - Conditional: 再判定日と担当を記録後に限定進行。
  - No-Go: 見送り理由・再判定日・担当を記録するまで進行禁止。

### Consequences

- 「分類完了→KPI計測→公開判定」の単方向トレースが可能になる。
- 記録項目は増えるが、判定理由欠落による再作業を抑制できる。

## 4) Phase 3 Plan（AC/DoD不足補完）

### 4.1 Acceptance criteria

- [x] Gate C→D→E の実行順序が明文化される。
- [x] Gate C 完了条件（`未分類=0` または `保留理由 + 再判定日`）を Gate D 開始条件に固定する。
- [x] Gate D 必須入力（測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク）を固定する。
- [x] Gate E Proceed 条件（Go/Conditional/No-Go）を固定する。
- [x] evidence形式を `Date / Gate / Command / Result / Decision / Next action` に統一する。

### 4.2 DoD

- [x] `issue-0019` / `issue-0020` / `04_Documentation/operations.md` の3文書で Gate C→D→E と evidence形式が一致する。
- [x] docs-check結果（validator + 用語照合 + diff整合）が記録される。
- [x] Proceed（次アクション）が Gate E 判定と整合している。

## 5) Phase 4 Execute（KPI/監査指標/運用手順整合）

### 5.1 Gate C（feedback operation）

- 入力: 変更候補・レビューコメント・障害報告。
- 判定: requirements / architecture / test / product gap / 未分類。
- 出力条件: `未分類=0` または `未分類に保留理由と再判定日を付与`。

### 5.2 Gate D（KPI scorecard integrity）

- 開始条件: Gate C の出力条件を満たしたデータのみ対象。
- 必須入力: 測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク。
- 計測: TFS / Decision Readiness / Support Deflection / Feedback Closure。

### 5.3 Gate E（Release decision）

- 入力: Gate C分類結果 + Gate D scorecard。
- 判定: Go / Conditional / No-Go。
- Proceed条件:
  - Go: 記録確定後に次工程へ進行。
  - Conditional: 再判定日と担当を記録後に限定進行。
  - No-Go: 見送り理由・再判定日・担当を記録するまで停止。

## 6) Phase 5 Verify（docs-check + 指標整合確認）

### 6.1 Validation evidence（統一形式）

- Date: 2026-04-12
  - Gate: docs-check
  - Command: `python3 01_Plans/issues/validate_active_issue_memos.py --root .`
  - Result: Pass（issue memo validator 正常終了）
  - Decision: Gate C/D/E 記述を確定
  - Next action: 用語一致の照合へ進む
- Date: 2026-04-12
  - Gate: cross-file terminology check
  - Command: `rg -n "Gate C|Gate D|Gate E|TFS|Decision Readiness|Support Deflection|Feedback Closure|Go / Conditional / No-Go|Date / Gate / Command / Result / Decision / Next action|Proceed条件|未分類|しきい値|閾値" 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 04_Documentation/operations.md`
  - Result: Pass（3文書で順序・語彙・evidence形式の一致を確認）
  - Decision: 形式統一を維持
  - Next action: diff整合確認へ進む
- Date: 2026-04-12
  - Gate: diff integrity
  - Command: `git diff -- 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 04_Documentation/operations.md`
  - Result: Pass（許可ファイルのみ差分）
  - Decision: Proceed可
  - Next action: 次の定点レビュー計画を記録

### 6.2 修復上限

- docs-check / 用語整合 / diff整合の自己修復は最大3回。
- 4回目相当の不一致は Fail-safe 停止。

## 7) Fail-safe

以下を検知した時点で作業を停止し、修正提案のみ記録する。

- 指標定義の曖昧化（算出対象・単位・判定基準が未確定）
- 責務未定義（Gate実行担当または承認担当が未記載）
- 未承認の閾値変更（承認ログ無しのしきい値改定）
- evidence不整合（CommandとResultが対応しない）
- Gate順序の多義化（C→D→E以外が許容される記述）

## 8) Phase 6 Proceed（次工程引き渡し）

### 8.1 次回監査Runbook（Gate C→D→E）

1. Gate C: feedback分類を完了し、`未分類=0` または `保留理由 + 再判定日` を記録する。
2. Gate D: 4KPI（TFS / Decision Readiness / Support Deflection / Feedback Closure）を評価し、必須入力6項目を記録する。
3. Gate E: Go / Conditional / No-Go を判定し、Proceed条件に従って次アクションを固定する。
4. evidence記録は各Gateごとに `Date / Gate / Command / Result / Decision / Next action` を残す。
5. docs-check / 用語整合 / diff整合を実行し、不一致は3回まで自己修復する。
6. 監査記録確定後に次回定点レビューへ引き継ぐ。

- 完了: Gate C→D→E 順序、Gate D必須入力、Gate E Proceed条件、evidence形式を3文書で固定。
- 未完了: KPIしきい値の数値最適化（本ストリーム範囲外）。
- 残リスク: Conditional運用で再判定日の遅延が起きる可能性。
- 次アクション: 次工程へは「運用契約の固定結果」のみを引き渡し、実装依頼は含めない。
- 次回定点レビュー: **2026-04-26 09:00 UTC**。
- 担当: **Stream G（Operations Gate C→D→E Evaluator）**。
