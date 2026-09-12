# 非LLM認知基質の所有と配置 — SUI Sensemaking / SEI Cognition境界

- Status: Research / Non-normative
- Date: 2026-09-12
- Related: `COGNITIVE-ASSOC-01`, `fly-inspired-affinity-semantic-field-research-2026-09-10.md`, `information-network-query-and-qualitative-analysis-2026-09-12.md`

## 1. 根幹の趣旨

SEI Cognitionは認知場と簡易記憶を持ち、軽量な連想・意味処理・推論を行う認知主体として扱う。

SUI Sensemakingはその呼び出し元ではなく、**SEI、人間、外部AI、組織が共有可能な情報ネットワークを蓄積し、問いに応じて様々な様式へ整形して返す外在化されたsensemaking環境**として扱う。

SUIがSEIへ提供する価値は、単なる保存・検索ではない。

- 情報を空間・関係・来歴つきで蓄積する
- 問いに応じて情報ネットワークの一部を切り出す
- 近傍、比較、橋渡し、残余、時間、来歴等の異なる観点へ再構成する
- subgraph、card stack、空間配置、table、narrative等の様式へ投影する
- 外部collaboratorや外部systemから流入した情報を来歴つきで再利用可能にする

SEIはその結果を認知場へ取り込み、仮説・注意・次のqueryを更新する。

```text
SEI cognition
   │ inquiry / focus
   ▼
SUI information network
   │ selection / qualitative analysis / projection
   ▼
SEI cognition
   │ re-cognition / hypothesis update
   └─────────────── repeat
```

したがって、**再利用可能な非LLM認知基質、SUI固有の情報ネットワークQuery、親和図法固有の意味境界**を分離する。

## 2. 所有方針

再利用可能な認知基質は、SEI Cognition方向の共通認知基盤（現在の旧SOZA repository）へ寄せる。

SEI Cognition側が所有する候補:

- deterministic feature hashing
- sparse random expansion
- k-WTA / local competition
- compact sparse signature
- associative recall
- small-set bundle primitive
- novelty signal
- lightweight candidate index
- static semantic representationを差し込むための汎用境界
- 認知場・簡易記憶からquery intentを組み立てる上位制御

SUI Sensemakingが自身で所有するもの:

- 長期的・共有可能な情報ネットワーク
- card本文・relation・layout・history・provenance
- 情報ネットワークを選択・分析するQuery機能
- neighborhood / contrast / bridge / residual / temporal / provenance等のprojection
- subgraph / spatial / table / card stack / narrative等への整形
- 外部collaborationと来歴保持
- lexical / graph / spatial / history channelをSEIへ渡すprojection
- singleton / hold / Critique / residualの保護規則
- 候補を島・表札・relationへ自動昇格させない境界
- 親和図法固有のbenchmark、human adjudication、受入判定

この分離により、SEIがSUIの永続schemaやUIを抱えず、SUIもSEIの認知場や軽量推論器を内製し直さない。

## 3. SUI Queryは検索APIより広い

SUIのQueryは「該当recordを返す」だけに限定しない。

概念的には次の2段を持つ。

1. **Selection / Analysis** — 情報ネットワークの何を選び、どの関係・差・残余を見るか
2. **Projection / Presentation** — 選んだ情報をどの様式で返すか

同じ情報ネットワークから、問いによって異なるViewが成立してよい。

```text
information network
   ├─ neighborhood
   ├─ contrast
   ├─ bridge/path
   ├─ residual/unresolved
   ├─ temporal/process
   ├─ provenance/perspective
   └─ affinity/small-set
            │
            ▼
   subgraph / spatial / table /
   card stack / ordered readout / narrative
```

Query結果は派生Viewであり、Canonicalな意味や唯一の解釈ではない。元情報、source、scope、projection ruleへ戻れることを優先する。

## 4. 所有とdeploymentは別

```text
semantic / implementation ownership
        !=
runtime deployment topology
```

SEI Cognitionが基質を所有することは、SUIが毎回remote serviceを呼ぶことを意味しない。

高速・低memoryを優先するため、実行配置は次の順に比較する。

1. **in-process library / linked package**
   - 最小latency
   - network serialization不要
   - SUI processのmemoryへ直接載る
2. **same-host local helper**
   - process隔離が必要になった場合
   - Unix domain socket等のlocal IPCを候補にできる
3. **remote service**
   - 複数productで共有する実運用上の利点が、network hopと障害面の増加を上回る場合だけ検討

最初からservice化しない。

一方、SUIの情報ネットワークQuery自体はSUI側の責務であり、SEIはその内部DBやgraph implementationを知る必要がない。

## 5. 認知処理の優先順位

SEIから見た認知処理は、重い方式へ段階的に上げる。

