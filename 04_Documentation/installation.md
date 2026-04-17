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


## Stream F docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **Plan**: AC/DoD を先に定義する。不足時はドラフトを提示し、合意後に実行へ進む。
3. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
4. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
5. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 参照仕様未確定、または競合検知時は作業を停止する。
- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## Phase 1-5 execution record (2026-04-16, DOC-OPS-05-06/07/08/09/10 scope)

### Phase 1: Read
- 再Read: 本文冒頭メタ（Audience / Goal / Non-goal / Public boundary / Outcome / Related）と Requirement meta I/F を再確認。
- スコープ確認: 本タスクは「当該Issue本文 + 当該Scope文書」のみを編集対象とする。

### Phase 2: Plan
- 再Read: 関連ADR（特に ADR-0019）と `01_Plans/documentation_quality.md` の参照導線を再確認。
- 計画: Read → Plan → Execute → Verify → Proceed を単一サイクルで実施し、記録を追記する。
- フェイルセーフ: Verify 失敗時の自己修復は最大3回まで、4回目相当は停止。

### Phase 3: Execute
- 再Read: 直前差分と本文の禁止事項（SafeMode後退、公開境界逸脱）を再確認してから編集。
- 実施内容: 本セクションを追記し、Phase運用・再Read・修復上限ルールを明文化。

### Phase 4: Verify
- 再Read: 追記後の本文を再読し、語彙ドリフト・参照不整合・体裁崩れの有無を確認。
- 実施: `git diff --check` と対象ファイルの目視確認を実施。
- 修復回数: 0回（3回超過なし）。

### Phase 5: Proceed
- 再Read: Verify結果とスコープ逸脱の有無を再確認。
- 判定: **Ready**（docs-only、許可範囲内、停止条件なし）。
- 継続条件: 後続差分でも同じ5Phase + 再Read + 修復上限3回を維持する。

## Stream H 専任: DOC-OPS-05後半 実行記録（2026-04-16）

### Phase 1 Read

- 対象本文と関連正本（`00_Prompt/*` / `01_Plans/adr/ADR-0001` / `02_Architecture/*`）を再読し、公開境界を確認した。
- 用語・責務の整合（特に security 系は `Security Officer / System Owner / Platform Operator`）を事前確認した。

### Phase 2 Plan（AC/DoD補完）

- AC補完:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related の冒頭メタを維持する。
  - 本文は docs-only で更新し、実装仕様・設定値の新規決定を持ち込まない。
  - 参照導線（関連文書・issue memo）を切断しない。
- DoD補完:
  - Read → Plan → Execute → Verify → Proceed の記録を残す。
  - Verify で `docs-check` とリンク整合を確認する。

### Phase 3 Execute

- 本文の方針を維持したまま、Stream H後半の実行責務（Phase運用・停止条件）を追記した。
- 編集範囲外（backend/frontendコード、shared統合3ファイル）は変更しない。

### Phase 4 Verify（docs-check + リンク整合）

- `rg` で必須メタ語彙・Phase見出し・停止条件語彙を確認した。
- `git diff --check` で体裁崩れがないことを確認した。
- security 系は D1〜D4 と役割語彙の整合を追加確認した。

### Phase 5 Proceed

- 判定: **Ready**
- 継続条件: 次回更新でも同一フェーズ順序と docs-only 制約を維持する。

### 停止条件（固定）

- 責務用語不整合（`Security Officer / System Owner / Platform Operator` の混在・崩れ）を検知した場合は停止。
- D1〜D4 固定値矛盾（`4h / 2h / 代理承認なし / 48h+15m/60m`）を検知した場合は停止。
- Verify の自己修復が3回を超える場合は `StoppedForClarification` として停止。

## Stream J execution record（2026-04-17, DOC-OPS-05-08 pair）

### Phase 1 Read

- `01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md` と本書を最新状態で同期し、Classification が **Improve external** で固定されていることを確認した。
- 本書の公開境界（Public boundary）と非目標（Non-goal）が、組織内限定手順を除外する方針と一致することを再確認した。

### Phase 2 ADR CDC

- 判定: 方針変更なしのため **ADR追加なし**。
- Context: 初回導入者向け公開手順の再現性を維持する。
- Decision: 既存の Audience / Goal / Public boundary / Go/No-Go gate を維持する。
- Consequences: 後続更新は docs-check と参照整合の範囲に限定し、実装変更に踏み込まない。

### Phase 3 Plan

- AC補完: 「最小起動・疎通・停止」の3手順が順序通りに再現できることを維持基準に固定。
- DoD補完: Read → ADR CDC → Plan → Execute → Verify/Proceed をこのペアで記録し、次ペアへ引き継げる状態にする。

### Phase 4 Execute

- 本書では方針ドリフト防止のため、DOC-OPS-05-08 の運用記録を追記した（手順本体は変更しない）。

### Phase 5 Verify / Proceed

- docs-check:
  - `rg -n "Improve external|Public boundary|Go/No-Go gate|Stream J execution record" 04_Documentation/installation.md`
  - `rg -n "Classification|GoNoGoGate|DecisionStatus|Stream J execution record" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `git diff --check`
- 判定: **Ready**
- Proceed条件: 用語不整合・参照切れ・未定義競合が検出された場合は停止し、自己修復は最大3回までとする。
