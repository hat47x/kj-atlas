# Issue Draft: 0019 Phase6 Feedback Loop Operations

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

運用フィードバック（Gate C）とKPI監査（Gate D）が分断されると、Gate E（Proceed判定）の根拠が監査不能になる。Stream F は **feedback運用とKPI監査を単一路線で固定** し、再現可能な runbook と証跡を同期維持する。

## 2) Phase 1 Read（状態同期）

- 実行順序は `Read → CDC → Plan → Execute → Verify(docs-check) → Proceed` で固定する。

- Status / Priority / Scope は `In Progress / P1 / issues+operations` を維持する。
- Gate依存は `C→D→E` の固定順序とし、Gate C 完了前に Gate D を開始しない。
- evidence形式は `Date / Gate / Command / Result / Decision / Next action` の6項目を必須とする。
- KPIしきい値は承認済み台帳の値のみ有効とし、未承認変更を禁止する。
- 2026-04-13 の Read同期で、`issue-0019` / `issue-0020` / `issue-doc-ops-05-11` / `operations.md` の4文書に同一契約を適用した。

## 3) Phase 2 CDC（Context / Decision / Consequences の固定）

- 上流整合は `ADR-0001`（価値要件）、`ADR-0019`（検証方針）、`ADR-0024`（DOC-OPS運用）、`ADR-0028`（CE系の安全/監査境界）を参照し、相互矛盾を持ち込まない。
- Gate C→D→E、4KPI、evidence6項目、Proceed条件（Go/Conditional/No-Go）を **CDC契約（ADR整合）** として固定する。
- 停止条件を次で固定する（Fail-safe）:
  1. 修復試行が3回を超過。
  2. 前提崩れ（Gate順序・KPI定義・承認済みしきい値前提の崩壊）。
  3. 未定義競合（上流ADR間で解釈不能な競合が残存）。

### 3.1 Context
- Gate C（feedback分類）と Gate D（KPI監査）の境界が曖昧だと、Gate E の Proceed 判定根拠が監査不能になる。
- QA公開境界（PUB/I18N/readOnly）の失敗を「運用逸脱」へ誤集計しないため、入力契約の粒度統一が必要。

### 3.2 Decision
- Gate C→D→E の順序、evidence6項目、停止条件3項目を運用固定値として扱う。
- Gate D の記録は KPI 判定だけでなく「逸脱有無」と「反映先リンク」を必須化し、再監査を可能にする。

### 3.3 Consequences
- 監査時に「未分類残件」と「KPI逸脱」を分離して追跡できる。
- Proceed 判定（Go/Conditional/No-Go）の説明責任を文書単体で満たせる。
- 次サイクルでのドリフト検知（語彙・順序・閾値）を自動照合しやすくなる。

## 4) Phase 3 Plan（AC/DoD補完）

### 4.1 Acceptance Criteria

- [x] Gate C→D→E の固定順序が4文書で同一語彙・同一順序で明文化されている。
- [x] Gate C 完了条件（`未分類=0` または `保留理由 + 再判定日`）が Gate D 開始条件に固定されている。
- [x] Gate D 入力契約（測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク）が固定されている。
- [x] Gate E Proceed条件（Go / Conditional / No-Go）が固定されている。
- [x] 停止条件（3回超過 / 前提崩れ / 未定義競合）が4文書で一致している。
- [x] evidence形式（Date / Gate / Command / Result / Decision / Next action）が4文書で一致している。

### 4.2 DoD

- [x] `issue-0019` / `issue-0020` / `issue-doc-ops-05-11` / `operations.md` の記述が同一契約で同期されている。
- [x] docs-check / 用語照合 / diff整合の実行結果を記録している。
- [x] 次回測定サイクルの開始条件（Proceed条件）が明文化されている。
- [x] 停止条件に該当する場合は Proceed せず CDC 化する導線を明文化している。

## 5) Phase 4 Execute（KPI定義→監査指標→運用Runbook の直列実行）

### 5.0 直列固定（必須）

1. KPI定義（4KPI）を固定。
2. 監査指標（Gate D 入力6項目 + 逸脱判定）を固定。
3. 運用Runbook（Gate C→D→E と Proceed条件）を同期更新。

