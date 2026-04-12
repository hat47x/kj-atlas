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
- CE4運用では Phase 1〜6 を通じて API/CLI/GUI 同値性（同一query→同一bundleHash）と監査4点セットを維持する

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

- `KJ_ATLAS_DATABASE_URL`：
  - dev: `sqlite+aiosqlite:///./data/kj_atlas.db`
  - prod: `postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas`

- `KJ_ATLAS_LLM_PROVIDER`：`none | local | local_http | large-scale | large_scale | external`
- `KJ_ATLAS_CE4_EQUIVALENCE_MODE`：`equivalence_and_bundle_hash`（`equivalenceKey + bundleHash` AND 固定）
- `KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT`：`true`（dry-run副作用0強制）
- `KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS`：`true`（監査4イベント欠損を成功扱いしない）
- `KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK`：`true`（`sourceBundleHash=mock:<hash>` を許容）

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
      - KJ_ATLAS_DATABASE_URL=postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas
      - KJ_ATLAS_LLM_PROVIDER=none
      - KJ_ATLAS_CE4_EQUIVALENCE_MODE=equivalence_and_bundle_hash
      - KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT=true
      - KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS=true
      - KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK=true
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

## 5. CE4 API/CLI/監査統合デプロイ契約

### 5.1 同値性契約

- API/CLI/GUIは同一の canonical query から `equivalenceKey` を生成する。
- 同一 `equivalenceKey` の実行は同一 `bundleHash` を返す。
- Phase 1〜6 の全工程で、同値性判定は `equivalenceKey + bundleHash` のAND条件を維持する。
- 同値性定義を多義化する設定（複数判定モードの混在）は禁止。

### 5.2 監査4点セット契約

以下のイベントが 1トランザクションで揃っていることを成功条件とする。

1. `query`
2. `bundle`
3. `proposal`
4. `apply`

いずれか欠損した場合は成功扱いしない（fail-closed）。

### 5.3 dry-run 契約

- `apply --dry-run` は `sideEffect=none` を必須とする。
- `dryRun=true` の成功記録に `sideEffect=none` が無い場合は必ず失敗扱いとする。
- DB永続化、外部送信、review昇格を禁止する。
- 監査ログに `dryRun=true` と `sideEffect=none` の両方が存在しない場合は失敗扱い。

### 5.4 CE3依存切離し契約

- CE4 は CE3完了待ちで停止しない。
- `sourceBundleHash` は `mock:<hash>` 形式を受理し、同値性検証を継続する。

---

## 6. イントラ運用（想定）

- `web` と `api` は社内ネットワーク内に閉じる
- `KJ_ATLAS_LLM_PROVIDER=local` の場合、`KJ_ATLAS_LOCAL_LLM_BASE_URL` を社内URLに向ける
- 外部送信（external provider）は無効化をデフォルトにする

---

## 7. クラウドへの載せ替え方針

### 7.1 Cloud Run

- `web` は静的ホスティング（Cloud Storage + CDN）でもよい
- `api` を Cloud Run に載せる
- `db` は Cloud SQL（Postgres）など

### 7.2 低価格VM / 自前サーバ

- Composeをそのまま利用
- バックアップは `db` のスナップショット or `pg_dump`

---

## 8. フェイルセーフ停止条件（CE4）

以下を検知した場合、デプロイ承認を停止する。

1. 同値性定義の多義化
2. 監査ログ欠損成功扱い
3. safeMode後退要求（share/export保護緩和、未レビュー保護緩和）

---

## 9. 次に作るもの

- `03_Implement` の雛形（backend/frontend）
- CI（最低限：lint/test/build）
