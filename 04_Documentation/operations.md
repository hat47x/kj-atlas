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

### Polygon手動編集（FB-P2C-04）

- 対象: `shape.kind = "polygon"` の island。
- 操作: Side Panel の **Edit island boundary** をONにすると、頂点ハンドルを表示できます。
- 頂点移動: ハンドルをドラッグして移動（保存は pointer up 時に1回だけ確定）。
- 頂点追加: `Alt+Click` で辺上に頂点を追加。
- 頂点削除: `Alt+Click` で頂点を削除（ただし最小3点制約を維持）。
- 制約違反時（自己交差/最小頂点数未満）は操作を拒否し、直前の確定済み polygon を維持します。
- read-only モードでは編集チェックボックスは disabled となり、頂点ハンドルは表示されません。

### Bundle export の監査ファイル

- `Export bundle (.zip)` には `merge_decision_audit.json` が同梱されます。
- 本ファイルには merge decision の監査最小情報（`decisionId` / `groupId` / `decisionType` / `actorType` / `decidedAt` / `representativeCardId` / `sourceCardIds` / `missingSourceCardIds`）を含みます。
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

4. 改ざん検知（SHA-256 + 署名）

- `publish:static` は `integrity.json` を自動生成し、公開物のハッシュ一覧を記録します。
- 署名を付与する場合は `--signing-key`（RSA private key PEM）と `--key-id` を指定します。

```bash
cd 03_Implement/frontend
npm run publish:static -- \
  --document ./tests/fixtures/worker/doc.small.json \
  --out ../deploy/public \
  --pack-id public-main \
  --title "Public sample" \
  --signing-key ./keys/publish-private.pem \
  --key-id ops-2026q1

node ./scripts/verify_artifact_integrity.mjs \
  --root ../deploy/public \
  --public-key ./keys/publish-public.pem \
  --key-id ops-2026q1
```

- 検証失敗時（hash mismatch / signature mismatch / key-id mismatch）は **配布停止（fail-safe）** し、再生成または鍵ローテーション手順へ進みます。


#### Visibility metadata 運用（FB-RM-PUB-01）

- `view.json` の `visibility` は `Public | Unlisted | Org | Restricted` のみ許可されます。
- 既存互換のため、`view.json` で未設定なら `Restricted` として読み込みます。
- `packs/index.json` の各packでも同じ enum を使い、未設定なら `Public` を補完します。
- `visibility` が存在する場合、enum外値（例: `FriendsOnly`）や型不正（`null`/number/object）は strict validation で拒否されます。
- 互換fallback（欠損時補完）と strict validation（不正値拒否）は責務を分離し、補完後に再exportすると `visibility` は必ず明示されます。
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
curl -fsS -X PUT http://localhost:8080/api/docs/<doc_id> -H 'content-type: application/json' --data-binary @/tmp/e2e_doc.json
curl -fsS http://localhost:8080/api/docs/<doc_id>

cd /path/to/kj-atlas/03_Implement/frontend
npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line
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
curl -fsS -X PUT http://localhost:8000/docs/<doc_id> -H 'content-type: application/json' --data-binary @/tmp/e2e_doc.json
curl -fsS http://localhost:8000/docs/<doc_id>

