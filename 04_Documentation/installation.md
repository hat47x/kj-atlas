# インストール（Docker Compose / イントラ向け最小手順）

この手順は、`kj-atlas` をイントラネット・自前ホスト環境で最小構成起動するためのものです。

## 前提条件

- Docker Engine
- Docker Compose v2（`docker compose` コマンド）

## クイックスタート

1. リポジトリへ移動します。

```bash
cd /path/to/kj-atlas/03_Implement/deploy
```

2. 起動します（初回はビルドあり）。

```bash
docker compose up --build -d
```

3. 稼働確認を行います。

```bash
docker compose ps
docker compose logs api --tail=50
```

4. ブラウザで確認します。

- `http://localhost:8080`

5. 停止する場合。

```bash
docker compose down
```

## 補足

- 既定で `web` / `api` / `db`（PostgreSQL）の3サービスが起動します。
- 既定値は `LLM_PROVIDER=none` で、外部LLMへの送信は行いません。
- 画面から JSON Export / Import が利用できます。
