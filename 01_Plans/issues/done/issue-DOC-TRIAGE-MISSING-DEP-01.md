# issue-DOC-TRIAGE-MISSING-DEP-01 — 欠落依存でもtriageを継続しfail-closedにする

- Type: Process / Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Scope: `01_Plans/triage_actionable_plans.py`, `01_Plans/tests/`
- Related ADR/Spec: `ADR-0000`
- Expected verification level: `unit`

## 課題

存在しないissue依存を持つActive memoでは、`dependency_stage()` が既知依存だけへ絞った結果 `max()` の入力を空にし、triage errorを返す前に例外終了し得る。また、欠落issue/ADR依存はエラーとして記録されてもblockerへ入らず、issueが `Ready` と誤判定され得る。

## 対応

- 欠落issue依存をdependency stageの未解決sentinelとして保持し、triage処理を継続する。
- 欠落issue依存を `<Backlog ID>:Missing` blockerとして扱う。
- 欠落ADR依存を `ADR-xxxx:Missing` blockerとして扱う。
- 診断用のtriage errorは従来どおり保持する。
- 回帰テストで「エラーを返しつつBlockedになる」ことを固定する。

## 受入条件

- 欠落issue依存でtriageが例外終了しない。
- 欠落issue/ADR依存を持つOpen issueがReadyにならない。
- 欠落参照のtriage errorが失われない。
- 既存triageテストと実リポジトリtriageが成功する。
