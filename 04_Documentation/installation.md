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

## どの手順を選ぶか

| 状況 | 推奨手順 |
| --- | --- |
| 初めて試す、または評価環境で確認する | Docker Compose |
| backend や frontend を個別に編集しながら確認する | Docker を使わない最小起動 |
| 本番相当の構成を検証する | Docker Compose を起点に、組織の認証・監視・バックアップ方針を追加 |

Docker Compose は、必要な `web`、`api`、`db` をまとめて起動します。個別起動は中身を開発・調査するときに便利ですが、端末を2つ以上使い、DB や環境変数も自分で管理します。

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

`--build` は Docker image を作り直す指定、`-d` は裏側で起動し続ける指定です。初回や依存関係が変わった後は `--build` を付けます。

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
export KJ_ATLAS_DATABASE_URL="sqlite:///./kj_atlas.db"
export KJ_ATLAS_LLM_PROVIDER="none"
alembic upgrade head
python -m uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8000
```

Windows PowerShell では環境変数を次のように設定します。

```powershell
$env:KJ_ATLAS_DATABASE_URL="sqlite:///./kj_atlas.db"
$env:KJ_ATLAS_LLM_PROVIDER="none"
```

この手順では `pip install -e ".[test]"` によって backend package が開発用に登録されるため、Python の import path を個別に設定する必要はありません。

### Frontend

別の端末で実行します。

```bash
cd 03_Implement/frontend
npm ci
npm run dev -- --host 127.0.0.1 --port 4173
```

このリポジトリには `package-lock.json` があるため、通常は `npm ci` を使います。依存関係そのものを更新する場合だけ `npm install` を使います。

ブラウザで開きます。

```text
http://127.0.0.1:4173
```

## 起動後の確認

- 画面が表示される。
- `curl -fsS http://localhost:8080/api/healthz` または `curl -fsS http://127.0.0.1:8000/healthz` が成功する。
- 新規ドキュメントを作成し、再読み込み後も内容が残る。
- 既定では `KJ_ATLAS_LLM_PROVIDER=none` のため、外部 LLM にデータを渡さない。

画面が正常に開くと、次のように SafeMode、表示モード、共有と再現、キャンバス、右側の操作パネルが同じ画面内に表示されます。最初の確認では、サンプル文書または新規文書を使い、秘密情報や実データを入力しない状態で確認してください。

![起動後の標準画面](assets/screenshots/app-canvas-overview.png)

`curl` は HTTP の接続先が応答するか確認するコマンドです。`curl` が使えない場合は、ブラウザで `http://localhost:8080/api/healthz` を開いても確認できます。

## よくある問題

### `docker: command not found`

Docker Engine と Docker Compose v2 をインストールしてください。Docker を使えない場合は「Docker を使わない最小起動」を使います。

### `port is already allocated`

`KJ_ATLAS_WEB_PORT` を変えて起動します。

```bash
KJ_ATLAS_WEB_PORT=8081 docker compose up --build -d
```

### API が 401 を返す

`KJ_ATLAS_API_KEY` を設定している環境では、`/healthz` 以外の API に `X-API-Key` ヘッダーが必要です。詳しくは [configuration.md](configuration.md) を参照してください。

### 画面は開くが保存できない

まず API と DB を確認します。

```bash
cd 03_Implement/deploy
curl -fsS http://localhost:8080/api/healthz
docker compose logs api --tail=100
docker compose logs db --tail=100
```

API key を有効にしている場合は、ブラウザ側の API 呼び出しにもキー設定が必要です。

## 関連文書

- [configuration.md](configuration.md)
- [operations.md](operations.md)
- [e2e_testing.md](e2e_testing.md)
- [security.md](security.md)
