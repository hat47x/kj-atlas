# 多主体の認知合意形成場 — SUI Sensemakingの上位役割

- Status: Research / Non-normative
- Date: 2026-09-12
- Related: `information-network-query-and-qualitative-analysis-2026-09-12.md`, `non-llm-cognitive-substrate-placement-2026-09-12.md`, `00_Prompt/domain.md`

## 1. 根幹の趣旨

SUI Sensemakingは、単一の人間または単一のAIが情報を整理するためだけの道具ではない。

**人間、生成AI、SEI Cognition、外部の協力者やシステムが、それぞれ異なる関心・能力・責任・インターフェースを持ったまま同じ情報ネットワークへ参加し、どこまで認知を共有できるかを形成する場**として捉える。

ここでいう「合意形成」は、全主体を一つの結論へ収束させることではない。

- 一致している点
- 異なる見方
- 未解決の対立
- 保留
- 少数意見
- まだ誰も十分に理解していない領域

を区別したまま、**共有可能な認知状態を育てること**を指す。

SUIは合意を強制しない。むしろ、合意できていない場所を失わずに扱えることが重要である。

```text
Human Working View ─┐
Generative AI View ─┼─> SUI shared information network
SEI Cognitive View ─┤          │
External Actor View ┘          │
                               ├─ agreed / approved
                               ├─ divergent
                               ├─ held
                               ├─ unresolved
                               └─ provenance-preserved
```

## 2. 主体ごとに同じ世界を同じ形で見せない

参加主体は同一のinterface・同一のcontext・同一の目的を持たない。

SUIは「全情報を一つの巨大promptとして全主体へ渡す」構成を避ける。

各主体には、役割と現在の関心に応じたContext Projectionを返す。

```text
shared information network
          │
          ├─ Human projection
          ├─ Generative AI projection
          ├─ SEI projection
          └─ External collaborator projection
```

Projectionはアクセス制御だけではなく、**認知上の焦点を調整するinterface**でもある。

同じ元情報から異なるprojectionが生成されてもよい。どのprojectionもCanonicalな唯一の見方ではない。

## 3. 主体ごとの基本役割

### 3.1 人間

人間は、意味・価値・違和感・責任を引き受ける主体である。

主な関心:

- 自分や他者の経験・文脈を壊さないこと
- 何がしっくり来ないか
- どこまでなら共有・承認できるか
- 何をまだ決めないか
- 他者やAIの提案をどう受け取るか

主なinterface:

- 空間配置
- card / relation / island
- hold / critique
- compare / query / filter
- annotation
- proposal review
- patch approval / reject
- collaborative discussion

人間が最終的な意味判断・承認責任を持つ領域を、生成AIやSEIが自動で奪わない。

### 3.2 生成AI

生成AIは、共有情報を別の角度から読み直し、仮説・説明・比較・代案・文章化を提案する主体である。

主な関心:

- 問いに必要なcontextを得ること
- 複数の見方を生成すること
- 暗黙の関係を言語化すること
- 反例・欠落・別解を提示すること
- 人間やSEIが利用できる形に説明すること

主なinterface:

- ContextProjectionGraph
- bounded context query
- structured query result
- proposal / patch
- critique candidate
- narrative / summary draft

生成AIはConsensus Graphを直接更新せず、proposalとして差分を返す。

### 3.3 SEI Cognition

SEIは、認知場・簡易記憶・常時軽量な連想・注意制御・必要に応じたlocal reasoningを持つ認知主体として扱う。

主な関心:

- 現在の問いに関連する情報
- 新奇性
- 近接・離隔
- 未解決
- 矛盾候補
- 次に調べるべき領域
- 何を人間または生成AIへ渡すべきか

主なinterface:

- machine-oriented query
- structured subgraph / feature projection
- residual / novelty query
- provenance / temporal query
- collaboration state query
- proposal submission

SEIはSUIの全永続情報を自前memoryへ複製せず、必要なときにSUIを外部認知環境としてqueryする。

### 3.4 外部collaborator / system

人間の共同作業者、別AI、TEI、MCP、外部document source等も参加主体となり得る。

主な関心と責務は一律に固定せず、role / permission / provenanceとともに扱う。

SUIは「外部から来た」という理由だけで情報を劣位・上位に置かない。誰が、どの経路で、どの目的で追加したかを保持する。

## 4. 関心（Interest）と役割（Role）を分ける

Roleは責務・権限を表す。

Interestは、その時点で何を見ようとしているかを表す。

