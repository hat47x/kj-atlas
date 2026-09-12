# D1 Lexical Sparse — Execution Evidence 2026-09-12

- Status: Executable evidence
- Scope: formal `QualitativeNetworkSnapshot` synthetic fixture only
- Runtime: GitHub Actions, Ubuntu 24.04, CPython 3.12.14
- Formal architecture: `../../../02_Architecture/information_network_projection_contract.md`

## 1. 実行結果

`01_Plans/research/qualitative_query_d0`で次を実行した。

```bash
python -m unittest -v
python -m py_compile *.py
```

結果:

- **42 tests passed**（D0 / formal Request / D1合計）
- unittest reported **0.030s**
- Python compile: success
- fixed affinity-benchmark non-consumption guard: success
- `python 01_Plans/docs_check.py`: success
- `git diff --check origin/main...HEAD`: success
- GitHub Actions workflow conclusion: success

検証用one-shot workflowは実行後に削除した。

## 2. D1で追加確認したこと

1. NFKC + casefoldでUnicode表記差を決定論的に正規化する。
2. character 2-gram / 3-gramをsurface featureとしてのみ用いる。
3. anchor自身をcandidateへ返さない。
4. candidate順はoverlap量ではなくstable ref ID順である。
5. 根拠は共有character n-gramそのものとして保持する。
6. `score / confidence / importance / rank`を返さない。
7. 語彙表面が離れたtextをsemantic matchとして発明しない。
8. scopeでcandidate generationをboundedにできる。
9. multiple anchor時にどのanchorと表層一致したかを保持する。
10. textを持たないnodeを無理に特徴化しない。
11. unknown anchor / invalid thresholdをfail-closedする。
12. source snapshotを変更しない。

## 3. 意味境界

D1のcandidateは、

> 表層語彙上、一緒に再確認する価値がある可能性

だけを意味する。

次は意味しない。

- semantic agreement
- 同じ親和的まとまり
- causal relation
- importance
- confidence
- consensus

D0とD1が異なる候補を返す場合、その不一致を消さず別channelとして保持する。

## 4. Benchmark停止線

本検証では `COGNITIVE-ASSOC-01` の固定benchmarkを実行していない。

コード/testについて、次の固定source IDを参照しないguardも成功した。

- `doc_cognitive_dogfood_meta_r1`
- historical technical ID `doc_kj_atlas_dogfood_r3`

Human adjudication gateがfreezeされる前に、このD1を当該benchmarkへ適用してbaseline結果を生成しない。

## 5. 次段階

次は同じformal snapshotへD2 sparse associative cognitionを独立channelとして接続する。

D2はD0/D1 resultを上書きせず、activationをtruth/confidenceへ変換しない。
