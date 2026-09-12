# D0 Deterministic Qualitative Query — Execution Evidence 2026-09-12

- Status: Executable research evidence
- Scope: synthetic information network + R0 Context Projection integration
- Runtime: GitHub Actions, Ubuntu 24.04, CPython 3.12.14
- Production claim: none

## 1. 実行結果

branch上の実ファイルをcheckoutし、`01_Plans/research/qualitative_query_d0`で次を実行した。

```bash
python -m unittest -v
```

2段階で検証した。

### D0 core

- **12 tests passed**
- unittest reported 0.007s
- workflow conclusion: success

### R0 Context Projection接続後

- **21 tests passed**
- unittest reported 0.017s
- workflow conclusion: success

一時validation workflowは検証後にbranchから削除し、merge対象には含めない。

## 2. D0 coreで確認したこと

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

## 3. R0 Context Projection接続で追加確認したこと

1. Human / Generative AI / SEIが、同じcontrast inquiryとfocusから**同一selection digest**を得る。
2. 同一selectionをHumanには`comparison_table + spatial_layout`、SEIには`subgraph`として返せる。
3. Generative AIが`compact_narrative`を要求しても、D0では生成せずD4へ明示的にdeferする。
4. opaque `actorRef`を既存`ContextQueryV1`へ混入させず、outer projection traceだけで保持できる。
5. 未レビューcardをfocusしたqueryは、SafeMode allowanceなしではfail-closedする。
6. `canSeeUnreviewed=true`かつSafeMode allowanceありの場合だけ未レビューcardをD0入力へ含められる。
7. Permissionが未レビュー閲覧を許さなければ、SafeMode allowanceだけでは見えない。
8. Query / Projection実行で元networkを変更しない。
9. E2E responseへ`score / confidence / importance / rank`を導入しない。
10. first sliceで複数D0 selection intentを同時指定した場合は曖昧に統合せずfail-closedする。
11. `affinity`をD0へ黙って読み替えず、D2/D3以降の対象として停止する。

## 4. 追加のsynthetic確認

container環境からgithub.comを直接cloneする経路はDNS解決できなかったため、同一fixtureと同一アルゴリズム境界についてローカルでも独立に確認した。

- c1近傍depth=1 / 2
- c1→c5の2本のexplicit shortest path
- c1→c7でexplicit pathなし
- c4 / c5 / c6 / c7 / c8のresidual理由
- contrastのsource facet
- provenance grouping

GitHub Actionsによるbranch実ファイルのunit test成功を正本の実行Evidenceとし、ローカル確認は補助Evidenceとして扱う。

## 5. このEvidenceが意味すること

- D0の7種queryを生成モデルなしで決定論的に実行できる。
- residual / unresolvedをrankingではなく理由と状態として返せる。
- bridge pathを意味の強さへ昇格させず候補経路として返せる。
- SelectionとProjectionを分離し、同じselectionを主体別interfaceへ整形できる。
- R0 compilerのreviewFilterをD0入力前に適用できる。
- Human / AI / SEIでProjection Formが違っても、selection自体をActor kindだけで変えずに共有できる。
- query / projectionはread-only derived viewとして実行できる。

## 6. このEvidenceが意味しないこと

- production `DocumentV1`への統合が完了したこと。
- Authorization layerが実装済みであること。
- 実データ規模で十分なlatency / memoryを持つこと。
- D0だけで深層意味近接を扱えること。
- sparse associative / static semantic / local SLMが不要であること。
- Queryが人間・AI・SEIの認知品質を実際に向上させたこと。
- ContextQuery / ContextBundle v2が必要または不要と確定したこと。
- Actorごとに異なるselectionを作るべきケースの規則が確定したこと。

次は、production schemaを変えずに`DocumentV1 / ContextBundleV1`相当からD0 research networkへ投影するadapterを検討し、syntheticだけでなく既存dogfood構造をread-onlyで利用できるかを確認する。
