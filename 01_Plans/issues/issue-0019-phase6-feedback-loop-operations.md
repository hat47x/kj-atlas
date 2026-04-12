# Issue Draft: 0019 Phase6 Feedback Loop Operations

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Stream F
- Scope: `01_Plans/issues/` + `04_Documentation/operations.md`
- Related ADR/Spec: `ADR-0001`, `ADR-0019`, `ADR-0024`, `04_Documentation/operations.md`
- Expected verification level: `docs-check`

## 1) Problem statement

運用フィードバック（Gate C）とKPI監査（Gate D）を別系統で管理すると、Gate E（Proceed判定）で根拠が分断される。Stream F では **feedback運用とKPI監査を一本化** し、同一runbookで再現可能にする。

## 2) Phase 1 Read（状態同期）

- Status / Priority / Scope は `In Progress / P1 / issues+operations` を維持する。
- Gate依存は `C→D→E` の固定順序とし、Gate C 完了前に Gate D を開始しない。
- evidence形式は `Date / Gate / Command / Result / Decision / Next action` の6項目を必須とする。
- KPIしきい値は「承認済み台帳の値のみ有効」とし、未承認変更を禁止する。
- 2026-04-12 の Read同期で、`issue-0019` / `issue-0020` / `operations.md` の3文書に同一契約を適用した。

## 3) Phase 2 Plan（KPI定義・監査スコアカードAC/DoD）

### 3.1 KPI定義（Gate D必須）

- TFS
- Decision Readiness
- Support Deflection
- Feedback Closure

### 3.2 Acceptance criteria

- [x] Gate C→D→E の固定順序が明文化されている。
- [x] Gate C 完了条件（`未分類=0` または `保留理由 + 再判定日`）が Gate D 開始条件に固定されている。
- [x] Gate D 入力契約（測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク）が固定されている。
- [x] Gate E Proceed条件（Go / Conditional / No-Go）が固定されている。
- [x] evidence形式（Date / Gate / Command / Result / Decision / Next action）が3文書で一致している。

### 3.3 DoD

- [x] `issue-0019` / `issue-0020` / `operations.md` の記述が同一語彙・同一順序で同期されている。
- [x] docs-check / 用語照合 / diff整合の実行結果を記録している。
- [x] 次回測定サイクルの開始条件（Proceed条件）が明文化されている。

## 4) Phase 3 Execute（運用手順と計測手順の同期）

### 4.1 Gate C（feedback operation）

- 入力: 変更候補・レビューコメント・障害報告。
- 分類: requirements / architecture / test / product gap / 未分類。
- 出力条件: `未分類=0` または `未分類に保留理由 + 再判定日` を付与。

### 4.2 Gate D（KPI scorecard audit）

- 開始条件: Gate C の出力条件を満たしたデータのみ対象。
- 記録契約: 測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク。
- 判定契約: KPIしきい値は承認済み台帳のみ参照。

### 4.3 Gate E（Proceed decision）

- 入力: Gate C分類結果 + Gate D scorecard。
- 判定:
  - Go: 記録確定後に次工程へ進行。
  - Conditional: 再判定日 + 担当記録後に限定進行。
  - No-Go: 見送り理由 + 再判定日 + 担当記録まで停止。

## 5) Phase 4 Verify（矛盾チェック）

### 5.1 Validation evidence（統一形式）

- Date: 2026-04-12
  - Gate: docs-check
  - Command: `python3 01_Plans/issues/validate_active_issue_memos.py --root .`
  - Result: Pass（issue memo validator 正常終了）
  - Decision: 契約形式を維持
  - Next action: 横断語彙照合へ進む
- Date: 2026-04-12
  - Gate: terminology consistency
  - Command: `rg -n "Gate C|Gate D|Gate E|TFS|Decision Readiness|Support Deflection|Feedback Closure|Go / Conditional / No-Go|Date / Gate / Command / Result / Decision / Next action|Proceed条件|未分類|しきい値|閾値|Stream F" 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 04_Documentation/operations.md`
  - Result: Pass（3文書の語彙・順序・役割整合を確認）
  - Decision: 用語ドリフトなし
  - Next action: 差分整合確認へ進む
- Date: 2026-04-12
  - Gate: diff integrity
  - Command: `git diff -- 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 04_Documentation/operations.md`
  - Result: Pass（許可ファイルのみ差分）
  - Decision: Proceed可能
  - Next action: 次回測定サイクル条件を確定

### 5.2 修復上限

- docs-check / 用語整合 / diff整合の自己修復は最大3回。
- 4回目相当の不一致は Fail-safe 停止。

## 6) Phase 5 Proceed（次の測定サイクル条件）

次サイクルに進む条件を以下で固定する。

1. Gate C が完了し、未分類の扱い（0件または保留理由+再判定日）が記録済み。
2. Gate D の入力契約6項目が欠落なく記録済み。
3. Gate E 判定と Proceed条件（Go / Conditional / No-Go）が一致。
4. evidence 6項目形式が各Gateで充足。
5. docs-check / 用語照合 / diff整合の3確認がPass。

- 次回定点レビュー: **2026-04-26 09:00 UTC**。
- 担当: **Stream F（Unified Feedback & KPI Audit Owner）**。

## 7) Fail-safe（ADR衝突時のCDC化）

以下を検知した場合は作業を停止し、**CDC（Context / Decision / Consequences）として論点化** する。

- KPI定義・Proceed条件が `ADR-0001` / `ADR-0019` / `ADR-0024` と衝突。
- 未承認の閾値変更（承認ログなし）。
- Gate順序が `C→D→E` 以外で記述される。
- evidence項目の欠落または Command と Result の不整合。
