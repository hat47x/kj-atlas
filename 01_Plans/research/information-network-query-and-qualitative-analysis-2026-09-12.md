# 情報ネットワークQueryと定性分析 — 設計根拠

- Status: Research rationale
- Date: 2026-09-12
- Formal contract: `02_Architecture/information_network_projection_contract.md`
- Related: `non-llm-cognitive-substrate-placement-2026-09-12.md`, `COGNITIVE-ASSOC-01`

## 1. 根幹の趣旨

SUI Sensemakingは、情報を単に保存・検索するrepositoryではない。

人間、SEI Cognition、生成AI、外部systemが蓄積した情報を一つの長期的・共有可能なInformation Networkとして保持し、問いに応じてその一部をSelection / Analysisし、複数様式へProjectionすることで、定性的理解と再探索を支援する。

```text
SEI / Human / AI / External system
        │ inquiry
        ▼
SUI Information Network
        │ materialize
        ▼
QualitativeNetworkSnapshot
        │ Query Intent
        ▼
Selection / Analysis
        │
        ▼
Context Projection
```

## 2. Query結果は派生View

Query結果はCanonicalな唯一解ではない。

- 元情報へ戻れる
- scope / method / projectionを追跡できる
- 未解決・矛盾・保留・孤立を消さない
- centralityや近接をtruth / importance / confidenceへ読み替えない
- View生成だけでInformation Networkを書き換えない

## 3. Query Intent

正式Intentはformal contractを正本とする。

- neighborhood
- contrast
- bridge
- residual
- unresolved
- temporal
- provenance
- affinity
- readout

### neighborhood

focus周辺のrelation、source、time、actor、spatial contextを返す。

### contrast

複数対象のshared / separate facets、relation、evidence、provenance差を並べる。差を自動的に対立へ読み替えない。

### bridge

二領域をつなぐ明示path、shared source / actor / temporal chain、後続tierによる暗黙bridge候補を返す。pathの短さを意味強度と同一視しない。

### residual / unresolved

singleton、hold、critique、未接続、provenance gap、contradiction、pending review、少数意見を意図的に残す。

### temporal

観測、revision、判断変更、proposal / review / apply等を時間順に読む。時間順をcausalityへ読み替えない。

### provenance

source、observer、contributor、AI/human、provider、external system等の経路を保持する。

### affinity

少数の情報を一緒に読む価値がある候補を返す。自動island形成ではない。

### readout

選択済み構造をtable、card stack、subgraph、spatial layout、narrative等へ投影する。

## 4. SelectionとProjectionを分ける

```text
Intent: contrast(A, B)

Selection / Analysis
  shared / A-only / B-only / contradictions / provenance

Projection
  Human -> spatial_layout + comparison_table
  Generative AI -> bounded structured context
  SEI -> subgraph
  External system -> typed machine-readable result
```

同一selectionを複数Formへ投影できることを原則とする。

## 5. 定性分析とgraph analytics

利用候補:

- connected components
- k-hop traversal
- shortest / alternative paths
- bridge / articulation candidate
- community / motif candidate
- temporal sequence
- source diversity
- local centrality

ただし、

```text
graph metric
  -> attention / candidate
  != importance
  != truth
  != confidence
  != final interpretation
```

とする。

## 6. SEI Cognitionとの責務分離

SEIは現在の目的・注意・簡易記憶・推論を持つ。

SUIは共有情報空間、provenance、history、collaboration state、Query / Projectionを持つ。

SEIが全情報を内部memoryへ複製する必要はなく、必要なときにSUIへ再queryできることを重視する。

## 7. 外部collaboration

同じInformation Networkへ次が参加できる。

- Human
- multiple SEI instances
- Generative AI
- MCP / external tools
- TEI等の別product
- imported datasets / sources

追加情報はactor / source / provider等のprovenanceを失わず保持する。

## 8. 非目標

- graph DBそのものになること
- network metricで重要情報を自動決定すること
- ProjectionをCanonicalな結論として保存すること
- 全QueryでLLMを必須にすること
- 一つの可視化方式へ固定すること
- residual / ambiguityをnoiseとして除去すること

## 9. 最終設計への収束

初期研究では既存Documentや旧Context contractへの対応可能性を検討していたが、最終設計ではその互換を要件にしない。

正式なターゲットは `02_Architecture/information_network_projection_contract.md` のみとする。

実装順は次へ固定する。

1. formal `QualitativeNetworkSnapshot` + `ContextProjectionRequest`
2. D0 deterministic selection / projection
3. D1 lexical sparse
4. D2 SEI sparse associative cognition
5. D3 static semantic
6. D4 bounded local SLM
7. D5 stronger model / human-led synthesis
8. WorkingGraph / ConsensusGraphの正式永続実装

旧Document / Query / Bundleへのadapterは作らない。
