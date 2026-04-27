# インストール（Docker Compose / イントラ向け最小手順）

> DOC-OPS-05 Classification: **Improve external**
> Audience: 初回導入者・運用担当者
> Goal: 最小インストールと疎通確認の公開手順を提供する。
> Public boundary: 標準導入手順のみ公開し、組織固有の内部運用メモは含めない。
> Non-goal: 社内限定の承認手順、未公開配布手順、個別環境の秘密情報共有。
> Related: `03_Implement/deploy/docker-compose.yml`, `04_Documentation/e2e_testing.md`, `01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書は外部導入者向けの最小手順に限定します。

## 前提条件

- Docker Engine
- Docker Compose v2（`docker compose` コマンド）

## クイックスタート

1. 配置ディレクトリへ移動します。

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

5. 停止します。

```bash
docker compose down
```

## API/DB連動を含む最小確認（推奨）

Compose起動後、最低限次を確認してください。

```bash
cd /path/to/kj-atlas/03_Implement/deploy
docker compose ps
curl -fsS http://localhost:8080/api/health
curl -fsS -X PUT http://localhost:8080/api/docs/<doc_id> -H 'content-type: application/json' --data-binary @/tmp/e2e_doc.json
curl -fsS http://localhost:8080/api/docs/<doc_id>
```

確認ポイント:

- `db` が `healthy` になっている
- `curl` がHTTP 200を返す
- `http://localhost:8080` で画面表示と保存/読込の往復ができる

詳細E2E（Playwright含む）の正本は `04_Documentation/e2e_testing.md` です。

## Docker未導入時の代替確認（SQLite）

Dockerが使えない環境では、`web + api + db(SQLite)` の2プロセス構成で代替確認できます。

1. API（SQLite）

```bash
cd /path/to/kj-atlas/03_Implement/backend
python -m venv .venv
source .venv/bin/activate
pip install -e "[test]"
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
```

## トラブルシュート

### `docker: command not found`

Docker未導入です。Docker Engine + Compose を導入するか、上記のSQLite代替手順を実施してください。

## Go/No-Go gate（公開判定）

公開「Go」は次を満たす場合のみ:

1. Audience / Goal / Public boundary / Non-goal が明示されている。
2. 初回導入者向け最小手順（起動・疎通・停止）が再現可能な順序で記載されている。
3. 詳細E2E正本（`04_Documentation/e2e_testing.md`）への導線が維持されている。

いずれか未充足の場合は「No-Go」として公開更新を停止します。

## Stream D serial cycle（2026-04-21 / DOC-OPS-05-08 前半 docs-only）

### Phase 1 Read
- 本書と対応Issue（`issue-doc-ops-05-08-04doc-installation.md`）を再読し、`Classification=Improve external` を確認。
- 編集境界を docs-only（`04_Documentation/installation.md` のみ）に固定し、`01_Plans/**`・`02_Architecture/**`・`03_Implement/**` 非編集を確認。

### Phase 2 Plan（AC/DoD補完）
- AC:
  1. Audience / Goal / Non-goal / Public boundary / Related / Go/No-Go が追跡可能であること。
  2. Compose手順と Docker未導入時の代替手順（SQLite）が共存し、導線が明確であること。
- DoD:
  1. Read → Plan → Execute → Verify → Proceed の5Phaseを記録すること。
  2. Verifyを docs-check で実施し、自己修復は最大3回までとすること。

### Phase 3 Execute
- 本節を追記し、前半担当（Stream D）の実行記録を追加。
- 既存の導入手順・公開境界・安全既定（内部情報非掲載）を維持し、仕様や実装の新規決定は行わない。

### Phase 4 Verify（docs-check）
- `rg -n "DOC-OPS-05 Classification|Audience|Goal|Non-goal|Public boundary|Related|Go/No-Go|Stream D serial cycle" 04_Documentation/installation.md`
- `git diff --check`
- 失敗時は原因を1点ずつ修正し、再実行は最大3回まで。超過時は Hold。

### Phase 5 Proceed
- 判定: **Ready**
- 次アクション: Compose系手順に変更が入る場合は、`04_Documentation/e2e_testing.md` の導線整合を同時確認する。


## DOC-OPS Track 1 serial execution（2026-04-22 / DOC-OPS-05-08）

### Phase 1 Read（同期）
- Read同期: `04_Documentation/installation.md` と `issue-doc-ops-05-08-04doc-installation.md` を再読。

