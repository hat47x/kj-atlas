# E2E Verification Log (2026-03-03)

> DOC-OPS-05 Classification: **Move internal**
> Audience: 内部QA/運用監査
> Goal: 日付付き検証ログを内部証跡として管理する。
> Public boundary: 04の恒久公開文書からは分離し、内部ログ置き場へ移管予定。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。


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

## 5) Compose復帰後アクションの再実行（本タスク: QA Lead運用確認）

- 実施日時: 2026-03-03（本セッション）
- 判定: **Blocked（環境制約）**

### 5.1 手順1) docker利用可否確認

実行コマンド:

```bash
docker --version && docker compose version
```

結果:

```text
bash: command not found: docker
```

判定:

- `docker` バイナリ未導入のため、Compose経路の後続手順（2)〜5) は実行不能。

### 5.2 手順2)〜5) の実行可否

| 手順 | コマンド/内容 | 状態 | 理由 |
|---|---|---|---|
| 2 | `docker compose up --build -d` | blocked | `docker` コマンド不在 |
| 3 | `docker compose ps` | blocked | 2) 未実行かつ `docker` コマンド不在 |
| 4 | health/docs roundtrip 再実行 | blocked | Composeスタック未起動（`web:8080` 不成立） |
| 5 | Playwright 再実行（Compose経路） | blocked | Compose経路未起動のため受入対象外 |

### 5.3 R-01〜R-04 判定（pass/fail/blocked）

| Risk | 状態 | 状態遷移理由 |
|---|---|---|
| R-01 PostgreSQL固有差分 | blocked（継続） | Compose + PostgreSQL 経路を起動できず、SQLite代替では同等確認不可 |
| R-02 web(Nginx)経由 `/api` 差分 | blocked（継続） | `web:80` コンテナ未起動のため `/api` rewrite/CORS を再検証不可 |
| R-03 Composeヘルス連鎖 | blocked（継続） | `docker compose ps` / `logs` を取得できず、`depends_on: service_healthy` 連鎖未観測 |
| R-04 Composeネットワーク境界 | blocked（継続） | web↔api↔db のコンテナ間接続試験を実施できない |

### 5.4 Blocked解除条件

1. 実行ホストに Docker Engine + Docker Compose v2 を導入する。
2. `docker --version` と `docker compose version` が成功することを確認する。
3. 本ログ「4) 後続アクション（Compose復帰後）」の5手順を順に再実行し、結果を追記する。
4. 5手順の結果に基づいて R-01〜R-04 を `pass` / `fail` に更新する（推測で `pass` 化しない）。
