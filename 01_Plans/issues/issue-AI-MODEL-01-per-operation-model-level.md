# Issue: AI-MODEL-01 KJ操作別モデルレベル定義

- Type: Feature
- Status: Draft
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer
- Scope: `00_Prompt/kj_technique.md`, `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, `AGENTS.md`
- Related ADR/Spec: `ADR-0067-three-element-constraint-design-method.md`, `02_Architecture/dogfooding-ai-collaboration-plan.html`
- Expected verification level: `unit`

## 課題

- 現在の問題: KJ法の各操作（カード化・束ね・表札作成・関係線・島形成・ナラティブ・違和感検出・矛盾検出・タイトル提案）に必要なAI推論深度が定義されていない。すべての操作に同じモデルが使われており、安価なモデルで十分な操作にも高コストなモデルを使っている
- 利用者または開発への影響: API費用の非効率。また、操作ごとの品質要件が不明確なため、AI提案の品質評価基準が定まらない

## 対応方針

- 実施すること:
  1. 各KJ操作の必要推論深度を低・中・高の3段階で定義
  2. 推論深度ごとに推奨モデルを割り当て（DeepSeek / Sonnet / Opus）
  3. モデル選択を環境変数で操作別に上書き可能にする仕組み（KJ_ATLAS_MODEL_LEVEL_LOW / _MEDIUM / _HIGH）
  4. AGENTS.md と llm/provider.py にモデルレベル対応を実装
- 実施しないこと:
  1. 利用者向けUIでのモデル選択機能（現段階では開発者向け設定に留める）
  2. 操作ごとの品質スコアリング・自動評価

## モデルレベル定義（案）

| KJ操作 | 推論深度 | 推奨モデル | 根拠 |
|--------|---------|-----------|------|
| カード化（RawNote→Card） | 低 | DeepSeek | テキスト構造化。名詞止め→述語文は規則的 |
| 束ね（2〜3枚のグループ化） | 低〜中 | DeepSeek | 近接性判断。幾何情報も利用可能 |
| 表札作成（島ラベル） | 中 | DeepSeek / Sonnet | 共通性抽出。分類名ではなくadvocacy |
| 関係線（5種別） | 中 | DeepSeek / Sonnet | 論理的関係の識別 |
| 違和感検出（Critique） | 中〜高 | Sonnet | 「なんとなく違う」の言語化 |
| 島形成（空間構造化） | 中 | DeepSeek / Sonnet | 空間配置提案 |
| ナラティブ（B型叙述） | 高 | Sonnet / Opus | 空間→文章。A型照合を含む |
| 矛盾検出 | 中〜高 | Sonnet | 論理的矛盾の検出 |
| 文書タイトル提案 | 低〜中 | DeepSeek | 低品質許容・人間が編集前提 |
| 三要素整合チェック | 中 | DeepSeek / Sonnet | 構造化された判断記録が入力 |

## 受入条件

- [ ] 10操作の推論深度と推奨モデルが定義されている
- [ ] 環境変数 KJ_ATLAS_MODEL_LEVEL_LOW / _MEDIUM / _HIGH でモデル指定可能
- [ ] provider=none 時は全操作でAI呼び出しをスキップ
- [ ] モデルレベル定義が AGENTS.md に反映されている

## 補足

- DeepSeek API の provider 追加（issue-AI-PROVIDER-01）に依存
- 操作の60-70%はDeepSeekでカバー可能と見積もる
