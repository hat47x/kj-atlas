# Phase6 Public Documentation Architecture

- Status: Draft for integration stream G
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
- Gate C完了条件は `未分類=0` または `未分類項目に保留理由と再判定日が付与`。
- 運用ログは `issue-0019` の Validation evidence へ反映される。

### Gate D: KPI scorecard integrity

- Gate C完了条件を満たしたデータのみを scorecard 対象にする。
- scorecard は TFS / Decision Readiness / Support Deflection / Feedback Closure を計測する。
- KPI結果は `issue-0020` の Validation evidence と矛盾しない。

### Gate E: Release decision

- A〜D の判定を踏まえ、公開更新の Go / Conditional / No-Go を明示する。
- Conditional / No-Go 時は、見送り理由・再判定日・次アクションを必ず記録する。

## Gate execution order

Gate運用は次の順序を固定し、逆順実行を禁止する。

1. Gate C（feedback分類）
2. Gate D（KPI scorecard）
3. Gate E（release decision）

※ Gate A/B は前提整備ゲートとして先行確認し、C以降の実行中に不整合が見つかった場合はFail-safeで停止する。

## Evidence schema（統一形式）

各Gateの証跡は次フォーマットで記録する。

- Date
- Gate
- Command
- Result
- Decision
- Next action

## Quality gate alignment

`Quality gate` は Gate A〜E を横断する最終整合として扱う。

- 入力: README導線、feedback運用証跡、scorecard結果
- 判定: Pass / Conditional / Fail
- 記録先: `issue-0019`・`issue-0020` の Validation evidence

## Known limitations

- `planning_queue.py` が未配置の環境では、キュー検証を自動化できない。
- 本文書は運用統合の最小I/Fを定義し、各stream固有本文の内容品質までは保証しない。
- scorecard閾値は暫定であり、将来の運用実績で見直しが必要。

## Fail-safe

次を検知した場合は、Gate E判定へ進まず停止する。

- Gate定義矛盾
- evidence不整合
- 未定義参照

## Operational note

- `planning_queue` 実行結果が取得できない場合は、理由と代替確認（`rg`結果）を Validation evidence へ残す。
