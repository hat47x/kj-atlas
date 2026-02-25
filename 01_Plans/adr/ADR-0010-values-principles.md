# ADR-0010: 価値原則の明示（ADR-0001分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0001-value-to-requirements.md`

## Context

`ADR-0001` は価値観・要求・バックログ・チケット化規則を単一文書で保持しており、参照単位が粗い。

## Decision

価値原則（保留尊重、反スコアリング、人間レビュー中心、safeMode既定ON）を本ADRに独立させる。
要求や実装計画は別ADRへ分離する。

## Consequences

- 価値判断の参照先を短く固定できる。
- 下流文書は本ADRを前提として要求や受入条件を記述する。

## Traceability

- Derived sections: `ADR-0001` の「1. 価値観（原則）」
- Related: `ADR-0011`, `ADR-0012`
