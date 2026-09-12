# Multi-channel Query Envelope Contract

- Status: **Normative / v1alpha1**
- Date: 2026-09-12
- Parent: `information_network_projection_contract.md`
- Related: `associative_cognition_provider_contract.md`

## 1. 目的

SUI Information Networkに対するQueryでは、異なる認知channelが同じ対象について異なる候補を返し得る。

この違いを一つのscoreへ畳み込まず、次を同時に守る。

1. D0の決定論的Selectionを、Query時点の唯一のSelectionとして保持する。
2. D1 lexical sparse / D2 associative sparseを補助candidate channelとして保持する。
3. channel間の一致・不一致を観察可能にする。
4. candidateをSelection / relation / island / Consensusへ自動昇格させない。
5. Provider内部のactivation / similarity / confidence等を再流入させない。

```text
D0 deterministic Selection ───────────────┐
                                          │
D1 lexical candidate channel ─────────────┼─> Multi-channel Query Envelope
                                          │
D2 associative candidate channel ─────────┘

Envelope != merged ranking
Envelope != voting
Envelope != consensus
Envelope != automatic selection expansion
```

## 2. Selection authority

v1alpha1では、`deterministicSelection`のみがSelection authorityを持つ。

```text
candidate mentioned by D1/D2
  != selected

candidate mentioned by both D1 and D2
  != more true
  != more important
  != higher confidence
  != consensus
```

D0で既にselectedなrefがD1/D2にも現れることは許す。その場合も、Selectionの根拠はD0 resultに残し、candidate channelの出現をSelection根拠へ混ぜない。

## 3. Formal envelope

```ts
type MultiChannelQueryEnvelopeV1Alpha1 = {
  schema: "sui.multi-channel-query-envelope/v1alpha1";
  requestId: string;
  networkId: string;
  intent: QueryIntent;

  deterministicSelection: SelectionResult;

  candidateChannels: Array<
    LexicalSparseChannelResult |
    AssociativeSparseChannelResult
  >;

  channelPresence: Array<{
    ref: string;
    channels: Array<"lexical_sparse" | "associative_sparse">;
  }>;

  trace: {
    selectionAuthority: "d0_deterministic_only";
    candidateAutoPromotion: false;
    compositeRanking: false;
    crossChannelPresenceIsVote: false;
    sourceNetworkMutated: false;
  };
};
```

## 4. Invariants

### 4.1 同一snapshot

`deterministicSelection`と全candidate channelは同一`networkId`に由来しなければならない。

異なるsnapshot / networkのresultを暗黙に混ぜない。

### 4.2 ref境界

- selected node refはsnapshot内に存在する
- selected edge refはsnapshot内に存在する
- anchor refはsnapshot内に存在する
- candidate refはsnapshot内に存在する
- channel内でanchor自身をcandidateにしない

### 4.3 channel閉世界

v1alpha1のcandidate channelは次だけを許す。

- `lexical_sparse`
- `associative_sparse`

同名channelを複数入れない。

D3以降を追加するときは意味を曖昧に拡張せず、contractを明示的に改訂する。

### 4.4 ranking / provider signalの遮断

Envelopeに次を持ち込まない。

- `score`
- `confidence`
- `importance`
- `rank`
- `activation`
- `similarity`
- `novelty_signal`

内部実装がこれらを利用していても、Query Envelopeへは候補集合と外在化可能な根拠だけを持ち込む。

## 5. channelPresence

`channelPresence`は、あるrefがどのcandidate channelに**現れたか**だけを外在化する。

例:

```json
{
  "ref": "c8",
  "channels": ["associative_sparse", "lexical_sparse"]
}
```

ここから次を導出しない。

- channel数
- vote count
- confidence
- priority
- rank
- automatic escalation
- automatic relation

複数channel一致が人間や後続Methodにとって有用な観察材料になることはあるが、その意味づけは別の認知段階で行う。

## 6. channel disagreement

不一致も捨てない。

```text
D0 near / D1 far
D0 far / D1 near
D1 near / D2 abstain
D1 absent / D2 candidate
D1 candidate / D2 candidate / D0 not selected
```

これらは異常ではなく、各channelが異なる認知機能を担っていることから自然に生じる。

将来のD3/D4は、この不一致そのものをWorking Setの材料にできる。

## 7. Projectionとの関係

Envelopeはactor-facing UIを直接規定しない。

```text
Multi-channel Query Envelope
  -> Context Projection
```

Projection側は、主体・Role・Interest・表示能力に応じて、たとえば次を選べる。

- D0 Selectionだけを表示
- D1候補を「語彙上の再確認候補」として別欄表示
- D2候補を「連想上の再確認候補」として別欄表示
- channel disagreementを検討材料として表示

ただし表示差によってcanonical Selectionを変更しない。

## 8. Consensusとの関係

Candidate channelはConsensusGraphへ直接書き込まない。

```text
candidate observation
  -> human / approved Method review
  -> explicit proposal
  -> review / approval boundary
  -> canonical relation or Consensus candidate
```

必要な承認境界を飛ばさない。

## 9. Benchmark停止線

本EnvelopeはQuery architectureのsynthetic executable contractである。

親和的な束ねの意味品質を測る`COGNITIVE-ASSOC-01`固定benchmarkへ、Human adjudication gate freeze前にD1/D2/D3を適用しない。

## 10. Non-goals

- candidate unionをSelectionへ自動追加すること
- channel数による多数決
- composite similarity / confidence score
- automatic island / relation creation
- automatic Consensus昇格
- D3 semantic providerの先取り定義
- D4 language generation
