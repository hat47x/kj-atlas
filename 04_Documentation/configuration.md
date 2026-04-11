# 設定（OSS / イントラ・自前ホスト向け）

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部運用者・管理者
> Goal: 公開設定ガイドとして最小安全設定と確認手順を提供する。
> Public boundary: 内部の意思決定メモは含めず、実行可能手順と正本参照のみ公開する。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。
> Non-goal: 組織固有の内部承認メモや未公開ネットワーク情報の共有。
> Outcome: 外部運用者が最小安全設定と確認手順を再現できる。
> Related: `02_Architecture/runtime_parameter_registry.md`, `04_Documentation/security.md`, `01_Plans/issues/issue-doc-ops-05-03-04doc-configuration.md`



> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
このドキュメントは、最小運用に必要な設定のみを記載します。

## 1. 基本方針（デフォルトは外部送信なし）

- `KJ_ATLAS_LLM_PROVIDER=none` が既定です。
- 既定のままでは外部LLMへのデータ送信は行いません。
- ローカル/社内LLMを使う場合のみ `KJ_ATLAS_LLM_PROVIDER=local` を明示設定します。

## 2. 主要環境変数

### `KJ_ATLAS_DATABASE_URL`

保存先DBを指定します。

- SQLite 例: `sqlite:///./kj_atlas.db`
- PostgreSQL 例: `postgresql+asyncpg://<user>:<password>@<host>:5432/<db>`

### `KJ_ATLAS_LLM_PROVIDER`

LLM連携方式を指定します。

- `none`（既定）
- `local`
- `external`（将来向け・現状未実装）



### `KJ_ATLAS_AUDIT_EXPORT_ENABLED` / `KJ_ATLAS_AUDIT_TRANSPORT`

閲覧/エクスポート監査イベントの外部送信を制御します。

- `KJ_ATLAS_AUDIT_EXPORT_ENABLED=false`（既定）: 監査外部送信を完全無効化（no-op）
- `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true` + `KJ_ATLAS_AUDIT_TRANSPORT=noop`: 送信処理は有効だが外部送信はしない（疎通試験向け）
- `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true` + `KJ_ATLAS_AUDIT_TRANSPORT=http`: `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` へ POST 送信

補助設定:

- `KJ_ATLAS_AUDIT_HTTP_ENDPOINT`（`KJ_ATLAS_AUDIT_TRANSPORT=http` 時に必須）
- `KJ_ATLAS_AUDIT_HTTP_API_KEY`（任意、Bearer トークン）
- `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS`（既定 2.0）
- `KJ_ATLAS_AUDIT_QUEUE_SIZE`（既定 100、失敗時メモリキュー上限）
- `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE`（既定 `false`。SafeMode時送信を許可する場合のみ `true`）

### `KJ_ATLAS_API_KEY`（任意）

簡易なAPI保護キーです。

- 未設定: 認証なし（既定動作）
- 設定時: `/healthz` 以外のAPIで `X-API-Key: <KJ_ATLAS_API_KEY>` を必須化

> 本機能はMVP向けの簡易ガードです。完全な認証/認可の代替ではありません。

## 3. `local` 設定（ローカル/社内LLM）

`KJ_ATLAS_LLM_PROVIDER=local` のときは以下を設定します。

- `KJ_ATLAS_LOCAL_LLM_BASE_URL`（必須）
  - 例: `http://localhost:8001`
- `KJ_ATLAS_LOCAL_LLM_MODEL`（任意）
  - 例: `local-model-name`

バックエンドは `KJ_ATLAS_LOCAL_LLM_BASE_URL + /generate` へ HTTP POST します。

## 4. Docker Composeでの設定例

`03_Implement/deploy/docker-compose.yml` では環境変数上書きが可能です。

### 既定（外部送信なし）

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export KJ_ATLAS_DATABASE_URL='postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas'
export KJ_ATLAS_LLM_PROVIDER='none'
docker compose up -d
```

### ローカル/社内LLMを利用

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export KJ_ATLAS_LLM_PROVIDER='local'
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
docker compose up -d
```


### APIキーを有効化（任意）

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export KJ_ATLAS_API_KEY='change-me'
docker compose up -d
```

## 5. データ搬送（JSON Export / Import）

フロントエンドで JSON Export / Import を利用できます。

- Export: 現在ドキュメントを JSON 保存
- Import: JSON を読み込み、バリデーション後に反映

イントラ運用時の持ち出し可否や保管場所は、組織ルールで管理してください。

## セキュリティ設定

最小運用の保護策（リバースプロキシ/TLS、IP制限、Basic認証、KJ_ATLAS_API_KEY など）は
[security.md](./security.md) を参照してください。


## 6. フロントエンドi18n辞書契約（FB-RM-I18N-02）

翻訳辞書は `03_Implement/frontend/src/i18n/locales/*.json` を正本とします。

- フォーマット: `{"<message.key>": "<localized string>"}` の JSON object
- 値型: すべて string（`validateLocaleMessages` で検証）
- 解決順序: `requested locale -> default locale (ja) -> key literal`

この順序により、要求locale側でキー欠損があっても既定言語（ja）へ復元され、
ja側にも存在しないキーのみ最終的に key 文字列を返します。

i18n表示差分を追加する場合は、UIコンポーネントの生文字列を直接変更せず、
`src/i18n/locales/ja.json` と `src/i18n/locales/en.json` に同一キーを追加して
`t("...")` 経由で参照してください（例: `search_bar.*`）。
