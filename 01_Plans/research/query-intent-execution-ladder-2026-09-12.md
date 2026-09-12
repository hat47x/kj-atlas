# Query Intent 実行階層 — 定性分析を軽量層から積み上げる

- Status: Research rationale / execution strategy
- Date: 2026-09-12
- Formal contract: `02_Architecture/information_network_projection_contract.md`
- Parent: `information-network-query-and-qualitative-analysis-2026-09-12.md`

## 1. 根幹の趣旨

SUIのQueryは生成AI wrapperではない。

正式 `QualitativeNetworkSnapshot` が持つ構造・配置・時間・provenance・review / hold / critique状態を最大限使い、定性的に意味のある切り口を高速・低メモリ・再現可能に作る。

処理階層は次の順に上げる。

```text
D0 deterministic structure
      ↓ 不足時のみ
D1 lexical sparse retrieval
      ↓ 不足時のみ
D2 sparse associative cognition
      ↓ 不足時のみ
D3 static semantic representation
      ↓ 不足時のみ
D4 bounded local SLM
      ↓ high novelty / high stakes / broad synthesisのみ
D5 stronger model / human-led synthesis
```

上位tierへ進んでも、下位tierの根拠・選択過程を捨てない。

## 2. Intentごとの第一責務

| Intent | 最初に使う処理 | 補完候補 | LLMを使う場合 |
|---|---|---|---|
| neighborhood | relation traversal, source/time/actor filter, spatial proximity | D1/D2 | 説明が必要な場合だけ |
| contrast | set intersection/difference, relation/evidence差分 | D2/D3 | 差異の言語化・別解 |
| bridge | graph path / shared source / shared actor / temporal chain | D2/D3 | 暗黙橋の仮説説明 |
| residual | singleton, hold, critique, unconnected, provenance gap | D2 novelty | 原則不要 |
| unresolved | contradiction, pending review, unresolved critique | D2 | 論点の文章化 |
| temporal | event ordering, before/after diff | motif detection | process narrativeのみ |
| provenance | source/contributor/provider traversal | source diversity | 原則不要 |
| affinity | small-set candidate generation | D2 + D3 | 2〜3件の読みの仮説化 |
| readout | 選択済み構造の整形 | deterministic formatter | narrative生成時のみ |

## 3. D0 — deterministic qualitative analysis

D0は意味推論なしで次を扱う。

- k-hop neighborhood
- structural contrast
- explicit shortest / alternative paths
- residual reasons
- unresolved state
- temporal ordering
- provenance grouping

停止線:

- hop数、degree、path lengthをimportanceへ変換しない
- 「異なる」を「対立」と自動解釈しない
- no explicit pathを`unrelated`と断定しない
- residualをnoiseとみなさない
- time orderをcausalityへ読み替えない

## 4. D1 — lexical sparse retrieval

文字n-gram、token、BM25系等で、明示relation外にある表層的近接候補を増やす。

D1の結果はD0とは別channelで保持し、表層語彙が近いことを意味的一致へ昇格させない。

## 5. D2 — sparse associative cognition

SEI Cognition側の共通認知基質を利用し、複数channelの疎連想、新奇性、small-set candidateを生成する。

SUI側が意味を所有するchannel例:

- lexical
- relation motif
- spatial context
- temporal context
- provenance
- human interaction / critique history

activationはtruth/confidenceではない。

## 6. D3 — static semantic

表層語彙が離れているが意味的に近い候補の回収へ限定して追加する。

semantic proximityだけでisland / relation / consensusを生成しない。

## 7. D4 — bounded local SLM

local SLMへ情報ネットワーク全体を渡さない。D0〜D3で選ばれたbounded selectionだけを入力する。

適する仕事:

- contrastの意味を短く説明する
- bridge candidateが何を媒介し得るか仮説化する
- affinity candidateへ複数の読みを出す
- contradictionの食い違いを言語化する
- readoutを人間向け文章へする

適さない仕事:

- authorization
- graph traversal
- review state判定
- ConsensusGraph更新
- human_reviewed昇格
- importance ranking

## 8. D5へ上げる条件

- current external evidenceが必要
- local SLMのcontext capacityを越える
- novel domainでnetwork内根拠が不足
- high-stakes判断
- 複数領域をまたぐ広い統合
- 外部共有向け正式文書化

単にlocal modelの出力が気に入らないことを自動escalation条件にしない。

## 9. Actor差はtierよりProjection Form

同じselectionでも返却interfaceを変えられる。

```text
same selected evidence
  ├─ Human -> spatial + card + comparison
  ├─ Generative AI -> bounded structured context
  ├─ SEI -> compact subgraph + residuals
  └─ External system -> typed machine-readable projection
```

Actor kindを処理品質の序列にしない。

## 10. Multi-channel result

最終resultは単一scoreへ畳まず、channelを並存させる。

```text
selection
  deterministic: ...
  lexical_candidates: ...
  associative_candidates: ...
  semantic_candidates: ...
  generated_interpretations: ...
  residuals: ...
  provenance: ...
```

`lexical near / human separate`、`graph near / spatial far`、`semantic near / provenance conflict`等の不一致そのものを情報として残す。

## 11. 実装順

D0と正式ContextProjectionRequestの接続は完了対象とする。以後は互換adapterを挟まず次へ進む。

1. D1 lexical sparseを追加する
2. D2 SEI sparse associative substrateを接続する
3. D3 static semanticを必要Intentだけへ追加する
4. D4 local SLMをbounded selection後へ接続する
5. Human / AI / SEI / External systemでdogfoodする
6. 各tierの独立増分とanchoring副作用を分離評価する
7. WorkingGraph / ConsensusGraphの永続実装をformal contractへ直接合わせる
