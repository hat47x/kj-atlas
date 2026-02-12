# 非矩形 Island 形状と形状編集の設計（F-01）

本ドキュメントは、`F-01 非矩形Island` を実装に着手可能な粒度へ分解するための設計案である。  
対象は **A型図解（キャンバス上のまとまり表現）** に限定し、MVP互換を維持しながら段階導入する。

- 上位方針: `01_Plans/roadmap.md`, `01_Plans/value_to_requirements.md`
- 既存整合: `02_Architecture/schemas.md`（DocumentV1拡張）
- 非目標: 正解判定・スコアリング・自由曲線

---

## 1. 目的と背景

現状の矩形囲みのみでは、以下の制約がある。

- 斜め配置・塊の偏りを持つカード群で視覚的ノイズが増える
- 「曖昧なまとまり（意味保留）」を柔らかく表現しにくい
- 俯瞰時に、関係線と囲みの重なりが増えて判読性が下がる

そのため、Islandの形状を段階的に拡張する。

---

## 2. サポートする形状（Rect / RoundedRect / Polygon）

### 2.1 Rect（既定・後方互換）

- 理由
  - 実装とヒットテストが最も単純
  - 既存データとの完全互換を保てる
  - MVPの既定値として安全
- 用途
  - 手動で明示的に囲みたい場面
  - 最小機能のフォールバック

### 2.2 RoundedRect（矩形の可読性改善）

- 理由
  - Rectの扱いやすさを維持しつつ、視覚的な固さを軽減
  - 角の衝突（線やカードとの視覚干渉）を減らせる
- 用途
  - Rect互換で見た目を改善したい場面

### 2.3 Polygon（非矩形の本命）

- 理由
  - カード群の実際の分布に追従できる
  - F-01の目的（曖昧なまとまりの自然表現）に最も適合
- 用途
  - 自動生成（カード群から輪郭作成）
  - 将来の頂点編集による微調整

> 採用しない形状（本フェーズ）: freehand / bezier（後述のOut-of-scope）。

---

## 3. データモデル提案

`schemas.md` の `Island` を以下に拡張する。

## 3.1 追加構造

```ts
export type IslandShape =
  | { kind: "rect"; params: { x: number; y: number; width: number; height: number } }
  | {
      kind: "rounded_rect";
      params: { x: number; y: number; width: number; height: number; radius: number };
    }
  | {
      kind: "polygon";
      params: { points: Array<{ x: number; y: number }>; closed: true };
    };

export type Island = {
  id: string;
  title?: string;
  cardIds: string[];
  shape: IslandShape;
};
```

## 3.2 JSON例

### Rect

```json
{
  "id": "is_1",
  "cardIds": ["c1", "c2"],
  "shape": {
    "kind": "rect",
    "params": { "x": 100, "y": 80, "width": 320, "height": 180 }
  }
}
```

### RoundedRect

```json
{
  "id": "is_2",
  "cardIds": ["c3", "c4", "c5"],
  "shape": {
    "kind": "rounded_rect",
    "params": { "x": 420, "y": 140, "width": 360, "height": 220, "radius": 24 }
  }
}
```

### Polygon

```json
{
  "id": "is_3",
  "cardIds": ["c6", "c7", "c8"],
  "shape": {
    "kind": "polygon",
    "params": {
      "closed": true,
      "points": [
        { "x": 100, "y": 100 },
        { "x": 260, "y": 80 },
        { "x": 360, "y": 180 },
        { "x": 280, "y": 300 },
        { "x": 140, "y": 280 }
      ]
    }
  }
}
```

## 3.3 制約（最低限）

- `rect/rounded_rect`
  - `width > 0`, `height > 0`
  - `radius >= 0` かつ `radius <= min(width, height)/2`
- `polygon`
  - `points.length >= 3`
  - 自己交差は「禁止推奨」。初期実装では `self-intersection` 検査を入れ、検出時は保存拒否（400）

## 3.4 review flags との整合

本機能は形状（幾何情報）の設計であり、形状そのものに正解スコアは持たせない。  
`value_to_requirements.md` の `DATA-03-1` / `AI-03-1` に合わせ、**AIが提案したIsland形状** を将来扱う場合は以下を適用する。

- AI提案由来のshapeは `unreviewed` で開始する
- 人間操作（承認/編集）でのみ `human_reviewed` へ遷移する
- 自動再生成ジョブがレビュー状態を自律変更しない

> 注: 本ドキュメントのスコープは形状設計であり、review flag の保存フィールド追加自体は別Issueで扱う。

---

## 4. 自動生成戦略（Polygon）

## 4.1 基本フロー

1. 対象Islandの `cardIds` からカード矩形（位置+サイズ）を収集
2. 各カードの代表点（中心）または外接矩形の頂点群を点集合化
3. 点集合から **convex hull** を計算
4. hull外側へ一様に **padding** を適用
5. 角を丸める簡易 **smoothing** を適用（任意）
6. `shape.kind = "polygon"` として保存

## 4.2 凸包入力の推奨

- 初期実装は **カード中心点** を使う（計算簡潔、実装容易）
- 将来改善で **カード外接矩形の4頂点** を使い、包絡精度を上げる

## 4.3 paddingルール

- 既定値: `padding = 24px`
- ズーム非依存のworld座標で保持
- 下限・上限: `8px <= padding <= 64px`

## 4.4 smoothingルール（簡易）

