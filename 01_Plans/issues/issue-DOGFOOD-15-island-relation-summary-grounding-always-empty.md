# Issue: DOGFOOD-15 島間関係要約の接地（grounding）がモックで常に空で、E2Eが固定できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 180（シナリオ110・動物園/水族館 実装時の実走行観察）。`summarize-island-relation` に `groundingCardIds:["z4"]` を指定しても、モックが `"groundingCardIds":[]`（空接地）を返し、島間関係の接地セマンティクスを E2E で固定できないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ110）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `01_Plans/issues/issue-DOGFOOD-13-island-summary-grounding-capped-at-three-cards.md`（同じく接地のモック盲点）, `02_Architecture/api.md`（summarize-island-relation 契約・groundingCardIds は allowed の部分集合）, `00_Prompt/kj_technique.md` §4（島間関係線と接地）
- Expected verification level: `e2e`

## 課題

`mock_local_llm.py` の `summarize_island_relation` は、応答の接地を**常に空**で返す:

```python
if task == "summarize_island_relation":
    return json.dumps({
        "text": "（モック）...",
        "groundingCardIds": [],
        "groundingEdgeIds": [],
        "warnings": [],
    })
```

一方、バックエンドのプロンプト（`ai_relations.py` の `_build_relation_summary_prompt`）は `allowed groundingCardIds=[...]` / `allowed groundingEdgeIds=[...]` を明示しており、応答契約は「groundingCardIds は allowed の部分集合」を要求する。したがって:

- **`summarize-island-relation` が島間関係をどのカード・エッジに接地しているかを E2E で一切検証できない**（scenario 106 は `"text"` キーの存在だけを assert）。
- バックエンドが接地を落とす（または LLM が常に空接地を返す）回帰が起きても、643チェックの業務フローE2E は全部 pass する。

実機再現（iteration 180）:

```text
# groundingCardIds:["z4"] を指定 → {"text":"...","groundingCardIds":[],"groundingEdgeIds":[],"warnings":[]}（接地が落ちる）
```

### なぜ問題か

- **接地は島間関係の根拠（grounding）の正本**（kj_technique.md §4）であり、その保全が検証されない。
- **DOGFOOD-13（島要約の接地3カード打ち切り）と同型の盲点**: 接地がモックの都合で消え、シナリオの「関係を根拠づける」主張を E2E が検証できない。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は島間関係（因果・対立）が**どのカード/エッジに根拠づけられているか**を参照したい。関係要約は根拠（grounding）付きでなければ判断の材料にならない | 関係要約は **proposal 相当（read-only の下書き）** のまま。自動適用・確定はしない |
| **データ設計** | プロンプトは `allowed groundingCardIds` / `allowed groundingEdgeIds` を含むため、モックは**許可された接地集合をそのままエコー**できる（response は allowed の部分集合で整合） | 既存の空接地応答を仮定するアサーションは無い（scenario 106 は `"text"` のみ assert）ため非後退 |
| **機能設計** | `summarize_island_relation` でプロンプトの allowed 接地リストをパースして応答へ反映する。API契約（`SummarizeIslandRelationResponse`）は不変 | 既存シナリオ（106）は `"text"` キー assert のため非後退。バックエンド実装は変更しない |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `summarize_island_relation` で、プロンプトの `allowed groundingCardIds` / `allowed groundingEdgeIds` をパースして**応答の接地へエコー**する。
  2. シナリオ110（水族館・動物園）の島間関係要約チェックを **`groundingCardIds:["z4"]` の接地**で固定し、関係の根拠が保全されることを業務フローE2E で検証する。
- 実施しないこと:
  - summarize-island-relation の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（106・島間関係要約）のアサーションの変更（`"text"` のみ assert・非後退）。

## 受入条件

- [x] `groundingCardIds:["z4"]` を指定した関係要約が `"groundingCardIds":["z4"]` を返す（実走行で確認）。
- [x] 接地を指定しない / 空指定の場合も契約整合（`[]` のまま）。
- [x] 既存シナリオ（106・警察/公安）の島間関係要約が従来どおり pass（`"text"` assert・非後退）。
- [x] シナリオ110の島間関係チェックが `"groundingCardIds":["z4"]` を assert し、業務フローE2E が **650/650 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 650/650（シナリオ110の ZO ⑤島間関係要約が接地エコー）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックの接地エコーは「allowed 接地集合をそのまま返す」だけであり、実LLMの接地選択品質とは独立（本issueは検証ハーネスの能力向上）。
- ドッグフーディング観察起点（2026-08-16・iteration 180）: 動物園・水族館の運営方針（体験価値と運営コストのトレードオフ・2島構成）で `summarize-island-relation` に `groundingCardIds:["z4"]` を指定して実行し、応答の接地が空になることを再現。関係の根拠が保全されるかを E2E で固定できないことを特定した。
