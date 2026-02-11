# 03_Implement run guide

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
- `DATABASE_URL` (default: `postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas`)
- `LLM_PROVIDER` (default: `none`)
- `POSTGRES_DB` (default: `kj_atlas`)
- `POSTGRES_USER` (default: `kj_atlas`)
- `POSTGRES_PASSWORD` (default: `kj_atlas`)
- `VITE_API_BASE` (default: `/api`)

## Manual frontend build (optional)

```bash
cd 03_Implement/frontend
npm ci
npm run build
```
