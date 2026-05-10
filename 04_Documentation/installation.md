# Installation

対象読者: kj-atlas を初めてローカルまたは検証環境で起動する利用者、運用担当者。

目的: Docker Compose を使った標準起動手順と、Docker が使えない場合の最小代替手順を示します。

範囲外: 本番用の認証基盤、組織固有のネットワーク設定、秘密情報の配布手順。

## 前提

- Git
- Docker Engine
- Docker Compose v2 (`docker compose` コマンド)
- ブラウザ

Docker が使えない環境では、後述の「Docker を使わない最小起動」を使います。

## Docker Compose で起動する

1. リポジトリを取得します。

```bash
git clone https://github.com/hat47x/kj-atlas.git
cd kj-atlas
```

2. デプロイ用ディレクトリへ移動します。

```bash
cd 03_Implement/deploy
```

3. 初回ビルドを含めて起動します。

```bash
docker compose up --build -d
```

4. サービス状態を確認します。

```bash
docker compose ps
docker compose logs api --tail=50
```

5. ブラウザで開きます。

```text
http://localhost:8080
```

6. API のヘルスチェックを確認します。

```bash
curl -fsS http://localhost:8080/api/healthz
```

正常なら次の応答になります。

```json
{"status":"ok"}
```

## 停止する

```bash
cd 03_Implement/deploy
docker compose down
```

データベース volume も削除する場合だけ、次を使います。

```bash
docker compose down -v
```

## Docker を使わない最小起動

この手順は開発・検証向けです。本番運用の代替ではありません。

### Backend

```bash
cd 03_Implement/backend
python -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
pip install alembic uvicorn
export PYTHONPATH=src
export KJ_ATLAS_DATABASE_URL="sqlite:///./kj_atlas.db"
export KJ_ATLAS_LLM_PROVIDER="none"
alembic upgrade head
python -m uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8000
```

Windows PowerShell では環境変数を次のように設定します。

```powershell
$env:PYTHONPATH="src"
$env:KJ_ATLAS_DATABASE_URL="sqlite:///./kj_atlas.db"
$env:KJ_ATLAS_LLM_PROVIDER="none"
```

### Frontend

別の端末で実行します。

```bash
cd 03_Implement/frontend
npm install
npm run dev -- --host 127.0.0.1 --port 4173
```

ブラウザで開きます。

```text
http://127.0.0.1:4173
```

## 起動後の確認

- 画面が表示される。
- `curl -fsS http://localhost:8080/api/healthz` または `curl -fsS http://127.0.0.1:8000/healthz` が成功する。
- 新規ドキュメントを作成し、再読み込み後も内容が残る。
- 既定では `KJ_ATLAS_LLM_PROVIDER=none` のため、外部 LLM へ送信されない。

## よくある問題

### `docker: command not found`

Docker Engine と Docker Compose v2 をインストールしてください。Docker を使えない場合は「Docker を使わない最小起動」を使います。

### `port is already allocated`

`WEB_PORT` を変えて起動します。

```bash
WEB_PORT=8081 docker compose up --build -d
```

### API が 401 を返す

`KJ_ATLAS_API_KEY` を設定している環境では、`/healthz` 以外の API に `X-API-Key` ヘッダーが必要です。詳しくは [configuration.md](configuration.md) を参照してください。

## 関連文書

- [configuration.md](configuration.md)
- [operations.md](operations.md)
- [e2e_testing.md](e2e_testing.md)
- [security.md](security.md)
