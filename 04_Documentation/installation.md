# インストール（Docker Compose）

この手順は、イントラネット/自前ホスト環境で `kj-atlas` を最小構成で起動するためのものです。

## 前提条件

- Docker Engine
- Docker Compose v2（`docker compose` コマンド）

## クイックスタート

1. リポジトリ直下へ移動します。

```bash
cd /path/to/kj-atlas
```

2. Compose を起動します。

```bash
cd 03_Implement/deploy
docker compose up --build -d
```

3. 起動確認を行います。

```bash
docker compose ps
docker compose logs api --tail=50
```

4. ブラウザで以下にアクセスします。

- `http://localhost:8080`

5. 停止する場合:

```bash
docker compose down
```

## 補足

- 既定では PostgreSQL を含む 3 サービス（`web` / `api` / `db`）が起動します。
- 既定設定では `LLM_PROVIDER=none` のため、データを外部 LLM へ送信しません。
- ドキュメントは画面から JSON Export / Import が可能です。
