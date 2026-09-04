# issue-DOC-TRIAGE-SELF-DEP-01 — 自己依存issueをfail-closedでBlockedにする

- Type: Process / Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Scope: `01_Plans/triage_actionable_plans.py`, `01_Plans/tests/`
- Related ADR/Spec: `ADR-0000`
- Expected verification level: `unit`

## 課題

自己依存を持つActive memoでは、`dependency_stage()` は循環として未解決sentinel `999` を返す一方、blocker生成側が自己参照を除外しているため、Open issueを `Ready` と誤判定できる。

## 対応

- 自己依存を `<Backlog ID>:SelfDependency` blockerとして扱う。
- 自己依存をtriage errorとして明示する。
- dependency stageの既存sentinel `999` は維持する。
- 回帰テストで「自己依存はReadyにならず、診断も残る」ことを固定する。

## 受入条件

- 自己依存を持つOpen issueがReadyにならない。
- `SelfDependency` blockerが出力される。
- self dependency triage errorが出力される。
- 既存triageテストと実リポジトリtriageが成功する。
