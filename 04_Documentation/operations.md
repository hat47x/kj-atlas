# 運用（最小）

## 1. バックアップ / リストア

最小手順はバックエンド README を参照してください。

- [03_Implement/backend/README.md - Minimal backup / restore](../03_Implement/backend/README.md#minimal-backup--restore)

要点のみ:

- SQLite: API停止中にDBファイルをコピーして保全
- PostgreSQL: `pg_dump` / `pg_restore` を利用

## 2. 更新手順（Docker Compose）

1. 停止

```bash
cd /path/to/kj-atlas/03_Implement/deploy
docker compose down
```

2. 配布元の運用手順に従ってコードを更新

3. 再ビルド・起動

```bash
docker compose up --build -d
```

4. 確認

```bash
docker compose ps
docker compose logs api --tail=100
```

## 3. 運用上の注意

- 既定の `LLM_PROVIDER=none` では外部送信は行いません。
- ローカル/社内LLM利用時は `LOCAL_LLM_BASE_URL` を到達可能な内部URLに設定してください。
- 画面の JSON Export / Import を利用可能です。


### Read-only 表示モード

- URL query で `readonly=true`（同義: `readOnly=1`, `isReadOnly=yes`, `mode=readonly`）を指定すると、Frontend は read-only モードで起動します。
- read-only モードでは編集系更新（カード/島/関係の更新、提案適用など）は保存されず、UI上でも編集操作は disabled 表示になります。
- 閲覧操作（パン/ズーム/検索/参照）は継続可能です。

### Bundle export の監査ファイル

- `Export bundle (.zip)` には `merge_decision_audit.json` が同梱されます。
- 本ファイルには merge decision の監査最小情報（`decisionId` / `groupId` / `decisionType` / `actorType` / `decidedAt` / `representativeCardId` / `sourceCardIds`）を含みます。
- 同一入力で同一出力となるよう、decision と cardIds は決定論順序で出力されます。

- `bundle_manifest.json` には `exportGranularity`（`overview` / `detail`）と `generatedAt` を記録します。
- `overview` は俯瞰用に selected-card trace（`evidence_trace_*` / `contradiction_trace_*` / `trace_analytics_*`）を同梱しません。
- `detail` は従来どおり selected-card trace を同梱できます（カード選択時）。

### 静的公開アーティファクト（FB-RM-PUB-03）

`index.html + assets + packs` の最小公開物を生成し、静的ホスティングだけで閲覧できる配布物を作成できます。

1. 生成コマンドを実行

```bash
cd 03_Implement/frontend
npm ci
npm run publish:static -- \
  --document ./tests/fixtures/worker/doc.small.json \
  --out ../deploy/public \
  --pack-id public-main \
  --title "Public sample"
```

2. 出力物を確認（最小構成）

- `03_Implement/deploy/public/index.html`
- `03_Implement/deploy/public/assets/*`
- `03_Implement/deploy/public/packs/index.json`
- `03_Implement/deploy/public/packs/public-main.document.json`

3. ローカル静的サーバで確認

```bash
cd 03_Implement/deploy/public
python3 -m http.server 4173
```

ブラウザで `http://localhost:4173/` を開くと、`pack=public-main&readonly=1` へ自動遷移して閲覧モードで表示されます。


#### Visibility metadata 運用（FB-RM-PUB-01）

- `view.json` の `visibility` は `Public | Unlisted | Org | Restricted` のみ許可されます。
- 既存互換のため、`view.json` で未設定なら `Restricted` として読み込みます。
- `packs/index.json` の各packでも同じ enum を使い、未設定なら `Public` を補完します。
- invalid値（例: `FriendsOnly`）を含む `view.json` は検証エラーとして拒否されます。
- これらの metadata は公開意図の表示用途であり、SafeMode既定ON・read-only公開の既存制御は継続されます。

#### SafeMode / 公開モード整合

- 公開packを読み込んだときは Frontend 側で `safeMode=true` を強制します。
- 生成された `index.html` は `readonly=1` 付きURLへ遷移するため、公開配布物は編集不可の閲覧モードを既定にします。
- `packs/index.json` には `enforceSafeMode: true` / `readOnly: true` を記録し、公開配布の意図を明示します。

## 4. セキュリティ運用メモ（MVP）

- 公開時は API を直接公開せず、Nginx / Traefik などのリバースプロキシ配下で TLS 終端してください。
- イントラネット / VPN 境界での運用を前提にし、可能であれば IP 許可リストを設定してください。
- 迅速な保護が必要な場合は、プロキシ側 Basic 認証を有効化してください。
- API と DB はネットワークを分離し、DB ポートの外部公開を避けてください。
- 定期バックアップとパッチ適用を運用手順に含めてください。

詳細は [security.md](./security.md) を参照してください。


## 5. E2E動作確認ポリシー（運用必須）

`03_Implement/*` に変更が入る場合は、原則として `docker compose` による
`web + api + db` の連動確認を実施します（詳細は `ADR-0019` / `e2e_testing.md`）。

最小手順:

```bash
cd /path/to/kj-atlas/03_Implement/deploy
docker compose up --build -d
docker compose ps
curl -fsS http://localhost:8080/api/health
```

- 実行不能時（Docker未導入等）は、ブロッカー/代替検証/後続手順をPRに明記してください。
- 本運用は「テストが通っていてもE2E未確認ならリスクを明示する」ことを目的とします。
- 本節の内容は `04_Documentation/e2e_testing.md`（正本）と常に一致させます。

## 6. Docker未導入時の代替運用（SQLite + ローカル起動）

Composeが利用できない場合、以下で運用確認できます。

```bash
# terminal A: backend
cd /path/to/kj-atlas/03_Implement/backend
source .venv/bin/activate
export PYTHONPATH=src
export DATABASE_URL="sqlite:///./kj_atlas.db"
alembic upgrade head
uvicorn kj_atlas_api.main:app --host 0.0.0.0 --port 8000

# terminal B: frontend
cd /path/to/kj-atlas/03_Implement/frontend
npm run dev -- --host 0.0.0.0 --port 4173

# terminal C: checks
curl -fsS http://localhost:8000/healthz
curl -fsS http://localhost:4173/api/healthz
```

- `PUT /docs/{doc_id}` と `GET /docs/{doc_id}` を往復し、SQLite永続化も確認してください。
- この代替手順を利用した場合も、PR本文に実施コマンドと結果を記載します。



## 監査連携（view/export）運用

### 1. 基本方針

- 監査連携は `AUDIT_EXPORT_ENABLED=false`（既定）で **完全ローカル動作**。
- 有効化時のみ、`view` / `export` の最小イベントを外部送信。
- 送信データは最小化され、`docId` / `eventType` / `safeMode` / 最小メタデータのみ送信します。
- `x-actor-ref` は平文保存せず、SHA-256短縮ハッシュ (`actorRefHash`) に変換します。

### 2. 最小イベントスキーマ

```json
{
  "schemaVersion": 1,
  "eventId": "audit-<uuid>",
  "occurredAt": "2026-03-01T12:34:56.000000+00:00",
  "eventType": "view | export",
  "docId": "<document-id>",
  "safeMode": true,
  "actorRefHash": "<optional-24hex>",
  "metadata": {
    "route": "...",
    "method": "...",
    "exportKind": "..."
  }
}
```

### 3. 障害時ポリシー（fail-open / queue / drop）

- 監査送信失敗時も、閲覧/エクスポート本体は継続（**fail-open**）。
- 失敗イベントはメモリキューへ退避し、次回送信時に best-effort flush。
- キュー上限 (`AUDIT_QUEUE_SIZE`) 超過時は最古イベントを drop（ログ警告のみ）。
- 送信障害は運用監視（ログ収集）で検知し、アプリの可用性を優先。

### 4. 鍵・エンドポイント設定

1. `AUDIT_EXPORT_ENABLED=true`
2. `AUDIT_TRANSPORT=http`
3. `AUDIT_HTTP_ENDPOINT=https://<audit-gateway>/events`
4. 必要なら `AUDIT_HTTP_API_KEY=<secret>` を設定（Bearer送信）
5. `AUDIT_HTTP_TIMEOUT_SECONDS` を短め（例: 2.0）に維持

### 5. SafeModeポリシー

- 既定は `AUDIT_ALLOW_IN_SAFE_MODE=false`（SafeMode時は外部送信しない）。
- 組織要件でSafeMode中の監査送信が必要な場合のみ明示的に `true` を設定。
- いずれの設定でも payload は最小化・マスキング済みを維持します。

