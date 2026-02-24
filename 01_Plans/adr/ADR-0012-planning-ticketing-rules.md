# ADR-0012: フェーズ計画・チケット化規則（ADR-0001分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0001-value-to-requirements.md`

## Context

`ADR-0001` の後半（フェーズ計画、Non-goals、Issue/Epicルール）が要求本体と同居していた。

## Decision

計画運用・チケット化・非目標管理を本ADRに分離し、
価値原則・要求定義のADRから独立して更新できるようにする。

## Consequences

- PM運用変更が要件定義へ波及しにくくなる。
- 受入判定と起票テンプレートの改訂を局所化できる。

## Traceability

- Derived sections: `ADR-0001` の「4. フェーズ計画」「5. Non-goals」「6. チケット化ルール」