cd /path/to/kj-atlas/03_Implement/frontend
npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line
```

- `PUT /docs/{doc_id}` と `GET /docs/{doc_id}` を往復し、SQLite永続化も確認してください。
- この代替手順を利用した場合も、PR本文に実施コマンドと結果を記載します。




## Access Control Adapter 運用境界（FB-RM-PUB-04）

### 1. 責務境界（何を本体で実装しないか）

- KJ Atlas本体は `roles/groups/policyRef` を **入力として受け渡すのみ** で、RBAC/ABACの評価式を実装しません。
- 認可判定（allow/deny/readOnly/reason）の生成は外部 policy adapter（IdP/Policy Engine 側）の責務です。
- `visibility` は公開範囲ラベル用途であり、単独で認可可否を確定しません。

### 2. 環境変数

- `ACCESS_CONTROL_ADAPTER=noop|mock|external_http|<custom>`（既定: `noop`）
  - `noop`: 後方互換のため既定許可。
  - `mock`: 契約検証用。`x-policy-ref: mock:deny` / `mock:read_only` で決定論テストが可能。
  - `external_http`: OIDC/SAML運用環境の policy engine（PDP）へ POST 委譲。
  - 未知の値は `noop` へフォールバック（既存挙動維持）。
- `ACCESS_CONTROL_FAIL_SAFE_MODE=read_only|deny`（既定: `read_only`）
  - `Org/Restricted` で `policyRef` 欠損・不達・無効・adapter例外時に fail-safe を適用。
- `ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT`（任意）
  - `external_http` 選択時の委譲先URL。未設定時は `noop` へフォールバック。
- `ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS`（既定: `1.5`）
  - 外部 policy adapter 呼び出しの timeout 秒数。
- `ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE=none|oidc|saml`（既定: `none`）
  - adapter が policy engine へ通知する認証モード。
- `ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN`（任意）
  - PDP 経路で静的トークンが必要な環境向け。
- `ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER`（任意）
  - OIDC/SAML の issuer/entity ID を `x-idp-issuer` ヘッダで引き渡す。
- `REVIEWER_REF_RESOLVER_ADAPTER=user_id|sso_subject`（既定: `user_id`）
  - `user_id`: `reviewerRef/ownerRef = user:<users.id>`（既存互換）。
  - `sso_subject`: `reviewerRef/ownerRef = user:sso:<provider>:<externalUid>`。subject欠損時は `actorRef` フォールバック。

### 3. 最小監査記録（PII非保存）

- 記録対象（最小）: `eventType`, `eventVersion`, `occurredAt`, `docId`, `action`, `decision_allow`, `policyRefPresent`。
- 任意記録: `decision_readOnly`, `decision_reason`, `visibility`, `adapterName`, `traceId`。
- 非保存: `roles/groups` 生値, `policyRef` 生値, ドキュメント本文。

### 3.1 AuthContext属性の監査取扱い（PII最小化）

- `amr/acr/aal/auth_time` はアプリDBへ保存しない。
- 監査へ出力する場合も生値は使用せず、次の正規化のみ許可する。
  - `hasStepUp`（boolean）
  - `assuranceLevel`（`low|substantial|high|unknown`）
  - `authAgeBucket`（`fresh|stale|unknown`）
- `roles/groups/policyRef` は外部照会入力であり、監査では `policyRefPresent` など存在フラグのみ扱う。

### 3.2 strict mode の例外承認責任

- `ALLOW_JIT_PROVISIONING=false` は本番標準（strict）とする。
- 例外的に緩和する場合（`true` へ変更）は Security Officer + System Owner の2者承認を必須とする。
- Platform Operator は実施時刻・理由・承認者を変更台帳へ記録し、承認記録がない変更を禁止する。
- backend 開発者はコードで一時バイパスを実装してはならない。

### 4. SafeMode/read-only 優先

- 判定順は常に `safeMode` → `readOnly` → adapter判定。
- adapterが許可を返しても、SafeMode/read-only拒否は上書きできません。
- `external_http` は HTTP 4xx(400/401/403/422)・不正JSON・契約不整合を `policy_ref_invalid` に、接続障害/timeout/5xx を `policy_ref_unreachable` に正規化します。
- adapter未設定/無効時でも `noop` にフォールバックし、既存運用を阻害しません。

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


## i18n SafeMode 漏洩防止検証（FB-RM-I18N-06）

### 1. テストマトリクス（経路 × モード × 期待値）

| 経路 | モード | シナリオ | 期待値 |
|---|---|---|---|
| fetch/XHR/Worker | SafeMode=ON | 翻訳アダプタが外部送信を試みる実装でも、ガード経由実行 | アダプタ未実行・送信試行 0 件・`translation.safe_mode_blocked` を記録 |
| telemetry/audit dispatch | SafeMode=ON | telemetry/audit 有効化フラグあり | dispatch 未実行（fail-safe block） |
| telemetry dispatch | SafeMode=OFF | telemetry dispatch が例外を返す | 翻訳処理を fail-safe で停止（adapter 未実行）、`fail_safe_dispatch` を返す |
| adapter timeout | SafeMode=OFF | タイムアウト到達 | `timeout` 返却、返却文とログが `[REDACTED]` のみ |
| adapter error | SafeMode=OFF | adapter error | `adapter_error` 返却、ログに生テキストを含めない |
| 正常系 | SafeMode=OFF | adapter 成功 + telemetry/audit 有効 | `success` 返却、dispatch payload は digest のみ（原文なし） |

### 2. 追加ガード一覧

- `runLocaleConversionWithGuard`:
  - SafeMode 時は翻訳処理・telemetry・audit dispatch を即時遮断。
  - telemetry/audit 送信で例外が出た場合は fail-safe（変換停止）に倒す。
  - timeout/adapter error 時は原文ではなく `SafeModePolicy.redactText` を返す。
  - ログは `SafeModePolicy.summarizeForSafeMode` の digest のみを記録。
- `installNetworkLeakMonitor`:
  - `fetch` / `XMLHttpRequest` / `Worker` をテスト時にフックし、送信経路を網羅監視。
  - 送信試行を即時例外化して漏洩を検出可能にする。

### 3. CI 組み込み方法

1. Frontend の script に以下を追加済み:

```bash
npm run test:i18n-security
```

2. GitHub Actions `CI` に専用ジョブ `Frontend i18n safe-mode leakage guards` を追加済み。

3. branch protection の required check に同ジョブを追加し、
   SafeMode 漏洩テスト未通過のマージを禁止する。

### 4. インシデント時手順（漏洩疑い）

1. `npm run test:i18n-security` をローカルで再実行し、どの経路（fetch/XHR/worker/dispatch）で失敗したかを確認。
2. 失敗ケースのログに原文（機微情報）が含まれていないかを確認（digestのみ許容）。
3. 直近変更で翻訳 adapter / telemetry / audit dispatch の呼び出し位置が SafeMode 判定より先行していないかを確認。
4. 必要なら一時的に翻訳機能を feature flag で停止し、`SafeMode=ON` 時の外部送信 0 件を復旧条件にする。
5. 復旧後に CI の `Frontend i18n safe-mode leakage guards` を required check として再確認する。

## i18n document hash 不変検証（FB-RM-I18N-05）

### 1. テスト観点（ハッシュ対象と分離保証）

- ハッシュ対象は **`document.json` のみ**。`view.json` や UI state は対象外。
- ハッシュ計算前に canonicalize（オブジェクトキー順序正規化）を適用し、順序差分を排除。
- 言語切替時の期待値は2系統で検証する。
  - `document hash` は常に不変。
  - `view metadata`（`viewState.locale` / 解決ソースなど）はシナリオに応じて変化。
- 差分検知時は `ui-state` / `view-metadata` / `document-payload` の層別診断ログで切り分ける。

### 2. ケース表（前提 / 操作 / 期待）

| ケースID | 前提 | 操作 | 期待値 |
|---|---|---|---|
| I18N05-01 | 同一 `document.json`、view locale=ja | `ja -> en -> ja` の順で bundle export | `document.json` hash が3回とも一致。`view.json` は locale 変化に追随 |
| I18N05-02 | metadata=ja, persisted=ja | URL `?locale=en` を付けて locale 解決 | locale source は `url`。`document.json` hash は URL なしケースと一致 |
| I18N05-03 | metadata=en, persisted=ja, read-only=true | locale 解決後に bundle export | `shouldPersist=false`。`document.json` hash は read-write ケースと一致 |

### 3. 失敗時の切り分け手順（層別診断ログ）

1. `npm run test:i18n-regression` を再実行し、失敗ケースIDを特定する。
2. テスト出力の層別診断を確認する。
   - `document-payload`: `document.json` canonical payload が変化（重大）。
   - `view-metadata`: `view.json` の locale など表示メタのみ差分（想定内）。
   - `ui-state`: locale 遷移事実のログ（想定内、ただし document 変化と同時発生なら要調査）。
3. `document-payload` が出た場合は、`buildExportBundle` へ渡す `doc` と `viewState` の境界を確認し、UI状態混入を除去する。
4. 併せて `resolveViewLocale` の source/shouldPersist 判定が read-only と URL 優先規約を満たしているかを再確認する。

### 4. CI組込要件

1. Frontend script:

```bash
npm run test:i18n-regression
```

2. GitHub Actions `CI` に専用ジョブ `Frontend i18n document hash regression` を追加済み。
3. branch protection の required check に同ジョブを設定し、hash不変テスト未通過のマージを禁止する。

### 5. 完了条件（DoD）

- `ja -> en -> ja`、URL優先、read-only の3シナリオで `document.json` hash が不変。
- 期待値を `document hash` と `view metadata` に分離して検証している。
- 差分発生時に、漏洩層（ui-state/view-metadata/document-payload）を診断ログで一意に特定できる。
- CIで deterministic 実行（固定時刻・canonicalize・乱数未使用）が維持される。

## i18n辞書更新ルール（FB-RM-I18N-03 運用）

新しい UI 文言キーを追加したときは、以下を同一PRで実施します。

1. `03_Implement/frontend/src/i18n/locales/ja.json` と `en.json` に同じキーを追加する。
2. 変数展開を使う場合は、`{name}` プレースホルダ名を ja/en で一致させる。
3. 追加後に次の検証を実行し、キー欠損・プレースホルダ不整合・機能回帰を検出する。

```bash
cd 03_Implement/frontend
pnpm -s vitest run src/i18n/catalog_integrity.test.ts src/i18n/key_consistency.test.ts src/ui/i18n_equivalence.integration.test.ts
```

4. 表示言語の切替が document payload に影響しないことを `document_locale_invariance.test.ts` で確認する。
5. SafeMode の漏洩防止回帰（`locale_conversion_guard.test.ts` 等）を必ず再実行する。
