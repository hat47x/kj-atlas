# Issue Draft: 0020 Phase6 Value KPI and Audit Scorecard

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Stream D
- Scope: `01_Plans/issues/` + `02_Architecture/phase6-public-documentation-architecture.md`
- Related ADR/Spec: `ADR-0001`, `ADR-0019`, `ADR-0024`, `phase6-public-documentation-architecture.md`
- Expected verification level: `docs-check`

## 1) Problem statement

KPI scorecard 自体は定義済みだが、Gate C（feedback分類）との接続条件と Gate E（公開判定）への引き渡し形式が統一されず、監査スコアカードとしての運用一貫性が不足していた。

## 2) Read（状態同期: Status / Priority / Scope / Gate依存 / evidence形式）

- Status / Priority / Scope は `In Progress / P1 / issue+architecture` を維持。
- Gate依存は `C→D→E` を固定し、Gate C 完了前の Gate D 実行を禁止する。
- evidence形式は `Date / Gate / Command / Result / Decision / Next action` を6項目必須で固定する。
- 想定差分: Gate E判定時の Proceed 条件が不足していたため、本Issueで固定する。

## 3) Plan（AC/DoD不足の補完提案）

### 3.1 KPI scope（固定）

- TFS
- Decision Readiness
- Support Deflection
- Feedback Closure

### 3.2 Acceptance criteria

- [x] scorecard 4項目が Gate D の必須入力として固定される。
- [x] Gate C 完了（未分類=0 または保留理由あり）を Gate D 開始条件に固定する。
- [x] Gate D 出力を Gate E 判定入力へ渡す最小evidence項目を固定する。
- [x] Gate E 判定時の Proceed 条件（Go/Conditional/No-Go）を固定する。
- [x] evidence 形式を `Date / Gate / Command / Result / Decision / Next action` で統一する。

### 3.3 DoD

- [x] `issue-0019` / `issue-0020` / `phase6-public-documentation-architecture.md` で Gate C→D→E の依存関係が一致する。
- [x] scorecard運用に未定義指標が存在しない。
- [x] docs-check + diff の結果が記録される。

## 4) Context / Decision / Consequences（CDC明文化）

### Context

- KPI scorecard は Gate D の中核だが、Gate C の分類完了を前提化しないと未分類データ混入が起こる。
- Gate E 判定で Proceed 条件が曖昧だと、同じ判定名でも次アクションが変動する。

### Decision

- Gate D 入力契約を `測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク` で固定する。
- Gate E Proceed 条件を次で固定する。
  - Go: 即時進行可（記録確定を条件）。
  - Conditional: 再判定日 + 担当の記録後に限定進行。
  - No-Go: 見送り理由 + 再判定日 + 担当を記録するまで進行禁止。

### Consequences

- KPI判定から公開判定までの監査導線が単方向化される。
- Conditional/No-Go での運用記録が必須化され、判定漏れの再発を抑制できる。

## 5) Execute（Gate C→D→E / evidence形式統一）

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
- 反映先リンク（issue/architecture）

### 5.3 Gate E（Release decision）

- Gate D の結果を使い、Go / Conditional / No-Go を判定する。
- Proceed条件:
  - Go: 記録確定後に次工程へ進行。
  - Conditional: 再判定日と担当を記録後に限定進行。
  - No-Go: 見送り理由・再判定日・担当を記録するまで停止。

## 6) Verify（docs-check + diff）

### 6.1 Validation evidence（統一形式）

- Date: 2026-04-11
  - Gate: KPI docs-check
  - Command: `python3 01_Plans/issues/validate_active_issue_memos.py --root .`
  - Result: Pass（issue memo validator 正常終了）
  - Decision: KPI定義の文書整合を確定
  - Next action: 横断grep検証へ進む
- Date: 2026-04-11
  - Gate: KPI cross-reference check
  - Command: `rg -n "Gate C|Gate D|Gate E|TFS|Decision Readiness|Support Deflection|Feedback Closure|Go / Conditional / No-Go|Date / Gate / Command / Result / Decision / Next action|Proceed条件|未分類" 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 02_Architecture/phase6-public-documentation-architecture.md`
  - Result: Pass（3文書でKPI語彙・Gate順序・evidence形式の一致を確認）
  - Decision: 形式統一を維持
  - Next action: diff整合確認へ進む
- Date: 2026-04-11
  - Gate: Diff integrity
  - Command: `git diff -- 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 02_Architecture/phase6-public-documentation-architecture.md`
  - Result: Pass（許可ファイルのみ差分）
  - Decision: Proceed可
  - Next action: 運用契約の固定結果を引き渡す

## 6.2 Phase execution contract（Stream D 固定）

- Phase 1 Read: 3ファイル（`issue-0019` / `issue-0020` / `phase6-public-documentation-architecture.md`）を各Phase開始時に再読する。
- Phase 2 CDC: Context / Decision / Consequences を Gate C→D→E の順序固定で同期する。
- Phase 3 Plan: AC/DoD に KPI運用不足があれば補完する。
- Phase 4 Execute: Gate C→Gate D→Gate E を固定し、順序崩壊時は停止する。
- Phase 5 Verify: `docs-check` と `diff` を必須実施し、証跡を6項目形式で記録する。
- Phase 6 Proceed: 引き渡し時に完了・未完了・残リスク・次アクションを明記する。
- self-correction: 失敗時は最大3回まで是正し、3回超過時は Fail-safe 停止とする。

## 7) Fail-safe

以下を検知した場合は停止する。

- Gate D の入力条件が Gate C の分類完了条件と矛盾
- KPI項目名の不一致または未定義指標の混入
- evidence項目欠落（Date/Gate/Command/Result/Decision/Next action）
- Gate順序の多義化（C→D→E以外が許容される記述）

## 8) Proceed（次工程引き渡し）

- 完了: Gate D入力契約とGate E Proceed条件を固定。
- 未完了: KPIしきい値の運用最適化（本ストリーム範囲外）。
- 残リスク: 反映先リンクの記入漏れによる監査追跡欠落。
- 次アクション: 次工程へは「運用契約の固定結果」のみを引き渡し、実装依頼は含めない。
