# D2 Associative Sparse Channel — Execution Evidence 2026-09-12

- Status: Executable provider-boundary evidence
- Scope: formal `QualitativeNetworkSnapshot` synthetic fixture + synthetic provider response
- Runtime: GitHub Actions, Ubuntu 24.04, CPython 3.12.14
- Formal contract: `../../../02_Architecture/associative_cognition_provider_contract.md`

## 1. 実行結果

`01_Plans/research/qualitative_query_d0`で次を実行した。

```bash
python -m unittest -v
python -m py_compile *.py
```

結果:

- **67 tests passed**（D0 / formal Request / D1 / D2合計）
- unittest reported **0.061s**
- Python compile: success
- fixed affinity-benchmark non-consumption guard: success
- concrete SOZA / SACS / SEI implementation import guard: success
- `python 01_Plans/docs_check.py`: success
- `git diff --check origin/main...HEAD`: success
- GitHub Actions workflow conclusion: success

検証用one-shot workflowは実行後に削除した。

## 2. D2 Requestで確認したこと

1. formal request schemaを使う。
2. text / graph / provenance / groupingをSUI側で意味づけたchannelとして渡す。
3. `reviewState`、permission、credential、観測時刻等をProvider payloadへ無差別に流さない。
4. scopeを明示的にboundedにできる。
5. unknown anchorをfail-closedする。
6. anchorがscope外ならfail-closedする。
7. `candidateLimit`を `1..64` に制限し、boolを整数として受理しない。
8. anchor数を最大32へ制限する。
9. scope item数を最大512へ制限する。

## 3. D2 Responseで確認したこと

1. Provider順ではなくstable ref順へ正規化する。
2. `activation / score / confidence / importance / rank / similarity / novelty_signal`を拒否する。
3. top-level responseをclosed-worldで検証する。
4. Provider metadataを`providerId / implementationVersion`だけへ限定する。
5. `requestId`不一致を拒否する。
6. request scope外candidateを拒否する。
7. anchor自身をcandidateとして返すことを拒否する。
8. candidate重複を拒否する。
9. candidateLimit超過を拒否する。
10. abstainはempty candidates + `noveltyCue=abstain`を必須にする。
11. candidate outcomeは`noveltyCue=none`を必須にする。
12. evidence refはcandidateの部分集合だけ許可する。
13. duplicate evidence refを拒否する。
14. 存在しないchannel provenanceの捏造を拒否する。
15. anchor/candidate双方に存在するchannel provenanceは受理する。
16. Providerが安全に説明できない場合、empty `matchedChannelRefs`を許す。
17. source snapshotとProvider responseを変更しない。

## 4. matchedChannelRefsの意味

`matchedChannelRefs`はsemantic matchの証明ではない。

Providerがcandidate化に利用したと申告する入力channel provenanceだけを表す。

例:

```text
channel:text
provenance:source:s1
graph:relationType:related
```

`channel:text`は双方にtext入力が存在したことと、Providerがそのchannel利用を申告したことだけを意味し、text内容の一致・意味近接を意味しない。

## 5. SEI Cognitionとの実装分離

SUI側D2 adapterは、次の具体moduleをimportしないことをCIでguardした。

- SOZA implementation
- SACS implementation
- `sei_cognition`
- `sparse_cognition`

したがってSEI側SACSがhash、k-WTA、learned sparse、HDC/VSA、Random Indexing等へ変わっても、formal SUI provider contractを保てる。

## 6. Benchmark停止線

本検証はsynthetic provider responseだけを利用した。

`COGNITIVE-ASSOC-01`の固定benchmark source IDをD2 implementation/testが参照しないこともCIで確認した。

Human adjudication gate freeze前にD2/SACSを当該benchmarkへ適用して意味品質baselineを生成しない。

## 7. 次段階

次はD0 / D1 / D2を**統合scoreへ潰さず**一つのQuery result envelopeへ束ねるmulti-channel orchestratorを作る。

その後、SEI Cognition側にformal provider adapterを置いて実SACSと接続する。固定意味品質benchmarkへの適用はhuman gate後まで行わない。
