# 設定

このドキュメントは OSS 利用時に最低限必要な設定のみをまとめています。

## 基本方針（デフォルト挙動）

- `LLM_PROVIDER=none` が既定です。
- 既定のままでは外部 LLM への送信は行いません。
- ローカル/社内 LLM を使う場合のみ `local_http` を明示設定します。

## 必須/主要な環境変数

### `DATABASE_URL`

バックエンドの保存先 DB を指定します。

- 例（SQLite）: `sqlite:///./kj_atlas.db`
- 例（PostgreSQL）: `postgresql+asyncpg://<user>:<password>@<host>:5432/<db>`

### `LLM_PROVIDER`

使用する LLM Provider を選択します。

- `none`（既定）
- `local_http`
- `external`（将来向け。現状は未実装）

## `local_http` 設定（ローカル/社内 LLM）

`LLM_PROVIDER=local_http` を使う場合は、以下を設定します。

- `LOCAL_LLM_BASE_URL`（必須）
  - 例: `http://localhost:8001`
- `LOCAL_LLM_MODEL`（任意）
  - モデル名を渡したい場合に指定

実装上、`local_http` は `LOCAL_LLM_BASE_URL + /generate` へ POST します。

## Compose での設定方法

`03_Implement/deploy/docker-compose.yml` は環境変数の上書きに対応しています。
必要な値をシェルで export してから起動してください。

### 外部送信なし（既定運用）

```bash
cd 03_Implement/deploy
export DATABASE_URL='postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas'
export LLM_PROVIDER='none'
docker compose up -d
```

### ローカル/社内 LLM を使う場合

```bash
cd 03_Implement/deploy
export LLM_PROVIDER='local_http'
export LOCAL_LLM_BASE_URL='http://localhost:8001'
export LOCAL_LLM_MODEL='local-model-name'
docker compose up -d
```

## データの持ち出し/持ち込み

フロントエンドには JSON の Export / Import 機能があります。

- Export: 現在のドキュメント状態を JSON 保存
- Import: JSON を読み込み（バリデーション後に反映）

イントラ運用では、必要に応じてこの機能でドキュメントを移送できます。
