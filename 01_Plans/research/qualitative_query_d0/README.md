# D0 Deterministic Qualitative Query — executable research slice

- Status: Research / Non-normative
- Date: 2026-09-12
- Parent: `../query-intent-execution-ladder-2026-09-12.md`
- Related: `../information-network-query-and-qualitative-analysis-2026-09-12.md`, `../actor-role-interest-context-projection-contract-2026-09-12.md`

## 1. 根幹の趣旨

SUI Sensemakingの定性分析を、最初から生成AIへ委ねない。

情報ネットワークがすでに持つ関係、配置、時間、来歴、保留、Critique、矛盾、review状態を使い、**意味解釈を追加しなくても再現可能に切り出せる定性的な見方**をD0として外在化する。

D0は次を行う。

- neighborhood: relation graph上の近傍を切り出す
- contrast: A/Bの構造・来歴・状態の共通点と差を並べる
- bridge: 離れた領域を結ぶgraph path候補を返す
- residual: 現在のまとまりから取りこぼしやすい情報を理由つきで列挙する
- unresolved: hold、Critique、未解決contradiction、未review等を列挙する
- temporal: event / revision / observationを時間順に投影する
- provenance: source / contributor / provider別に元情報への経路を返す

D0は次を行わない。

- 内容の重要度をscore化する
- path lengthやdegreeを意味の強さへ読み替える
- semantic similarityを推測する
- 島・relation・Consensusを自動確定する
- LLMを呼ぶ
- Canonicalな情報ネットワークを書き換える

## 2. SelectionとProjectionを分ける

```text
Synthetic information network
          │
          ▼
D0 Selection / Analysis
          │
          ├─ neighborhood selection
          ├─ contrast facets
          ├─ bridge paths
          ├─ residual reasons
          ├─ unresolved reasons
          ├─ temporal records
          └─ provenance groups
          │
          ▼
Deterministic Projection
          ├─ subgraph
          ├─ path_list
          ├─ card_stack
          ├─ comparison_table
          ├─ spatial_layout
          ├─ timeline
          └─ provenance_matrix
```

同じselectionをHuman / Generative AI / SEIへ異なる形で返しても、selection根拠は同じまま保持する。

## 3. Synthetic network

first sliceではproduction `DocumentV1`へ直接依存しない。必要な概念だけを持つ小さなresearch fixtureを使う。

- nodes
  - `id`, `kind`, `text`
  - optional `islandId`, `holdState`, `reviewState`, `x`, `y`, `observedAt`
  - `sourceRefs`, `actorRefs`
- edges
  - `id`, `fromId`, `toId`, `type`, `directed`, optional `createdAt`
- critiques
  - `id`, `targetRef`, `type`, `state`, optional `createdAt`
- contradictions
  - `id`, `fromId`, `toId`, `state`, optional `createdAt`
- events
  - `id`, `kind`, `targetRefs`, `at`, optional `actorRef`, `sourceRef`
- sources
  - `id`, `kind`, optional `label`

fixtureはproduction schema案ではない。

## 4. Residualの考え方

Residualは「低スコア」を意味しない。理由を別々に返す。

初期理由:

- `singleton_island`
- `held_or_pending`
- `has_critique`
- `unconnected`
- `unresolved_contradiction`
- `missing_provenance`

一つのnodeが複数理由を持ってよい。理由数でrankingしない。

## 5. Bridgeの考え方

D0では明示edge上のshortest path候補だけを扱う。

- pathが短い = 意味が強い、とはしない
- shortest pathが複数なら決定論的順序で複数返す
- pathが無いことを「無関係」と断定しない

D2/D3で暗黙のbridge候補を追加する場合も、D0 pathと別channelで保持する。

## 6. 実行物

- `query_engine.py`: deterministic selection / analysis
- `projection.py`: deterministic projection formatter
- `fixtures/network.json`: synthetic information network
- `test_query_engine.py`: queryと停止線のunit tests

## 7. 次へ進む条件

D0で次を確認してからD1/D2へ進む。

1. 各queryが同一fixtureから決定論的に再生成できる。
2. residual / unresolvedがscoreではなく理由として残る。
3. bridge pathがmeaning rankingへ昇格しない。
4. provenanceと元node/edgeへのtraceを保持できる。
5. 同じselectionを複数Projection Formへ変換できる。
6. query結果生成だけではsource networkが変更されない。

production API / schemaへはまだ昇格させない。
