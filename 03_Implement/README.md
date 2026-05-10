# 03_Implement run guide


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。

## 主要コマンド（本リポジトリ準拠）

| アクション | コマンド | 用途 |
|---|---|---|
| Frontend 開発サーバ | `cd 03_Implement/frontend && npm run dev` | UIのローカル確認 |
| Frontend 検証 | `cd 03_Implement/frontend && npm run typecheck && npm run test` | 型・単体テスト確認 |
| Backend 検証 | `cd 03_Implement/backend && ruff check src tests && pytest` | Lint・単体テスト確認 |
| E2E（UI変更時） | `cd 03_Implement/frontend && npx playwright test` | UIを含む結合確認 |
| 統合起動（推奨） | `cd 03_Implement/deploy && docker compose up --build` | web+api+db の統合動作確認 |

> 注: `pnpm` / `supabase` / `.kiro` 系コマンドは本リポジトリの標準手順ではありません。

## Build frontend and run full stack with Docker Compose

```bash
cd 03_Implement/deploy
docker compose up --build
```

This starts:

- `db` (PostgreSQL)
- `api` (FastAPI + Alembic migration on startup)
- `web` (Nginx serving frontend `dist` and proxying `/api` to `api`)

Open `http://localhost:8080`.

## Environment variables

Set values in shell env vars or `.env` in `03_Implement/deploy`.

- `WEB_PORT` (default: `8080`)
- `KJ_ATLAS_DATABASE_URL` (default: `postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas`)
- `KJ_ATLAS_LLM_PROVIDER` (default: `none`)
- `POSTGRES_DB` (default: `kj_atlas`)
- `POSTGRES_USER` (default: `kj_atlas`)
- `POSTGRES_PASSWORD` (default: `kj_atlas`)
- `VITE_API_BASE` (default: `/api`, current Docker Compose build arg)

Frontend source code also accepts `VITE_KJ_ATLAS_API_BASE` as the preferred API base key. The current Docker Compose path passes `VITE_API_BASE` to the Dockerfile, so use `VITE_API_BASE` for Compose builds unless the Docker build wiring is updated.

## Manual frontend build (optional)

```bash
cd 03_Implement/frontend
npm ci
npm run build
```

## Static publish artifact (index/assets/packs)

```bash
cd 03_Implement/frontend
npm ci
npm run publish:static -- \
  --document ./tests/fixtures/worker/doc.small.json \
  --out ../deploy/public \
  --pack-id public-main
```

Output:

- `03_Implement/deploy/public/index.html`
- `03_Implement/deploy/public/assets/*`
- `03_Implement/deploy/public/packs/*`

Serve with a static file server:

```bash
cd 03_Implement/deploy/public
python3 -m http.server 4173
```
