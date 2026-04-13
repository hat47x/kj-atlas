# Diagnostics Worker Protocol

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部運用者・開発者
> Goal: diagnostics worker 契約を公開runbookとして参照可能にする。
> Non-goal: worker実装ロジックの再設計や内部検証ログ形式の固定化は扱わない。
> Public boundary: 内部検討ログは含めず、契約/フォールバック条件を公開する。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。
> Outcome: 外部運用者が契約・フォールバック・決定論条件を単独で判断できる。
> Related: `02_Architecture/schemas.md`, `03_Implement/frontend/src/worker/diagnostics_protocol.ts`, `01_Plans/documentation_quality.md`, `01_Plans/issues/issue-doc-ops-05-04-04doc-diagnostics.md`


この文書は Frontend diagnostics worker の I/O 契約を定義する。  
公開運用時の用語は `reviewed / unreviewed` を正とし、`true/false` 表記は状態値の説明時にのみ補助的に使う。  
品質判定は `01_Plans/documentation_quality.md` の QG-1〜QG-6 に従う。
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
- `isolationRate`: `isolatedCardCount / max(1, cardCount)`
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
- `connectivityScore`:
  - 意味: `1 - (max(0, connectedComponentCount - 1) / max(1, cardCount - 1))`
  - 期待: 1.0 に近いほど一体、0.0 に近いほど分断
- `averageDegree`:
  - 意味: relation グラフの平均次数（`2 * |E| / max(1, cardCount)`）
  - 期待: 全体の接続密度の基準値として利用
- `degreeP95`:
  - 意味: card degree 分布の95パーセンタイル（nearest-rank）
  - 期待: 局所ハブの過密検知に利用
- `degreeSkewRatio`:
  - 意味: `degreeP95 / max(1, averageDegree)`
  - 期待: 1.0超で局所ハブ偏重の兆候
- `bridgeEdgeCount`:
  - 意味: 削除すると連結成分数が増える bridge edge 数（無向グラフ）
  - 期待: 値が高いほどボトルネック依存が高い

### Computation scope

- relation グラフの edge は以下を統合して構築する:
  - `evidenceLinks`（fromCardId/toCardId が既知カード）
  - `edges` の card-card 関係（fromKind/toKind が card または未指定）
- 自己ループは除外する。
- bridge 判定は正規化済み無向単純グラフで実施する。

### Metric definitions and formulas (FB-RM-RS-02)

集合を次のように定義する。

- `C`: 全カードID集合（`|C| = cardCount`）
- `E_evidence`: `evidenceLinks` のうち両端が `C` に含まれる link 集合
- `E_edge`: `edges` のうち card-card 関係（`fromKind/toKind` が `card` または未指定）かつ両端が `C` に含まれる集合
- `E`: `E_evidence ∪ E_edge` を無向単純グラフへ正規化した edge 集合（自己ループ除外・重複除去）
- `deg(v)`: 無向グラフ `G=(C,E)` における card `v` の次数

計算式:

- `connectedComponentCount = cc(G)`
- `largestComponentRatio = largestComponentSize(G) / max(1, |C|)`
- `connectivityScore = 1 - (max(0, connectedComponentCount - 1) / max(1, |C| - 1))`
- `isolationRate = isolatedCardCount / max(1, |C|)`
- `averageDegree = 2 * |E| / max(1, |C|)`
- `degreeP95 = percentile_nearest_rank({deg(v) | v ∈ C}, 95)`
  - nearest-rank: `rank = ceil(0.95 * n)`（`n=|C|`, 1-indexed）
- `degreeSkewRatio = degreeP95 / max(1, averageDegree)`
- `bridgeEdgeCount = |{ e ∈ E | cc(C, E \ {e}) > cc(G) }|`

意図:

- `connectedComponentCount`: 分断された島/論点群の多さを検知
- `largestComponentRatio`: 全体の一体性（最大連結塊への集中）を検知
- `connectivityScore`: 連結性の健全度を 0.0〜1.0 で比較
- `isolationRate`: 孤立カードの割合（孤立率）を比較
- `averageDegree`: 全体接続密度（平均的な結合度）を比較
- `degreeP95`: 局所ハブ偏重（過密接続）を検知
- `degreeSkewRatio`: 平均次数に対する偏り（ハブ偏重）を比較
- `bridgeEdgeCount`: 単一関係に依存する脆弱な接続（ボトルネック）を検知

