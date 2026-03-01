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
