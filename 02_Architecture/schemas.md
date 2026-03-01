# schemas — kj-atlas MVP スキーマ（02_Architecture）

本ドキュメントは、kj-atlas の **MVPで扱う永続データの最小スキーマ** を定義します。

- YAGNI方針に従い、MVPに不要な型は含めません
- 出自情報（記録者・記録時間など）は **MVPでは保持しません**
- 島（囲み）・画像・文章化・類似統合は後回しです

---

## 1. スコープ

MVPでは以下を成立させます。

- カード（テキスト）の配置
- 関係（線）の最小表現（任意）
- キャンバス表示のためのビュー変換（パン／ズーム）
- ドキュメントの保存・復元

---

## 2. ID・座標系の前提

### 2.1 ID

- すべてのエンティティは `id: string` を持つ
- ID生成はクライアント（UUID v4 等）で行う
- APIは基本的にIDを透過し、衝突時のみエラー

### 2.2 座標系

- world座標は任意の連続値（浮動小数）を許容
- 画面（screen）への変換は `Transform` で表現
- 単位は px 相当を想定（厳密な意味は持たせない）

---

## 3. エンティティ定義（TypeScript）

> 実装言語はフロントが TypeScript のため、まずTS型で定義します。  
> API側（Python）は同等のPydanticモデルへ写像します。

### 3.1 Transform

```ts
export type Transform = {
  panX: number; // world を画面へ移す平行移動（x）
  panY: number; // world を画面へ移す平行移動（y）
  zoom: number; // scale（例: 1.0 = 100%）
};
```

### 3.2 Card

```ts
export type Card = {
  id: string;
  text: string;
  x: number;
  y: number;
  mergedIntoCardId?: string;
  repOf?: string[];
};
```

> 備考：MVPでは `w/h` は固定でもよい。必要になったら追加する。

### 3.3 Edge

```ts
export type EdgeType = "related"; // MVPでは1種類のみ

export type Edge = {
  id: string;
  fromId: string; // Card.id
  toId: string;   // Card.id
  type: EdgeType;
};
```

> 備考：否定線などは将来 `EdgeType` を拡張する。

### 3.4 Document

```ts
export type DocumentV1 = {
  version: 1;
  id: string;
  title?: string;
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601

  transform: Transform;
  cards: Card[];
  edges: Edge[];
};
```

---

## 4. JSONスキーマ（サーバ検証用）

MVPでは、サーバ側で最低限の検証（型・必須フィールド）を行います。
厳密な制約（例：座標範囲や文字数）は後回し。

> 実装では Pydantic モデルで検証し、必要に応じてJSON Schema出力に対応する。

---

## 5. 将来拡張の指針（非MVP）

以下は **追加しやすい順に** 将来導入します。

1. `Card.w/h`（カードサイズ）
2. `EdgeType` の拡張（negate/hypothesis 等）
3. `Island`（囲み、タイトル、所属）
4. `Asset`（画像挿入・生成結果の参照）
5. `Card.meta`（出自情報、タグ、引用元など）
6. `Patch`（差分同期）

---

## 6. 互換性・マイグレーション

- `Document.version` を用いてスキーマバージョンを管理する
- 破壊的変更は version を上げ、API側で移行処理を提供する

---

## 7. 次に作るもの

- `02_Architecture/api.md`：DocumentV1 のCRUD I/F
- `02_Architecture/llm_provider.md`：将来AI用のProvider抽象（枠のみ）
- `02_Architecture/deployment.md`：Docker Compose案



## 8. Publishing / Access metadata（FB-RM-PUB-01）

公開配布（pack）および表示状態（view metadata）では、以下の visibility enum を共通契約として使う。

```ts
export type Visibility = "Public" | "Unlisted" | "Org" | "Restricted";
```

### 8.1 view metadata（`view.json`）

```ts
export type ViewMetadataV1 = {
  version: "1";
  generatedAt: string;
  docSignature: string;
  visibility: Visibility; // 互換読込時の既定: "Restricted"
  camera: { panX: number; panY: number; zoom: number };
  viewState: { /* 既存定義 */ };
  export: { mode: "viewport" | "bounds"; bounds?: { x: number; y: number; w: number; h: number }; padding?: number };
};
```

- 互換方針：旧データで `visibility` が無い場合は `Restricted` を補完する。
- strict validator 方針：`visibility` が存在する場合は enum（`Public` / `Unlisted` / `Org` / `Restricted`）以外を拒否する。
- 安全方針：`visibility` の有無に関わらず SafeMode 既定ON・share/export 制約の既存ポリシーを維持する。

### 8.2 public pack manifest（`packs/index.json`）

```ts
export type PublicPackManifest = {
  defaultPackId?: string;
  packs: Array<{
    id: string;
    documentPath: string;
    viewPath?: string;
    title?: string;
    enforceSafeMode?: boolean;
    readOnly?: boolean;
    visibility: Visibility; // 互換読込時の既定: "Public"
  }>;
};
```

- 互換方針：既存 manifest で `visibility` が無い場合は `Public` を補完する（公開配布の既存運用を維持）。
- strict validator 方針：`visibility` が存在する場合は enum（`Public` / `Unlisted` / `Org` / `Restricted`）以外を拒否する。
- import/export/validate は上記 enum を単一契約として扱う。