### Phase 2 ADR/CDC
- Context: 公開導入文書として最小導入と代替導入の再現性が必要。
- Decision: Improve external を維持し、導線を簡潔化する。
- Consequences: 初回導入者の失敗点を減らし、検証導線を維持できる。

### Phase 3 Plan（AC/DoDドラフト→合意）
- AC draft: 最小手順・代替手順・E2E正本導線の維持。
- DoD draft: 6Phase記録と docs-check、自己修復3回上限。
- 合意: Issueメモで合意済み。

### Phase 4 Execute
- 本節を追記し、Issueと本文の同期証跡を固定。

### Phase 5 Verify
- `rg -n "DOC-OPS Track 1 serial execution|Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed" 04_Documentation/installation.md`

### Phase 6 Proceed
- Ready。公開導入手順を継続保守。


## DOC-OPS Track 4 serial cycle（2026-04-22 / DOC-OPS-05-08）

### Phase 1 Read
- `AGENTS.md` Read Order、`ADR-0019`、対応Issue（`issue-doc-ops-05-08-04doc-installation.md`）を再読。
- Classification **Improve external** と公開導入文書の目的（最小導入 + 代替導入）を確認。

### Phase 2 Plan
- AC固定: Audience/Goal/Public boundary/Non-goal を維持し、Compose/SQLiteの両導線を再現可能順で保持。
- フェイルセーフ: docs-check失敗時は3回まで修復し、4回目相当はHold。

### Phase 3 Execute
- 本Trackの実行記録を追記し、既存の手順本文は仕様変更せず維持。
- 公開境界（秘密情報・内部承認ログを含めない）を再確認。

### Phase 4 Verify
- `rg -n "DOC-OPS Track 4 serial cycle|Improve external|Compose|SQLite|Go/No-Go" 04_Documentation/installation.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**
- 次アクション: Composeコマンド変更時は `04_Documentation/e2e_testing.md` との同期を同一差分で確認。

## Stream I strict serial execution（2026-04-26 / DOC-OPS-05-08）

### Phase 1 Read
- 対象再読: `04_Documentation/installation.md` と `issue-doc-ops-05-08-04doc-installation.md`。
- 直列前提: DOC-OPS-05-03 完了（Ready）後に着手。

### Phase 2 ADR/CDC
- Context: 公開導入ガイドとして最小導入手順と公開境界の両立が必要。
- Decision: **Improve external** を維持し、内部運用情報は追加しない。
- Consequences: 導入再現性を維持しつつ、詳細検証は `04_Documentation/e2e_testing.md` 導線へ委譲。

### Phase 3 Plan
- Scope: 本文書の直列実行ログ追記とIssue整合。
- Non-goals: 手順仕様の拡張、実装変更、指定外ファイル変更。
- AC: Audience/Goal/Public boundary/Non-goal/Go-NoGo が追跡可能。
- DoD: Phase 1〜6記録、docs-check成功、指定外差分0。
- Validation: `rg` + `git diff --check`。
- Stop conditions: 修復4回目相当 / Requirement meta I/F矛盾 / 指定外編集必要化。

### Phase 4 Execute
- 実施: Stream I の実行記録を追記。
- 維持: Compose手順・SQLite代替手順・Go/No-Go構造。

### Phase 5 Verify
- 実行: `rg -n "Stream I strict serial execution|Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed" 04_Documentation/installation.md`
- 実行: `git diff --check`
- 自己修復: 最大3回、4回目相当で停止。

### Phase 6 Proceed
- 判定: **Ready**
- 次アクション: docs-only PRへ進行。


## Stream G mini-Phase serial run（2026-04-27）

### Phase 1 Read
- 対応Issue（`DOC-OPS-05-08`）と本書の分類ヘッダを再読し、公開境界を確認。

### Phase 2 Plan
- 変更責務を docs-only の記録同期に限定し、本文の分類（Move internal / Improve external）を維持。
- 共通ACテンプレ（Scope固定 / 境界明示 / GoNoGo / docs-check / 3回上限）を適用。

### Phase 3 Execute
- 本節を追記し、Read→Plan→Execute→Verify→Proceed の直列実行証跡を固定。
- 指定外ファイル・実装コード・共有統合ファイルは未編集。

### Phase 4 Verify
- `rg -n "DOC-OPS|Classification|Audience|Goal|Public boundary|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/installation.md`
- `git diff --check`
- self-repair count: 0/3。

### Phase 5 Proceed
- 判定: **Ready**（分類方針と公開境界を維持）。