### 5.1 Gate C（feedback operation）

- 入力: 変更候補・レビューコメント・障害報告。
- 分類: requirements / architecture / test / product gap / 未分類。
- 出力条件: `未分類=0` または `未分類に保留理由 + 再判定日` を付与。

### 5.2 Gate D（KPI scorecard audit）

- 開始条件: Gate C の出力条件を満たしたデータのみ対象。
- 記録契約: 測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク。
- 判定契約: KPIしきい値は承認済み台帳のみ参照。

### 5.3 Gate E（Proceed decision）

- 入力: Gate C分類結果 + Gate D scorecard。
- 判定:
  - Go: 記録確定後に次工程へ進行。
  - Conditional: 再判定日 + 担当記録後に限定進行。
  - No-Go: 見送り理由 + 再判定日 + 担当記録まで停止。

## 6) Phase 5 Verify（docs-check）

### 6.1 Validation evidence（統一形式）

- Date: 2026-04-13
  - Gate: docs-check
  - Command: `python3 01_Plans/issues/validate_active_issue_memos.py --root .`
  - Result: Pass（issue memo validator 正常終了）
  - Decision: 契約形式を維持
  - Next action: 横断語彙照合へ進む
- Date: 2026-04-13
  - Gate: terminology consistency
  - Command: `rg -n "Gate C|Gate D|Gate E|TFS|Decision Readiness|Support Deflection|Feedback Closure|Go / Conditional / No-Go|Date / Gate / Command / Result / Decision / Next action|Proceed条件|未分類|しきい値|閾値|Stream F|3回超過|前提崩れ|未定義競合" 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md 04_Documentation/operations.md`
  - Result: Pass（4文書の語彙・順序・停止条件整合を確認）
  - Decision: 用語ドリフトなし
  - Next action: 差分整合確認へ進む
- Date: 2026-04-13
  - Gate: diff integrity
  - Command: `git diff -- 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md 04_Documentation/operations.md`
  - Result: Pass（許可ファイルのみ差分）
  - Decision: Proceed判定へ進む
  - Next action: 次回測定サイクル条件を確定

### 6.2 修復上限

- docs-check / 用語整合 / diff整合の自己修復は最大3回。
- 4回目相当の不一致は Fail-safe 停止（Proceed禁止）。

## 7) Phase 6 Proceed（次の測定サイクル条件）

次サイクルに進む条件を以下で固定する。

1. Gate C が完了し、未分類の扱い（0件または保留理由+再判定日）が記録済み。
2. Gate D の入力契約6項目が欠落なく記録済み。
3. Gate E 判定と Proceed条件（Go / Conditional / No-Go）が一致。
4. evidence 6項目形式が各Gateで充足。
5. docs-check / 用語照合 / diff整合の3確認がPass。
6. 停止条件（3回超過 / 前提崩れ / 未定義競合）のいずれにも該当しない。

- 次回定点レビュー: **2026-04-26 09:00 UTC**。
- 担当: **Stream F（Unified Feedback Loop Operations Owner）**。

## 8) Fail-safe（ADR衝突時のCDC化）

以下を検知した場合は作業を停止し、**CDC（Context / Decision / Consequences）として論点化** する。

- KPI定義・Proceed条件が `ADR-0001` / `ADR-0019` / `ADR-0024` / `ADR-0028` と衝突。
- 未承認の閾値変更（承認ログなし）。
- Gate順序が `C→D→E` 以外で記述される。
- evidence項目の欠落または Command と Result の不整合。
- 停止条件（3回超過 / 前提崩れ / 未定義競合）に該当。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## Stream H linkage (2026-05-10)
- QA判定境界連携: Gate C→D→E へ投入するQA結果は「Done/Hold/Stop」の3値で統一。
- Done条件: QA-UNIT-01 / QA-E2E-USE-01 / QA-PUB-01 のAC/DoDが全てYes。
- Hold条件: 依存未解決・環境制約・承認待ちのいずれか。
- Stop条件: flaky再試行3回超過、または安全境界後退。
- エスカレーション基準: P0境界失敗は即時にGate Dへ逸脱として送る。
