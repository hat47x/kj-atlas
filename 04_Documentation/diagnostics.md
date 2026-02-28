# diagnostics worker protocol

この文書は Frontend diagnostics worker の I/O 契約を定義する。
対象実装:
- `03_Implement/frontend/src/worker/diagnostics_protocol.ts`
- `03_Implement/frontend/src/worker/diagnostics_client.ts`
- `03_Implement/frontend/src/worker/diagnostics.worker.ts`

## diagnosticsData schemaVersion

- Current: `1`
- 対応方針: クライアントは `schemaVersion === 1` のみ受理する。
- pre-release 方針として、旧バージョン互換（schema欠損・旧versionマイグレーション）は提供しない。

## Worker message envelope

### Request
- `diagnostics.request`
- `diagnostics.cancel`

### Response
- `diagnostics.progress`
- `diagnostics.result`
- `diagnostics.error`
- `diagnostics.cancelled`

## Validation / fallback policy

`DiagnosticsWorkerClient` は次を検知した場合、worker結果を破棄し main-thread fallback 計算へ遷移する。

- invalid / unsupported `schemaVersion`
- malformed / array-shaped payload
- malformed result envelope（`result` がobjectでない、`diagnosticsMd` がstringでない）
- malformed progress（stage不正、percent不正）
- unknown message type
- malformed `diagnostics.error`（messageがstringでない）
- required fields 欠落（`recommendations`, `diagnosticsMd`, 各report object）

### requestId isolation

- 別requestIdのメッセージは無視する。
- 別requestIdで malformed なメッセージが来ても、対象requestの処理は継続する。

## Compatibility guarantee

- N（current）: 完全サポート
- N 以外: 互換なし（fallbackへ遷移し処理継続）

## Structural metrics contract

`diagnosticsData.structuralMetrics` は次の値を返す（同一入力で同一出力の決定論）。

### Existing metrics

- `cardCount`: ドキュメント中のカード件数
- `islandCount`: ドキュメント中の島件数
- `evidenceLinkCount`: 妥当なカード参照を持つ evidenceLinks 件数
- `evidenceLinkDensity`: `evidenceLinkCount / max(1, cardCount)`
- `isolatedCardCount`: relation（evidenceLinks + card-card edges）に接続していないカード数
- `contradictionRatio`（optional）: 型付き relation における否定系比率
- `reviewedCoverage`（optional）: `textReviewed === true` の割合
- `islandSizeDistribution`: 島ごとの有効カード数分布

### FB-RM-RS-02 metrics

- `connectedComponentCount`:
  - 意味: relation グラフ（card node、undirected edge）における連結成分数
  - 期待: 値が大きいほど分断の可能性が高い
- `largestComponentRatio`:
  - 意味: `largestConnectedComponentSize / max(1, cardCount)`
  - 期待: 1.0 に近いほど全体が連結、低いほど断片化
- `degreeP95`:
  - 意味: card degree 分布の95パーセンタイル（nearest-rank）
  - 期待: 局所ハブの過密検知に利用
- `bridgeEdgeCount`:
  - 意味: 削除すると連結成分数が増える bridge edge 数（無向グラフ）
  - 期待: 値が高いほどボトルネック依存が高い

### Computation scope

- relation グラフの edge は以下を統合して構築する:
  - `evidenceLinks`（fromCardId/toCardId が既知カード）
  - `edges` の card-card 関係（fromKind/toKind が card または未指定）
- 自己ループは除外する。
- bridge 判定は正規化済み無向単純グラフで実施する。

### Initial threshold hints (warning defaults)

- `connectedComponentCount >= 3`
- `largestComponentRatio < 0.7`
- `degreeP95 >= 6`
- `bridgeEdgeCount >= 5`

> しきい値は初期運用値であり、プロジェクトデータ特性に応じて調整する。
