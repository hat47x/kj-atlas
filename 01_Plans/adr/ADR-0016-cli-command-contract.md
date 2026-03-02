# ADR-0016: CLI コマンド契約と検証粒度（ADR-0008分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0008-cli-tooling-plan.md`

## Context

CLIコマンド仕様を早期に固定しすぎると、MVP後のAPI確定前提と衝突しやすい。
一方で、実装者が迷わないためには「何を契約として守るか」を先に決める必要がある。

## Decision

### 1) 今決める契約（固定）

1. CLI名は `kj`。
2. トップレベル名前空間は当面 `doc`, `view`, `policy`, `audit` を予約語として扱う。
3. 共通I/F契約:
   - `--format json|yaml|text`
   - `--input -` / `--output -`
   - `--quiet` / `--verbose` / `--debug`
4. exit code契約（暫定だが実装はこの番号を維持）:
   - `0`: success
   - `1`: validation failed
   - `2`: usage error
   - `3`: runtime error
   - `4`: auth error
5. 互換性契約:
   - 既存引数の意味変更は禁止。
   - 廃止予定機能は最低1フェーズの非推奨期間を置く。

### 2) 後で決める契約（保留）

- 各サブコマンド配下の詳細オプション。
- `--profile` / `--request-id` / `--dry-run` の既定値。
- エラー本文フォーマット（human-readableの詳細）。

## Command-level Acceptance（実装着手時の受入判定）

> 本節は「実装後に必ず満たすべき受入基準」。現時点ではテスト設計の固定が目的。

### A. 契約テスト（必須）

- `kj --help` にトップレベル名前空間が表示される。
- `kj <namespace> --help` が0終了し、usageを返す。
- 不正引数入力で exit code `2` を返す。

### B. I/O契約テスト（必須）

- `--input -` / `--output -` の標準入出力が機能する。
- `--format` 指定に応じてシリアライズ形式が切り替わる。

### C. 互換性テスト（必須）

- 既存サブコマンドの引数意味が変わっていないことをスナップショットで検知できる。

## Test Command Blueprint（検証コマンド粒度）

以下のコマンド名を受入判定の標準粒度として予約する。
実装時は同名で追加し、CIに組み込む。

1. `pytest 03_Implement/backend/tests/cli_contract/test_help_contract.py`
2. `pytest 03_Implement/backend/tests/cli_contract/test_exit_codes.py`
3. `pytest 03_Implement/backend/tests/cli_contract/test_stdio_contract.py`
4. `pytest 03_Implement/backend/tests/cli_contract/test_backward_compat.py`

合格条件:
- 上記4コマンドが全て終了コード0。
- 失敗時は互換性破壊として扱い、修正またはADR改訂のどちらかを同一PRで実施する。

## DoD

1. 契約テスト観点（Help / Exit / I/O / 互換）が欠落なく列挙される。
2. 受入判定に必要な最小コマンドが固定される。
3. ADR-0015（範囲）・ADR-0017（安全運用）と責務重複しない。

## Non-Goals

- 業務コマンドの機能仕様（例: `doc export` のパラメータ完全定義）。
- APIレスポンススキーマの新規確定。

## Consequences

- 実装者は「まず何のテストを作るか」を迷わない。
- 仕様未確定領域を残しつつ、破壊的変更を検知できる。

## Traceability

- Parent: `01_Plans/adr/ADR-0008-cli-tooling-plan.md`
- Related: `01_Plans/adr/ADR-0015-cli-scope-phasing.md`
- Related: `01_Plans/adr/ADR-0017-cli-security-ops-checks.md`
- Related: `02_Architecture/api.md`
- Related: `02_Architecture/schemas.md`
