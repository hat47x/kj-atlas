# 情報ネットワークQueryと定性分析 — SUI Sensemakingの役割整理

- Status: Research / Non-normative
- Date: 2026-09-12
- Related: `non-llm-cognitive-substrate-placement-2026-09-12.md`, `COGNITIVE-ASSOC-01`

## 1. 根幹の趣旨

SUI Sensemakingは、情報を単に保存・検索するだけのrepositoryではない。

人間、SEI Cognition、外部AI、組織内の他者が蓄積した情報を一つの情報ネットワークとして保持し、**問いに応じて、そのネットワークを異なる様式へ整形・投影して返すことで、定性的な理解と再探索に寄与する環境**として扱う。

SEI Cognitionとの関係では、SEIが認知場と簡易記憶を持ち、SUIはその外部にある長期的・共有可能な情報空間となる。

```text
SEI Cognition
  認知場 / 簡易記憶 / 推論
        │
        │ query intent
        ▼
SUI Sensemaking
  情報集積 / 関係 / 配置 / 来歴 / 協働
        │
        │ qualitative projection
        ▼
SEI Cognition
  再認知 / 仮説更新 / 次の問い
```

SUIのQueryは「該当データを返す」だけではなく、**情報ネットワークのどの側面を、どの形で見れば現在の問いを考えやすいかを構成する**ことを主眼とする。

## 2. Query結果は正解ではなく派生View

Queryによる整形結果はCanonicalな意味や唯一の解釈ではない。

同じ情報ネットワークから、問いや目的に応じて複数のViewが成立してよい。

```text
Canonical information network
          │
          ├─ neighborhood view
          ├─ contrast view
          ├─ bridge view
          ├─ residual view
          ├─ temporal view
          ├─ provenance view
          ├─ affinity view
          └─ narrative/readout view
```

したがって、Query結果は次を満たす。

- 元情報へ戻れる
- どのscope / rule / projectionで作られたか追跡できる
- 未解決・矛盾・保留・孤立を消さない
- 表示上の中心性や近接を、真理・重要度・確信度へ読み替えない
- Viewの生成だけでCanonical Graphを書き換えない

## 3. SUIが持つべきQueryの種類

### 3.1 Focus / Neighborhood

あるcard、島、概念、人物、出来事、問い等を中心に、その周辺を返す。

例:

- 1-hop / 2-hopのrelation近傍
- 同じsource / time / actorを共有する情報
- lexical / semantic / spatial / interaction近接
- 現在のfocusと関係するが、まだ島に属していないcard

用途は「この対象の周辺で何が起きているか」を見ること。

### 3.2 Contrast / Difference

二つ以上の対象を並べ、共通点・差異・片側にしかない情報を返す。

例:

- AとBで共有するrelation
- Aだけが持つsource / claim / observation
- 同じ語彙だが立場や因果方向が異なるcard
- 同じ島候補に見えるが分離を保つべき差

用途は早すぎる同一視を防ぐこと。

### 3.3 Bridge / Path

離れている二領域をつなぐ中間card、relation、source、actor、time sequence等を返す。

用途は「なぜこの二つが関係し得るのか」「どこで接続が切れているのか」を探索すること。

pathの短さを意味の強さと同一視しない。

### 3.4 Residual / Outlier / Unresolved

既存の束・中心テーマ・頻出relationから外れた情報を意図的に返す。

- singleton
- held
- critique
- 未接続card
- source不足
- contradictory observations
- dominant clusterへ吸収されない少数意見

用途は「今の理解が何を取りこぼしているか」を見ること。

### 3.5 Temporal / Process

情報ネットワークを時間やrevisionの軸で整形する。

- 観測順
- 判断変更
- 仮説の生成・棄却
- 島の分割・統合
- 外部情報の流入
- collaboratorごとの追加・修正

用途は、現在の構造だけでなく「どのようにここへ来たか」を読むこと。

### 3.6 Provenance / Perspective

source、observer、contributor、AI/human、組織、document、external provider等の違いで投影する。

用途は「誰の視点・どの資料・どの経路が現在の理解を支えているか」を確認すること。

