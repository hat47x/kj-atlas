# D0 Deterministic Qualitative Query — Execution Evidence 2026-09-12

- Status: Executable research evidence
- Scope: synthetic information network only
- Runtime: GitHub Actions, Ubuntu 24.04, CPython 3.12.14
- Production claim: none

## 1. 実行結果

branch上の実ファイルをcheckoutし、`01_Plans/research/qualitative_query_d0`で次を実行した。

```bash
python -m unittest -v
```

結果:

- **12 tests passed**
- execution time reported by unittest: 0.007s
- workflow conclusion: success
- temporary validation workflow was removed after execution and is not part of the intended merge result

確認したtest:

1. explicit graph BFSによるneighborhood
2. contrastでshared / left-only / right-only facetを保持
3. bridgeで複数のshortest pathを保持しstrength scoreを付けない
4. explicit pathが無いことを`unrelated`と断定しない
5. residualをparallel reasonsとして返しscore化しない
6. hold / unreviewed / Critique / contradictionをunresolvedとして保持
7. temporal orderingをcausalityへ読み替えない
8. provenanceをsource / actor別に保持し、source欠落も残す
9. 同一selectionをcomparison table / subgraph / spatial layoutへ投影できる
10. D0が`compact_narrative`生成を拒否しD4境界を維持する
11. query実行がsource networkを変更しない
12. unknown refsをfail-closedする

## 2. 追加のsynthetic確認

container環境からgithub.comを直接cloneする経路はDNS解決できなかったため、同一fixtureと同一アルゴリズム境界についてローカルでも独立に確認した。

- c1近傍depth=1 / 2
- c1→c5の2本のexplicit shortest path
- c1→c7でexplicit pathなし
- c4 / c5 / c6 / c7 / c8のresidual理由
- contrastのsource facet
- provenance grouping

GitHub Actionsによるbranch実ファイルのunit test成功を正本の実行Evidenceとし、ローカル確認は補助Evidenceとして扱う。

## 3. このEvidenceが意味すること

- D0の7種queryを生成モデルなしで決定論的に実行できる。
- residual / unresolvedをrankingではなく理由と状態として返せる。
- bridge pathを意味の強さへ昇格させず候補経路として返せる。
- SelectionとProjectionを分離し、同じselectionを複数interfaceへ整形できる。
- queryはread-only derived viewとして実行できる。

## 4. このEvidenceが意味しないこと

- production `DocumentV1`への統合が完了したこと。
- 実データ規模で十分なlatency / memoryを持つこと。
- D0だけで深層意味近接を扱えること。
- sparse associative / static semantic / local SLMが不要であること。
- Queryが人間・AI・SEIの認知品質を実際に向上させたこと。
- ContextQuery / ContextBundle v2が必要または不要と確定したこと。

次はR0 Actor-aware Context ProjectionとD0 Queryを接続し、同じselectionをHuman / Generative AI / SEIの異なるProjection Formへ返すend-to-end research sliceを作る。
