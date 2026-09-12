# D2 Associative Sparse Channel

- Status: Executable provider-boundary reference
- Date: 2026-09-12
- Formal provider contract: `../../../02_Architecture/associative_cognition_provider_contract.md`
- Parent architecture: `../../../02_Architecture/information_network_projection_contract.md`

## 1. 役割

D2は、D0の明示構造やD1の表層語彙だけでは拾いにくい候補を、交換可能なAssociative Cognition Providerから受け取るchannelである。

D2は意味判断器ではない。

```text
D2 candidate
  != semantic agreement
  != truth
  != confidence
  != importance
  != automatic affinity group
```

## 2. SUI / Providerの境界

SUIは、visibility-filter済みのbounded snapshotから、次の意味channelをProviderへ渡す。

- text
- graph relation types / neighbor kinds
- provenance source / actor refs
- grouping island / hold state

Providerは内部で任意の軽量認知実現を使える。

例:

- sparse expansion
- associative memory
- k-WTA / inhibition
- learned sparse representation
- HDC / VSA
- Random Indexing

ただしSUI契約はそれらの実装名を要求しない。

## 3. Bounded Cognitive Workspace

v1alpha1では次をhard limitとする。

```text
items <= 512
anchorRefs <= 32
candidateLimit <= 64
```

上限超過をProvider側で黙ってtruncateしない。SUI側でscopeを作り直すかfail-closedする。

これは重要度rankingではなく、認知帯域・privacy・latencyを守る境界である。

## 4. Provider内部Signalを外へ漏らさない

Provider内部ではactivationやnovelty scalarを使ってよい。

正式responseへは出さない。

禁止key:

- score
- confidence
- importance
- rank
- activation
- similarity
- novelty_signal

SUIが受け取るのはcandidate refs、abstention、外在化可能なchannel provenanceだけである。

## 5. matchedChannelRefs

`matchedChannelRefs`はproviderがcandidate化に使ったと申告する入力channel provenanceであり、意味一致の証拠ではない。

例:

```text
channel:text
provenance:source:s1
graph:relationType:related
```

SUIは、そのchannelがanchor側とcandidate側の双方に実在することを検証する。

Provider内部のhashやactivationを逆推定して寄与度を再現しない。安全に説明できなければ空配列でよい。

## 6. D0 / D1 / D2を統合scoreへしない

```text
D0 explicit structure
D1 lexical sparse
D2 associative sparse
```

は別channelである。

たとえば、

- D0: no explicit path
- D1: lexical far
- D2: candidate

であれば「構造・表層語彙では近くないが、連想基質が再確認候補にした」という不一致をそのまま保持する。

逆にD1で近くD2がabstainしても、どちらかを自動的に正しいとしない。

## 7. SEI Cognition / SACSとの接続

SEI Cognition側の現研究では、SACSをpre-attentive candidate narrowingとして置き、activationをTruth / confidenceへしない。

SUI側はその実装をimportしない。将来、SEI側にProvider adapterを置き、SACS内部resultからformal responseへ縮退させる。

この分離により、SEI内部実現が変わってもSUI Information Network contractを維持できる。

## 8. Benchmark停止線

本sliceはsynthetic provider responseのprotocol validationだけを行う。

`COGNITIVE-ASSOC-01`の固定benchmarkへD2 / SACSを適用しない。Human adjudication gate freeze前にbaseline結果を生成しない。

## 9. 次段階

D2 protocolが固定できた後、D0/D1/D2を別channelのまま一つのQuery result envelopeへ束ねるorchestratorを作る。

その後、SEI側の実SACS adapterをformal provider contractへ接続する。意味品質benchmarkはhuman gate後まで実行しない。
