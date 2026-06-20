# Local LLM Operations Guide

対象読者: local LLM または組織内 LLM endpoint を kj-atlas に接続する運用担当者、開発者。

目的: local provider の設定、HTTP contract、確認方法、失敗時の切り分けを示します。

範囲外: 特定モデルの導入手順、外部 large-scale LLM の契約管理、秘密情報の配布。

公開区分: 運用者向け公開候補。local LLM 連携の設定・戻し方を扱い、external provider や escalation は明示的 opt-in がない限り既定OFFとして扱います。

読後にできること: 既定では LLM が無効であることを理解し、local LLM を有効にするときの設定、疎通確認、戻し方を判断できます。

## 既定値

kj-atlas は既定で LLM を使いません。

```bash
export KJ_ATLAS_LLM_PROVIDER=none
```

この状態では、AI 機能は disabled として扱われ、LLM 連携による外部サービスとの共有は行われません。最初の評価、受け入れ確認、保存動作の確認では、この既定値を推奨します。

## local LLM とは

この文書での local LLM は、kj-atlas から見て管理できる範囲にある LLM endpoint を指します。同じ PC 上のサービスとは限りません。組織内サーバーを使う場合もあります。

local という名前でも、URL が外部サービスを指していれば、そのサービスとデータを共有する扱いです。接続先、保持期間、入力データの扱いを確認してから有効にしてください。

## local provider を有効にする

```bash
export KJ_ATLAS_LLM_PROVIDER=local
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
```

`local_http` は `local` の alias として扱われます。

設定を戻す場合は、provider を `none` に戻します。

```bash
export KJ_ATLAS_LLM_PROVIDER=none
```

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

まず local endpoint 側を直接確認します。

```bash
curl -fsS http://localhost:8001/generate \
  -H 'content-type: application/json' \
  --data '{"task":"health","prompt":"Say ok","temperature":0.2,"max_tokens":16,"model":"local-model-name"}'
```

次に kj-atlas backend とログを確認します。

```bash
curl -fsS http://localhost:8080/api/healthz
docker compose logs api --tail=100
```

`/healthz` が通っても、LLM endpoint の疎通まで保証するわけではありません。AI 提案を実行し、provider error や timeout が出ないことも確認してください。

## 運用上の注意

- 入力に秘密情報、個人情報、未レビューの機密情報を含めないでください。共有してよい情報か迷う場合は [data_handling.md](data_handling.md) を確認します。
- SafeMode の目的を緩める設定変更は、[security.md](security.md) と [security_operational_guidelines.md](security_operational_guidelines.md) を確認してから行ってください。
- provider が不安定な場合は、まず `KJ_ATLAS_LLM_PROVIDER=none` に戻し、保存や表示などの基本操作が正常か確認します。
- local provider の接続先（endpoint）のログに prompt 全文が残る場合があります。ログの保管先と閲覧権限を確認してください。

## よくある失敗

| 症状 | 確認すること |
| --- | --- |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL is not set` | base URL が未設定です |
| provider timeout | local provider の接続先（endpoint）が起動しているか、応答が遅すぎないか |
| response missing text field | 接続先（endpoint）の応答が `{ "text": "..." }` になっているか |
| AI disabled | `KJ_ATLAS_LLM_PROVIDER=none` のままではないか |
| 401 または 403 | 接続先（endpoint）側の認証、proxy、ネットワーク制限 |

## large-scale との違い

large-scale provider は、明示 opt-in、昇格許可、allowlist がすべて必要です。local provider とは別の安全境界として扱います。

```bash
export KJ_ATLAS_LLM_PROVIDER=large-scale
export KJ_ATLAS_LLM_ESCALATION_ENABLED=true
export KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true
export KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST='llm.example.com'
```

large-scale provider を使う場合は、[configuration.md](configuration.md) と [security.md](security.md) を確認してください。

## 関連文書

- [configuration.md](configuration.md)
- [data_handling.md](data_handling.md)
- [security.md](security.md)
- [ce2_low_risk_ai_assist.md](ce2_low_risk_ai_assist.md)
