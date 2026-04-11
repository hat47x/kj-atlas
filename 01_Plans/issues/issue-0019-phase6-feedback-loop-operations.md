# Issue Draft: 0019 Phase6 Feedback Loop Operations

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Stream D
- Scope: `01_Plans/issues/` + `02_Architecture/phase6-public-documentation-architecture.md`
- Related ADR/Spec: `ADR-0019`, `ADR-0024`, `phase6-public-documentation-architecture.md`
- Expected verification level: `docs-check`

## 1) Problem statement

公開ドキュメント更新時に、feedback分類（Gate C）とKPI判定（Gate D）と公開可否判定（Gate E）の実行順序・証跡形式・公開判定導線が統一されず、監査再現性が低下していた。

## 2) Read（状態同期: Status / Priority / Scope / Gate依存 / evidence形式）

- Status / Priority / Scope は `In Progress / P1 / issue+architecture` を維持。
- Gate依存は `C→D→E` を固定し、Gate C 完了前に Gate D を開始しない。
- evidence形式は `Date / Gate / Command / Result / Decision / Next action` を6項目必須で固定する。
- 想定差分: Gate E の Conditional 判定時の Proceed 条件が曖昧だったため、次節で固定する。

## 3) Plan（AC/DoD不足の補完提案）

### 3.1 Acceptance criteria

- [x] Gate C→D→E の実行順序が明文化される。
- [x] Gate C 完了条件（`未分類=0` または `保留理由 + 再判定日`）を Gate D 開始条件に固定する。
- [x] Gate D 必須入力を固定する（測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク）。
- [x] Gate E の Proceed 条件を固定する（Goは即時進行、Conditional/No-Goは再判定日と担当必須）。
- [x] evidence形式を `Date / Gate / Command / Result / Decision / Next action` に統一する。

### 3.2 DoD（本Issue完了条件）

- [x] `issue-0019` / `issue-0020` / `phase6-public-documentation-architecture.md` の3文書で Gate C→D→E と evidence形式が一致する。
- [x] docs-check結果（validator + grep系照合 + diff整合）が記録される。
- [x] Proceed（次アクション）が Gate E 判定と整合している。

## 4) Context / Decision / Consequences（CDC明文化）

### Context

- Gate C→D→E が運用ごとに入れ替わると、同一差分でも監査結果が再現できない。
- Gate D の入力項目が揺れると、Gate E の Go/Conditional/No-Go 判定根拠が比較不能になる。

### Decision

- 順序は Gate C（分類完了）→ Gate D（KPI評価）→ Gate E（公開判定）に固定する。
- Gate D 必須入力は `測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク` に固定する。
- Gate E Proceed 条件を次で固定する。
  - Go: 次工程へ進行可（同一サイクルで記録を確定）。
  - Conditional: 再判定日と担当を記録後に限定進行。
  - No-Go: 見送り理由・再判定日・担当を記録するまで進行禁止。

### Consequences

- 監査時に「分類完了→KPI計測→公開判定」の単方向トレースが可能になる。
- 記録負荷は増えるが、判定理由の欠落による再作業を減らせる。

## 5) Execute（Gate C→D→E / evidence形式統一）

### 5.1 Gate C（feedback operation）

- 入力: 変更候補・レビューコメント・障害報告。
- 判定: requirements / architecture / test / product gap / 未分類。
- 出力条件: `未分類=0` または `未分類に保留理由と再判定日を付与`。

### 5.2 Gate D（KPI scorecard integrity）

- 開始条件: Gate C の出力条件を満たしたデータのみ対象。
- 必須入力: 測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク。
- 計測: TFS / Decision Readiness / Support Deflection / Feedback Closure。

### 5.3 Gate E（Release decision）

- 入力: Gate C分類結果 + Gate D scorecard + Gate A/B整合結果。
- 判定: Go / Conditional / No-Go。
- Proceed条件:
  - Go: 記録確定後に次工程へ進行。
  - Conditional: 再判定日と担当を記録後に限定進行。
  - No-Go: 見送り理由・再判定日・担当を記録するまで停止。

## 6) Verify（docs-check + diff）

### 6.1 Validation evidence（統一形式）

- Date: 2026-04-11
  - Gate: Cross-Gate docs-check
  - Command: `python3 01_Plans/issues/validate_active_issue_memos.py --root .`
  - Result: Pass（issue memo validator 正常終了）
  - Decision: Gate C/D/E 記述を確定
  - Next action: 用語一致のgrep検証へ進む
- Date: 2026-04-11
  - Gate: Cross-Gate reference check
  - Command: `rg -n "Gate C|Gate D|Gate E|TFS|Decision Readiness|Support Deflection|Feedback Closure|Go / Conditional / No-Go|Date / Gate / Command / Result / Decision / Next action|Proceed条件|未分類" 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 02_Architecture/phase6-public-documentation-architecture.md`
  - Result: Pass（3文書で順序・語彙・evidence形式の一致を確認）
  - Decision: 形式統一を維持
  - Next action: diff整合確認へ進む
- Date: 2026-04-11
  - Gate: Diff integrity
  - Command: `git diff -- 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 02_Architecture/phase6-public-documentation-architecture.md`
  - Result: Pass（許可ファイルのみ差分）
  - Decision: Proceed可
  - Next action: 運用契約の固定結果を引き渡す

## 7) Fail-safe

以下を検知した時点で作業を停止し、修正提案のみ記録する。

- Gate定義矛盾（例: Gate CとGate Dで入力条件が不一致）
- evidence不整合（CommandとResultが対応しない）
- 未定義参照（存在しない文書/スクリプト/指標名）
- Gate順序の多義化（C→D→E以外が許容される記述）

## 8) Proceed（次工程引き渡し）

- 完了: Gate C→D→E 順序、Gate D必須入力、Gate E Proceed条件、evidence形式を3文書で固定。
- 未完了: KPI閾値の数値最適化（本ストリーム範囲外）。
- 残リスク: Conditional運用で再判定日の遅延が起きる可能性。
- 次アクション: 次工程へは「運用契約の固定結果」のみを引き渡し、実装依頼は含めない。
