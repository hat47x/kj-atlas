# Issue Draft: 0020 Phase6 Value KPI and Audit Scorecard

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Stream H
- Scope: `01_Plans/issues/` + integration references
- Related ADR/Spec: `ADR-0001`, `phase6-public-documentation-architecture.md`
- Expected verification level: `docs-check`

## 1) Problem statement

KPI scorecard の計測項目は定義されていても、Gate運用との接続と証跡更新のルールが統一されていなかった。

## 2) Proposed solution

- Gate D（KPI scorecard integrity）とQuality gateの整合を運用文書に反映。
- Validation evidenceに測定観点とコマンド結果を統合記録。

## 3) KPI scope

- TFS
- Decision Readiness
- Support Deflection
- Feedback Closure

## 4) Acceptance criteria

- [x] scorecard 4項目がGate Dの入力として明示される。
- [x] Gate C（feedback分類）完了をscorecard計測前提にする。
- [x] Validation evidenceに architecture/issue間整合の証跡を残す。

## 5) Validation evidence

- 2026-03-28 実行:
  - `rg -n "Gate A|Gate B|Gate C|Gate D|Gate E|Quality gate|Known limitations|scorecard|planning_queue" 02_Architecture/phase6-public-documentation-architecture.md 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md`
    - 結果: Gate Dのscorecard要件、Quality gate参照、planning_queue制約を確認。
  - `python3 01_Plans/tools/planning_queue.py`
    - 結果: ファイル未配置のため実行不可（Known limitations と整合）。

## 6) Operational contradiction resolution

- 旧状態: KPI監査結果がfeedback分類の成熟度を前提にしていなかった。
- 現状態: Gate C完了 → Gate D計測 → Gate E判定 の順序を固定。

## 7) Next action

- KPIテンプレート stream（G）で測定日/対象文書/判定/次アクション/反映先リンクを実装定着する。
