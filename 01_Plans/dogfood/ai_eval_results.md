# DeepSeek実API KJ操作品質評価結果

- 対応: `issue-AI-EVAL-01`（L2基準③）
- 更新: 2026-08-11
- 状態: **パイプライン検証済み・実API実行待ち（DeepSeek API key投入のみ）**

## 評価パイプラインの検証状況

### リハーサル完了（2026-08-11、モックLLMで8テスト合格）

`test_ai_eval_pipeline.py`（8 tests passed）で評価手順の実効性を実証済み:

| 検証項目 | テスト | 結果 |
|---------|--------|------|
| 評価用fixtureがDocumentV1として有効 | `test_fixture_is_valid_document_v1` | ✅ 4島/12カード/6エッジ |
| refine-card-textリクエスト組立 | `test_fixture_has_reviewed_cards_for_refine` | ✅ 10カード |
| suggest-island-summaryリクエスト組立 | `test_fixture_has_islands_for_summary` | ✅ 4島 |
| DeepSeek task-model配線 | `test_deepseek_provider_wired_for_eval_tasks` | ✅ |
| refine-card-textエンドポイント経由 | `test_refine_card_text_endpoint_mock_eval` | ✅ 200応答 |
| refine-card-text全10カード駆動 | `test_refine_card_text_eval_covers_all_fixture_cards` | ✅ 10回呼出 |
| suggest-island-summaryエンドポイント経由 | `test_suggest_island_summary_endpoint_mock_eval` | ✅ summary+groundingIds |
| suggest-island-summary全4島駆動 | `test_suggest_island_summary_eval_covers_all_fixture_islands` | ✅ 4回呼出 |

**結論**: 評価手順は実エンドポイント経由で完全に動作する。`KJ_ATLAS_DEEPSEEK_API_KEY` を設定し、backendを起動して同一の手順を実行するだけで実API評価が行える。コード変更は不要。

## 評価方法

定性3軸評価（反スコアリング原則により数値化しない）。各軸は「合格 / 不合格 / 要改善」で判定し、2軸以上合格で「実用可」とする。

### 対象操作

1. `refine_card_text`（カード化・低深度）— 10件
2. `suggest_island_summary`（表札作成・中深度）— 4島

### 使用fixture

`03_Implement/backend/tests/fixtures/ai_eval_kj_document.json`（島4・カード12・関係線6）

## 実行手順

```bash
# 1. API key設定
export KJ_ATLAS_LLM_PROVIDER=deepseek
export KJ_ATLAS_DEEPSEEK_API_KEY=<key>

# 2. backend起動
cd 03_Implement/backend
.venv/bin/uvicorn kj_atlas_api.main:app --port 8000

# 3. refine_card_text評価（10件）
#    fixtureのカードc01〜c10を1件ずつPOST /ai/refine-card-textへ

# 4. suggest_island_summary評価（4島）
#    fixtureの島i1〜i4を1件ずつPOST /ai/suggest-island-summaryへ

# 5. 結果を下表に記録
```

## 評価1: refine_card_text（カード化）

| # | 入力カード | 出力 | 名詞止め解除 | 元意味保持 | 過剰言い換えなし | 判定 |
|---|-----------|------|------------|-----------|----------------|------|
| 1 | c01「高齢者は一人で買い物に行けない」 |  |  |  |  |  |
| 2 | c02「商店街の店が次々と閉店している」 |  |  |  |  |  |
| 3 | c03「バスの本数が減って不便になっている」 |  |  |  |  |  |
| 4 | c04「宅配サービスを利用する高齢者が増えている」 |  |  |  |  |  |
| 5 | c05「若い世代はネット通販を日常的に使っている」 |  |  |  |  |  |
| 6 | c06「地元の食材を扱う直売所に人が集まる」 |  |  |  |  |  |
| 7 | c07「移動販売車が地域を巡回している」 |  |  |  |  |  |
| 8 | c08「公民館で週に一度サロンが開かれている」 |  |  |  |  |  |
| 9 | c09「住民同士の助け合い活動が活発だ」 |  |  |  |  |  |
| 10 | c10「買い物弱者を支える仕組みが十分でない」 |  |  |  |  |  |

合格数: __ / 10（3軸中2軸以上合格で実用可）

## 評価2: suggest_island_summary（表札作成）

| # | 島 | 島のカード | 出力表札 | 別島に載せても成立しない | 代弁性 | 名詞止め解除 | 判定 |
|---|----|-----------|---------|----------------------|--------|------------|------|
| 1 | i1 | c01/c02/c03 |  |  |  |  |  |
| 2 | i2 | c04/c05/c06 |  |  |  |  |  |
| 3 | i3 | c07/c08/c09 |  |  |  |  |  |
| 4 | i4 | c10/c11/c12 |  |  |  |  |  |

合格数: __ / 4（3軸中2軸以上合格で実用可）

## 総合判定

- refine_card_text: __ / 10 → 実用可 / 要改善 / 不合格
- suggest_island_summary: __ / 4 → 実用可 / 要改善 / 不合格
- L2基準③（2操作以上で実用可）: 達成 / 未達成

## メモ

- レイテンシ・エラー耐性・日本語品質の所見
- モデル選択（deepseek-chat vs deepseek-reasoner）の要否
