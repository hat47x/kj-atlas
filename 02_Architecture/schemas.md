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

- 既定値（default）:
  - `view.json`: `visibility` 未定義時は `Restricted` を補完。
  - `packs/index.json`: `visibility` 未定義時は `Public` を補完。
- fallback は **import読込時に正規化して内部モデルへ反映** し、export時は常に enum を明示出力する。

| Artifact | Field | 欠損時 default（互換読込） | enum外値 | export時 |
| --- | --- | --- | --- | --- |
| `view.json` | `visibility` | `Restricted` を補完 | reject（strict validator） | 常に enum を明示 |
| `packs/index.json` | `packs[*].visibility` | `Public` を補完 | reject（strict validator） | 常に enum を明示 |
| `document.json` | （対象外） | 変更なし（`visibility` を持たない） | N/A | N/A |

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
- 運用解釈：`visibility` は公開範囲の意図を示すメタデータであり、外部送信可否（SafeMode や export制御）を直接変更しない。

### 8.1.1 SafeMode / readOnly / visibility の評価優先順位

競合時の評価順は次で固定する（上位が優先）。

1. **SafeMode / share-export policy**（既定ON、漏えい防止）
2. **readOnly**（書込・共有・export など破壊/外部送信系を抑止）
3. **visibility**（公開範囲ラベル。UI表示・監査ラベル用途）

補足:
- `visibility=Public` でも SafeMode により export/share が拒否され得る。
- `visibility=Restricted` でも readOnly=false かつ SafeMode許可条件を満たす操作は、既存ポリシーに従って評価する。
- `visibility` は判定入力にはなり得るが、SafeMode/readOnly の拒否結果を上書きしてはならない。

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
- 運用解釈：pack の `visibility` も配布上の分類情報として扱い、SafeMode 既定ONおよび漏洩防止ポリシーとは分離する。

### 8.2.1 I/F 境界（実装者向け）

- **Schema契約（本書）**
  - `Visibility` の値域、default/fallback、不正値拒否条件の単一正本。
- **Importer / Loader（Backend/Frontend 共通責務）**
  - 欠損時 default 補完（`view.json` は `Restricted`、`packs/index.json` は `Public`）。
  - 補完後の内部モデルは `visibility` 必須状態で保持する。
- **Validator（Backend/Frontend 共通責務）**
  - enum外値・型不正は互換対象にせず reject する。
  - `packs/index.json` は entry 単位で黙って救済せず、manifest 全体を失敗扱いにする。
- **Exporter（Backend/Frontend 共通責務）**
  - 互換補完で受理した旧データを含め、再出力時は必ず `visibility` を明示する。
- **Policy層（Non-Goalの明確化）**
  - `visibility` は分類メタデータであり、RBAC/認可/SafeMode 判定ロジックそのものは本タスクの対象外（FB-RM-PUB-01 のスコープ外）。

### 8.3 旧データ互換（旧→新）

- 旧 `view.json`（`visibility` 欠損）
  - 読込時: `Restricted` を補完して `ViewMetadataV1` として扱う。
  - 再export時: `visibility: "Restricted"` を明示出力する。
- 旧 `packs/index.json`（entry の `visibility` 欠損）
  - 読込時: `Public` を補完して `PublicPackManifest` として扱う。
  - 再export時: 各 entry に `visibility` を明示出力する。
- 旧データに `visibility` が存在しても enum 外値の場合は **互換読込対象にしない**（strict validator で拒否）。

#### 8.3.1 既存 document の欠損解釈（明示）

- `document.json` は FB-RM-PUB-01 の適用対象外であり、`visibility` 欠損という状態自体を扱わない。
- 互換読込で default 補完を行うのは `view.json` / `packs/index.json` のみ。
- 既存 `document.json` をそのまま読めること（非破壊）を互換要件とする。

### 8.4 失敗ケース（拒否すべき入力）

- `visibility` が文字列以外（`null`, number, object）
- `visibility` が enum 外（例: `"FriendsOnly"`, `"private"`）
- pack manifest で `packs[*].visibility` が欠損以外の不正（例: `""` や空白のみ）
- view metadata で `visibility` が空文字または大文字小文字違い（例: `"public"`）

### 8.5 Definition of Done（FB-RM-PUB-01）

1. **schema検証**
   - `view.json` / `packs/index.json` が enum 制約（`Public | Unlisted | Org | Restricted`）を満たす。
   - 不正値は import/export validator が拒否する。
2. **互換読込**
   - `visibility` 欠損の旧 `view.json` が `Restricted` として読める。
   - `visibility` 欠損の旧 `packs/index.json` が `Public` として読める。
3. **回帰観点**
   - SafeMode既定ON・share/export漏えい防止の既存テストが通る。
   - `visibility` 追加により readOnly/SafeMode の拒否挙動が緩まない。

### 8.6 importer / validator / exporter テスト観点

- importer（互換補完）:
  - `view.json` の `visibility` 欠損時は `Restricted` を補完して読込成功。
  - `packs/index.json` の `packs[*].visibility` 欠損時は `Public` を補完して読込成功。
- strict validator（不正拒否）:
  - `visibility` が enum 外または型不正（number/null/object/空文字）は失敗として拒否。
  - `packs/index.json` は entry 単位で黙って破棄せず、manifest 全体を失敗扱いにする。
- exporter（再出力明示）:
  - 互換補完で読んだ旧データは再出力時に `visibility` を必ず明示。
  - `visibility` 追加後も SafeMode/readOnly の拒否優先順は不変。

### 8.7 トレーサビリティ（FB-RM-PUB-01）

- 要求元: `01_Plans/adr/ADR-0007-future-backlog.md` の `FB-RM-PUB-01`（schema検証と既存データ互換）。
- 上位整合: `02_Architecture/architecture.md` §11（visibility enum / default補完 / SafeMode優先）。
- 本節（schemas.md）は、実装者向けの単一契約として default/fallback/strict validation/I/F境界を具体化する。


## 9. Island hierarchy compatibility contract（FB-P2A-01）

`DocumentV2.islands[*]` では、階層表現を次で扱う。

```ts
export type Island = {
  id: string;
  cardIds: string[];
  parentIslandId?: string;
};
```

- `parentIslandId` は任意（未設定時はルート島として扱う）。
- 既存データ互換のため、`parentIslandId` が欠損していても読み込みを失敗させない。
- `parentIslandId` が存在しない島を参照する場合は、import 正規化で `undefined` にフォールバックする。
- 循環参照（self-parent 含む）は import 正規化で `undefined` にフォールバックする。
- save/reload では有効な `parentIslandId` を欠落させず往復保持する。
