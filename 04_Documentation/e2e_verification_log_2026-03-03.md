# E2E Verification Log (2026-03-03)

目的: ADR-0019 の第一選択（Compose統合経路）を優先し、実行不能時は SQLite 代替経路の証跡と未確認リスク差分を明示する。

## 1) Compose統合経路（第一選択）

- Status: **Blocked**
- Blocker:
  - `docker` コマンドが環境に存在しない（`bash: command not found: docker`）。

実行コマンド:

```bash
docker compose version && docker --version
```

結果:

```text
bash: command not found: docker
```

## 2) SQLite代替経路（第二選択）

- Status: **Pass（代替確認）**
- Scope: health / docs roundtrip / Playwright smoke + 変更フロー

### 2.1 起動・ヘルス

```bash
cd 03_Implement/backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pip install alembic uvicorn
export PYTHONPATH=src
export DATABASE_URL='sqlite:///./kj_atlas.db'
alembic upgrade head
uvicorn kj_atlas_api.main:app --host 0.0.0.0 --port 8000

cd 03_Implement/frontend
npm ci
npm run dev -- --host 0.0.0.0 --port 4173

curl -fsS http://localhost:8000/healthz
curl -fsS http://localhost:4173/api/healthz
```

結果:

- `{"status":"ok"}`
- `{"status":"ok"}`

### 2.2 docs roundtrip

```bash
curl -fsS -X PUT http://localhost:8000/docs/doc-qa-compose-gap -H 'content-type: application/json' --data-binary @/tmp/doc_payload.json
curl -fsS http://localhost:8000/docs/doc-qa-compose-gap
```

結果要約:

- `put_id == get_id == doc-qa-compose-gap`
- `cards=1`, `title="qa roundtrip"`
- `roundtrip_match=True`

### 2.3 Playwright smoke + 変更フロー

実行コマンド:

```bash
cd 03_Implement/frontend
npx playwright install chromium
npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line
```

結果:

- 初回失敗（ブラウザ依存ライブラリ不足）:
  - `libatk-1.0.so.0: cannot open shared object file`
- 追加対応:

```bash
apt-get update
apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2t64 libpangocairo-1.0-0 libpango-1.0-0 libcairo2 libatspi2.0-0
```

- 再実行結果: `2 passed (7.9s)`
  - `smoke: locale query switches shell labels to English`
  - `locale=en keeps document replace flow behavior equivalent`

## 3) 未確認リスク差分（Compose未実施に伴うもの）

- R-01 PostgreSQL 固有差分（SQLiteでは再現しない型/制約/接続挙動）
- R-02 `web:80`（Nginx経由）での `/api` ルーティング差分
- R-03 Compose の `depends_on: service_healthy` 起動連鎖
- R-04 コンテナネットワーク（web↔api↔db）境界

## 4) 後続アクション（Compose復帰後）

1. `docker compose up --build -d`
2. `docker compose ps`
3. `curl -fsS http://localhost:8080/api/health`
4. `PUT /api/docs/{doc_id}` + `GET /api/docs/{doc_id}`
5. `npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line`

上記を実行し、本ログの R-01〜R-04 をクローズする。
