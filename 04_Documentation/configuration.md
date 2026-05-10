# Configuration

対象読者: kj-atlas を起動・運用する管理者、検証担当者。

目的: 安全な既定値、主要な環境変数、設定変更後の確認方法を示します。

範囲外: 組織固有の秘密管理、未公開ネットワーク情報、承認履歴。

## 基本方針

- すべての backend 実行時設定は `KJ_ATLAS_*` 接頭辞を使います。
- 接頭辞のない旧キーは使いません。
- 既定では LLM 連携は無効です。
- 外部送信や大規模 LLM は、明示的な opt-in と宛先 allowlist がある場合だけ有効にします。

## 最小設定

Docker Compose の既定値で起動する場合、通常は追加設定なしで動きます。明示するなら次を使います。

```bash
export KJ_ATLAS_LLM_PROVIDER=none
export KJ_ATLAS_DATABASE_URL='postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas'
```

ローカル SQLite で backend を直接起動する場合:

```bash
export KJ_ATLAS_DATABASE_URL='sqlite:///./kj_atlas.db'
export KJ_ATLAS_LLM_PROVIDER=none
```

## 主要な backend 環境変数

| 変数 | 既定値 | 用途 |
| --- | --- | --- |
| `KJ_ATLAS_DATABASE_URL` | `sqlite:///./kj_atlas.db` | backend が使う DB 接続先 |
| `KJ_ATLAS_LLM_PROVIDER` | `none` | `none`, `local`, `local_http`, `large-scale`, `large_scale`, `external` |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL` | 未設定 | local LLM の base URL |
| `KJ_ATLAS_LOCAL_LLM_MODEL` | 未設定 | local LLM に渡す model 名 |
| `KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL` | 未設定 | large-scale LLM の base URL |
| `KJ_ATLAS_LARGE_SCALE_LLM_MODEL` | 未設定 | large-scale LLM に渡す model 名 |
| `KJ_ATLAS_LLM_ESCALATION_ENABLED` | `false` | large-scale への昇格許可 |
| `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN` | `false` | large-scale 利用の明示 opt-in |
| `KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST` | 未設定 | large-scale 接続を許可するホスト名のカンマ区切り |
| `KJ_ATLAS_API_KEY` | 未設定 | `/healthz` 以外の API を `X-API-Key` で保護 |
| `KJ_ATLAS_AUDIT_EXPORT_ENABLED` | `false` | 監査イベントの外部送信を有効化 |
| `KJ_ATLAS_AUDIT_TRANSPORT` | `noop` | `noop` または `http` |
| `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` | 未設定 | audit HTTP 送信先 |
| `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS` | `2.0` | audit HTTP timeout |
| `KJ_ATLAS_AUDIT_QUEUE_SIZE` | `100` | audit queue 上限 |
| `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE` | `false` | SafeMode 中の audit 外部送信許可 |
| `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` | `noop` | access control adapter |
| `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` | `read_only` | access control 障害時の既定動作 |

## Frontend の API 接続先

frontend は `VITE_KJ_ATLAS_API_BASE` を優先し、未設定なら `VITE_API_BASE`、さらに未設定なら `/api` を使います。

```bash
export VITE_KJ_ATLAS_API_BASE=/api
```

Docker Compose の標準構成では nginx が `/api/` を backend の `:8000` に proxy するため、通常は変更不要です。

## API キーを有効にする

```bash
export KJ_ATLAS_API_KEY='change-me'
```

`/healthz` は API キーなしで確認できます。それ以外の API には次のヘッダーを付けます。

```bash
curl -H "X-API-Key: change-me" http://localhost:8080/api/docs/example
```

## local LLM を使う

local provider は `<base_url>/generate` に JSON を POST します。応答は `{ "text": "..." }` を返す必要があります。

```bash
export KJ_ATLAS_LLM_PROVIDER=local
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
```

## large-scale LLM を使う

large-scale provider は既定で無効です。利用する場合は、昇格許可、明示 opt-in、allowlist をすべて設定します。

```bash
export KJ_ATLAS_LLM_PROVIDER=large-scale
export KJ_ATLAS_LLM_ESCALATION_ENABLED=true
export KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true
export KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL='https://llm.example.com'
export KJ_ATLAS_LARGE_SCALE_LLM_MODEL='model-name'
export KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST='llm.example.com'
```

## 設定後の確認

```bash
curl -fsS http://localhost:8080/api/healthz
docker compose logs api --tail=100
```

直接 backend を起動している場合:

```bash
curl -fsS http://127.0.0.1:8000/healthz
```

## 関連文書

- [installation.md](installation.md)
- [security.md](security.md)
- [local_llm_ops_guide.md](local_llm_ops_guide.md)
- [runtime_parameter_registry.md](../02_Architecture/runtime_parameter_registry.md)
