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


## DOC-OPS user-requested serial execution（2026-04-22 / Issue 05-01）

### Phase 1 Read
- Phase開始時再Read: `04_Documentation/canonicalization.md` と対応Issueを再読。

### Phase 2 Plan
- Phase開始時再Read: 本文ヘッダメタ（Audience/Goal/Public boundary/Non-goal）を再読。
- AC/DoD不足判定: 不足なし。既存stub構成を維持。

### Phase 3 Execute
- Phase開始時再Read: Go/No-Go節を再読。
- 実施: 本直列実行ログを追記（分類は Move internal のまま）。

### Phase 4 Verify
- Phase開始時再Read: Verify対象キーワードを再読。
- 実行: `rg -n "DOC-OPS user-requested serial execution|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 04_Documentation/canonicalization.md`。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- 判定: **Ready**（公開stub + 内部正本導線を維持）。


## DOC-OPS-05-01 Stream G final sync（2026-04-26）

### Phase 1 Read
- `04_Documentation/canonicalization.md` と対応Issueを再読し、分類・公開境界・検証レベルの整合を確認。

### Phase 2 ADR/CDC
- Context: canonicalization の詳細は設計正本に集約し、公開文書は概要に限定する必要がある。
- Decision: **Move internal** を継続し、本書は公開stubとして維持する。
- Consequences: 公開境界の明確化により露出リスクを抑制し、詳細は `02_Architecture/schemas.md` / `02_Architecture/architecture.md` 参照へ統一。

### Phase 3 Plan
- Scope: 本書の配置方針と導線の固定。
- Non-goals: 実装仕様変更、他文書の横展開編集。
- AC/DoD: Audience / Goal / Public boundary / Migration policy / Non-goal / Go-NoGo 条件の維持、docs-check実施、6Phase記録。

### Phase 4 Execute
- 実施: Stream G完了ログを追記し、Issueとの整合（Move internal + 公開stub運用）を固定。

### Phase 5 Verify
- docs-check相当: ヘッダメタ・Go/No-Go条件・内部正本導線を再確認。
- 自己修復回数: 0/3。

### Phase 6 Proceed
- 判定: **Ready**。
- 後続最小メモ: 設計正本が更新された場合のみ、stub導線を同期更新する。


## Stream G mini-Phase serial run（2026-04-27）

### Phase 1 Read
- 対応Issue（`DOC-OPS-05-01`）と本書の分類ヘッダを再読し、公開境界を確認。

### Phase 2 Plan
- 変更責務を docs-only の記録同期に限定し、本文の分類（Move internal / Improve external）を維持。
- 共通ACテンプレ（Scope固定 / 境界明示 / GoNoGo / docs-check / 3回上限）を適用。

### Phase 3 Execute
- 本節を追記し、Read→Plan→Execute→Verify→Proceed の直列実行証跡を固定。
- 指定外ファイル・実装コード・共有統合ファイルは未編集。

### Phase 4 Verify
- `rg -n "DOC-OPS|Classification|Audience|Goal|Public boundary|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/canonicalization.md`
- `git diff --check`
- self-repair count: 0/3。

### Phase 5 Proceed
- 判定: **Ready**（分類方針と公開境界を維持）。
