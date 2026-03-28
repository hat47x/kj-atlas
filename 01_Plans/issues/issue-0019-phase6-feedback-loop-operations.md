# Issue Draft: 0019 Phase6 Feedback Loop Operations

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Stream H
- Scope: `01_Plans/issues/` + integration references
- Related ADR/Spec: `ADR-0019`, `phase6-public-documentation-architecture.md`
- Expected verification level: `docs-check`

## 1) Problem statement

公開ドキュメントの更新時に、feedback運用の分類・判定導線が分断され、Gate運用と証跡が乖離していた。

## 2) Proposed solution

- Gate C（feedback operation）を中心に、Gate A〜Eとの接続点を明示する。
- Validation evidenceを更新し、運用矛盾（分類不足・判定不一致）を解消する。

## 3) Acceptance criteria

- [x] Gate Cの分類要件が requirements / architecture / test / product gap / 未分類 で固定される。
- [x] Gate A〜EとQuality gateの接続先が architecture 文書に一致する。
- [x] Validation evidenceに実行コマンドと結果（成功/制約）を記録する。

## 4) Validation evidence

- 2026-03-28 実行:
  - `rg -n "Gate A|Gate B|Gate C|Gate D|Gate E|Quality gate|Known limitations|scorecard|planning_queue" 02_Architecture/phase6-public-documentation-architecture.md 01_Plans/issues/issue-0019-phase6-feedback-loop-operations.md 01_Plans/issues/issue-0020-phase6-value-kpi-and-audit-scorecard.md`
    - 結果: Gate A〜E、Quality gate、Known limitations、scorecard、planning_queue を3文書で確認。
  - `python3 01_Plans/tools/planning_queue.py`
    - 結果: ファイル未配置のため実行不可（運用制約として記録）。

## 5) Operational contradiction resolution

- 旧状態: feedback記録とKPI判定が別系統で、Gate CからGate Dへの移送条件が未定義。
- 現状態: Gate C分類完了をGate D入力条件として明示し、Quality gateで最終整合する。

## 6) Next action

- templates側での実運用ログ定着を次streamへ引き渡す（本Issueは共有導線の整合まで）。
