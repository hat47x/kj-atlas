# ADR-0011: 価値→要求マッピング（ADR-0001分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0001-value-to-requirements.md`

## Context

UX/Data/AI要求が価値原則と混在しており、要件レビュー時に参照範囲が大きい。

## Decision

要求マッピング（UX / Data / AI / review flags / safeMode制約）を独立管理する。
バックログ連携とチケット化ルールは別ADRで扱う。

## Consequences

- 仕様変更時に要件差分のみレビュー可能。
- 計画ADRとのトレーサビリティが改善する。

## Traceability

- Derived sections: `ADR-0001` の「2. 価値観ごとの要求」「3. Backlog整合」
- Related: `ADR-0010`, `ADR-0012`
