# インストール（Docker Compose / イントラ向け最小手順）

> DOC-OPS-05 Classification: **Improve external**
> Audience: 初回導入者・運用担当者
> Goal: 最小インストールと疎通確認を公開ガイドとして提供する。
> Public boundary: 内部環境依存の作業メモは除外し、標準手順に限定する。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。
> Non-goal: 組織内限定の配布手順や未公開運用ノートの共有。
> Outcome: 初回導入者が最小起動・疎通・停止を再現できる。
> Related: `03_Implement/deploy/docker-compose.yml`, `04_Documentation/e2e_testing.md`, `01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`



> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
この手順は、`kj-atlas` をイントラネット・自前ホスト環境で最小構成起動するためのものです。

## 前提条件

- Docker Engine
- Docker Compose v2（`docker compose` コマンド）

## クイックスタート

1. リポジトリへ移動します。

```bash
cd /path/to/kj-atlas/03_Implement/deploy
```

2. 起動します（初回はビルドあり）。

```bash
docker compose up --build -d
```

3. 稼働確認を行います。

```bash
docker compose ps
docker compose logs api --tail=50
```

4. ブラウザで確認します。

- `http://localhost:8080`

5. 停止する場合。

```bash
docker compose down
```

## 補足

- 既定で `web` / `api` / `db`（PostgreSQL）の3サービスが起動します。
- 既定値は `KJ_ATLAS_LLM_PROVIDER=none` で、外部LLMへの送信は行いません。
- 画面から JSON Export / Import が利用できます。


## API/DB連動を含むE2E確認（推奨チェック）

Compose起動後、最低限次を確認してください。

```bash
cd /path/to/kj-atlas/03_Implement/deploy
docker compose ps
docker compose logs api --tail=100
curl -fsS http://localhost:8080/api/health
curl -fsS -X PUT http://localhost:8080/api/docs/<doc_id> -H 'content-type: application/json' --data-binary @/tmp/e2e_doc.json
curl -fsS http://localhost:8080/api/docs/<doc_id>

cd /path/to/kj-atlas/03_Implement/frontend
npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line
```

確認ポイント:
- `db` が `healthy` になっている
- `api` ログで `alembic upgrade head` が成功している
- `curl` が HTTP 200 を返す
- `http://localhost:8080` で画面が表示され、保存/読込など主要操作が1往復できる
- Playwright の smoke + 変更フロー（document replace）が通る
- E2E詳細手順の正本は `04_Documentation/e2e_testing.md` です。コマンド/受入基準は同書と一致させて運用してください。

## Docker未導入時の代替E2E手順（SQLite）

Dockerが使えない環境では、以下の2プロセス起動で `web + api + db(SQLite)` を代替できます。

1. API（SQLite）

```bash
cd /path/to/kj-atlas/03_Implement/backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pip install alembic uvicorn
export PYTHONPATH=src
export KJ_ATLAS_DATABASE_URL="sqlite:///./kj_atlas.db"
alembic upgrade head
uvicorn kj_atlas_api.main:app --host 0.0.0.0 --port 8000
```

2. Frontend（別ターミナル）

```bash
cd /path/to/kj-atlas/03_Implement/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 4173
```

3. 連動確認

```bash
curl -fsS http://localhost:8000/healthz
curl -fsS http://localhost:4173/api/healthz
curl -fsS -X PUT http://localhost:8000/docs/<doc_id> -H 'content-type: application/json' --data-binary @/tmp/e2e_doc.json
curl -fsS http://localhost:8000/docs/<doc_id>

cd /path/to/kj-atlas/03_Implement/frontend
npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line
```

必要に応じて `PUT /docs/{doc_id}` と `GET /docs/{doc_id}` を往復し、SQLite永続化を確認してください。

## トラブルシュート（環境要因）

### `docker: command not found`

Docker Engine / Docker Compose が未導入です。
- Linux: Docker Engine + Compose Plugin を導入
- macOS/Windows: Docker Desktop を導入

ただし、導入前でも本書の「Docker未導入時の代替E2E手順（SQLite）」で連動確認は可能です。
PRには実施手順と結果を必ず記載してください。

## Go/No-Go gate（公開判定）

公開「Go」は次を満たす場合のみ:

1. Audience / Goal / Non-goal / Public boundary / Outcome / Related が明示されている。
2. 初回導入者向けに最小手順（起動・疎通・停止）が再現可能な順序で記載されている。
3. 詳細E2Eの正本が `04_Documentation/e2e_testing.md` である導線が維持されている。

いずれか未充足の場合は「No-Go」として公開更新を停止します。

## DOC-OPS-05 実行記録（Phase 1〜5）

### Phase 1 Read

- Latest Read: 2026-04-13
- Audience / Goal / Public boundary / Related を確認し、公開境界を再確認。

### Phase 2 Plan

- Latest Read: 2026-04-13
- 本文は docs-only の範囲で更新し、仕様正本（00〜02）を上書きしない方針を固定。

### Phase 3 Execute

- Latest Read: 2026-04-13
- DOC-OPS-05 classification に沿って本文の公開メタと導線を整備。

### Phase 4 Verify

- Latest Read: 2026-04-13
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/installation.md`
- `git diff --check`

### Phase 5 Proceed

- Latest Read: 2026-04-13
- 状態: **Ready**
- 次アクション: 初回導入者向けの最小手順（起動・疎通・停止）を維持し、組織固有手順は含めない。


## Stream G docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **CDC**: Context / Decision / Consequences を明文化し、分類結果（Move internal / Improve external）を固定する。
3. **Plan**: AC/DoD を先に定義し、docs-only スコープ（`03_Implement/**` 非変更）を明示する。
4. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
5. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
6. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。
