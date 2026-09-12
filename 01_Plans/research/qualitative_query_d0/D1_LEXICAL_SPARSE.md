# D1 Lexical Sparse Channel

- Status: Executable reference layer
- Date: 2026-09-12
- Formal architecture: `../../../02_Architecture/information_network_projection_contract.md`
- Parent: `../query-intent-execution-ladder-2026-09-12.md`

## 1. 役割

D1は、D0の明示graph / state / provenanceだけでは拾えない**表層語彙上の再確認候補**を増やす。

D1は意味表現ではない。

```text
D0 explicit structure
   +
D1 lexical sparse candidates
   != semantic agreement
   != importance
   != confidence
   != automatic grouping
```

## 2. 初期feature

日本語を含む多言語テキストへ外部分かち書き依存を持ち込まず、first sliceは次とする。

1. Unicode NFKC
2. casefold
3. Unicode alphanumeric以外を除去
4. character 2-gram / 3-gram集合
5. anchorとの共有featureが実行threshold以上のnodeをcandidate化

thresholdは内部の候補生成規則であり、利用者向けsimilarity scoreではない。

## 3. Result contract

```text
channel = lexical_sparse
anchorRefs
candidateRefs              # ref asc。類似順ではない
items[]
  ref
  matchedAnchorRefs
  evidence
    sharedCharacterNgrams  # 表層根拠そのもの
trace
  method
  candidateOrdering = ref_asc
  semanticInference = false
```

`score / confidence / importance / rank`は返さない。

## 4. D0との関係

D1はD0 resultを上書きしない。

将来のorchestratorでは例えば、

```text
selection
  deterministic: D0 result
  lexical_candidates: D1 result
```

として並存させる。

D0で明示relationがない一方、D1で表層語彙が近い場合、その不一致自体を残す。

## 5. Permission / SafeMode

D1はauthorizationやSafeMode判定を行わない。

**既にvisibility-filter済みの `QualitativeNetworkSnapshot` だけを入力とする。**

未レビュー情報をD1の都合で再取得したり、visibility外nodeを候補生成へ混ぜたりしない。

## 6. 非目標

- synonym推定
- sentence embedding
- semantic similarity
- topic classification
- island / relation / consensus確定
- candidate ranking
- lexical overlapを意味近接へ読み替えること

語彙が離れた意味近接はD2/D3の責務として残す。

## 7. COGNITIVE-ASSOC-01との停止線

本実装はQuery layerのsynthetic fixtureでD1の責務を固定するものであり、`COGNITIVE-ASSOC-01`の事前登録benchmarkを実行しない。

特にHuman adjudication gateが凍結される前に、Meta R1 / R3の固定benchmarkへ本D1を適用してbaseline結果を生成しない。

したがって本sliceのtestは `qualitative_query_d0/fixtures/network.json` のみを利用する。

## 8. 次段階

D1の次はD2 SEI sparse associative channelを同じ`QualitativeNetworkSnapshot`上へ接続する。

D2もD0/D1と別channelとして保持し、channel間不一致を一つの総合scoreへ潰さない。
