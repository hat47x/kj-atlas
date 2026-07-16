# Deployment Policy And Docker Compose

> 環境変数・実行時パラメータの正本は `02_Architecture/runtime_parameter_registry.md` です。本書ではデプロイ構成の考え方だけを説明し、設定キーの追加・変更は必ず正本と同時に行います。

## 基本方針

- 標準の評価・検証構成は Docker Compose です。
- Compose は `web`、`api`、`db` の3サービスで構成します。
- 利用者が設定する環境変数は、例外なく `KJ_ATLAS_` で始めます。
- サードパーティコンテナや build tool が内部的に別名を要求する場合でも、公開設定キーは `KJ_ATLAS_*` だけにします。
- 本番相当の構成では、Compose を起点に組織の認証、監視、バックアップ、秘密管理を追加します。

サードパーティイメージが要求する変数名は、`01_Plans/adr/ADR-0029-third-party-runtime-env-boundary.md` に基づく private adapter 名として扱います。運用者が設定する値は `KJ_ATLAS_*` だけです。

環境別の推奨値は [runtime_parameter_registry.md](runtime_parameter_registry.md) の `Runtime profiles` を参照します。ローカル開発、評価、企業・行政の本番相当では、同じキーでも推奨値や確認事項が異なります。

## 標準構成

| Service | 役割 |
| --- | --- |
| `web` | build 済み frontend を Nginx で配信し、`/api` を backend へ proxy する |
| `api` | FastAPI backend と Alembic migration を実行する |
| `db` | PostgreSQL を提供する |

ローカル開発だけで確認する場合は、`db` を省略して SQLite を使えます。

## 公開設定キー

Compose と frontend build で利用者が設定する公開キーは次です。

| Key | Default | Purpose |
| --- | --- | --- |
| `KJ_ATLAS_RUNTIME_PROFILE` | `evaluation` | backend実行profile。現行Composeは評価用途を既定とし、`saas-multitenant`は起動拒否。 |
| `KJ_ATLAS_WEB_PORT` | `8080` | `web` の公開 port |
| `KJ_ATLAS_POSTGRES_DB` | `kj_atlas` | Compose PostgreSQL の database 名 |
| `KJ_ATLAS_POSTGRES_USER` | `kj_atlas` | Compose PostgreSQL の user 名 |
| `KJ_ATLAS_POSTGRES_PASSWORD` | `kj_atlas` | Compose PostgreSQL の password |
| `KJ_ATLAS_FRONTEND_API_BASE` | `/api` | frontend build 時に埋め込む API base path（`/` 始まりのみ許可。不正値は `/api` へフォールバック） |
| `KJ_ATLAS_DATABASE_URL` | Compose では PostgreSQL 接続先 | backend が使う DB 接続先 |
| `KJ_ATLAS_LLM_PROVIDER` | `none` | LLM provider |

全量の backend runtime key は [runtime_parameter_registry.md](runtime_parameter_registry.md) を参照します。


## Registry / Deploy alignment matrix

`runtime_parameter_registry.md` を基準に、deploy 面で次を固定します。

| Public key | Compose mapping | 備考 |
| --- | --- | --- |
| `KJ_ATLAS_RUNTIME_PROFILE` | `api.environment.KJ_ATLAS_RUNTIME_PROFILE` | backend profile selector |
| `KJ_ATLAS_WEB_PORT` | `web.ports` | web 公開ポート |
| `KJ_ATLAS_POSTGRES_DB` | `db.environment.POSTGRES_DB` | third-party private adapter への内部写像 |
| `KJ_ATLAS_POSTGRES_USER` | `db.environment.POSTGRES_USER` | third-party private adapter への内部写像 |
| `KJ_ATLAS_POSTGRES_PASSWORD` | `db.environment.POSTGRES_PASSWORD` | third-party private adapter への内部写像 |
| `KJ_ATLAS_FRONTEND_API_BASE` | `web.build.args.KJ_ATLAS_FRONTEND_API_BASE` | `/` 始まり path のみ許可 |
| `KJ_ATLAS_DATABASE_URL` | `api.environment.KJ_ATLAS_DATABASE_URL` | backend DB 接続先 |
| `KJ_ATLAS_LLM_PROVIDER` | `api.environment.KJ_ATLAS_LLM_PROVIDER` | provider 切替 |

運用者が設定する公開キーは `KJ_ATLAS_*` のみとし、`POSTGRES_*` は Compose 内部で完結する private adapter 名として扱います。

## Docker Compose の設定例

利用者が値を変える場合は、次のように `KJ_ATLAS_*` だけを設定します。

```bash
export KJ_ATLAS_WEB_PORT=8080
export KJ_ATLAS_POSTGRES_DB=kj_atlas
export KJ_ATLAS_POSTGRES_USER=kj_atlas
export KJ_ATLAS_POSTGRES_PASSWORD=kj_atlas
export KJ_ATLAS_FRONTEND_API_BASE=/api
export KJ_ATLAS_LLM_PROVIDER=none
```

DB 名、user、password を既定値から変える場合は、backend の接続先も同じ値に合わせます。

```bash
export KJ_ATLAS_DATABASE_URL='postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas'
```

## CE4 契約

- API/CLI/GUI は同じ canonical query から `equivalenceKey` を生成します。
- 同じ `equivalenceKey` の実行は同じ `bundleHash` を返します。
- 同値性判定は `equivalenceKey + bundleHash` の AND 条件を維持します。
- `apply --dry-run` は `sideEffect=none` を必須にし、副作用を起こしません。
- query、bundle、proposal、apply の audit event が欠ける場合は成功扱いにしません。

関連設定:

- `KJ_ATLAS_CE4_EQUIVALENCE_MODE`
- `KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT`
- `KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS`
- `KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK`
- `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS`

## 運用境界

- `web` と `api` は同一 Compose network 内で通信します。
- 既定では `KJ_ATLAS_LLM_PROVIDER=none` とし、外部 LLM にデータを渡しません。
- local LLM を使う場合は `KJ_ATLAS_LOCAL_LLM_BASE_URL` を管理できる接続先（endpoint）に向けます。
- large-scale LLM を使う場合は、明示 opt-in、昇格許可、allowlist をすべて設定します。
- access control を外部 PDP に委譲する場合は、接続先（endpoint）、timeout、fail-safe を同時に確認します。

## Cloud への載せ替え

- `web` は静的 hosting や CDN に置き換えられます。
- `api` は container 実行環境に載せ替えられます。
- `db` は managed PostgreSQL に置き換えられます。
- どの構成でも、公開設定キーは `KJ_ATLAS_*` だけを使います。

## 変更時のルール

1. 設定キーを追加・改名・削除する場合は、先に `runtime_parameter_registry.md` を更新します。
2. 実装、Compose、04 文書、release 手順を同じ PR で同期します。
3. 旧キーや互換キーを公開設定として残しません。
4. SafeMode、share/export、外部サービスとの共有の安全境界を緩める変更は ADR で判断します。
