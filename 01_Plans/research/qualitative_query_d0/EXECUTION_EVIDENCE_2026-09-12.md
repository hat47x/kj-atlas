# D0 Deterministic Qualitative Query — Execution Evidence 2026-09-12

- Status: Executable evidence for formal projection contract
- Scope: `QualitativeNetworkSnapshot` + formal `ContextProjectionRequest` + D0 query/projection
- Runtime: GitHub Actions, Ubuntu 24.04, CPython 3.12.14
- Formal contract: `../../../02_Architecture/information_network_projection_contract.md`

## 1. 実行結果

branch上の実ファイルをcheckoutし、`01_Plans/research/qualitative_query_d0`で次を実行した。

```bash
python -m unittest -v
python -m py_compile *.py
```

結果:

- **31 tests passed**
- unittest reported **0.024s**
- Python compile: success
- legacy executable import guard: success
- `python 01_Plans/docs_check.py`: success
- `git diff --check origin/main...HEAD`: success
- GitHub Actions workflow conclusion: success

検証用one-shot workflowは実行後にbranchから削除し、merge対象には含めない。

## 2. Formal ContextProjectionRequestで確認したこと

1. request / actor / interest / permissionをclosed-worldで検証する。
2. Permissionは`server_resolved`のみ受理する。
3. Roleが`approve` / `publish`でもpermissionを付与しない。
4. Actor kindを変えても同一selection入力を恣意的に変更しない。
5. set-like listは決定論的に正規化する。
6. legacy `document` source scopeを拒否し、formal `network / working / consensus`だけを受理する。
7. unknown Actor kindをfail-closedする。
8. readable scope空集合をfail-closedする。
9. unreviewed visibilityはpermissionとtrusted SafeMode allowanceのAND条件で決める。
10. legacy request keyをunknown keyとして拒否する。

## 3. D0 coreで確認したこと

1. explicit graph BFSによるneighborhood
2. contrastでshared / left-only / right-only facetを保持
3. bridgeで複数shortest pathを保持しstrength scoreを付けない
4. explicit pathが無いことを`unrelated`と断定しない
5. residualをparallel reasonsとして返しscore化しない
6. hold / unreviewed / Critique / contradictionをunresolvedとして保持
7. temporal orderingをcausalityへ読み替えない
8. provenanceをsource / actor別に保持し、欠落も残す
9. 同一selectionをcomparison table / subgraph / spatial layoutへ投影できる
10. D0が`compact_narrative`生成を拒否しD4境界を維持する
11. query実行がsource networkを変更しない
12. unknown refsをfail-closedする

## 4. Multi-actor E2Eで確認したこと

1. Human / Generative AI / SEIが同じcontrast inquiryとfocusから**同一selection digest**を得る。
2. 同一selectionをHumanには`comparison_table + spatial_layout`、SEIには`subgraph`として返せる。
3. Generative AIの`compact_narrative`要求をD0で生成せずD4へ明示deferする。
4. actor identityはtraceとして保持するがselection内容へ混入しない。
5. SafeMode allowanceなしで未レビューfocusをfail-closedする。
6. `canSeeUnreviewed=true`かつSafeMode allowanceありの場合だけ未レビューnodeを入力へ含める。
7. Permissionが未レビュー閲覧を許さなければSafeMode allowanceだけでは見えない。
8. Query / Projection実行で元networkを変更しない。
9. E2E responseへ`score / confidence / importance / rank`を導入しない。
10. 複数D0 selection intentを曖昧に統合せずfail-closedする。
11. `affinity`をD0へ黙って読み替えずD2/D3以降へ残す。

## 5. Legacy boundary

実行検証では、D0実装ディレクトリに次が残っていないことも確認した。

- `context_projection_r0`
- `compile_projection_request`
- `compiledContextQuery`

旧 `DocumentV1 / ContextQueryV1 / ContextBundleV1` へのcompile・adapterは正式pipelineに含めない。

正式pipelineは次である。

```text
SUI Information Network
 -> QualitativeNetworkSnapshot
 -> ContextProjectionRequest
 -> D0..D5 Selection / Analysis
 -> Context Projection
```

## 6. このEvidenceが意味すること

- D0の7種Queryを生成モデルなしで決定論的に実行できる。
- formal Requestを旧Queryへの変換なしで直接D0へ渡せる。
- residual / unresolvedをrankingではなく理由と状態として返せる。
- bridge pathを意味の強さへ昇格させず候補経路として返せる。
- SelectionとProjectionを分離し、同じselectionを主体別interfaceへ整形できる。
- Actor kind / RoleとPermissionを分離できる。
- Query / Projectionはread-only derived viewとして実行できる。

## 7. このEvidenceが意味しないこと

- SUI Information Networkの永続storageが完成したこと。
- WorkingGraph / ConsensusGraphの永続実装が完成したこと。
- Authorization layer全体が完成したこと。
- 実データ規模でlatency / memory要件を満たすこと。
- D0だけで深層意味近接を扱えること。
- D1 / D2 / D3 / D4が不要であること。
- Queryが実利用で認知品質を向上させたこと。

次は旧仕様互換を挟まず、formal snapshot上へD1 lexical sparseを追加する。