### 3.7 Affinity / Small-set

2〜3枚程度を一緒に読んだときに立ち上がるまとまりを候補として返す。

これは自動島形成ではない。SEIまたは人間が再度読むためのquery resultである。

### 3.8 Readout / Narrative

networkの一部を、順序のある説明、比較表、箇条書き、カード束、graph fragment等へ整形する。

LLMを利用する場合も、元node / edge / sourceへ戻れる参照を保持する。

## 4. 返却様式をQuery意図から分離する

同じQuery intentでも、返し方は複数あり得る。

```text
Intent: "AとBの間に何があるか"

Projection candidates:
- subgraph
- ordered path list
- card stack
- comparison table
- spatial arrangement
- provenance matrix
- compact narrative
```

そのため、Queryは概念的に次の2段へ分ける。

1. **Selection / Analysis** — 何を含めるか
2. **Projection / Presentation** — どの様式で返すか

SUIの価値は、検索アルゴリズムだけでなく、この二段を組み合わせて**情報ネットワークを多面的に読めること**にある。

## 5. 定性分析へ寄与するための原則

SUIはgraph analyticsを導入してよいが、数値をそのまま意味判断へ昇格させない。

利用候補:

- connected components
- k-hop traversal
- shortest / alternative paths
- bridge / articulation candidate
- community detection
- motif / repeated relation pattern
- temporal sequence
- source diversity
- local centrality

これらは、次のように扱う。

```text
graph metric
  → attention / query candidate
  != importance
  != truth
  != confidence
  != final interpretation
```

数値は内部の探索補助として利用できるが、利用者へ内容の価値順位として提示しない。

## 6. SEI Cognitionとの責務分離

SEIは問い・目的・現在の認知状態を持つ。

SUIはそれを受けて、情報ネットワークの適切な部分と投影を返す。

概念的な呼出しは次のように考える。

```text
SEI -> SUI.query(
  focus,
  inquiry,
  scope,
  relation_preferences,
  diversity_need,
  unresolved_need,
  projection_hint
)

SUI -> SEI
  selected_nodes
  selected_edges
  groups
  residuals
  paths
  provenance
  temporal_context
  projection
  reconstruction_metadata
```

SEIはこの結果を認知場へ取り込み、必要に応じて再queryする。

SUIがSEIの仮説そのものを所有する必要はない。SEIの簡易記憶が失われても、SUI側に外在化されたcard / relation / source / revision / collaboration historyから再び探索できることが望ましい。

## 7. 外部collaborationとの関係

SUIはSEI専用のbackendではない。

同じ情報ネットワークへ、次が参加できる。

- 人間
- 複数のSEI instance
- 外部AI
- MCP / external tools
- TEI等の別product
- imported documents / datasets

SUIは、それぞれが追加した情報を来歴つきで保持し、query時にperspective / source / contributorを保持したまま返す。

これにより、SEIは外部主体とのintegrationを一つずつ直接抱えず、SUIを通して共有可能な情報ネットワークへ参加できる。

## 8. 非目標

- graph DBそのものになること
- network metricで自動的に重要情報を決めること
- Query結果をCanonicalな結論として保存すること
- すべてのQueryへLLMを必須にすること
- 一つの最適な可視化方式へ固定すること
- residual / ambiguityをnoiseとして除外すること

## 9. 次の設計課題

本書の順序から、次の課題へ展開する。

1. Query Intentの最小語彙を定義する。
2. SelectionとProjectionを分離した内部contract候補を作る。
3. 既存Document / Card / Edge / Island / provenanceとの対応を確認する。
4. deterministic graph queryで実現できる範囲を先に実装する。
5. sparse associative cognitionをcandidate selectionの補助として接続する。
6. static semantic / local LLMを、必要なqueryだけに追加する。
7. 同一queryをsubgraph / spatial / table / narrative等へ複数投影できるかdogfoodする。
8. 情報ネットワークの定性分析が実際に新しい気づき・反証・残余発見へ寄与したかを評価する。

production API、Canonical Graphの新型、永続Query View等が必要だと確認できるまでは、研究境界に留める。
