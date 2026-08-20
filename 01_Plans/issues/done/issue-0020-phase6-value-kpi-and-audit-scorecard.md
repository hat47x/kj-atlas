# Issue Draft: 0020 Phase6 Value KPI and Audit Scorecard

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream F
- Scope: `01_Plans/issues/` + `04_Documentation/operations.md`
- Related ADR/Spec: `ADR-0001`, `ADR-0019`, `ADR-0024`, `ADR-0028`, `04_Documentation/operations.md`
- Dependencies: N/A
- Expected verification level: `docs-check`

## 1) Problem statement

KPIスコアカードは定義済みでも、feedback分類（Gate C）と公開判定（Gate E）への受け渡しが揺れると監査結果の比較が不能になる。Stream F は **KPI監査を運用フィードバックと一体運用** し、単一路線の監査導線を固定する。

## 2) Phase 1 Read（状態同期）

- Gate依存を `C→D→E` に固定し、逆順・並列判定を禁止する。
- 実行順序を `Read → CDC → Plan → Execute → Verify(docs-check) → Proceed` で固定する。
- evidence形式を `Date / Gate / Command / Result / Decision / Next action` で統一する。
- KPIしきい値は承認済み台帳のみ有効とする。
- 2026-04-13 の Read同期で、4文書（`issue-0019` / `issue-0020` / `issue-doc-ops-05-11` / `operations.md`）の入力契約一致を再確認した。

## 3) Phase 2 CDC（Context / Decision / Consequences の固定）

- 上流整合は `ADR-0001` / `ADR-0019` / `ADR-0024` / `ADR-0028` を参照し、KPI契約の独自解釈を禁止する。
- Gate C→D→E、4KPI、evidence6項目、Proceed条件（Go/Conditional/No-Go）を ADR整合契約として固定する。
- 停止条件を次で固定する（Fail-safe）:
  1. 修復試行が3回を超過。
  2. 前提崩れ（Gate順序・KPI定義・承認済みしきい値前提の崩壊）。
  3. 未定義競合（上流ADR間で解釈不能な競合が残存）。

## 4) Phase 3 Plan（AC/DoD補完）

### 4.1 KPI scope（固定）

- TFS
- Decision Readiness
- Support Deflection
- Feedback Closure

### 4.1.1 KPI 測定定義（再現可能性優先）

- **TFS**: `期限内完了feedback件数 / 対象feedback総件数`（測定期間ごと、0除算時は N/A と記録）
- **Decision Readiness**: `Gate E 判定に必要な必須項目充足件数 / Gate E 対象件数`
- **Support Deflection**: `文書参照で自己解決した問い合わせ件数 / 問い合わせ総件数`
- **Feedback Closure**: `再判定日までにクローズしたfeedback件数 / 当期対応対象feedback件数`

注記:
- 分母・分子の集計対象は同一測定期間に固定する。
- しきい値は承認済み台帳のみを参照し、本メモでは閾値値そのものを再定義しない。

### 4.2 Acceptance Criteria

- [x] scorecard 4項目が Gate D の必須評価対象として固定されている。
- [x] Gate C 完了条件（未分類=0 または保留理由あり）が Gate D の開始条件として固定されている。
- [x] Gate D 入力契約6項目が固定されている。
- [x] Gate E Proceed条件（Go / Conditional / No-Go）が固定されている。
- [x] 停止条件（3回超過 / 前提崩れ / 未定義競合）が4文書で一致している。
- [x] evidence形式が4文書で一致している。

### 4.3 DoD

- [x] 4文書で Gate C→D→E と KPI語彙が一致。
- [x] 未定義KPIが混入していない。
- [x] docs-check / 横断語彙照合 / diff整合の結果を記録。
- [x] 停止条件に該当する場合の CDC 化導線を明文化。

## 5) Phase 4 Execute（KPI定義→監査指標→運用Runbook の直列実行）

### 5.0 直列固定（必須）

1. KPI定義（TFS / Decision Readiness / Support Deflection / Feedback Closure）を固定。
2. 監査指標（Gate D 入力6項目 + 逸脱有無）を固定。
3. 運用Runbook（Gate C→D→E と Proceed条件）を同期更新。

