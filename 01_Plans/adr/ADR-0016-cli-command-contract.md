# ADR-0016: CLI コマンド体系と共通I/F（ADR-0008分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0008-cli-tooling-plan.md`

## Context

CLI名空間設計（`kj doc/view/policy/audit`）と共通引数規約が大きな計画文書に埋もれている。

## Decision

コマンド体系、共通フラグ、exit code、最小コマンドセットを本ADRに独立させる。

## Consequences

- CLI実装/レビュー時の参照先が明確になる。
- セキュリティ・運用チェックは `ADR-0017` で管理。

## Traceability

- Derived sections: `ADR-0008` の「4章」
