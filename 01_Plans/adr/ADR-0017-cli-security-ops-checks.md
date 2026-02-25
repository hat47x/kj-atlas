# ADR-0017: CLI セキュリティ/運用受入チェック（ADR-0008分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0008-cli-tooling-plan.md`

## Context

CLI計画の後半（機密情報マスク、TODO維持条件、受入チェック）が実装仕様と混在していた。

## Decision

セキュリティ要件、直近タスク、受入チェックリストを本ADRで分離管理する。

## Consequences

- 監査観点のレビューを独立実施できる。
- 仕様変更と運用チェックの更新サイクルを分離できる。

## Traceability

- Derived sections: `ADR-0008` の「6章」「7章」
