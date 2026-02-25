# ADR-0015: CLI 対象範囲と段階導入（ADR-0008分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0008-cli-tooling-plan.md`

## Context

CLI計画は対象ユーザー、非対象、Phase X-0〜X-4が同居し、導入判断が複雑化している。

## Decision

CLIの対象範囲（対象/非対象）とフェーズ導入計画のみを本ADRに分離する。

## Consequences

- どこまでCLI化するかの合意形成が容易になる。
- コマンド仕様は `ADR-0016` へ委譲。

## Traceability

- Derived sections: `ADR-0008` の「2章」「3章（Phase計画）」
