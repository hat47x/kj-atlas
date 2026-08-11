# ADR-0013: Phase2 要求・データ影響（ADR-0005分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0005-phase2-qualitative-integration.md`

## Context

Phase2 ADRが問題定義から実装チェックまで単一化され、仕様議論が長文化している。

## Decision

Phase2の前半（問題定義、ユーザーストーリー、要求一覧、データモデル/UI影響）を本ADRで扱う。

## Three-Element Verification（ADR-0067 遡及適用）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | Phase2 ADRが問題定義から実装チェックまで単一化され仕様議論が長文化している。Phase2の前半（問題定義・ユーザーストーリー・要求一覧・データモデル/UI影響）を独立管理する | 機能: 要求変更時のレビュー範囲を縮小する。データ: Phase2の受入基準・導入計画はADR-0014で扱う |
| **データ設計** | ADR-0005の「1〜7章」を本ADRへ独立させる。Phase2の要求をデータモデル/UI影響とともに保持 | 業務: 要求レビューを局所化し仕様議論の長文化を防ぐ。機能: 受入基準とのトレーサビリティをADR-0014と分離 |
| **機能設計** | Phase2の要求定義を参照しやすい単位に分割し、実装の前提として利用できるようにする | 業務: 受入基準・導入計画（ADR-0014）との責務分離を明確化。データ: データモデル/UI影響を要求とともに一箇所で保持 |

## Consequences

- 要求変更時のレビュー範囲が縮小される。
- 受入基準・導入計画は `ADR-0014` で扱う。

## Traceability

- Derived sections: `ADR-0005` の「1〜7章」
