# デプロイ方針と Docker Compose


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
本ドキュメントは、kj-atlas を **多様な環境（ローカル／クラウド／イントラ）** で動かすための
デプロイ方針と、最小の Docker Compose 構成案を定義します。

---

## 1. 基本方針

- 最優先の配布形態は **Docker Compose**
- クラウドは「Composeで動く構成」をベースに載せ替える
- DBは本番で PostgreSQL を推奨
- ローカル開発は SQLite で完結できる

---

## 2. コンテナ構成（MVP）

MVPでは、以下の3要素で十分です。

- `web`：静的配信（ビルド済みフロントを配る）
- `api`：FastAPI
- `db`：PostgreSQL（本番想定）

ローカルのみの開発では `db` を省略して SQLite にしてもよい。

---

## 3. 環境変数（例）

### 3.1 API

- `DATABASE_URL`：
  - dev: `sqlite+aiosqlite:///./data/kj_atlas.db`
  - prod: `postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas`

- `LLM_PROVIDER`：`none | fixture | local | external`

### 3.2 DB

- `POSTGRES_DB=kj_atlas`
- `POSTGRES_USER=kj_atlas`
- `POSTGRES_PASSWORD=kj_atlas`

---

## 4. docker-compose.yml（案）

> 注：ここはアーキテクチャ文書のため、厳密なパスは実装で調整する。

```yaml
version: "3.9"

services:
  web:
    image: nginx:alpine
    depends_on:
      - api
    ports:
      - "8080:80"
    volumes:
      - ./dist:/usr/share/nginx/html:ro
      - ./deploy/nginx.conf:/etc/nginx/conf.d/default.conf:ro

  api:
    build:
      context: ./03_Implement/backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas
      - LLM_PROVIDER=none
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=kj_atlas
      - POSTGRES_USER=kj_atlas
      - POSTGRES_PASSWORD=kj_atlas
    ports:
      - "5432:5432"
    volumes:
      - kj_atlas_pgdata:/var/lib/postgresql/data

volumes:
  kj_atlas_pgdata:
```

---

## 5. イントラ運用（想定）

- `web` と `api` は社内ネットワーク内に閉じる
- `LLM_PROVIDER=local` の場合、`LOCAL_LLM_BASE_URL` を社内URLに向ける
- 外部送信（external provider）は無効化をデフォルトにする

---

## 6. クラウドへの載せ替え方針

### 6.1 Cloud Run

- `web` は静的ホスティング（Cloud Storage + CDN）でもよい
- `api` を Cloud Run に載せる
- `db` は Cloud SQL（Postgres）など

### 6.2 低価格VM / 自前サーバ

- Composeをそのまま利用
- バックアップは `db` のスナップショット or `pg_dump`

---

## 7. 次に作るもの

- `03_Implement` の雛形（backend/frontend）
- CI（最低限：lint/test/build）

