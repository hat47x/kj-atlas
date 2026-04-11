# Phase6 Public Documentation Architecture

- Status: Draft for integration stream D
- Scope: `04_Documentation` public information path and operation gates

## Goal

公開導線と運用判定を一貫させ、ドキュメント変更が `Gate A` から `Gate E` まで監査可能になる構造を定義する。

## Information path

利用者導線は `04_Documentation/README.md` で固定し、次順序を必須とする。

- Overview
- Tutorial
- Scenario
- Reference

## Context / Decision / Consequences（CDC明文化）

### Context

- Phase6の公開運用では、Gate C→D→E の順序揺れが監査再現性を低下させる。
- Gate D 入力と Gate E Proceed 条件が曖昧だと、同じ判定名でも運用結果が再現できない。

### Decision

- 実行順序を Gate C→Gate D→Gate E に固定し、逆順実行を禁止する。
- Gate D 入力契約を `測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク` に固定する。
- Gate E Proceed 条件を固定する。
  - Go: 記録確定後に次工程へ進行。
  - Conditional: 再判定日 + 担当の記録後に限定進行。
  - No-Go: 見送り理由 + 再判定日 + 担当の記録完了まで進行禁止。
- evidence形式を `Date / Gate / Command / Result / Decision / Next action` の6項目必須に固定する。

### Consequences

- Gate実行の単方向依存が明確化され、監査で同一手順を再現しやすくなる。
- 判定記録の必須化により運用負荷は増えるが、公開判定の説明責任を強化できる。

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
- Gate C 完了前は Gate D を開始しない。

### Gate D: KPI scorecard integrity

- Gate C完了条件を満たしたデータのみを scorecard 対象にする。
- scorecard は TFS / Decision Readiness / Support Deflection / Feedback Closure を計測する。
- 必須入力は `測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク`。

### Gate E: Release decision

- Gate C分類結果 + Gate D scorecard + Gate A/B整合結果を入力として扱う。
- 判定は Go / Conditional / No-Go。
- Proceed条件:
  - Go: 記録確定後に次工程へ進行。
  - Conditional: 再判定日と担当を記録後に限定進行。
  - No-Go: 見送り理由・再判定日・担当を記録するまで停止。

## Gate execution order

Gate運用は次の順序を固定し、逆順実行を禁止する。

1. Gate C（feedback分類）
2. Gate D（KPI scorecard）
3. Gate E（release decision）

※ Gate A/B は前提整備ゲートとして先行確認し、C以降の実行中に不整合が見つかった場合はFail-safeで停止する。

## Evidence schema（統一形式）

各Gateの証跡は次フォーマットで記録する（6項目必須）。

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
- Gate順序の多義化（C→D→E以外が許容される記述）

## Operational note

- `planning_queue` 実行結果が取得できない場合は、理由と代替確認（`rg`結果）を Validation evidence へ残す。

## Stream G phase protocol（Gate C→D→E 運用整合）

運用整合タスクは次の5Phaseを固定し、各Phase開始時に対象3文書の再読で状態同期する。

1. Phase 1 Read（現行Gate定義再読）: 各Phase冒頭で `issue-0019` / `issue-0020` / 本アーキテクチャ文書を再読する。
2. Phase 2 CDC: CDC差分がある場合のみ Gate C→D→E 固定で更新する。
3. Phase 3 Plan（AC/DoD不足補完合意）: Gate D の4KPIと入力契約、Gate E Proceed 条件の不足を補完して合意する。
4. Phase 4 Execute（C→D→E順序, evidence 6項目固定）: Gate C→D→E を順序固定で実行し、証跡を `Date / Gate / Command / Result / Decision / Next action` 形式で記録する。
5. Phase 5 Verify/Proceed（docs-check、3回自己修復上限、超過停止）: `docs-check` と `diff` を実施し、自己修復は最大3回までとし、超過時はFail-safe停止とする。

失敗時は self-correction を最大3回まで許容し、以下に該当した場合はFail-safeで停止する。

- Gate順序崩壊
- evidence形式不一致
- self-correction の3回超過
