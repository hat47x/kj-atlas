# ADR-0065: KJ法タスク複雑度に応じた LLM モデル選択戦略

- Status: Proposed
- Date: 2026-08-09
- Deciders: Project Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/llm/`, settings, テスト

## Context

現在の kj-atlas は全 AI タスク（10 tasks）に単一の LLM モデルを使用する。
しかし KJ 法のタスクは要求される思考レベルが大きく異なる：

| タスク | 要求される能力 | 複雑度 |
|---|---|---|
| `re_layout` | 空間配置（座標計算） | 低 |
| `suggest_merges` | テキスト類似性判定 | 低〜中 |
| `refine_card_text` | 文章改善（言い換え） | 中 |
| `suggest_island_summary` | 複数カードの要約 | 中 |
| `summarize_island_relation` | 関係性の説明 | 中 |
| `suggest_card_groups` | カテゴリ分類 | 中〜高 |
| `check_narrative` | 論理的一貫性検証 | 高 |
| `detect_contradiction` | 矛盾検出（論理推論） | 高 |
| `generate_narrative` | 創造的文章生成 | 最高 |

軽量タスクに高性能モデルを使うとコストが無駄になり、
高負荷タスクに軽量モデルを使うと品質が低下する。

## Decision

### D1: タスク→モデルマッピングを設定可能にする

```python
# settings.py / 環境変数
KJ_ATLAS_LLM_TASK_MODEL_MAP = "re_layout=deepseek-v4-flash,..."
```

未設定タスクはデフォルトモデルにフォールバックする。

### D2: 3層のオーバーライド優先順位

| 優先度 | レベル | 設定方法 | 用途 |
|---|---|---|---|
| 1 (最高) | リクエスト | API リクエストボディの `model` フィールド | プロンプト単位の動的切替 |
| 2 | テナント | `tenant_settings` テーブル（将来） | 組織単位のポリシー |
| 3 (最低) | グローバル | `KJ_ATLAS_LOCAL_LLM_MODEL` + `KJ_ATLAS_LLM_TASK_MODEL_MAP` | デプロイ全体の既定値 |

v1 では優先度 1 と 3 を実装する。優先度 2 は Phase 2。

### D3: 推奨モデルマッピング

| 複雑度 | 推奨モデル | 月額コスト目安 (DeepSeek) |
|---|---|---|
| 低 (re_layout, suggest_merges) | `deepseek-v4-flash` | $0.14/1M tokens |
| 中 (refine, summary, groups, relation) | `deepseek-v4-flash` | $0.14/1M tokens |
| 高 (check_narrative, detect_contradiction) | `deepseek-v4-flash` または `deepseek-v4-pro` | $0.55/1M tokens |
| 最高 (generate_narrative) | `deepseek-v4-pro` | $0.55/1M tokens |

> DeepSeek の場合、`deepseek-v4-flash` でも十分な品質が得られる。コスト最適化が重要になる
> までは全タスクに `deepseek-v4-flash` を使用し、タスク別マッピングは後から注入する。

### D4: 段階的実装計画

**Phase 1 (今回)**: 設定ベースのタスク→モデルマッピング
- `KJ_ATLAS_LLM_TASK_MODEL_MAP` 環境変数
- リクエストレベルの `model` オーバーライド
- テストでの検証

**Phase 2 (将来)**: テナントレベル設定
- `tenant_settings` テーブル
- テナント管理 UI

**Phase 3 (将来)**: ユーザ/キャンバスレベル設定
- パーソナライズされた AI 設定
- コスト追跡・使用量制限

## Consequences

- 同一デプロイ内で複数モデルの併用が可能になる
- コスト最適化: 軽量タスクに軽量モデルを使用可能
- 設定の複雑性が増す → デフォルトで十分動作するよう設計

## Non-goals

- リアルタイムのモデルパフォーマンス監視
- 自動モデル選択（ML-based）
- コスト上限の自動強制
