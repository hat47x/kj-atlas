# 設定（OSS / イントラ・自前ホスト向け）

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部運用者・管理者
> Goal: 公開設定ガイドとして最小安全設定と確認手順を提供する。
> Public boundary: 実行可能な設定手順のみ公開し、内部判断メモ・組織固有運用は含めない。
> Non-goal: 未公開ネットワーク情報、内部承認フロー、組織固有の秘密管理手順の共有。
> Related: `02_Architecture/runtime_parameter_registry.md`, `04_Documentation/security.md`, `01_Plans/issues/issue-doc-ops-05-03-04doc-configuration.md`

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書は外部利用者向けに最小構成のみ記載します。

## 1. 基本方針（既定は外部送信なし）

- `KJ_ATLAS_LLM_PROVIDER=none` が既定です。
- 既定のままでは外部 LLM へのデータ送信は行いません。
- ローカル/社内 LLM を使う場合のみ `KJ_ATLAS_LLM_PROVIDER=local` を明示設定します。

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

- `KJ_ATLAS_AUDIT_EXPORT_ENABLED=false`（既定）: 監査外部送信を無効化
- `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true` + `KJ_ATLAS_AUDIT_TRANSPORT=noop`: 送信処理のみ有効（外部送信なし）
- `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true` + `KJ_ATLAS_AUDIT_TRANSPORT=http`: `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` へPOST送信

補助設定:

- `KJ_ATLAS_AUDIT_HTTP_ENDPOINT`（`http`利用時に必須）
- `KJ_ATLAS_AUDIT_HTTP_API_KEY`（任意、Bearerトークン）
- `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS`（既定 2.0）
- `KJ_ATLAS_AUDIT_QUEUE_SIZE`（既定 100）
- `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE`（既定 `false`。SafeMode時送信を許可する場合のみ `true`）

### `KJ_ATLAS_API_KEY`（任意）

簡易なAPI保護キーです。

- 未設定: 認証なし（既定動作）
- 設定時: `/healthz` 以外のAPIで `X-API-Key: <KJ_ATLAS_API_KEY>` を必須化

> 本機能はMVP向けの簡易ガードです。完全な認証/認可の代替ではありません。

## 3. `local` 設定（ローカル/社内LLM）

`KJ_ATLAS_LLM_PROVIDER=local` のときは以下を設定します。

- `KJ_ATLAS_LOCAL_LLM_BASE_URL`（必須）例: `http://localhost:8001`
- `KJ_ATLAS_LOCAL_LLM_MODEL`（任意）例: `local-model-name`

バックエンドは `KJ_ATLAS_LOCAL_LLM_BASE_URL + /generate` へ HTTP POST します。

## 4. Docker Composeでの設定例

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export KJ_ATLAS_DATABASE_URL='postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas'
export KJ_ATLAS_LLM_PROVIDER='none'
docker compose up -d
```

ローカル/社内LLMを利用する場合:

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export KJ_ATLAS_LLM_PROVIDER='local'
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
docker compose up -d
```

APIキーを有効化する場合:

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export KJ_ATLAS_API_KEY='change-me'
docker compose up -d
```

## 5. データ搬送（JSON Export / Import）

- Export: 現在ドキュメントをJSON保存
- Import: JSONを読み込み、バリデーション後に反映

イントラ運用時の持ち出し可否や保管場所は、組織ルールで管理してください。

## 6. 関連ドキュメント

- セキュリティ運用: `04_Documentation/security.md`
- インストール手順: `04_Documentation/installation.md`
- 実行パラメータ正本: `02_Architecture/runtime_parameter_registry.md`

## Go/No-Go gate（公開判定）

公開「Go」は次を満たす場合のみ:

1. Audience / Goal / Public boundary / Non-goal が明示されている。
2. 既定の安全設定（`KJ_ATLAS_LLM_PROVIDER=none`、監査外部送信OFF既定）が明記されている。
3. 追加/改名パラメータの正本が `02_Architecture/runtime_parameter_registry.md` であることを明記している。

いずれか未充足の場合は「No-Go」として公開更新を停止します。

## Stream D serial cycle（2026-04-21 / DOC-OPS-05-03 前半 docs-only）

### Phase 1 Read
- 本書と対応Issue（`issue-doc-ops-05-03-04doc-configuration.md`）を再読し、公開境界と `Classification=Improve external` を確認。
- 編集範囲を docs-only（本ファイルのみ）に固定し、担当外ファイルへ非接触で進行する。

### Phase 2 Plan（AC/DoD補完）
- AC:
  1. 既定安全値（`KJ_ATLAS_LLM_PROVIDER=none`、監査外部送信OFF既定）が明確であること。
  2. 環境変数の正本が `02_Architecture/runtime_parameter_registry.md` である導線が維持されること。
- DoD:
  1. Read → Plan → Execute → Verify → Proceed を記録すること。
  2. Verifyで docs-check を実施し、失敗時は3回以内の自己修復に限定すること。

### Phase 3 Execute
- 本節を追記し、Stream D 前半担当の実行証跡を追加。
- 変数仕様の新規決定は行わず、既存公開ガイドの責務（最小安全設定と確認手順）を維持。

### Phase 4 Verify（docs-check）
- `rg -n "DOC-OPS-05 Classification|Audience|Goal|Non-goal|Public boundary|Related|Go/No-Go|KJ_ATLAS_LLM_PROVIDER=none|Stream D serial cycle" 04_Documentation/configuration.md`
- `git diff --check`
- 自己修復は最大3回。4回目相当は停止して Hold。

### Phase 5 Proceed
- 判定: **Ready**
- 次アクション: 追加/改名パラメータ発生時は runtime parameter registry と同時同期する。


## DOC-OPS Track 1 serial execution（2026-04-22 / DOC-OPS-05-03）

### Phase 1 Read（同期）
- Read同期: `04_Documentation/configuration.md` と `issue-doc-ops-05-03-04doc-configuration.md` を再読。

### Phase 2 ADR/CDC
- Context: 公開設定ガイドとして安全既定と正本導線の一貫性が必要。
- Decision: Improve external を維持し、公開境界を厳守する。
- Consequences: 内部情報混入を抑制し、外部利用者の設定失敗を低減。

### Phase 3 Plan（AC/DoDドラフト→合意）
- AC draft: 安全既定・正本導線・Go/No-Go 条件の追跡可能性。
- DoD draft: 6Phase記録と docs-check 成功、失敗時3回自己修復上限。
- 合意: Issueメモで合意済み。

### Phase 4 Execute
- 本節を追記し、Issueとの整合運用を固定。

### Phase 5 Verify
- `rg -n "DOC-OPS Track 1 serial execution|Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed" 04_Documentation/configuration.md`

### Phase 6 Proceed
- Ready。docs-onlyで継続改善。
