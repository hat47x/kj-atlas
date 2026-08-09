# Issue: AI-PROVIDER-01 DeepSeek API provider 追加

- Type: Feature
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, `03_Implement/backend/src/kj_atlas_api/settings.py`
- Related ADR/Spec: `issue-AI-MODEL-01-per-operation-model-level.md`, `02_Architecture/dogfooding-ai-collaboration-plan.html`

## 課題

- 現在の問題: kj-atlasのLLM providerは既存のモデル（Claude等）のみに対応しており、安価なDeepSeek APIをKJ操作の大部分に使うことができない
- 利用者または開発への影響: API費用が高い。KJ操作の60-70%は低〜中の推論深度で十分であり、高コストなモデルを使う必要がない

## 対応方針

- 実施すること:
  1. `llm/provider.py` に DeepSeek API 対応を追加（OpenAI互換APIのため既存基盤を流用可能）
  2. 環境変数 `KJ_ATLAS_DEEPSEEK_API_KEY` / `KJ_ATLAS_DEEPSEEK_BASE_URL` / `KJ_ATLAS_DEEPSEEK_MODEL` で設定可能にする
  3. 既存のモデルレベル定義（issue-AI-MODEL-01）と統合し、操作別にDeepSeekを選択可能にする
  4. SafeMode・proposal-only・反スコアリング等の既存安全境界はDeepSeek利用時も維持
- 実施しないこと:
  1. DeepSeek APIキーの管理機能（環境変数での設定のみ）
  2. ローカルLLMの最適化・サポート（provider abstractionの範囲内で理論上選択可能だが、実用性は検証しない）

## 予算申告

- 複雑性予算（ADR-0043 CB-1..4）: 初期表示への純増=なし（provider追加のみ、UI変更なし）
- 性能予算（ADR-0046 PB-1..5）: N/A
- 触れるUQ次元（ADR-0044）: N/A

## 受入条件

- [ ] `KJ_ATLAS_LLM_PROVIDER=deepseek` でDeepSeek APIが使用可能
- [ ] 環境変数でAPI key・base URL・model名が設定可能
- [ ] provider=none時は当然に全AI呼び出しをスキップ（既存動作を変更しない）
- [ ] 既存の安全境界（SafeMode・提案のサニタイズ・未レビュー除外）がDeepSeek利用時も機能する

## 補足

- DeepSeek API は OpenAI 互換のため、既存のOpenAI用コードの大部分を流用可能
- model名の既定値は `deepseek-chat`（最新のV3系列を想定）
- `KJ_ATLAS_DEEPSEEK_BASE_URL` の既定値は `https://api.deepseek.com`
