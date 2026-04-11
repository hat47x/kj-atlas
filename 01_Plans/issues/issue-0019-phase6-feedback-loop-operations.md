# Issue Draft: 0019 Phase6 Feedback Loop Operations

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Stream G
- Scope: `01_Plans/issues/` + `02_Architecture/phase6-public-documentation-architecture.md`
- Related ADR/Spec: `ADR-0019`, `ADR-0024`, `phase6-public-documentation-architecture.md`
- Expected verification level: `docs-check`

## 1) Problem statement

公開ドキュメント更新時に、feedback分類（Gate C）とKPI判定（Gate D）と公開可否判定（Gate E）の実行順序・証跡形式が統一されず、監査再現性が低下していた。

## 2) Read（現状確認: Gate A〜E と scorecard 接続）

- Gate A/B は導線・用語整合を判定するが、実行証跡のテンプレートが明文化されていなかった。
- Gate C は分類軸（requirements / architecture / test / product gap / 未分類）を持つが、Gate Dへの入力条件が曖昧だった。
- Gate D は scorecard 4項目を定義済みだが、Gate C完了済みデータのみを対象にする条件が不足していた。
- Gate E は Go/No-Go を持つが、Conditional判定時のProceed条件が明文化不足だった。

## 3) Plan（AC/DoD不足の補完提案）

### 3.1 Acceptance criteria

- [x] Gate C→D→E の実行順序が明文化される。
- [x] Gate C の分類完了（未分類=0 または保留理由あり）を Gate D 開始条件に固定する。
- [x] evidence 形式を `Date / Gate / Command / Result / Decision / Next action` に統一する。
- [x] Gate定義矛盾・evidence不整合・未定義参照を検知した場合は停止（Fail-safe）を明示する。

### 3.2 DoD（本Issue完了条件）

- [x] `issue-0019` / `issue-0020` / `phase6-public-documentation-architecture.md` の3文書で Gate C→D→E と evidence形式が一致する。
- [x] docs-check結果（validator + grep系照合 + diff整合）が記録される。
- [x] Proceed（次アクション）が Gate E 判定と整合している。

## 4) Execute（Gate C→D→E / evidence形式統一）

### 4.1 Gate C（feedback operation）

- 入力: 変更候補・レビューコメント・障害報告。
- 判定: requirements / architecture / test / product gap / 未分類。
- 出力条件: `未分類=0` または `未分類に保留理由と再判定日を付与`。

### 4.2 Gate D（KPI scorecard integrity）

- 開始条件: Gate C の出力条件を満たしたデータのみ対象。
- 計測: TFS / Decision Readiness / Support Deflection / Feedback Closure。
- 出力条件: 4項目の測定値 + 逸脱有無 + 改善アクション候補。

### 4.3 Gate E（Release decision）

- 入力: Gate C分類結果 + Gate D scorecard + Gate A/B整合結果。
- 判定: Go / Conditional / No-Go。
- 記録: 判定理由、再判定日（Conditional/No-Go時）、次アクション。

## 5) Verify（docs-check + diff）

### 5.1 Validation evidence（統一形式）

- Date: 2026-04-11
  - Gate: Cross-Gate docs-check
  - Command: `python3 01_Plans/issues/validate_active_issue_memos.py --root .`
  - Result: Pass（issue memo validator 正常終了）
  - Decision: Gate C/D/E 記述を継続
  - Next action: 用語一致のgrep検証へ進む
- Date: 2026-04-11
  - Gate: Cross-Gate reference check
  - Command: `rg -n "Gate A|Gate B|Gate C|Gate D|Gate E|Quality gate|scorecard|未分類|Go / Conditional / No-Go" 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 02_Architecture/phase6-public-documentation-architecture.md`
  - Result: Pass（3文書で用語/判定軸の一致を確認）
  - Decision: evidence形式を採用
  - Next action: diff整合確認へ進む
- Date: 2026-04-11
  - Gate: Diff integrity
  - Command: `git diff -- 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 02_Architecture/phase6-public-documentation-architecture.md`
  - Result: Pass（許可ファイルのみ差分）
  - Decision: Proceed可
  - Next action: Stream G handoffを記載

## 6) Fail-safe

以下を検知した時点で作業を停止し、修正提案のみ記録する。

- Gate定義矛盾（例: Gate CとGate Dで入力条件が不一致）
- evidence不整合（CommandとResultが対応しない）
- 未定義参照（存在しない文書/スクリプト/指標名）

## 7) Proceed（次アクション）

- Stream G は次サイクルで、Gate C分類ログのテンプレート（実データ欄）を issue-0020 のscorecard記録フォーマットへ接続し、Gate Eの再判定日運用を定着させる。
