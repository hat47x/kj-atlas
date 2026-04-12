# Issue Draft: 0020 Phase6 Value KPI and Audit Scorecard

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Stream I
- Scope: `01_Plans/issues/` + `04_Documentation/operations.md`
- Related ADR/Spec: `ADR-0001`, `ADR-0019`, `ADR-0024`, `04_Documentation/operations.md`
- Expected verification level: `docs-check`

## 1) Problem statement

KPI scorecard 自体は定義済みだが、Gate C（feedback分類）との接続条件と Gate E（公開判定）への引き渡し形式が統一されず、監査スコアカードとしての運用一貫性が不足していた。

## 2) Phase 1 Read（状態同期）

- Status / Priority / Scope は `In Progress / P1 / issues+operations` を維持。
- Gate依存は `C→D→E` を固定し、Gate C 完了前の Gate D 実行を禁止。
- evidence形式は `Date / Gate / Command / Result / Decision / Next action` を6項目必須で固定。
- KPIしきい値は承認済み定義のみ有効とし、未承認変更は禁止。
- 2026-04-12 の Read同期で、Gate C完了条件→Gate D scorecard→Gate E Proceed条件の依存を Stream I 観点で再確認。

## 3) Phase 2 ADR CDC（新規ADR要否判定）

### Context

- KPI scorecard は Gate D の中核だが、Gate C の分類完了を前提化しないと未分類データ混入が起こる。
- Gate E 判定で Proceed 条件が曖昧だと、同じ判定名でも次アクションが変動する。

### Decision

- 既存ADR（`ADR-0001`, `ADR-0019`, `ADR-0024`）で要件と運用原則を包含できるため、**新規ADRは不要**。
- Gate D 入力契約を `測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク` で固定する。
- Gate E Proceed 条件を次で固定する。
  - Go: 即時進行可（記録確定を条件）。
  - Conditional: 再判定日 + 担当の記録後に限定進行。
  - No-Go: 見送り理由 + 再判定日 + 担当を記録するまで進行禁止。

### Consequences

- KPI判定から公開判定までの監査導線が単方向化される。
- Conditional/No-Go での運用記録が必須化され、判定漏れ再発を抑制できる。

## 4) Phase 3 Plan（AC/DoD不足補完）

### 4.1 KPI scope（固定）

- TFS
- Decision Readiness
- Support Deflection
- Feedback Closure

### 4.2 Acceptance criteria

- [x] scorecard 4項目が Gate D の必須入力として固定される。
- [x] Gate C 完了（未分類=0 または保留理由あり）を Gate D 開始条件に固定する。
- [x] Gate D 出力を Gate E 判定入力へ渡す最小evidence項目を固定する。
- [x] Gate E 判定時の Proceed 条件（Go/Conditional/No-Go）を固定する。
- [x] evidence形式を `Date / Gate / Command / Result / Decision / Next action` で統一する。

### 4.3 DoD

- [x] `issue-0019` / `issue-0020` / `04_Documentation/operations.md` で Gate C→D→E の依存関係が一致する。
- [x] scorecard運用に未定義指標が存在しない。
- [x] docs-check + diff の結果が記録される。

## 5) Phase 4 Execute（KPI/監査指標/運用手順整合）

### 5.1 Gate C to Gate D 接続

- Gate C で分類済みのエントリのみを scorecard対象に含める。
- `未分類` が残る場合は Gate D を停止し、保留理由・再判定日を先に記録する。

### 5.2 Gate D（KPI scorecard integrity）

scorecard記録の必須項目を次に固定する。

- 測定日
- 対象文書
- 4KPIの判定（数値または段階）
- 逸脱有無
- 次アクション
- 反映先リンク（issue/operations）

### 5.3 Gate E（Release decision）

- Gate D の結果を使い、Go / Conditional / No-Go を判定する。
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
  - Decision: KPI定義の文書整合を確定
  - Next action: 横断語彙検証へ進む
- Date: 2026-04-12
  - Gate: KPI cross-reference check
  - Command: `rg -n "Gate C|Gate D|Gate E|TFS|Decision Readiness|Support Deflection|Feedback Closure|Go / Conditional / No-Go|Date / Gate / Command / Result / Decision / Next action|Proceed条件|未分類|しきい値|閾値" 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 04_Documentation/operations.md`
  - Result: Pass（3文書でKPI語彙・Gate順序・evidence形式の一致を確認）
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

以下を検知した場合は停止する。

- 指標定義の曖昧化（式・単位・対象範囲の未固定）
- 責務未定義（測定責任者・承認責任者の欠落）
- 未承認の閾値変更（承認記録なしのKPIしきい値改定）
- KPI項目名の不一致または未定義指標の混入
- evidence項目欠落（Date/Gate/Command/Result/Decision/Next action）
- Gate順序の多義化（C→D→E以外が許容される記述）

## 8) Phase 6 Proceed（次工程引き渡し）

### 8.1 次回監査Runbook（Gate C→D→E）

1. Gate C: feedback分類を完了し、未分類エントリの残存有無を監査ログに固定する。
2. Gate D: KPI scorecard（4KPI）を更新し、逸脱有無と次アクションを明記する。
3. Gate E: Go / Conditional / No-Go 判定と Proceed条件の整合を確認する。
4. evidence記録は `Date / Gate / Command / Result / Decision / Next action` で統一する。
5. docs-check / KPI語彙照合 / diff整合を実行し、必要なら3回まで修復する。
6. 次回監査予定（日時/担当/対象文書）を確定して引き渡す。

- 完了: Gate D入力契約と Gate E Proceed条件を固定。
- 未完了: KPIしきい値の運用最適化（本ストリーム範囲外）。
- 残リスク: 反映先リンクの記入漏れによる監査追跡欠落。
- 次アクション: 次工程へは「運用契約の固定結果」のみを引き渡し、実装依頼は含めない。
- 次回定点レビュー: **2026-04-19 09:00 UTC**。
- 担当: **Stream I（Operations KPI & Audit Scorecard Evaluator）**。
