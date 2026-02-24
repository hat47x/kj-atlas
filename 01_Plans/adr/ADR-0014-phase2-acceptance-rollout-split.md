# ADR-0014: Phase2 受入基準・導入計画（ADR-0005分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0005-phase2-qualitative-integration.md`

## Context

Phase2の後半（受入基準、リスク、段階導入、テンプレート）が運用更新頻度の高い情報である。

## Decision

受入基準・リスク緩和・2A/2B/2C rollout・着手前チェックを本ADRで独立管理する。

## Consequences

- リリース判定の改訂を素早く行える。
- 要求本体は `ADR-0013` に固定し、運用更新と分離する。

## Traceability

- Derived sections: `ADR-0005` の「8〜11章」
