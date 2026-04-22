# Canonicalization（公開概要）

> DOC-OPS-05 Classification: **Move internal**
> Audience: 外部利用者（概要参照のみ）
> Goal: canonicalization の公開境界を固定し、内部正本への導線を明示する。
> Public boundary: 本書は概要のみ公開し、設計詳細・運用詳細・変更管理は内部正本で管理する。
> Migration policy: 詳細説明は `02_Architecture/schemas.md` と `02_Architecture/architecture.md` を正本として扱う。
> Non-goal: アルゴリズム詳細、内部レビュー手順、運用判断ログの公開。
> Related: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`

本書は公開向けの最小説明（stub）です。実装・運用の詳細は内部正本を参照してください。

## 公開する最小説明

- canonicalization は、重複や類似を整理するための概念です。
- AI は候補提案に限定され、確定は人間レビューで実施します。
- SafeMode および review 境界（未レビュー情報の自動確定禁止）を緩和しません。

## 内部正本への導線

- データ契約・型整合: `02_Architecture/schemas.md`
- 全体責務境界: `02_Architecture/architecture.md`
- 分類判断トラッキング: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`

## Go/No-Go gate（公開判定）

公開「Go」は次を満たす場合のみ:

1. Audience / Goal / Public boundary / Migration policy / Non-goal が明示されている。
2. 「AI提案は自動確定しない」境界が明示されている。
3. 詳細情報が本書に混在せず、内部正本への導線が維持されている。

いずれか未充足の場合は「No-Go」として公開更新を停止します。


## DOC-OPS Track 1 serial execution（2026-04-22 / DOC-OPS-05-01）

### Phase 1 Read（同期）
- Read同期: `04_Documentation/canonicalization.md` と `issue-doc-ops-05-01-04doc-canonicalization.md` を再読。

### Phase 2 ADR/CDC
- Context: canonicalization の詳細は内部正本へ集約する必要がある。
- Decision: Move internal を維持し、本書は公開stubとして運用する。
- Consequences: 公開境界を明確化し、詳細の重複管理を削減。

### Phase 3 Plan（AC/DoDドラフト→合意）
- AC draft: Migration policy と AI非自動確定境界の維持。
- DoD draft: 6Phase記録と docs-check、自己修復3回上限。
- 合意: Issueメモで合意済み。

### Phase 4 Execute
- 本節を追記し、stub運用の固定記録を追加。

### Phase 5 Verify
- `rg -n "DOC-OPS Track 1 serial execution|Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed" 04_Documentation/canonicalization.md`

### Phase 6 Proceed
- Ready。詳細は内部正本で継続管理。
