# Phase6 Public Documentation Architecture

- Status: Draft for integration stream H
- Scope: `04_Documentation` public information path and operation gates

## Goal

公開導線と運用判定を一貫させ、ドキュメント変更が `Gate A` から `Gate E` まで監査可能になる構造を定義する。

## Information path

利用者導線は `04_Documentation/README.md` で固定し、次順序を必須とする。

- Overview
- Tutorial
- Scenario
- Reference

## Gate design (A〜E)

### Gate A: Entry coherence

- READMEに **Overview → Tutorial → Scenario → Reference** が明示されている。
- 入口文書が重複正本を作らない。

### Gate B: Structural alignment

- アーキテクチャ文書とIssue運用文書の用語が一致する。
- Gate名称（A〜E）と判定責務が混在しない。

### Gate C: Feedback operation

- feedback分類が requirements / architecture / test / product gap / 未分類 で記録される。
- 運用ログが issue-0019 の Validation evidence へ反映される。

### Gate D: KPI scorecard integrity

- scorecard が TFS / Decision Readiness / Support Deflection / Feedback Closure を計測する。
- KPI結果が issue-0020 の Validation evidence と矛盾しない。

### Gate E: Release decision

- A〜Dの判定を踏まえ、公開更新のGo/No-Goを明示する。
- 見送り時は次アクションと再判定日を記録する。

## Quality gate alignment

`Quality gate` は Gate A〜E を横断する最終整合として扱う。

- 入力: README導線、feedback運用証跡、scorecard結果
- 判定: Pass / Conditional / Fail
- 記録先: issue-0019・issue-0020 の Validation evidence

## Known limitations

- `planning_queue.py` が未配置の環境では、キュー検証を自動化できない。
- 本文書は運用統合の最小I/Fを定義し、各stream固有本文の内容品質までは保証しない。
- scorecard閾値は暫定であり、将来の運用実績で見直しが必要。

## Operational note

- `planning_queue` 実行結果が取得できない場合は、理由と代替確認（rg結果）をValidation evidenceへ残す。
