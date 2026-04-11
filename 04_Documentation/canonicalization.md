# Canonicalization（公開概要）

> DOC-OPS-05 Classification: **Move internal**
> Audience: 外部利用者（概要参照のみ）
> Goal: canonicalization の公開境界を明示し、内部正本への導線を提供する。
> Non-goal: 詳細運用手順・内部レビュー手順・実装契約の公開。
> Public boundary: 本書は概要のみを公開し、詳細設計/運用は内部文書へ移設する。
> Outcome: 読者が「公開範囲」と「正本参照先」を誤解なく判断できる。
> Related: `02_Architecture/schemas.md`, `02_Architecture/architecture.md`, `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`

本ページは公開向けの**最小概要**です。canonicalization の詳細手順は内部正本で管理します。

## 公開する最小説明

- canonicalization は、類似カードを代表カードへ束ねるための概念です。
- AI は候補提案のみを行い、確定は人間レビューで実施します。
- SafeMode/レビュー境界（未レビューの自動確定禁止）を緩和しません。

## Go/No-Go gate（公開判定）

公開「Go」は次を満たす場合のみ:

1. Audience / Goal / Non-goal / Public boundary / Outcome / Related が明示されている。
2. AI提案の自動確定を許可しない旨が明記されている。
3. 詳細運用は内部文書へ誘導され、公開文書へ混在していない。

いずれか未充足の場合は「No-Go」として公開更新を停止します。

## 詳細参照先（内部正本）

- 設計整合: `02_Architecture/schemas.md`
- 全体境界: `02_Architecture/architecture.md`
- トラッキング: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