決定論ルール:

- graph 正規化時に undirected pair をソートし、重複排除後も安定順序を維持する。
- bridge 判定 DFS は隣接ノードをID昇順で走査する。
- 小数は `round(value * 10_000) / 10_000` で丸める。
- これにより同一入力で同一 `diagnosticsData.structuralMetrics` を返す。

## E2E verification (FB-RM-RS-02)

- Playwright: `03_Implement/frontend/e2e/diagnostics_structural_metrics.spec.ts`
- Scope:
  - Share Panel から `document.json` を置換し、bundle export を実行する。
  - export された `diagnostics.md` に構造メトリクス行（`connectedComponentCount`, `largestComponentRatio`, `bridgeEdgeCount`, `isolationRate`, `connectivityScore`, `degreeSkewRatio`）が含まれることを確認する。
  - 同一入力で 2 回 export した `diagnostics.md` が一致すること（決定論）を確認する。

### Initial threshold hints (warning defaults)

- `connectedComponentCount >= 3`
- `largestComponentRatio < 0.7`
- `degreeP95 >= 6`
- `bridgeEdgeCount >= 5`

> しきい値は初期運用値であり、プロジェクトデータ特性に応じて調整する。

## Quality gate (Phase 1〜6, Doc-Ops-05 Set 2)

本書の更新時は、次の順序で品質ゲートを適用する。

1. **Phase 1: Scope固定**
   - 変更範囲を `04_Documentation/diagnostics.md` のみ（またはSet 2許可範囲）に限定する。
2. **Phase 2: 構造整合**
   - Audience / Goal / Public boundary が冒頭メタで判別できることを確認する。
3. **Phase 3: 用語整合**
   - review状態の語彙を `reviewed / unreviewed` に統一し、他表現を混在させない。
4. **Phase 4: 導線整合**
   - 関連正本（Architecture / Plans / 実装パス）への参照が維持されていることを確認する。
5. **Phase 5: 再現性整合**
   - E2E確認項目と期待結果（決定論確認を含む）が本文から追跡できることを確認する。
6. **Phase 6: 公開判定**
   - 公開不可情報がなく、Go/No-Go判断に必要な情報が本文だけで読めることを確認する。

失敗時は **最大3回まで修復して再判定** し、3回を超える場合は変更を停止して論点を `01_Plans/` にエスカレーションする。

## 共通ワークフローとフェイルセーフ（DOC-OPS-05 共通）

本書の更新は次の固定順序で実施する。

1. Phase 1 Read
2. Phase 2 ADR CDC（Context / Decision / Consequences）
3. Phase 3 Plan
4. Phase 4 Execute
5. Phase 5 Verify
6. Phase 6 Proceed

フェイルセーフ:

- Verify 失敗時は **自己修復を最大3回まで** 実施する。
- 4回目相当は作業を停止し、`01_Plans/issues/` にブロッカーを記録してエスカレーションする。

## Related

- `01_Plans/documentation_quality.md`
- `02_Architecture/schemas.md`
- `04_Documentation/diagnostics.md`（本書）
- `03_Implement/frontend/src/worker/diagnostics_protocol.ts`
- `03_Implement/frontend/src/worker/diagnostics_client.ts`
- `03_Implement/frontend/src/worker/diagnostics.worker.ts`


## Stream G docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **CDC**: Context / Decision / Consequences を明文化し、分類結果（Move internal / Improve external）を固定する。
3. **Plan**: AC/DoD を先に定義し、docs-only スコープ（`03_Implement/**` 非変更）を明示する。
4. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
5. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
6. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## Phase6 KPI/Audit 連携メモ（Stream F）

diagnostics の構造メトリクスは Gate D（KPI scorecard audit）の補助指標として扱えるが、**KPI定義そのものを置き換えない**。
運用時は次の直列を固定する。

1. KPI定義（TFS / Decision Readiness / Support Deflection / Feedback Closure）を `issue-0020` で確定。
2. 監査指標として diagnostics の該当メトリクス（`isolationRate`, `connectivityScore`, `bridgeEdgeCount` など）を補助参照。
3. Runbook判定は `operations.md` の Gate C→D→E と Proceed条件に従って記録する。

Fail-safe: diagnostics 指標とKPI判定が矛盾した場合は、Gate E の前に CDC（Context / Decision / Consequences）を作成し、未承認のしきい値変更を禁止する。
