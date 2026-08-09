# kj-atlas LLM クイックスタート

AI 支援機能（レイアウト提案、マージ候補、ナラティブ生成など）をローカルで動作させる手順です。

## 前提

kj-atlas の LLM プロバイダは独自の `/generate` 契約を使用します（OpenAI API 非互換）。
実際の LLM 推論サーバがなくても、付属の mock サーバで全 AI 機能の動作を確認できます。

## 方法 1: Mock LLM（GPU不要、全6タスク対応）

`mock_local_llm.py` は決定論的なスタブで、全 AI タスクに有効な最小限の応答を返します。

```bash
# 1. Mock LLM を起動
cd 03_Implement/deploy
python3 tools/mock_local_llm.py --host 127.0.0.1 --port 8001

# 2. 別のターミナルでバックエンドを起動
cd 03_Implement/backend
KJ_ATLAS_LLM_PROVIDER=local \
KJ_ATLAS_LOCAL_LLM_BASE_URL=http://localhost:8001 \
KJ_ATLAS_LOCAL_LLM_MODEL=mock \
KJ_ATLAS_DATABASE_URL=sqlite:///./kj_atlas.db \
.venv/bin/uvicorn kj_atlas_api.main:app --reload

# 3. 動作確認
curl http://localhost:8000/ai/provider-status
# → {"providerKind":"local"}
```

## 方法 2: Docker Compose llm-stub（re_layout + suggest_merges のみ）

```bash
cd 03_Implement/deploy
docker compose -f docker-compose.yml -f docker-compose.llm-stub.yml up -d

# 確認
curl http://localhost:8000/ai/provider-status
# → {"providerKind":"local"}
```

## 方法 3: 実 LLM サーバ（Ollama / llama.cpp / vLLM）

実際の LLM を使う場合は、kj-atlas の `/generate` 契約に準拠するアダプタが必要です。

**リクエスト形式**:
```json
POST {base_url}/generate
{
  "task": "re_layout",
  "prompt": "<プロンプト文字列>",
  "temperature": 0.2,
  "max_tokens": 2000,
  "model": "任意のモデル識別子"
}
```

**レスポンス形式**:
```json
{"text": "<タスク別の厳密なJSON文字列>"}
```

各タスクの出力スキーマは `02_Architecture/llm_provider_spec.md` を参照してください。

## 方法 4: DeepSeek API（クラウドLLM、高品質）

DeepSeek API は OpenAI 互換の chat completions API を提供します。

```bash
# 1. API キーを設定
export DEEPSEEK_API_KEY="sk-..."

# 2. アダプタを起動
python3 deploy/tools/deepseek_adapter.py --port 8001 --model deepseek-chat

# 3. バックエンドに接続
KJ_ATLAS_LLM_PROVIDER=local \
KJ_ATLAS_LOCAL_LLM_BASE_URL=http://localhost:8001 \
KJ_ATLAS_LOCAL_LLM_MODEL=deepseek-chat \
.venv/bin/uvicorn kj_atlas_api.main:app

# 4. テスト実行
pytest tests/test_kj_session_e2e.py -v -m "not ollama"
```

| アダプタ | ファイル | 利点 | 欠点 |
|---|---|---|---|
| モック | `mock_local_llm.py` | GPU不要・決定論的 | 固定出力のみ |
| Ollama | `ollama_adapter.py` | ローカル実行・無料 | CPUでは低速 |
| **DeepSeek** | **`deepseek_adapter.py`** | **高品質・高速** | **APIキー・従量課金** |

## 全 AI エンドポイント一覧

| エンドポイント | メソッド | LLM タスク | 説明 |
|---|---|---|---|
| `/ai/provider-status` | GET | — | プロバイダ設定の表示 |
| `/ai/suggest-layout` | POST | `re_layout` | カード配置の提案 |
| `/ai/suggest-merges` | POST | `suggest_merges` | 統合候補の提案 |
| `/ai/suggest-island-summary` | POST | `suggest_island_summary` | アイランド要約 |
| `/ai/proposals/island-summary` | POST | `suggest_island_summary` | 同上（ProposalEnvelope形式） |
| `/ai/proposals/audit` | POST | — | 提案の受理/拒否/保留を記録 |
| `/ai/generate-narrative` | POST | `generate_narrative` | ナラティブ生成 |
| `/ai/check-narrative` | POST | `check_narrative` | ナラティブ検証 |
| `/ai/summarize-island-relation` | POST | `summarize_island_relation` | アイランド間関係の要約 |

## 設定リファレンス

| 環境変数 | 既定値 | 説明 |
|---|---|---|
| `KJ_ATLAS_LLM_PROVIDER` | `none` | `none` / `local` / `large-scale` |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL` | — | local プロバイダの `/generate` エンドポイント |
| `KJ_ATLAS_LOCAL_LLM_MODEL` | — | モデル識別子（任意の文字列） |
| `KJ_ATLAS_LLM_ESCALATION_ENABLED` | `false` | large-scale に必須 |
| `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN` | `false` | large-scale に必須 |

`KJ_ATLAS_LLM_PROVIDER=none`（既定）では、全 AI エンドポイントが `503 provider_unavailable` を返します。
これは安全な既定値であり、AI を使わない運用を妨げません。

## トラブルシューティング

| 現象 | 原因 | 解決 |
|---|---|---|
| `503 provider_unavailable` | LLM サーバが未起動または到達不能 | Mock LLM または実サーバを起動 |
| `422 provider_validation` | プロンプトが不正（空、過大、タスク名不正） | プロンプトを確認 |
| `504 provider_timeout` | LLM サーバが 60 秒以内に応答しない | モデルを小さくするかタイムアウトを調整 |
| `provider=none` でも 200 | `/ai/provider-status` は常に動作（設定表示のみ） | — |
