# issue-DOC-TRIAGE-CYCLE-01 — Active issue間の循環を診断しDone依存を終端化する

- Type: Process / Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Scope: `01_Plans/triage_actionable_plans.py`, `01_Plans/tests/`
- Related ADR/Spec: `ADR-0000`
- Expected verification level: `unit`

## 課題

Active issue同士が循環依存している場合、現行triageは各issueを直接依存のblockerによって `Blocked` にできる一方、循環そのものを診断しない。そのため、stageが未解決sentinel `999` となる理由を出力から特定しにくい。

また、Done memoもdependency stageの再帰探索対象になっているため、すでに満たされた依存の過去メモ内にActive issueへの逆参照が残っているだけで、現在のActive issueが `dependency_stage=999` になることがある。Done memoから伸びる過去の依存辺は、現在のactionabilityやunlocksを構成する辺として扱うべきではない。

## 対応

- Active issueだけからなる依存グラフについて、強連結成分を用いて複数issue間の循環を検出する。
- 自己依存は既存の `SelfDependency` 診断に委ね、循環診断で重複させない。
- 循環を `dependency cycle among active issues: ...` のtriage errorとして明示する。
- Done memoはdependency stage計算上の満たされた終端として扱い、その内部の過去依存を再帰探索しない。
- `unlocks` はActive issueから伸びる現在の依存辺だけから構成し、Done memoの過去依存で汚染しない。

## 受入条件

- 2件以上のActive issueによる循環依存がtriage errorとして明示される。
- 循環に含まれるActive issueは従来どおり `Blocked` かつ `dependency_stage=999` のままである。
- Done dependencyを満たしているActive issueは、Done memo内の過去の逆参照だけを理由に `999` にならない。
- Done memoの過去依存がActive issueの `unlocks` に現れない。
- 既存triageテストと実リポジトリtriageを壊さない。
