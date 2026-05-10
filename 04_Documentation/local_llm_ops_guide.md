# Local LLM Operations Guide

対象読者: local LLM または組織内 LLM endpoint を kj-atlas に接続する運用担当者、開発者。

目的: local provider の設定、HTTP contract、確認方法、失敗時の切り分けを示します。

範囲外: 特定モデルの導入手順、外部 large-scale LLM の契約管理、秘密情報の配布。

## 既定値

kj-atlas は既定で LLM を使いません。

```bash
export KJ_ATLAS_LLM_PROVIDER=none
```

この状態では AI 機能は disabled として扱われ、外部送信は行われません。

## local LLM とは

この文書での local LLM は、kj-atlas から見て管理できる範囲にある LLM endpoint を指します。必ずしも同じ PC 上という意味ではありません。組織内サーバーを使う場合も、送信先、保持期間、入力データの扱いを確認してください。

## local provider を有効にする

```bash
export KJ_ATLAS_LLM_PROVIDER=local
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
```

`local_http` も `local` の alias として扱われます。

## HTTP contract

backend は `<base_url>/generate` に POST します。

Request:

```json
{
  "task": "string",
  "prompt": "string",
  "temperature": 0.2,
  "max_tokens": 2000,
  "model": "local-model-name"
}
```

Response:

```json
{
  "text": "generated text"
}
```

`text` が文字列でない場合、provider validation error として扱われます。

## 疎通確認

local endpoint 側:

```bash
curl -fsS http://localhost:8001/generate \
  -H 'content-type: application/json' \
  --data '{"task":"health","prompt":"Say ok","temperature":0.2,"max_tokens":16,"model":"local-model-name"}'
```

kj-atlas backend:

```bash
curl -fsS http://localhost:8080/api/healthz
docker compose logs api --tail=100
```

## 運用上の注意

- local という名前でも、URL が外部サービスを指していれば外部送信です。
- 入力に秘密情報や未レビューの機密情報を含めないでください。
- SafeMode の目的を緩める設定変更は、[security.md](security.md) と [security_operational_guidelines.md](security_operational_guidelines.md) を確認してから行ってください。
- provider が不安定な場合は、まず `KJ_ATLAS_LLM_PROVIDER=none` に戻して基本操作が正常か確認します。

## よくある失敗

| 症状 | 確認 |
| --- | --- |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL is not set` | base URL が未設定 |
| provider timeout | local endpoint が起動していない、または応答が遅い |
| response missing text field | endpoint の応答が `{ "text": "..." }` ではない |
| AI disabled | `KJ_ATLAS_LLM_PROVIDER=none` のまま |

## large-scale との違い

large-scale provider は、明示 opt-in、昇格許可、allowlist がすべて必要です。local provider とは別の安全境界として扱います。

```bash
export KJ_ATLAS_LLM_PROVIDER=large-scale
export KJ_ATLAS_LLM_ESCALATION_ENABLED=true
export KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true
export KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST='llm.example.com'
```

## 関連文書

- [configuration.md](configuration.md)
- [security.md](security.md)
- [ce2_low_risk_ai_assist.md](ce2_low_risk_ai_assist.md)
