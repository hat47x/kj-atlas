# kj-atlas MVP API I/F

本ドキュメントは、kj-atlas の **MVP API（DocumentV1の保存・取得）** を定義します。

- MVPでは **スナップショット保存** を基本とします
- 認証・共有・差分同期は後回しです
- APIはイントラ利用を含むため、単純で監査しやすい設計を優先します

---

## 1. 基本方針

### 1.1 リソース単位

- 主リソース：`Document`
- 最小のCRUD：Create / Read / Update

DeleteはMVPでは必須ではない（必要なら追加）。

### 1.2 更新方式

- `PUT /docs/{doc_id}` で **Document全体** を置き換える
- クライアントは `updatedAt` を更新して送る
- サーバは検証後に保存し、保存後のDocumentを返す

### 1.3 競合

MVPでは以下のいずれかで簡素に扱う。

- Last Write Wins（デフォルト）
- もしくは `If-Match` / `ETag` による楽観ロック（Phase 2以降）

MVPではまず LWW とし、将来 ETag を追加できる形にする。

---

## 2. エンドポイント

### 2.1 Create

**POST** `/docs`

- Request body：任意（空でも良い）
- Response：作成された `DocumentV1`

> サーバでIDを採番しても良いが、フロント主導を優先するならクライアント採番でも良い。
> どちらでも成立するよう、実装では「bodyにidがあれば採用、なければ生成」を許容してよい。

---

### 2.2 Read

**GET** `/docs/{doc_id}`

- Response：`DocumentV1`
- Not found：404

---

### 2.3 Update

**PUT** `/docs/{doc_id}`

- Request body：`DocumentV1`
- Response：保存後の `DocumentV1`
- Validation error：400

---

### 2.4 List（任意：MVPでは後回し可）

**GET** `/docs`

- Response：最小の一覧（id/title/updatedAt）

イントラ想定では一覧があると便利だが、MVPでは必須ではない。


### 2.5 Export監査イベント（FB-RM-PUB-05）

**POST** `/docs/{doc_id}/export-audit`

- Request body: `{ "safeMode": boolean, "exportKind": string }`
- Response: `{ "status": "accepted" }`
- 目的: export完了通知を監査連携アダプタへ委譲（監査送信失敗でも本体機能を阻害しない）

---

## 3. レスポンス例（概要）

### 3.1 DocumentV1（レスポンス）

```json
{
  "version": 1,
  "id": "doc_...",
  "title": "",
  "createdAt": "2026-02-10T00:00:00Z",
  "updatedAt": "2026-02-10T00:00:00Z",
  "transform": {"panX": 0, "panY": 0, "zoom": 1},
  "cards": [{"id": "c1", "text": "...", "x": 120, "y": 80}],
  "edges": [{"id": "e1", "fromId": "c1", "toId": "c2", "type": "related"}]
}
```

---

## 4. エラー設計（最小）

MVPでは、エラーを過度に作り込まない。

- 400：入力スキーマ不正（Pydanticのvalidation errorを整形）
- 404：doc not found
- 500：内部エラー

---

## 5. 将来拡張（非MVP）

- ETag（楽観ロック）
- Patch API（差分同期）
- 認証（OIDC / SSO / API Key）
- 共有（read-only link / ACL）
- AI用エンドポイント（draft, re-layout, merge suggestions）

---

## 6. 次に作るもの

- `02_Architecture/llm_provider.md`
- `02_Architecture/deployment.md`

---

## 7. Publishing metadata の扱い（FB-RM-PUB-01）

- `view.json` / `packs/index.json` の `visibility` は **公開範囲ラベル用メタデータ** として扱う。
- `visibility` の値は `Public | Unlisted | Org | Restricted` を採用し、不正値は validator で拒否する。
- 後方互換として、`view.json` 欠損時は `Restricted`、`packs/index.json` 欠損時は `Public` を補完する。
- `visibility` は APIの送信可否判定を上書きしない。外部送信制御は引き続き SafeMode / share/export policy を正本とする。


## 8. AccessControlAdapter API契約（FB-RM-PUB-04）

roles/groups/policyRef に基づく認可判定は、API本体ではなく `AccessControlAdapter` へ外部委譲する。

### 8.1 入力（API → adapter/hook）

- `action`: `read | write | export | share`
- `subject.actorRef`: `x-actor-ref` ヘッダ（任意）
- `subject.roles`: `x-auth-roles` ヘッダ（`,` 区切り、任意）
- `subject.groups`: `x-auth-groups` ヘッダ（`,` 区切り、任意）
- `resource.visibility`: `x-doc-visibility` ヘッダ（`Public | Unlisted | Org | Restricted`）
- `resource.policyRef`: `x-policy-ref` ヘッダ（任意）
- `safeMode`: ルート側のsafeMode（export-auditではpayload.safeMode）
- `readOnly`: `X-Read-Only` ヘッダ（`1`/`true`）

正規化ルール:

- `x-auth-roles` / `x-auth-groups` が未指定・空文字・`null` 相当値のときは `[]` として扱う。
- `x-policy-ref` は trim 後に空文字なら `null` として扱う。
- API本体は roles/groups/policyRef の意味解釈を行わない（外部委譲）。

### 8.2 出力（adapter/hook → API）

```ts
type AccessDecision = {
  allow: boolean;
  readOnly?: boolean;
  reason?: string;
};
```

- `allow=false` の場合は API は `403` を返す。
- `reason` は `Access denied: <reason>` として観測可能。
- 本体は decision の解釈のみを行い、roles/groups の評価規則は持たない。

### 8.3 fail-safe

- 条件: `visibility in {Org, Restricted}` かつ `policyRef` 欠損。
- 既定 `read_only`: `read` のみ許可、`write/export/share` は `403`。
- オプション `deny`: 全アクション `403`。
- 実装パラメータ: `ACCESS_CONTROL_FAIL_SAFE_MODE=read_only|deny`。

追加条件:

- `policyRef` 不達（接続失敗/timeout）・無効（形式不正/失効）・adapter例外でも fail-safe を適用する。
- 上記時の `reason` は `policy_ref_unreachable | policy_ref_invalid | adapter_error` の定義済みコードを使う。
- `visibility` が `Public/Unlisted` の場合は強制fail-safe対象外。

### 8.4 監査イベント連携点

- `GET /docs/{doc_id}` でアクセス許可後に `eventType=view` を送信。
- `POST /docs/{doc_id}/export-audit` でアクセス許可後に `eventType=export` を送信。
- 監査送信は既存の fail-open dispatcher 方針を維持する（監査送信失敗で本体機能は停止しない）。

最小記録項目（PII非保存）:

- 必須: `eventType`, `eventVersion`, `occurredAt`, `docId`, `action`, `decision.allow`, `policyRefPresent`
- 任意: `decision.readOnly`, `decision.reason`, `visibility`, `adapterName`, `traceId`
- 非保存: `policyRef` 生値、`roles/groups` 生値、ドキュメント本文

### 8.5 互換性

- adapter未設定（`noop`）では既存挙動を維持する。
- API本体にRBACエンジンは実装しない（非目標）。
