# Local LLM Operations Guide

対象読者: local LLM または組織内 LLM endpoint を kj-atlas に接続する運用担当者、開発者。

目的: local provider の設定、HTTP contract、確認方法、失敗時の切り分けを示します。

範囲外: 特定モデルの導入手順、外部 large-scale LLM の契約管理、秘密情報の配布。

読後にできること: 既定では LLM が無効であることを理解し、local LLM を有効にするときの設定、疎通確認、戻し方を判断できます。

## 既定値

kj-atlas は既定で LLM を使いません。

```bash
export KJ_ATLAS_LLM_PROVIDER=none
```

この状態では、AI 機能は disabled として扱われ、LLM 連携による外部サービスとの共有は行われません。最初の評価、受け入れ確認、保存動作の確認では、この既定値を推奨します。

## local LLM とは

この文書での local LLM は、kj-atlas から見て管理できる範囲にある LLM endpoint を指します。同じ PC 上のサービスとは限りません。組織内サーバーを使う場合もあります。

local という名前でも、URL が外部サービスを指していれば、そのサービスにデータを渡す扱いです。接続先、保持期間、入力データの扱いを確認してから有効にしてください。

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

## 運用手順（DOC-OPS-05）
1. 対象読者（Audience）と目的（Goal）を先に確認する。
2. 公開境界（Public boundary）を確認し、内部手順は公開文書へ直接書かない。
3. 実行後は関連文書の導線（Related links）と矛盾がないか確認する。

## 判断基準（DOC-OPS-05 品質ゲート）
- 可読性: 用語が定義済み語彙と一致し、読者の次アクションが明確であること。
- 検証可能性: 手順・確認コマンド・期待結果が対応していること。
- 保守性: 上流（00〜02）と矛盾せず、関連文書へ責務を分離していること。

## 失敗時対応
- 参照不整合、用語不一致、公開境界の曖昧化を検出した場合は更新を停止する。
- 自己修復は最大3回までとし、4回目相当は Hold として論点化する。
- Architecture/ADR 本体の変更が必要な場合は、この文書では確定せず提案に留める。
