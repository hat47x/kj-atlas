# kj-atlas backend (Phase 1 MVP)


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
現行実装では `DocumentV1` のスナップショット保存/読込を提供します。

## API

- `GET /healthz`
- `GET /docs/{doc_id}`
- `PUT /docs/{doc_id}`

## Persistence

- テーブル: `documents(id TEXT PK, version INT, updated_at TEXT, payload_json TEXT)`
- `payload_json` に `DocumentV1` 全体(JSON文字列)を保存
- スキーマ管理は Alembic migration を利用

## Environment variables

- `KJ_ATLAS_DATABASE_URL`
  - 既定値: `sqlite:///./kj_atlas.db`
  - driverを省略したURL（例: `mysql://...`）と対応済みasync URLは、能力レジストリに記録した検証済み同期driverへ正規化して利用
  - 明示driverは検証済みの組合せだけを受理する。例としてMySQLは`mysql+pymysql`、SQL Serverは`mssql+pymssql`、Oracleは`oracle+oracledb`を使用し、未導入・未検証driverはengine生成前に拒否する
  - 正式対応はSQLite、PostgreSQL 16、MySQL 8.4、MariaDB 11.4、SQL Server 2022、CockroachDB 26.2.3、Oracle AI Database Free 23.26.2
  - 対応状況と昇格条件: `02_Architecture/database_portability.md`
- `KJ_ATLAS_LLM_PROVIDER`
  - 既定値: `none`
  - 値: `none | local | large-scale`（後方互換エイリアス: `local_http`, `external`）
- `KJ_ATLAS_LLM_FALLBACK_TO_NONE`
  - 既定値: `true`
  - `true` の場合、`local`/`large-scale` 呼び出し失敗時は `none` 退避として fail-closed（HTTP 501）

## Run

```bash
cd 03_Implement/backend
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy alembic pydantic pydantic-settings psycopg[binary]
export PYTHONPATH=src
export KJ_ATLAS_DATABASE_URL="sqlite:///./kj_atlas.db"
export KJ_ATLAS_LLM_PROVIDER="none"
alembic upgrade head
uvicorn kj_atlas_api.main:app --reload
```

PostgreSQL を使う場合は `KJ_ATLAS_DATABASE_URL` を PostgreSQL の URL に変更してください。

MySQL/MariaDBはoptional driverを導入し、single-tenant構成で使用します。

```bash
pip install -e ".[mysql]"
export KJ_ATLAS_DATABASE_URL="mysql+pymysql://user:password@localhost:3306/kj_atlas"
# MariaDB: mariadb+pymysql://user:password@localhost:3306/kj_atlas
alembic upgrade head
```

SQL Server 2022もoptional driverを導入し、single-tenant構成で使用します。接続先databaseは事前に作成してください。

```bash
pip install -e ".[mssql]"
export KJ_ATLAS_DATABASE_URL="mssql+pymssql://user:password@localhost:1433/kj_atlas"
alembic upgrade head
```

CockroachDB 26.2.3もoptional dialectを導入し、single-tenant構成で使用します。接続先databaseは事前に作成してください。

```bash
pip install -e ".[cockroachdb]"
export KJ_ATLAS_DATABASE_URL="cockroachdb+psycopg://user:password@localhost:26257/kj_atlas"
alembic upgrade head
```

`--insecure`はローカル試験専用です。本番ではCockroachDBのTLS構成と適切な`sslmode`を使用してください。

Oracle AI Database Free 23.26.2もThin modeのoptional driverを導入し、single-tenant構成で使用します。URLのpathはSIDとして解釈されるため、PDBへ接続するときは`service_name` query parameterを使用してください。

```bash
pip install -e ".[oracle]"
export KJ_ATLAS_DATABASE_URL="oracle+oracledb://user:password@localhost:1521?service_name=FREEPDB1"
alembic upgrade head
```

Oracle Database FreeにはCPU、RAM、ユーザーデータ量、同一論理環境内のinstance数に製品上限があります。本番採用前にOracleの現行ライセンス条件と必要editionを確認してください。

## Minimal backup / restore

`documents.payload_json`には`DocumentV1`全体をJSON snapshotとして保存しています。バックアップは取得だけで完了とせず、本番とは別のdatabase／schema／pathへ復元してDocument、判断ログ、schema revision、大容量本文を照合してください。

SQLite、PostgreSQL、MySQL、MariaDB、SQL Server、CockroachDB、Oracleの検証済み最小手順と中断条件は、公開運用正本の[`operations.md`「バックアップと隔離復元」](../../04_Documentation/operations.md#バックアップと隔離復元)を参照してください。製品別コマンドをこのREADMEへ重複記載しません。


## Tests

```bash
cd 03_Implement/backend
export PYTHONPATH=src
pytest
```

PostgreSQL roundtrip test を実行する場合:

```bash
export KJ_ATLAS_DATABASE_URL="postgresql+psycopg://kj_atlas:kj_atlas@localhost:5432/kj_atlas"
export KJ_ATLAS_RUN_PG_TESTS=1
alembic upgrade head
pytest -m postgres
```

tenant RLSの実地matrixは、migration所有者とは別のruntime roleで実行します。runtime roleには対象schemaの通常DML権限を付与し、superuser属性と`BYPASSRLS`を付与しないでください。同じ資格情報やRLSを迂回できるroleではテストが失敗します。

```bash
export KJ_ATLAS_DATABASE_URL="postgresql+psycopg://migration_owner:...@localhost:5432/kj_atlas"
export KJ_ATLAS_TEST_POSTGRES_RUNTIME_DATABASE_URL="postgresql+psycopg://kj_atlas_runtime:...@localhost:5432/kj_atlas"
export KJ_ATLAS_RUN_PG_RLS_TESTS=1
pytest -q tests/test_document_access_rls_postgres.py
```

Auth federation Level2（Mock SP/IdP）を実行する場合:

```bash
cd 03_Implement/backend
export PYTHONPATH=src
export KJ_ATLAS_LEVEL2_DIAG_DIR=.artifacts/auth-level2/legacy-federation
./scripts/run_auth_level2.sh
```

- provider profile fixtures: `tests/level2/fixtures/provider_profile_*.json`, `tests/federation/profiles/*.json`
- 差異再現観点: ヘッダー名 / claim名 / groups形式 / amr-acr有無
- 診断JSONは `KJ_ATLAS_LEVEL2_DIAG_DIR` を明示したときだけ出力する。通常の `pytest` は作業ツリーへ診断ファイルを書き込まない。

同じ統合ハーネスを直接実行する場合:

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
