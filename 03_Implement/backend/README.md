# kj-atlas backend (Phase 1 MVP)

Phase 1 では `DocumentV1` のスナップショット保存/読込のみを実装しています。

## API

- `GET /healthz`
- `GET /docs/{doc_id}`
- `PUT /docs/{doc_id}`

## Persistence

- テーブル: `documents(id TEXT PK, version INT, updated_at TEXT, payload_json TEXT)`
- `payload_json` に `DocumentV1` 全体(JSON文字列)を保存
- スキーマ管理は Alembic migration を利用

## Environment variables

- `DATABASE_URL`
  - 既定値: `sqlite:///./kj_atlas.db`
  - `sqlite+aiosqlite://...` / `postgresql+asyncpg://...` が与えられた場合は、Phase 1 の同期SQLAlchemy実装で扱えるよう内部で同期ドライバURLへ正規化して利用
- `LLM_PROVIDER`
  - 既定値: `none`（Phase 1では未使用だが設定としては保持）

## Run

```bash
cd 03_Implement/backend
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy alembic pydantic pydantic-settings psycopg[binary]
export PYTHONPATH=src
export DATABASE_URL="sqlite:///./kj_atlas.db"
export LLM_PROVIDER="none"
alembic upgrade head
uvicorn kj_atlas_api.main:app --reload
```

PostgreSQL を使う場合は `DATABASE_URL` を PostgreSQL の URL に変更してください。
