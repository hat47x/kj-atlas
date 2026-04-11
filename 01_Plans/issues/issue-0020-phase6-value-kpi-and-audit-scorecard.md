# Issue Draft: 0020 Phase6 Value KPI and Audit Scorecard

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Stream G
- Scope: `01_Plans/issues/` + `02_Architecture/phase6-public-documentation-architecture.md`
- Related ADR/Spec: `ADR-0001`, `ADR-0019`, `ADR-0024`, `phase6-public-documentation-architecture.md`
- Expected verification level: `docs-check`

## 1) Problem statement

KPI scorecard 自体は定義済みだが、Gate C（feedback分類）との接続条件と Gate E（公開判定）への引き渡し形式が統一されず、監査スコアカードとしての運用一貫性が不足していた。

## 2) Read（現状確認: Gate A〜E と scorecard 接続）

- Gate D の計測軸（TFS / Decision Readiness / Support Deflection / Feedback Closure）は存在する。
- ただし、Gate C完了条件が明確でないため、未分類データを含む計測混入リスクがあった。
- Gate E の判定へ渡す最小項目（測定日、対象文書、判定、次アクション、反映先）が未固定だった。

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
- [x] evidence 形式を `Date / Gate / Command / Result / Decision / Next action` で統一する。

### 3.3 DoD

- [x] `issue-0019` / `issue-0020` / `phase6-public-documentation-architecture.md` で Gate C→D→E の依存関係が一致する。
- [x] scorecard運用に未定義指標が存在しない。
- [x] docs-check + diff の結果が記録される。

## 4) Execute（Gate C→D→E / evidence形式統一）

### 4.1 Gate C to Gate D 接続

- Gate C で分類済みのエントリのみを scorecard対象に含める。
- `未分類` が残る場合は Gate D を停止し、保留理由・再分類期限を先に記録する。

### 4.2 Gate D（KPI scorecard integrity）

scorecard記録の最小項目を次に固定する。

- 測定日
- 対象文書
- 4KPIの判定（数値または段階）
- 逸脱有無
- 次アクション
- 反映先リンク（issue/architecture）

### 4.3 Gate E（Release decision）

- Gate D の結果を使い、Go / Conditional / No-Go を判定する。
- Conditional / No-Go の場合、再判定日と担当を必須記録にする。

## 5) Verify（docs-check + diff）

### 5.1 Validation evidence（統一形式）

- Date: 2026-04-11
  - Gate: KPI docs-check
  - Command: `python3 01_Plans/issues/validate_active_issue_memos.py --root .`
  - Result: Pass（issue memo validator 正常終了）
  - Decision: KPI定義の文書整合を継続
  - Next action: 横断grep検証へ進む
- Date: 2026-04-11
  - Gate: KPI cross-reference check
  - Command: `rg -n "Gate C|Gate D|Gate E|TFS|Decision Readiness|Support Deflection|Feedback Closure|Go / Conditional / No-Go|未分類" 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 02_Architecture/phase6-public-documentation-architecture.md`
  - Result: Pass（3文書でKPI語彙とGate依存関係の一致を確認）
  - Decision: 形式統一を維持
  - Next action: diff整合確認へ進む
- Date: 2026-04-11
  - Gate: Diff integrity
  - Command: `git diff -- 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 02_Architecture/phase6-public-documentation-architecture.md`
  - Result: Pass（許可ファイルのみ差分）
  - Decision: Proceed可
  - Next action: 運用定着アクションを明記

## 6) Fail-safe

以下を検知した場合は停止する。

- Gate D の入力条件が Gate C の分類完了条件と矛盾
- KPI項目名の不一致または未定義指標の混入
- evidence項目欠落（Date/Gate/Command/Result/Decision/Next action）

## 7) Proceed（次アクション）

- Stream G は次サイクルで、実運用ログ1件（仮値可）を scorecard形式で記録し、Gate E 判定（Go/Conditional/No-Go）までの往復をテンプレート化する。