同じ人間でも、ある時は観察者、別の時は承認者、別の時は批判者になり得る。同じ生成AIも、探索、反証、文章化など異なる役割で呼ばれ得る。

したがってconceptually、projectionは次のように決まる。

```text
Actor
 + Role
 + Current Interest
 + Inquiry
 + Permission
 + History / Provenance constraints
        ↓
Context Projection
```

Roleを固定personaへしない。Interestを長期的な属性へ固定しない。

## 5. Working Graph / Projection / Consensus Graphの関係

既存domainでは次が定義されている。

- `WorkingGraph`: 探索・仮説・未確定を保持する作業面
- `ContextProjectionGraph`: 問い合わせ目的に合わせた読み取り専用の投影面
- `ConsensusGraph`: 人間承認済み差分だけを保持する統合面

本研究では、複数主体運用時にこれを次のように発展させる仮説を置く。

```text
Human Working Graph ─────┐
AI Proposal Graph ───────┤
SEI Working State ───────┼─> Context Projection(s)
External Contributions ──┘          │
                                    ▼
                              review / dialogue
                                    │
                             patch + approval
                                    ▼
                              Consensus Graph
```

ただしConsensusGraphは「全員が完全に同意した世界」ではない。

**共有状態として承認された差分**を保持する統合面であり、未承認・異論・保留はWorking側や関連記録として失わず残す。

## 6. 合意には複数段階がある

単純な`agreed / disagreed`二値だけでは不足する。

研究上は少なくとも次を区別する余地がある。

- observed: 事実・発言・資料として共有された
- acknowledged: 存在を認識した
- understood: 意味の理解が共有された
- accepted-for-working: 当面の作業前提として採用した
- approved: ConsensusGraphへ反映することを承認した
- disputed: 明示的に異論がある
- held: 判断を保留している

これらを直ちに新しいproduction enumへしない。まず、現在の`patch + approval`、Critique、HoldState、provenanceでどこまで表現できるかを確認する。

## 7. SUI Queryは合意形成のための「見方」を提供する

情報ネットワークQueryは、単なる検索機能ではなく、主体間の認知差を確認する手段でもある。

例:

- HumanとAIが共通に参照しているcard
- AIだけが根拠にしているsource
- 人間がholdしているがAIがcluster候補にしたcard
- collaborator間でrelationの解釈が異なる部分
- ConsensusGraphには入ったが後続のWorkingGraphで再び疑義が出た部分
- 同じ問いに対する複数projectionの差

SUIはこれらをsubgraph、比較表、空間配置、timeline、provenance matrix等へ投影できることを目指す。

## 8. 「合意形成場」として守る停止線

- 合意率を内容の品質scoreにしない
- 多数派を自動的に正しいと扱わない
- AIと人間の意見数を投票として単純集計しない
- 保留や異論をConsensusGraphへ押し込まない
- actor-specific Working stateを無断で他主体の確定状態へ変換しない
- AI proposalをapprovalと同一視しない
- Query projectionをCanonical meaningと同一視しない
- provenanceを消して「システムの結論」として均すことをしない

## 9. SEIとの循環

SEIはSUIの情報ネットワークと協働状態をqueryし、認知場へ必要な断片だけを取り込む。

```text
SEI Inquiry
   ↓
SUI Query
   ↓
role / interest aware projection
   ↓
SEI cognition / local reasoning
   ↓
proposal / question / request for human review
   ↓
SUI collaboration space
   ↓
human / AI / other actor response
   ↓
updated shared state
   ↓
SEI re-query
```

この循環によって、SEIは単独で万能な認知主体になるのではなく、SUIを介して他者の認知へ接続する。

## 10. 文書・設計の展開順

本概念を上位に置き、下位文書は次の順で展開する。

1. **SUI = 多主体の認知合意形成場** — 本書
2. **SUI = 情報ネットワークのQuery / 定性分析環境** — `information-network-query-and-qualitative-analysis-2026-09-12.md`
3. **SEI / SUIの責務配置** — `non-llm-cognitive-substrate-placement-2026-09-12.md`
4. Query Intent / Projection Contract
5. actor / role / interest / permissionの最小contract
6. Working / Projection / Consensus Graphの複数主体化
7. API / UI / machine interface
8. dogfood / Evidence

現在は研究段階であり、`domain.md`の規範語彙、production schema、ConsensusGraph型を直ちに変更しない。既存契約で表現できない意味差が実証された時点で、上位規範から順に更新する。