- 初期は「見た目用」の軽量処理のみ
  - 連続3点の内角が閾値未満（例: 25°）なら中央点を1回だけ緩和
- 幾何学的厳密性より安定描画を優先
- smoothing無効でも動作する実装にする（フラグでOFF可）

---

## 5. 手動編集戦略（将来拡張）

## 5.1 頂点ハンドル（future）

- Polygonの各頂点にドラッグ可能ハンドルを表示
- 操作対象
  - 頂点移動
  - 頂点追加（辺中点ハンドル）
  - 頂点削除（最小3点を維持）

## 5.2 制約（シンプル優先）

- 最小頂点数3を強制
- 自己交差は禁止（発生時は操作をキャンセル or 直前状態へロールバック）
- 高度制約（直交固定・角度固定・スナップ）は本フェーズ対象外

## 5.3 UI段階導入

- Phase 1: 自動生成のみ（手動編集なし）
- Phase 2: 頂点移動のみ
- Phase 3: 頂点追加/削除

---

## 6. レンダリング・ヒットテストへの影響

## 6.1 レンダリング

- SVGを前提
  - Rect/RoundedRect: `<rect>`
  - Polygon: `<polygon>`（将来 `<path>` へ移行可能）
- 描画順
  - Island fill → edge → card → selection overlay
- スタイル
  - fillは低不透明度（例: 0.08〜0.16）
  - strokeは細線（1〜2px）でカード可読性を優先

## 6.2 ヒットテスト

- Rect/RoundedRect: bbox判定
- Polygon: point-in-polygon（ray casting）
- 選択優先順位（誤操作低減）
  1. カード
  2. エッジ
  3. Island

## 6.3 パフォーマンス

- 同一Islandのポリゴンは再計算を最小化
  - カード移動中はthrottle（例: 60〜120ms）
  - ドラッグ終了時に最終確定再計算

---

## 7. 移行計画（互換性）

## 7.1 既存データ互換

- 既存Islandは `rect` として扱う（デフォルト）
- `shape` が未存在の旧データを読む際は、従来矩形情報から `shape.kind="rect"` を合成

## 7.2 段階導入

1. スキーマ拡張（`shape` 追加、Rect既定）
2. レンダラー分岐（Rect / RoundedRect / Polygon）
3. Polygon自動生成（オプション）
4. UIから「Polygon化」トリガー追加

## 7.3 API互換

- `DocumentV1` 互換を維持するため、初期は `version=1` のまま拡張可能なoptional fieldとして導入
- 厳格運用が必要になった時点で `version=2` を検討

---

## 8. Out-of-scope（この設計でやらない）

- freehand（手描き輪郭）
- bezier / spline編集
- 自動意味解釈による形状最適化
- スコアリングによる形状の良し悪し判定

---

## 9. 実装Issue化のための分割案

### Epic: F-01 非矩形Island

- Issue 1: `Island.shape` スキーマ拡張（Rect既定・バリデーション含む）
- Issue 2: Renderer対応（Rect/RoundedRect/Polygonの描画分岐）
- Issue 3: Polygonヒットテスト実装（point-in-polygon + 選択優先順位）
- Issue 4: Polygon自動生成（convex hull + padding + smoothing最小）
- Issue 5: 互換読み込み（旧データ→Rect合成）
- Issue 6（future）: Polygon頂点ハンドル（移動のみ）

### Issueごとの着手条件（DoD）

- Issue 1 完了条件
  - `shape.kind` が `rect | rounded_rect | polygon` を受理する
  - 不正shapeで 400 を返す
- Issue 2 完了条件
  - 3形状すべてで描画崩れなくズーム/パン追従する
- Issue 3 完了条件
  - Polygon内クリックで選択でき、カード選択を阻害しない
- Issue 4 完了条件
  - 同一入力で再現可能なpolygonが生成される（非ランダム）
- Issue 5 完了条件
  - 旧ドキュメント読み込み時にshape欠損でも表示エラーにならない
- Issue 6 完了条件（future）
  - 頂点ドラッグ時に最小3頂点・自己交差禁止を満たす

### 受け入れ条件（共通）

- Rect既存ドキュメントが非破壊で表示・保存できる
- Polygonが任意Islandで選択・移動対象として機能する
- 正解/採点/ランキングをUI・APIに導入しない
- 人間操作なしに形状確定状態を変更しない

---

## 10. 実装開始チェックリスト（Issue作成時に転記）

### 10.1 スキーマ/保存

- [ ] `Island.shape.kind` の3値を受理するバリデータを追加
- [ ] `shape` 欠損の旧データを `rect` 合成で読める
- [ ] `polygon.points` の最小点数・自己交差チェックを追加

### 10.2 Canvas Engine

- [ ] convex hull 計算ユーティリティを追加（非ランダム）
- [ ] padding / smoothing のデフォルト値を設定化
- [ ] point-in-polygon ヒットテストを追加

### 10.3 Renderer/UI

- [ ] Rect / RoundedRect / Polygon の描画分岐
- [ ] 選択優先順位（カード→エッジ→Island）の回帰確認
- [ ] Polygon化トリガーをオプション機能として追加

### 10.4 受け入れ確認

- [ ] 既存Rectドキュメントの表示・保存が非破壊
- [ ] Polygonでパン/ズーム/選択が成立
- [ ] freehand / bezier / correctness scoring を導入していない
- [ ] AI提案形状のレビュー状態は人間操作でのみ確定される
