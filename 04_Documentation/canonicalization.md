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


## DOC-OPS-05 実行記録（Phase 1〜5）

### Phase 1 Read

- Latest Read: 2026-04-13
- Audience / Goal / Public boundary / Related を確認し、公開境界を再確認。

### Phase 2 Plan

- Latest Read: 2026-04-13
- 本文は docs-only の範囲で更新し、仕様正本（00〜02）を上書きしない方針を固定。

### Phase 3 Execute

- Latest Read: 2026-04-13
- DOC-OPS-05 classification に沿って本文の公開メタと導線を整備。

### Phase 4 Verify

- Latest Read: 2026-04-13
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/canonicalization.md`
- `git diff --check`

### Phase 5 Proceed

- Latest Read: 2026-04-13
- 状態: **Ready**
- 次アクション: 内部正本への参照stub化を維持し、詳細運用情報は 02_Architecture 側で管理する。


## Stream F docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **Plan**: AC/DoD を先に定義する。不足時はドラフトを提示し、合意後に実行へ進む。
3. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
4. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
5. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 参照仕様未確定、または競合検知時は作業を停止する。
- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## DOC-OPS-05 追加実行記録（2026-04-16 / Target 05-01..05）

### Phase 1 Read（再Read）
- 本書と関連Issueを再Readし、公開境界とdocs-onlyスコープを確認。

### Phase 2 Plan（再Read）
- 5Phase（Read→Plan→Execute→Verify→Proceed）で進行し、対象外文書へは非接触とする。

### Phase 3 Execute（再Read）
- 本書の既存分類・公開境界メタを維持しつつ、05-01..05セットの実行記録を追記。

### Phase 4 Verify（再Read）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/canonicalization.md 01_Plans/documentation_quality.md`
- `git diff --check`
- 修復は最大3回まで。3回超過は停止（Hold）。

### Phase 5 Proceed（再Read）
- 判定: **Ready**
- 次アクション: 同一セット内Issue本文とScope本文の整合を維持して進行。

## DOC-OPS-05 Stream G 前半フェーズ実行記録（2026-04-16）

- Classification確認: **Move internal**（再判定なし）
- フェイルセーフ固定: 用語ドリフト検知・固定値不一致検知・自己修復3回超過で停止（Hold）

### Phase 1: Read（対象ファイル再読）
- 本ファイルを再読し、Scope / Audience / Goal / Public boundary / Related の整合を確認。

### Phase 2: Plan（対象ファイル再読）
- 本ファイルを再読したうえで、docs-only の変更範囲と受入条件を固定。

### Phase 3: Execute（対象ファイル再読）
- 本ファイルを再読したうえで、分類方針（Move internal / Improve external）を維持して更新。

### Phase 4: Verify（docs-check、対象ファイル再読）
- 本ファイルを再読したうえで docs-check を実施。
- 推奨確認: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/canonicalization.md`
- 体裁確認: `git diff --check`

### Phase 5: Proceed（対象ファイル再読）
- 本ファイルを再読したうえで状態を判定し、`Ready / Hold / Needs-decision` を記録。
- 判定: **Ready**（現時点で保留なし）。