```text
exact / deterministic
       ↓
lexical sparse
       ↓
sparse associative
       ↓
static semantic（必要な場合だけ）
       ↓
heavier local encoder（さらに必要な場合だけ）
       ↓
LLM（生成・高度な解釈が必要な場合だけ）
```

SUI Queryも、可能な範囲では決定論的なgraph traversal、filter、relation、time、provenance処理を先に使う。意味近接が必要な場合にだけSEIの疎連想・static semantic・local reasoningを補助的に利用する。

### 5.1 exact / deterministic

relation種別、hold状態、document contract、明示constraint、graph traversal、source/time filteringなど、決定論で扱える情報はモデル化しない。

### 5.2 lexical sparse

文字n-gram、token、局所共起等を低負荷に扱う。表層candidate retrievalの第一候補とする。

### 5.3 sparse associative

複数channelを疎な高次元codeへ写し、局所的な近接・small-set bundle・noveltyを扱う。ここがSEI Cognition側の共通基質の中心となる。

### 5.4 static semantic

表層特徴と疎展開だけでは、語彙が離れた深層意味近接が不足する可能性がある。

その場合、attentionを持たないstatic embeddingを補助channelとして比較する。SUIからはmodel固有APIを直接呼ばず、adapterが出した意味vectorまたは上位dimensionを共通feature境界へ渡す。

### 5.5 LLM

LLMはdefault fallbackにしない。新規文章生成、高度な意味説明、非構造入力からの解釈など、軽量層では代替しにくい処理に限定する。

## 6. 定性分析とgraph analyticsの境界

SUIは情報ネットワークの定性分析へ寄与するため、graph analyticsを候補探索に利用できる。

例:

- connected component
- k-hop neighborhood
- path / alternative path
- bridge / articulation candidate
- community candidate
- repeated motif
- temporal sequence
- source diversity
- local centrality

ただし、graph metricをそのまま意味へ昇格させない。

```text
graph metric
  → attention / query candidate
  != importance
  != truth
  != confidence
  != final interpretation
```

中心性が高いnodeが重要とは限らず、孤立したcardがノイズとも限らない。SUIは、むしろdominant structureから外れる情報もQuery対象として保持する。

## 7. 現時点の実装境界

SEI Cognition方向の旧SOZA repositoryには、`Sparse Associative Cognitive Substrate`というevaluation-only境界があり、Cognitive Methodそのものではなく複数Methodから利用できる認知プリミティブとして定義されている。

2026-09-12時点で、同領域には依存ゼロGo prototypeが入り、synthetic taskで疎展開・k-WTA・bundle・novelty・top-k retrievalの実行Evidenceまで進んでいる。SUI側へ同じkernelを複製実装しない。

SUIで先に進めるのは、情報ネットワークQueryの意味設計、feature projection、candidateをproposalとして受け取るadapter境界までとする。

ただし、現在の`COGNITIVE-ASSOC-01` benchmarkではhuman adjudicationが完了していない。したがって、この配置方針や上流prototypeの進展を理由にsemantic baselineを実行しない。

## 8. 深層意味を一つの技術へ賭けない

FlyHash型の疎展開は、入力空間の近傍を軽量に保持するには有効でも、入力にない深層意味を自動的に生成しない。

したがって、共通基質の価値をFlyHash単体の成否と同一視しない。

- graph / exact relationにはdeterministic query
- 表層・構造近接にはlexical sparse + sparse associative
- 文章意味の補完にはstatic semantic
- 文脈依存の複雑な意味には必要に応じてlocal encoder
- 文章生成や説明にはLLM

という分業を許す。

SUIにとっての採用判断は「どの技術が最も新しいか」ではなく、**情報ネットワークから新しい見え方・反証・残余・関係を取り出しつつ、常時使えるlatency / memoryで動くか**によって行う。

## 9. 次に接続する課題

本書はproduction topologyやQuery APIを確定するADRではない。

次の順でEvidenceを積む。

1. SUI Query Intentの最小語彙を整理する。
2. Selection / AnalysisとProjection / Presentationを分離したcontract候補を作る。
3. deterministic graph queryだけで有用な定性Viewをどこまで作れるかdogfoodする。
4. SUI側のhuman adjudicationを先に完了してsemantic benchmarkを凍結する。
5. SUI固有feature projectionを定義し、SEIのsparse associative kernelへ接続する。
6. lexical sparse / sparse associative / static semanticを同一candidate contractで比較する。
7. 同一queryをsubgraph / spatial / table / narrative等へ複数投影し、認知上の差を評価する。
8. 結果からin-process package、same-host helper、または採用見送りを判断する。
9. production API・永続schema・新しい安全境界が必要になった場合だけADRへ昇格する。
