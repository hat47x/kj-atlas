# Multi-channel Query Envelope — Execution Evidence 2026-09-12

- Status: Executable research evidence
- Scope: D0 deterministic Selection + D1 lexical sparse + D2 associative sparse composition
- Runtime: GitHub Actions / Ubuntu 24.04 / CPython 3.12.14
- Production claim: none

## 1. 実行結果

branch実体をcheckoutし、`01_Plans/research/qualitative_query_d0`で実行した。

```bash
python -m unittest -v
```

結果:

- **80 tests passed**
- unittest reported **0.065s**
- workflow conclusion: success

併せて次を確認した。

- `python -m py_compile *.py`: success
- Query Envelopeへのranking/provider内部signal混入guard: success
- `COGNITIVE-ASSOC-01`固定benchmark source非参照guard: success
- `python 01_Plans/docs_check.py`: success
- `git diff --check origin/main...HEAD`: success

検証用one-shot workflowは成功後にbranchから削除した。

## 2. 新たに確認した境界

1. D1/D2 candidateをEnvelopeへ加えても、D0 `selectedNodeRefs`は増えない。
2. D0で既にselectedなrefがcandidate channelにも現れてよいが、Selection authorityはD0のまま維持される。
3. `channelPresence`はrefとchannel名だけを保持し、票数・score・confidence・priorityを生成しない。
4. D1/D2の順序は入力順ではなくchannel名で安定化される。
5. 同一channelの重複はfail-closedする。
6. 未定義channelはfail-closedする。
7. snapshot外candidateはfail-closedする。
8. 異なるnetwork由来のSelection / channelを混在させない。
9. Provider内部の`activation`等をEnvelopeから再流入させない。
10. D2 abstainはcandidate presenceを生成しない。
11. Envelope compositionはsnapshot / Selection / channel inputを変更しない。
12. Intent mismatchはfail-closedする。

## 3. 意味上の停止線

```text
cross-channel presence != vote
cross-channel presence != confidence
cross-channel presence != consensus
candidate != selected
candidate != relation
candidate != island membership
candidate != canonical write
```

Envelopeは異なる認知channelを並置するだけであり、その一致を一つの意味強度へ圧縮しない。

## 4. Benchmark停止線

本検証はsynthetic `qualitative_query_d0/fixtures/network.json`のみを利用した。

親和的な束ねの意味品質を評価する`COGNITIVE-ASSOC-01`固定benchmarkにはD1/D2/Envelopeを適用していない。Human adjudication gate freeze前に意味品質baselineを生成しない。

## 5. 次段階

次は、SEI Cognition側のSACS evaluation implementationをSUIの`Associative Cognition Provider Contract`へ接続するadapterを、正式境界の外側に実装する。

その際もSUIへ渡すのは、

- candidate refs
- abstain
- 外在化可能なchannel provenance
- provider/version trace

に限定し、SACS内部のactivation / similarity / novelty numeric signalはProvider内に閉じる。
