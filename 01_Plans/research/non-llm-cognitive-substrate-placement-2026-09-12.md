# 非LLM認知基質の所有と配置 — SUI Sensemaking / SEI Cognition境界

- Status: Research / Non-normative
- Date: 2026-09-12
- Related: `COGNITIVE-ASSOC-01`, `fly-inspired-affinity-semantic-field-research-2026-09-10.md`

## 1. 根幹の趣旨

SUI Sensemakingが必要としているのは、LLMを常時呼び出さなくても、親和図作業の前段で「一緒に読んでみる価値のある組合せ」、近接のずれ、新奇性、孤立などを高速に浮上させられる認知支援である。

ここで重要なのは、**認知プリミティブの再利用性**と、**親和図法に固有の意味境界**を同じ実装責務へ混ぜないことである。

汎用の近傍想起や疎連想をSUI内部へ閉じ込めると、他用途で同じ仕組みを再実装しやすい。一方、親和図法に固有の「何を特徴として見るか」「候補をどう解釈するか」「人間の意味生成をどこで守るか」まで外部基盤へ移すと、SUIのProduct Valueと認知境界が外へ漏れる。

したがって、**再利用可能な非LLM認知基質と、SUI固有の認知adapterを分離する**。

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

SUI Sensemakingが自身で所有するもの:

- card本文・relation・layout・historyからどのfeatureを作るか
- lexical / graph / spatial / history channelの意味
- singleton / hold / Critique / residualの保護規則
- 「一緒に読んでみる価値がある」candidateとしての解釈
- 候補を島・表札・relationへ自動昇格させない境界
- 親和図法固有のbenchmark、human adjudication、受入判定

この分離により、SUIの意味論をSEI側へ移さず、認知計算の重複実装も避ける。

## 3. 所有とdeploymentは別

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

## 4. 認知処理の優先順位

SUIから見た実行順序は、重い方式へ段階的に上げる。

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

### 4.1 exact / deterministic

relation種別、hold状態、document contract、明示constraintなど、決定論で扱える情報はモデル化しない。

### 4.2 lexical sparse

文字n-gram、token、局所共起等を低負荷に扱う。表層candidate retrievalの第一候補とする。

### 4.3 sparse associative

複数channelを疎な高次元codeへ写し、局所的な近接・small-set bundle・noveltyを扱う。ここがSEI Cognition側の共通基質の中心となる。

### 4.4 static semantic

表層特徴と疎展開だけでは、語彙が離れた深層意味近接が不足する可能性がある。

その場合、attentionを持たないstatic embeddingを補助channelとして比較する。SUIからはmodel固有APIを直接呼ばず、adapterが出した意味vectorまたは上位dimensionを共通feature境界へ渡す。

### 4.5 LLM

LLMはdefault fallbackにしない。新規文章生成、高度な意味説明、非構造入力からの解釈など、軽量層では代替しにくい処理に限定する。

## 5. 現時点の実装境界

SEI Cognition方向の旧SOZA repositoryには、すでに`Sparse Associative Cognitive Substrate`というevaluation-only境界があり、Cognitive Methodそのものではなく複数Methodから利用できる認知プリミティブとして定義されている。

2026-09-12時点で、同領域に依存ゼロGo prototypeを追加する作業を進めている。SUI側へ同じkernelを複製実装しない。

SUIで先に実装してよいのは、将来の共通kernelへ渡すfeature projectionと、kernelから返るcandidateをproposalとして受け取るadapter境界までとする。

ただし、現在の`COGNITIVE-ASSOC-01` benchmarkではhuman adjudicationが完了していない。したがって、この配置方針や上流prototypeの進展を理由にsemantic baselineを実行しない。

## 6. 深層意味を一つの技術へ賭けない

FlyHash型の疎展開は、入力空間の近傍を軽量に保持するには有効でも、入力にない深層意味を自動的に生成しない。

したがって、共通基質の価値をFlyHash単体の成否と同一視しない。

- 表層・構造近接にはlexical sparse + sparse associative
- 文章意味の補完にはstatic semantic
- 文脈依存の複雑な意味には必要に応じてlocal encoder
- 文章生成や説明にはLLM

という分業を許す。

SUIにとっての採用判断は「どの技術が最も新しいか」ではなく、**必要な親和図上の発見を保ちつつ、常時使えるlatency / memoryで動くか**によって行う。

## 7. 次に接続する課題

本書はproduction topologyを確定するADRではない。

次の順でEvidenceを積む。

1. SEI Cognition側の汎用疎連想kernelをsynthetic taskで実装・計測する。
2. SUI側のhuman adjudicationを先に完了してbenchmarkを凍結する。
3. SUI固有feature projectionを定義する。
4. lexical sparse / sparse associative / static semanticを同一candidate contractで比較する。
5. latency / memory / candidate recall / false activation / singleton preservationを分離して評価する。
6. 結果から、in-process package、same-host helper、または採用見送りを判断する。
7. production API・永続schema・新しい安全境界が必要になった場合だけADRへ昇格する。