### 5.1 Gate C → Gate D 接続

- Gate C で分類済みのエントリのみ scorecard 対象に含める。
- 未分類が残る場合、Gate D を停止し保留理由・再判定日を先に記録する。

### 5.2 Gate D（KPI scorecard integrity）

scorecard必須入力は次で固定する。

- 測定日
- 対象文書
- 4KPI判定（数値または段階）
- 逸脱有無
- 次アクション
- 反映先リンク（issue/operations）

加えて、各KPIの分子/分母または判定根拠（算出ログ参照先）を記録し、再計算可能性を担保する。

### 5.3 Gate E（Proceed decision）

- Gate D 結果を入力として Go / Conditional / No-Go を判定する。
- Proceed条件:
  - Go: 記録確定後に次工程へ進行。
  - Conditional: 再判定日 + 担当記録後に限定進行。
  - No-Go: 見送り理由 + 再判定日 + 担当記録まで停止。

## 6) Phase 5 Verify（docs-check）

### 6.1 Validation evidence（統一形式）

- Date: 2026-04-13
  - Gate: docs-check
  - Command: `python3 01_Plans/issues/validate_active_issue_memos.py --root .`
  - Result: Pass（issue memo validator 正常終了）
  - Decision: KPI定義整合を維持
  - Next action: KPI語彙照合へ進む
- Date: 2026-04-13
  - Gate: KPI cross-reference
  - Command: `rg -n "Gate C|Gate D|Gate E|TFS|Decision Readiness|Support Deflection|Feedback Closure|Go / Conditional / No-Go|Date / Gate / Command / Result / Decision / Next action|Proceed条件|未分類|しきい値|閾値|Stream F|3回超過|前提崩れ|未定義競合" 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md 04_Documentation/operations.md`
  - Result: Pass（4文書でKPI語彙・Gate依存・停止条件が一致）
  - Decision: 監査導線を固定
  - Next action: 差分整合確認へ進む
- Date: 2026-04-13
  - Gate: diff integrity
  - Command: `git diff -- 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md 04_Documentation/operations.md`
  - Result: Pass（許可ファイルのみ差分）
  - Decision: Proceed判定へ進む
  - Next action: 次回測定条件を確定

### 6.2 修復上限

- docs-check / 用語照合 / diff整合の自己修復は最大3回。
- 4回目相当は Fail-safe 停止（Proceed禁止）。

## 7) Phase 6 Proceed（次の測定サイクル条件）

1. Gate C 完了条件（未分類の扱い）を満たしている。
2. Gate D 入力契約6項目が揃っている。
3. Gate E 判定と次アクションが Proceed条件に一致している。
4. evidence 6項目形式を各Gateで満たしている。
5. docs-check / KPI語彙照合 / diff整合が Pass。
6. 停止条件（3回超過 / 前提崩れ / 未定義競合）のいずれにも該当しない。

- 次回定点レビュー: **2026-04-26 09:00 UTC**。
- 担当: **Stream F（Unified KPI & Audit Scorecard Owner）**。

## 8) Fail-safe（ADR衝突時のCDC化）

次を検知した場合は停止し、CDC（Context / Decision / Consequences）を作成して論点化する。

- KPI定義が `ADR-0001` / `ADR-0019` / `ADR-0024` / `ADR-0028` と矛盾。
- 未承認のしきい値変更。
- 未定義KPIの混入またはKPI名称不一致。
- Gate順序が `C→D→E` 以外。
- evidence項目欠落または Result の根拠不在。
- 停止条件（3回超過 / 前提崩れ / 未定義競合）に該当。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## Stream H linkage (2026-05-10)
- KPI接続: QA結果を 4KPI に反映する際、P0失敗は `Decision Readiness` を No-Go 相当に固定。
- 監査記録: `Date/Gate/Command/Result/Decision/Next action` に加え `QA Boundary (P0/P1/P2)` を必須化。
- エスカレーション: P0未達は再試行前に監査ログへ先行記録し、再開条件を明示する。
