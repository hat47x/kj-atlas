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
  - 既定値: `none`
  - 値: `none | local | large-scale`（後方互換エイリアス: `local_http`, `external`）
- `LLM_FALLBACK_TO_NONE`
  - 既定値: `true`
  - `true` の場合、`local`/`large-scale` 呼び出し失敗時は `none` 退避として fail-closed（HTTP 501）

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

## Minimal backup / restore

`documents.payload_json` に `DocumentV1` 全体を JSON スナップショットとして保存しています。

### SQLite

- DB ファイル場所（既定）: `03_Implement/backend/kj_atlas.db`（`DATABASE_URL=sqlite:///./kj_atlas.db` の場合）
- バックアップ: API 停止中にファイルをそのままコピー

```bash
cp 03_Implement/backend/kj_atlas.db 03_Implement/backend/kj_atlas.db.bak
```

- リストア: 退避しておいた `.bak` を元ファイル名へ戻す

```bash
cp 03_Implement/backend/kj_atlas.db.bak 03_Implement/backend/kj_atlas.db
```

### PostgreSQL

- バックアップ（最小例: custom format）

```bash
pg_dump -Fc "$DATABASE_URL" -f kj_atlas_pg.dump
```

- リストア（最小例）

```bash
pg_restore -d "$DATABASE_URL" --clean --if-exists kj_atlas_pg.dump
```


## Tests

```bash
cd 03_Implement/backend
export PYTHONPATH=src
pytest
```

PostgreSQL roundtrip test を実行する場合:

```bash
export DATABASE_URL="postgresql+psycopg://kj_atlas:kj_atlas@localhost:5432/kj_atlas"
export RUN_PG_TESTS=1
alembic upgrade head
pytest -m postgres
```


Auth Level2（Mock SP/IdP、境界変更PR向け）:

```bash
cd 03_Implement/backend
tests/scripts/run_auth_level2.sh
```

- provider profile fixture: `tests/federation/profiles/*.json`
- 失敗時ログ: `.artifacts/auth-level2/`


## LLM provider audit metadata

`/ai/*` エンドポイントでは、監査可能性のために以下の項目を構造化ログへ記録します。

- `provider` / `provider_kind`
- `model_id`
- `requested_at`（UTC ISO8601）
- `transport`
- `trace_id`
- `fallback_to_none`
