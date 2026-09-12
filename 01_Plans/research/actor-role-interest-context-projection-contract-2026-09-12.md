# Actor / Role / Interest → Context Projection 最小研究契約

- Status: Research / Non-normative
- Date: 2026-09-12
- Parent: `multi-actor-cognitive-consensus-space-2026-09-12.md`
- Related: `information-network-query-and-qualitative-analysis-2026-09-12.md`, `02_Architecture/schemas.md`

## 1. 根幹の趣旨

SUI Sensemakingでは、人間、生成AI、SEI Cognition、外部主体が同じ情報ネットワークへ参加するが、同じ情報を同じ形で見る必要はない。

Context Projectionは、単なるaccess-control後のデータ返却ではなく、**現在の主体・役割・関心・問いに必要な情報だけを、元情報へ戻れる形で構成した認知用のView**である。

一方で、Context Projectionが主体の判断を先回りしてはならない。

- Projectionはtruthではない。
- Projectionはimportance rankingではない。
- ProjectionはConsensusではない。
- Projectionに含まれなかった情報は、価値が低いことを意味しない。
- Projectionを生成しただけでCanonicalな情報ネットワークを書き換えない。

## 2. 既存契約を壊さない

現行`ContextQueryV1`はclosed-world契約であり、top-level keyの追加はv2でのみ許される。

そのため本研究では、Actor / Role / Interestを`ContextQueryV1`へ直接追加しない。

代わりに、論理的に一段上の研究用requestを置く。

```text
ProjectionRequestR0
       │
       │ compile / validate
       ▼
ContextQueryV1
       │
       ▼
ContextBundleV1
       │
       │ project
       ▼
ContextProjectionR0
```

`ProjectionRequestR0`と`ContextProjectionR0`はproduction schemaではない。現行CE1 contractの変更を必要とするかを調べるための研究契約である。

## 3. Actor / Role / Interestを分離する

### Actor

「誰／何が問い合わせているか」。

Actorはidentityそのものを公開する必要はなく、SUI内部ではopaque referenceで扱える。

研究上のkind例:

- `human`
- `generative_ai`
- `sei_cognition`
- `external_system`

Actor kindは権限を意味しない。

### Role

「今回の相互作用で何をする責任があるか」。

例:

- `observe`
- `explore`
- `compare`
- `critique`
- `synthesize`
- `propose`
- `review`
- `approve`
- `publish`

Roleはpersonaではなく、**そのinteractionにおける責務**である。同じActorが複数Roleを持ち得る。

Roleだけから権限を決めない。`approve`を名乗ったActorがapproval権限を得ることはない。

### Interest

「今、何に注意を向けたいか」。

Interestは長期profileではなく、一時的・変更可能な認知焦点である。

例:

- unresolved contradictions
- minority observations
- source diversity
- temporal change
- bridge between two areas
- cards excluded from current grouping
- evidence supporting or contradicting a claim

Interestは保存してもよいが、Actorの恒久的属性として固定しない。

### Inquiry

今回答えたい問い。自然言語でもmachine-readable intentでもよい。

InquiryはInterestより具体的で、一つのquery cycleに対応する。

### Permission

何を読む／提案する／承認する／共有する権限があるか。

Permissionは**requester自己申告値を信頼しない**。authorization layerが解決したeffective permissionをprojection compilerへ渡す。

## 4. Projection Request R0

概念型:

```ts
type ProjectionActorR0 = {
  actorRef: string; // opaque, no email/provider uid
  kind: "human" | "generative_ai" | "sei_cognition" | "external_system";
};

type ProjectionRoleR0 =
  | "observe"
  | "explore"
  | "compare"
  | "critique"
  | "synthesize"
  | "propose"
  | "review"
  | "approve"
  | "publish";

type ProjectionInterestR0 = {
  focusRefs?: string[];
  themes?: string[];
  seek?: (
    | "neighborhood"
    | "contrast"
    | "bridge"
    | "residual"
    | "unresolved"
    | "temporal"
    | "provenance"
    | "affinity"
  )[];
};

type EffectivePermissionR0 = {
  readableScopes: string[];
  canSeeUnreviewed: boolean;
  canCreateProposal: boolean;
  canReview: boolean;
  canApprove: boolean;
  canPublish: boolean;
};

type ProjectionRequestR0 = {
  requestId: string;
  actor: ProjectionActorR0;
  roles: ProjectionRoleR0[];
  interest: ProjectionInterestR0;
  inquiry: string;
  permission: EffectivePermissionR0; // server-derived
  sourceScope: "document" | "view" | "island";
  desiredProjection?: ProjectionFormR0[];
  diversityNeed?: "default" | "increase";
  unresolvedNeed?: "default" | "increase";
};
```

### 4.1 最初から含めないもの

- actorの人格profile
- sensitive traits
- model confidence
- importance score
- consensus percentage
- hidden chain-of-thought
- long-term preference inferred from query history

必要な認知焦点はInterestとしてその都度渡す。

## 5. Query IntentとProjection Formを分ける

Query Intentは「何を見るか」。Projection Formは「どう返すか」。

```ts
type QueryIntentR0 =
  | "neighborhood"
  | "contrast"
  | "bridge"
  | "residual"
  | "unresolved"
  | "temporal"
  | "provenance"
  | "affinity"
  | "readout";

type ProjectionFormR0 =
  | "subgraph"
  | "path_list"
  | "card_stack"
  | "comparison_table"
  | "spatial_layout"
  | "timeline"
  | "provenance_matrix"
  | "compact_narrative";
```

