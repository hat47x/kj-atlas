# Associative Cognition Provider Contract

- Status: **Normative / v1alpha1 provider boundary**
- Date: 2026-09-12
- Parent: `information_network_projection_contract.md`
- External realization example: SEI Cognition SACS (evaluation-only implementation)

## 1. 目的

D2 sparse associative cognitionを、SUI Information Networkの耐久的意味と特定アルゴリズムを結合せず利用する。

SUIが必要とするのは、

> visibility-filter済みのboundedな情報集合について、追加で一緒に確認する候補があるか

というcandidate channelである。

SUIはFlyHash、BioHash、k-WTA、HDC、Random Indexing、embedding等の実装名を正式意味へ持ち込まない。

```text
SUI D2 contract
  != SACS internal algorithm
  != activation semantics
  != model confidence
```

## 2. 責務分離

### SUI owns

- permission / SafeMode適用
- bounded scope
- node / relation / provenance等のfeature meaning
- stable refs
- Query Intent
- candidateを別channelとして保持すること
- canonical network / Consensus境界

### Provider owns

- feature encoding realization
- sparse expansion / associative memory等の内部実現
- competition
- candidate narrowing
- internal novelty calculation
- runtime / device / compute placement

Provider内部値はSUIのTruth / Confidence / Unknown / Importanceへ自動変換しない。

## 3. Request

```ts
type AssociativeRecallRequestV1Alpha1 = {
  schema: "sui.associative-recall-request/v1alpha1";
  requestId: string;
  networkId: string;
  intent: QueryIntent;
  anchorRefs: string[];
  items: AssociativeItem[];
  policy: {
    candidateLimit: number;
  };
};

type AssociativeItem = {
  ref: string;
  kind: string;
  channels: {
    text?: string;
    graph?: {
      relationTypes: string[];
      neighborKinds: string[];
    };
    provenance?: {
      sourceRefs: string[];
      actorRefs: string[];
    };
    grouping?: {
      islandRef?: string;
      holdState?: string;
    };
  };
};
```

### 3.1 Request invariants

- requestはvisibility-filter済みsnapshotから作る
- `items[].ref`は一意
- `anchorRefs`はitems内に存在する
- v1alpha1のbounded上限は `items <= 512`, `anchorRefs <= 32`, `1 <= candidateLimit <= 64`
- 上限超過時にscopeをProvider側で黙ってtruncateしない。SUI側でscopeを再構成するかfail-closedする
- SUIが持たないprovenanceを推測して埋めない
- raw permission / credentialをProviderへ渡さない
- Providerへcanonical networkのwrite authorityを渡さない

上限は内容価値のrankingではなく、Providerへ渡すCognitive Workspaceの帯域境界である。

## 4. Response

```ts
type AssociativeRecallResponseV1Alpha1 = {
  schema: "sui.associative-recall-response/v1alpha1";
  requestId: string;
  provider: {
    providerId: string;
    implementationVersion: string;
  };
  outcome: "candidates" | "abstain";
  candidateRefs: string[];
  evidence: Array<{
    ref: string;
    matchedChannelRefs: string[];
  }>;
  noveltyCue: "none" | "abstain";
};
```

### 4.1 Response invariants

- closed-world。未定義top-level keyを許可しない
- `requestId`一致必須
- candidateはrequest scope内だけ
- anchor自身をcandidateにしない
- candidate重複禁止
- `candidateRefs.length <= candidateLimit`
- SUI境界ではcandidateをstable ref昇順へ正規化する
- `outcome=abstain`なら`candidateRefs=[]`かつ`noveltyCue=abstain`
- `outcome=candidates`なら`noveltyCue=none`
- evidenceのrefはcandidateRefsの部分集合
- `score / confidence / importance / rank / activation / similarity`をresponse contractへ入れない

Providerが内部でactivation等を利用してもよいが、SUI境界より内側でcandidate narrowingへ使い、正式responseには漏らさない。

## 5. matchedChannelRefs は「一致証明」ではなく channel provenance

`matchedChannelRefs`は、Providerがcandidate化に利用したと申告する**入力channelの由来**である。

これは、

- semantic matchの証明
- relationの確定
- similarity scoreの代用品

ではない。

SUIは、少なくともanchor側とcandidate側の双方にそのchannel由来が実在することだけを検証する。Provider内部のhashやactivationを再構成して「本当に寄与したか」までは推測しない。

例:

```text
channel:text
 graph:relationType:related
 graph:neighborKind:card
 provenance:source:s1
 provenance:actor:human:a
 grouping:island:i2
 grouping:hold:held
```

`channel:text`は「双方のtext channelがProvider入力に存在し、Providerがそのchannelを利用したと申告した」ことだけを意味する。text内容が一致した、意味が近い、という意味ではない。

Providerが内部表現から安全にchannel provenanceを外在化できない場合は、`matchedChannelRefs=[]`を返す。説明を捏造しない。

## 6. SUI側ChannelResult

formal responseを検証した後、SUIは次の独立channelへ変換する。

```ts
type AssociativeChannelResult = {
  channel: "associative_sparse";
  anchorRefs: string[];
  candidateRefs: string[];
  items: Array<{
    ref: string;
    evidence: { matchedChannelRefs: string[] };
  }>;
  noveltyCue: "none" | "abstain";
  trace: {
    networkId: string;
    providerId: string;
    implementationVersion: string;
    semanticAuthority: false;
    sourceNetworkMutated: false;
  };
};
```

D0 / D1 resultへ自動mergeしない。

```text
D0 deterministic
D1 lexical sparse
D2 associative sparse
```

を並存させ、channel間不一致を保持する。

## 7. SEI Cognitionとの整合

SEI Cognition側のSACS研究では、sparse representation、competition、associative recall、novelty / abstentionをpre-attentive primitiveとして扱い、activationをTruth / confidenceへしない境界を置いている。

本contractはその内部アルゴリズムを採用契約にせず、候補集合へ縮退した交換面だけを固定する。

したがって将来、SACSが次へ変更されてもSUI側を変更する必要はない。

- hash方式変更
- learned sparse expansion
- HDC / VSA
- Random Indexing
- 別process / local device / distributed execution

## 8. COGNITIVE-ASSOC-01との停止線

本contractとsynthetic provider validationは、親和的な束ねの意味品質benchmarkではない。

Human adjudication gate freeze前に固定benchmarkへSACS / D2を適用して評価結果を生成しない。

## 9. Non-goals

- Provider activationのUI表示
- candidate ranking UI
- automatic island / relation creation
- noveltyCueをSOZA/SEIのUnknownへ変換
- candidateをRecommendation / Decision / Consensusへ昇格
- SUIからSEI内部memory schemaを規定すること
