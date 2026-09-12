# D0 Deterministic Qualitative Query

- Status: Executable reference for the formal query contract
- Date: 2026-09-12
- Formal contract: `../../../02_Architecture/information_network_projection_contract.md`
- Parent: `../query-intent-execution-ladder-2026-09-12.md`

## 1. 根幹の趣旨

SUI Sensemakingの定性分析を、最初から生成AIへ委ねない。

正式 `QualitativeNetworkSnapshot` が持つrelation、配置、時間、provenance、hold、Critique、contradiction、review stateから、意味推論なしで再現可能な見方をD0として切り出す。

D0は次を扱う。

- neighborhood
- contrast
- bridge
- residual
- unresolved
- temporal
- provenance

D0は次を行わない。

- 内容価値のscore / confidence / importance / rank化
- path lengthやdegreeの意味強度化
- semantic similarityの推測
- island / relation / Consensusの自動確定
- generated narrative
- source networkの変更

## 2. 正式pipeline

```text
SUI Information Network
        ↓ materialize
QualitativeNetworkSnapshot
        ↓
ContextProjectionRequest
        ↓
D0 Selection / Analysis
        ↓
Deterministic Projection
        ├─ subgraph
        ├─ path_list
        ├─ card_stack
        ├─ comparison_table
        ├─ spatial_layout
        ├─ timeline
        └─ provenance_matrix
```

旧Document / Query / Bundle contractへのcompileまたはadapterは置かない。

## 3. 実行物

- `projection_request.py`: 正式ContextProjectionRequestのclosed-world validation
- `query_engine.py`: D0 selection / analysis
- `projection.py`: deterministic projection formatter
- `execute_projection_request.py`: Request → review visibility → D0 → Projection
- `fixtures/network.json`: `QualitativeNetworkSnapshot`の実行fixture
- `fixtures/projection_requests.json`: Human / Generative AI / SEI request fixture
- `test_projection_request.py`: formal request / permission boundary tests
- `test_query_engine.py`: D0 query / invariant tests
- `test_projection_e2e.py`: multi-actor end-to-end tests

fixtureは保存schemaではなく、正式なQuery substrate contractの例である。

## 4. Residual

Residualは「低スコア」を意味しない。理由を別々に返す。

- `singleton_island`
- `held_or_pending`
- `has_critique`
- `unconnected`
- `unresolved_contradiction`
- `missing_provenance`

一つのnodeが複数理由を持ってよい。理由数でrankingしない。

## 5. Bridge

D0では明示edge上のpathだけを扱う。

- shortest pathが短い = 意味が強い、とはしない
- shortest pathが複数なら決定論的順序で複数返す
- pathが無いことを「無関係」と断定しない
- D2/D3の暗黙bridge候補はD0と別channelで保持する

## 6. Multi-actor boundary

同一permission / scope / inquiry / focusでは、Human / Generative AI / SEIのactor identityだけを理由にselectionを変えない。

Actor差はまずProjection Formとして表す。

未レビュー情報は、server-resolved permissionとtrusted SafeMode allowanceの双方が許可した場合だけsnapshotへ含める。

## 7. 次の実装順

D0は最終architectureの最下層として維持し、次は互換作業を挟まず直接進む。

1. D1 lexical sparse
2. D2 SEI sparse associative cognition
3. D3 static semantic（必要Intentのみ）
4. D4 bounded local SLM
5. Human / AI / SEI / External systemのdogfood
6. WorkingGraph / ConsensusGraphの正式永続実装
