# Query Intent 実行階層 — 定性分析を軽量層から積み上げる

- Status: Research / Non-normative
- Date: 2026-09-12
- Parent: `information-network-query-and-qualitative-analysis-2026-09-12.md`
- Related: `actor-role-interest-context-projection-contract-2026-09-12.md`

## 1. 根幹の趣旨

SUIのQueryは、生成AIに自然言語で質問を投げるためのwrapperではない。

情報ネットワークが既に持つ構造・配置・時間・来歴・レビュー状態を最大限使い、**定性的に意味のある切り口を、できるだけ高速・低メモリ・再現可能な処理で作る**ことを第一とする。

処理階層は次の順に上げる。

```text
D0 exact / deterministic
      ↓ 不足時のみ
D1 lexical / sparse retrieval
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

## 2. Queryごとの第一責務

| Intent | 最初に使う処理 | 補完候補 | LLMを使う場合 |
|---|---|---|---|
| neighborhood | relation traversal, source/time/actor filter, spatial proximity | lexical / sparse associative | 説明が必要な場合だけ |
| contrast | set intersection/difference, relation/evidence差分 | static semantic, sparse associative | 差異の言語化・別解 |
| bridge | graph path / shared source / shared actor / temporal chain | sparse associative, static semantic | 暗黙橋の仮説説明 |
| residual | singleton, hold, critique, unconnected, low-support detection | novelty / sparse associative | 原則不要。意味解釈時のみ |
| unresolved | contradiction state, pending review, unresolved critique | sparse associative | 論点の文章化 |
| temporal | revision/event ordering, before/after diff | motif detection | process narrativeが必要な場合 |
| provenance | source/contributor/provider traversal | source diversity calculation | 原則不要 |
| affinity | small-set candidate generation | sparse associative + static semantic | 2〜3枚の訴えの仮説化のみ |
| readout | 既に選択済みの構造を整形 | template / deterministic formatter | narrative生成が必要な場合 |

## 3. D0 — deterministic qualitative analysis

「定性分析」は必ずしも生成モデルを意味しない。

### 3.1 Neighborhood

- k-hop relation traversal
- same source / actor / document / time-window
- spatial vicinity
- same island / outside current island
- review / hold / critique filter

返却時にhop数や近接度をimportanceへ変換しない。

### 3.2 Contrast

A/Bについて次を分離する。

- shared refs
- A-only refs
- B-only refs
- supporting evidence difference
- contradictory evidence difference
- provenance difference
- temporal difference
- hold / review state difference

「異なる」を「対立」と自動解釈しない。

### 3.3 Bridge

- shortest path
- alternative path
- shared source
- shared actor
- shared evidence
- temporal handoff
- articulation candidate

path lengthやcentralityを意味の強さへ昇格させない。

### 3.4 Residual / Unresolved

- singleton island
- pending / held / shelved
- critique attached
- no relation / weakly connected
- contradictory evidence unresolved
- source unavailable / missing grounding
- current projectionから除外されたがscope内に存在するもの

「外れ」をnoiseとみなさない。

### 3.5 Temporal / Provenance

- immutable/revision timestamp順
- proposal → review → apply trace
- source chain
- contributor / provider separation
- imported vs locally authored

時間順を因果関係と自動解釈しない。

## 4. D1〜D3 — 非生成の認知補完

### D1 lexical / sparse retrieval

文字n-gram、token、BM25系等で表層的に関連する候補を高速に増やす。

### D2 sparse associative cognition

SEI Cognition側の共通基質を利用し、複数channelの疎な連想、novelty、small-set bundleを候補生成へ使う。

SUIはfeature meaningを所有する。

例:

- lexical channel
- relation motif
- spatial context
- temporal context
- provenance
- human interaction / critique history

activationはtruth/confidenceではない。

### D3 static semantic

表層語彙が離れているが意味的に近い候補の回収に限定して追加する。

static semanticの近さだけで島・relation・consensusを生成しない。

## 5. D4 — bounded local SLM

local SLMへ全Documentを渡さない。

D0〜D3で作ったbounded Working Setを入力する。

適する仕事:

- contrastの意味を短く説明する
- bridge candidateが何を媒介し得るか仮説化する
- 2〜3枚のaffinity candidateから複数の読みを出す
- contradictionを「何が食い違っているか」へ言語化する
- readoutを人間向け文章へする

適さない仕事:

- authorization
- source existence判定
- graph traversal
- review state判定
- ConsensusGraph更新
- human_reviewed昇格
- importance ranking

## 6. D5へ上げる条件

stronger modelまたはhuman-led synthesisへ上げるのは、少なくとも次の一つがある場合に限定する。

- current external evidenceが必要
- local SLMのcontext capacityを越える
- novel domainで既存情報ネットワークに十分な根拠がない
- high-stakes判断
- 複数領域をまたぐ広い統合
- 外部collaboratorとの正式な共有文書化

単に「local modelの答えが気に入らない」ことを自動escalation条件にしない。

## 7. Actorによる違いはtierではなくinterfaceを中心にする

人間だから重いモデル、SEIだから軽いモデル、という固定をしない。

同じselectionでも返却interfaceが異なる。

```text
same selected evidence
  ├─ Human -> spatial + card + comparison
  ├─ Generative AI -> bounded structured context
  ├─ SEI -> compact subgraph + features + residuals
  └─ External system -> typed machine-readable projection
```

Actor kindを処理品質の序列として扱わない。

## 8. Query結果の合成

最終Query resultは、単一modelの出力ではなく、複数channelを並存させられる。

例:

```text
contrast result
  deterministic:
    shared = [...]
    a_only = [...]
    b_only = [...]
    contradictory = [...]
  associative_candidates:
    [...]
  semantic_candidates:
    [...]
  generated_interpretations:
    [...]
  residuals:
    [...]
  provenance:
    [...]
```

channel間の不一致を一つのscoreへ潰さない。

- lexical near / human separate
- graph near / spatial far
- semantic near / provenance conflict
- AI proposes / human holds

といった不一致そのものが定性分析の材料になる。

## 9. 実装順

1. D0 Queryをsynthetic networkで実装・検証する。
2. R0 Actor-aware ProjectionからD0 Queryを呼べるようにする。
3. D1 lexicalを追加する。
4. D2 SEI sparse associative substrateとのadapterを追加する。
5. D3 static semanticを必要なIntentだけで比較する。
6. D4 local SLMはbounded Working Setが安定した後に接続する。
7. human / AI / SEIで同一selectionを異なるProjectionへ返してdogfoodする。
8. 各tierの追加で新しい発見が増えたか、残余や異論を消していないかを分離評価する。

production APIや永続schemaの変更は、上記で必要性が実証されるまで行わない。
