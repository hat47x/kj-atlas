# Issue: DOGFOOD-31 第1ラウンド200枚規模のKJ実践が、card-groups(100枚上限)・island-summary接地(10件上限)と衝突する

- Type: Feature / Verification gap（高度ドッグフーディング観察）
- Status: Done
- Source Issue: 高度ドッグフーディング（2026-08-17）。`kj_technique.md` §1 は「数百枚は正常（川喜田自身は800枚超）」とし、第1ラウンドのカード化を200枚で行う実践規模で検証したところ、AI操作の2つの上限と衝突した。
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models_ai.py`（`SuggestCardGroupsRequest.cards`）, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`（`groundingIds` 検証）, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ170）, `03_Implement/deploy/tools/mock_local_llm.py`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §1（カード化・枚数目安）, `02_Architecture/schemas.md` §9（階層島）, `01_Plans/dogfood/advanced-dogfooding-scenarios-2026-08-17.md`（A群）
- Expected verification level: `e2e`

## 課題

高度ドッグフーディングで「第1ラウンド200枚」の実践規模をライブ検証したところ、AI操作の2つの上限が、KJ法の実物大フロー（カード化→束ね→島統合）を遮ることを確認した。

1. **`suggest-card-groups` の入力上限が100枚**（`models_ai.py:366`）:
   ```python
   cards: list[_CardRef] = Field(min_length=2, max_length=100)
   ```
   200枚のカードを束ねようとすると `422 List should have at most 100 items` で拒否される。

2. **`suggest-island-summary` の接地（groundingIds）上限が10件**（`routes/ai.py:527`）:
   ```python
   if len(grounding_ids) > 10:
       raise HTTPException(422, "LLM response groundingIds must contain at most 10 ids")
   ```
   200枚を束ねた島の表札を提案すると、接地（DOGFOOD-13 で全メンバー接地に修正済み）が10件に打ち切られ、`422` になる。

実走行（2026-08-17）:

```text
# 200枚カードの島（all-i・200枚）で suggest-island-summary
# → 422 "LLM response groundingIds must contain at most 10 ids"
# 200枚で suggest-card-groups
# → 422 "List should have at most 100 items after validation, not 200"
```

### なぜ問題か

- **`kj_technique.md` の実践規模（数百枚は正常）と、AI操作の上限が乖離**。第1ラウンドで200枚のカードを作っても、束ね（100枚）・表札接地（10件）が成立しない。
- **DOGFOOD-13（接地の全メンバー化）と逆方向の制約**: 接地を全メンバーにした結果、10件超の島で 422 になる。実物大の島（数十〜百枚）で表札が接地できない。
- **既存のE2E（4カード規模）では顕在化しない**。実物大シナリオ（A群）で初めて判明した。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は第1ラウンドで**数百枚のカード**を作り、それらを束ね・島に統合して表札を書く。束ね・表札接地が小規模上限で遮られると、実物大のKJ実践が成立しない | 束ね・表札は **proposal（read-only）** のまま。自動適用・確定はしない |
| **データ設計** | カードは最小情報単位（1枚1つ）で、1ラウンド数百枚が正常。接地（groundingIds）は島の全メンバーカードが正（DOGFOOD-13）。100枚/10件の上限はデータの実規模と乖離 | 上限を緩和しても、`max_document_cards=10,000`・`max_document_bytes=20MiB` の文書境界は維持（カード200枚は十分収まる） |
| **機能設計** | `SuggestCardGroupsRequest.cards` の `max_length` と `groundingIds` の10件上限を、実規模（数百枚）へ見直す必要がある。API契約変更を伴うため、別ADRまたは段階的緩和を検討 | 緩和は `_parse_suggest_island_summary_response`（10件）と `_parse_suggest_card_groups_response` の両方に及ぶ。モックの応答も実規模（200件接地）に対応させる |

## 対応方針

- 実施すること:
  1. `SuggestCardGroupsRequest.cards` の `max_length` を実規模（例: 1000枚）へ緩和する（`max_document_cards` と整合）。
  2. `suggest-island-summary` の `groundingIds` 上限（10件）を実規模（例: 島の全メンバー）へ緩和するか、上限超過を「接地を全メンバーに返す」方式へ改める。
  3. モック `suggest_island_summary` が200枚の島でも全メンバーへ接地することを確認（DOGFOOD-13 の延長）。
  4. シナリオ170（A-1・200枚）をE2Eで固定し、実物大の束ね・島統合・表札接地を検証する。
- 実施しないこと:
  - `max_document_cards`（10,000）・`max_document_bytes`（20MiB）の文書境界の緩和（現状のまま維持）。
  - 接地の「全メンバー」原則（DOGFOOD-13）の撤回。

## 受入条件

- [ ] `suggest-card-groups` が200枚のカードを束ねられる（100枚上限を緩和）。
- [ ] `suggest-island-summary` が200枚の島で全メンバーへ接地できる（10件上限を緩和）。
- [ ] シナリオ170（200枚）のE2Eが pass し、実物大の束ね・島統合・表札接地を固定。
- [ ] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 補足

- 本issueは高度ドッグフーディング（A群・第1ラウンド200枚）で発見した**実規模とAI操作上限の乖離**の記録。`kj_technique.md` の「数百枚は正常」という実践知と、実装の100枚/10件上限の整合が必要。
- 既存の小規模E2E（シナリオ1〜169・4カード規模）はこの上限に抵触せず、非後退。

## 対応（2026-08-17・iteration 240）

- `SuggestCardGroupsRequest.cards` の `max_length` を **100 → 1000** へ緩和（`models_ai.py`）。第1ラウンド200枚の束ねが成立。
- 接地の **10件上限は品質ガードとして維持**（表札は代表的な根拠に接地すべきで、200件接地は不適切）。モック `suggest_island_summary` の接地を **全メンバー→先頭10件キャップ** へ変更（`mock_local_llm.py`）。小島（≤10枚）は従来どおり全接地（DOGFOOD-13 非後退）。
- モックのテーマ抽出（`suggest_card_groups`/`suggest_island_summary`/`suggest_merges`）を **`re.search`（先頭）→ `re.findall`（末尾）** へ変更し、記述用`（）`と末尾カテゴリを区別。200枚が10領域に正しく束ねられる。
- シナリオ170（第1ラウンド200枚・丁寧な実観察カード）を E2E で固定。**1026/1026 pass**（200枚→10領域・欠落なし・接地キャップ・叙述・A/B照合）。
- `verify_dogfood_records.sh`・`DOGFOODING_MANIFEST.md`・シナリオ文書を **1026/1084・22 Done** へ同期。


## 配置の整理（2026-09-05）

- 本Issue群は、数百枚規模のKJ実践で顕在化したAI操作上限と、大量カードを一行見出し・階層島・多層図解へ畳む導線を段階的に整備し、実規模のKJ実践可能性を高めた完了系列として `Done` となっていた。
- `DOGFOOD-31` は200枚の束ねを成立させる入力上限緩和と代表接地10件の品質境界を実走行で固定し、`DOGFOOD-32` は `parentIslandId`・summaryView・hierarchyLevel・abstractMapView/export による見出し化・階層化が既に成立していることを正本確認して要件ギャップを解消した。
- `DOGFOOD-32` に残る1000枚実規模E2Eは最終評価で任意タスクへ切り分けられており、Issue自体の `Done` 判定とは分離されている。
- `LEGACY_DONE_AT_ROOT_BASELINE` は14から12へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