同一selectionを複数Formへ投影できることが望ましい。

例:

```text
Intent: contrast(A, B)
Selection: shared / A-only / B-only / contradictory evidence
Projection:
  - human -> spatial_layout + comparison_table
  - generative AI -> compact_narrative + provenance_matrix
  - SEI -> subgraph + machine-readable feature projection
```

Projectionの違いは元情報の違いではなく、認知interfaceの違いである。

## 6. ContextQueryV1へのcompile方針

R0は既存CE1契約を破らないため、次へcompileする。

- `goal`: inquiry + query intentの要約
- `scope`: sourceScope
- `depth`: intent / focusからboundedに決定
- `constraints`: selection条件、effective permissionで許された範囲、diversity/unresolved hintを格納
- `reviewFilter`: `permission.canSeeUnreviewed`とSafeModeから決定
- `safeModePolicy`: 現行通り`strict`
- `outputMode`: candidate / proposal / summaryの既存三値へ写像
- `previewConfirmed`: 現行Preview gateに従う

重要:

- Permissionを`constraints`へrequesterの自己申告値として丸写ししない。
- `reviewFilter=includeUnreviewed`はeffective permissionだけでなく既存SafeMode条件も満たす必要がある。
- `approve` RoleがあってもContextQueryがapproval actionへ変わるわけではない。
- R0 compileで`ContextQueryV1`のclosed-world keyを増やさない。

## 7. Context Projection R0

ContextBundleV1をそのまま全主体へ返す必要はない。

研究上のprojection outputは次のように考える。

```ts
type ProjectionTraceR0 = {
  requestId: string;
  queryCanonicalHash: string;
  bundleHash: string;
  sourceRefs: string[];
  excludedReasons: string[];
};

type ContextProjectionR0 = {
  actorRef: string;
  inquiry: string;
  intents: QueryIntentR0[];
  forms: ProjectionFormR0[];
  selectedRefs: string[];
  relationRefs: string[];
  residualRefs: string[];
  contradictionRefs: string[];
  provenanceRefs: string[];
  payloads: Record<string, unknown>;
  trace: ProjectionTraceR0;
};
```

`payloads`は研究上のplaceholderであり、productionへそのまま採用しない。

## 8. Actor別の初期interface

| Actor | 主な入力 | 主な返却 | 書込境界 |
|---|---|---|---|
| Human | spatial focus, direct query, hold/critique | spatial/table/card/narrative | 明示操作。approval可能なのは権限がある場合だけ |
| Generative AI | bounded query, task, Context Projection | structured proposal, critique candidate, narrative draft | proposal-only。Consensus direct write禁止 |
| SEI Cognition | inquiry, focus, novelty/unresolved need | compact subgraph, residual, provenance, temporal context | proposal/question/review request。Consensus direct write禁止 |
| External system | declared integration task + server-resolved permission | machine-readable projection | role/permission別。provenance必須 |

## 9. Consensusとの境界

Context ProjectionはConsensus形成の入力になり得るが、Consensusそのものではない。

次を分離する。

```text
seen / observed
    !=
acknowledged
    !=
understood
    !=
accepted-for-working
    !=
approved
```

現行`human_reviewed`は内容レビュー状態であり、この合意段階を表すenumとして流用しない。

現行`ConsensusGraph`へ入る経路は引き続き`patch + approval`だけである。

## 10. Fail-closed境界

- Actor kindから権限を推測しない。
- Roleから権限を推測しない。
- Interestから秘密情報へのaccess scopeを拡大しない。
- Query結果の欠落を「存在しない」と断定しない。
- Projection生成失敗時にraw full datasetをfallback返却しない。
- SafeModeをProjection利便性のために緩めない。
- AI/SEI outputを`human_reviewed`へ自動昇格しない。
- projection-specific derived groupingをCanonical islandへ自動保存しない。

## 11. 最初の検証シナリオ

### R0-A Human vs SEI

同じInquiryに対し、人間にはspatial layout、SEIにはcompact subgraphを返す。selection sourceが同じで、元情報へ戻れるか確認する。

### R0-B Human vs Generative AI

人間がholdしているcardをAI queryから消さず、hold状態つきでContext Projectionへ含められるか確認する。

### R0-C Role separation

同じHuman Actorが`explore`時と`approve`時で異なるProjectionを得ても、approval permissionはserver-derivedで変化しないことを確認する。

### R0-D Residual request

SEIの`unresolvedNeed=increase`で、dominant cluster外のsingleton / critique / contradictory evidenceを優先的に候補化しても、importance scoreとして表面化しないことを確認する。

### R0-E Permission shrink

同一Inquiryでもeffective permissionを狭めた場合、Projectionが狭まり、excluded reasonが残ることを確認する。権限縮小時に以前のProjection payloadを再利用しない。

## 12. 次に進む条件

R0 dogfoodで次が確認できた場合だけ、production contract候補へ進む。

1. Actor / Role / Interestを分離する実益がある。
2. 現行`ContextQueryV1.constraints`へのcompileで十分か、v2 fieldが必要かを判定できる。
3. Human / AI / SEIでProjection Formを分ける実益がある。
4. permission / SafeMode / provenanceを壊さず実装できる。
5. ConsensusGraph / human_reviewedへ意味衝突を起こさない。

満たさなければ、Actor-aware projectionを新しいproduction概念へ昇格させない。
