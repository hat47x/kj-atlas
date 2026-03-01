# 設定（OSS / イントラ・自前ホスト向け）

このドキュメントは、最小運用に必要な設定のみを記載します。

## 1. 基本方針（デフォルトは外部送信なし）

- `LLM_PROVIDER=none` が既定です。
- 既定のままでは外部LLMへのデータ送信は行いません。
- ローカル/社内LLMを使う場合のみ `LLM_PROVIDER=local_http` を明示設定します。

## 2. 主要環境変数

### `DATABASE_URL`

保存先DBを指定します。

- SQLite 例: `sqlite:///./kj_atlas.db`
- PostgreSQL 例: `postgresql+asyncpg://<user>:<password>@<host>:5432/<db>`

### `LLM_PROVIDER`

LLM連携方式を指定します。

- `none`（既定）
- `local_http`
- `external`（将来向け・現状未実装）



### `AUDIT_EXPORT_ENABLED` / `AUDIT_TRANSPORT`

閲覧/エクスポート監査イベントの外部送信を制御します。

- `AUDIT_EXPORT_ENABLED=false`（既定）: 監査外部送信を完全無効化（no-op）
- `AUDIT_EXPORT_ENABLED=true` + `AUDIT_TRANSPORT=noop`: 送信処理は有効だが外部送信はしない（疎通試験向け）
- `AUDIT_EXPORT_ENABLED=true` + `AUDIT_TRANSPORT=http`: `AUDIT_HTTP_ENDPOINT` へ POST 送信

補助設定:

- `AUDIT_HTTP_ENDPOINT`（`AUDIT_TRANSPORT=http` 時に必須）
- `AUDIT_HTTP_API_KEY`（任意、Bearer トークン）
- `AUDIT_HTTP_TIMEOUT_SECONDS`（既定 2.0）
- `AUDIT_QUEUE_SIZE`（既定 100、失敗時メモリキュー上限）
- `AUDIT_ALLOW_IN_SAFE_MODE`（既定 `false`。SafeMode時送信を許可する場合のみ `true`）

### `API_KEY`（任意）

簡易なAPI保護キーです。

- 未設定: 認証なし（既定動作）
- 設定時: `/healthz` 以外のAPIで `X-API-Key: <API_KEY>` を必須化

> 本機能はMVP向けの簡易ガードです。完全な認証/認可の代替ではありません。

## 3. `local_http` 設定（ローカル/社内LLM）

`LLM_PROVIDER=local_http` のときは以下を設定します。

- `LOCAL_LLM_BASE_URL`（必須）
  - 例: `http://localhost:8001`
- `LOCAL_LLM_MODEL`（任意）
  - 例: `local-model-name`

バックエンドは `LOCAL_LLM_BASE_URL + /generate` へ HTTP POST します。

## 4. Docker Composeでの設定例

`03_Implement/deploy/docker-compose.yml` では環境変数上書きが可能です。

### 既定（外部送信なし）

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export DATABASE_URL='postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas'
export LLM_PROVIDER='none'
docker compose up -d
```

### ローカル/社内LLMを利用

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export LLM_PROVIDER='local_http'
export LOCAL_LLM_BASE_URL='http://localhost:8001'
export LOCAL_LLM_MODEL='local-model-name'
docker compose up -d
```


### APIキーを有効化（任意）

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export API_KEY='change-me'
docker compose up -d
```

## 5. データ搬送（JSON Export / Import）

フロントエンドで JSON Export / Import を利用できます。

- Export: 現在ドキュメントを JSON 保存
- Import: JSON を読み込み、バリデーション後に反映

イントラ運用時の持ち出し可否や保管場所は、組織ルールで管理してください。

## セキュリティ設定

最小運用の保護策（リバースプロキシ/TLS、IP制限、Basic認証、API_KEY など）は
[security.md](./security.md) を参照してください。


## 6. フロントエンドi18n辞書契約（FB-RM-I18N-02）

翻訳辞書は `03_Implement/frontend/src/i18n/locales/*.json` を正本とします。

- フォーマット: `{"<message.key>": "<localized string>"}` の JSON object
- 値型: すべて string（`validateLocaleMessages` で検証）
- 解決順序: `requested locale -> default locale (ja) -> key literal`

この順序により、要求locale側でキー欠損があっても既定言語（ja）へ復元され、
ja側にも存在しないキーのみ最終的に key 文字列を返します。
