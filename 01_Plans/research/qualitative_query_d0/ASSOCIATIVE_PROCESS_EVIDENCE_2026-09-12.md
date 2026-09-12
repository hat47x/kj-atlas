# Associative Provider Subprocess — Execution Evidence 2026-09-12

- Status: Executable research evidence
- Scope: formal D2 request → subprocess transport → formal response → D2 normalization
- Runtime: GitHub Actions / Ubuntu 24.04 / CPython 3.12.14
- Production claim: none

## 1. 実行結果

branch実体をcheckoutし、`01_Plans/research/qualitative_query_d0`で次を実行した。

```text
python -m unittest -v
```

結果:

- **91 tests passed**
- unittest reported **0.330s**
- workflow conclusion: success

併せて確認した。

- Python compile: success
- `shell=True`非使用guard: success
- `COGNITIVE-ASSOC-01`固定benchmark source非参照guard: success
- docs check: success
- diff check: success

検証用one-shot workflowは成功後にbranchから削除した。

## 2. Process境界で確認したこと

1. SUIがformal `AssociativeRecallRequest`を構築し、stdinへJSONとして渡せる。
2. Provider stdoutのformal responseをstrict JSONとして読み、D2 normalizerへ接続できる。
3. argvは明示的な文字列配列に限定し、shell command stringを受理しない。
4. process timeout時はkillしてfail-closedする。
5. executableが存在しない場合はfail-closedする。
6. 非0終了時はresponseとして扱わない。
7. malformed JSON stdoutを拒否する。
8. duplicate JSON keyを拒否する。
9. responseがD2 contractへ違反した場合、candidate channelを生成しない。
10. request byte上限はspawn前に検査する。
11. responseはtemporary fileへ受け、byte数確認後にだけJSONとして読み込む。
12. synthetic providerとのE2Eでもsource networkを変更しない。

## 3. Transportと意味契約の分離

```text
Process transport
  != Associative Cognition semantics
  != Selection authority
  != provider ranking
  != Consensus
```

Process clientはProvider outputを解釈しない。formal responseを取得した後、既存`normalize_associative_response`がscope、candidate、abstain、provider internal signal等の意味境界を検査する。

したがって、将来transportをlocal service、container、Distributed Execution Fabric等へ変更しても、D2 response contractを変える必要はない。

## 4. 今回のProvider

E2E testではrepository同梱のsynthetic providerだけを使用した。

このsynthetic providerは候補品質を評価するものではない。目的は、

```text
Request
 -> process
 -> Response
 -> D2 normalization
```

という実行経路とfailure boundaryを検証することに限定している。

SEI Cognition側では別途、Go SACSを同じrequest/response contractへ接続するCLIを実装済みであるが、このrunではそのbinaryを取得・実行していない。

## 5. 未検証

- SUI checkoutとSEI Cognition checkoutを同一環境へ配置したactual cross-repository process execution
- production process supervision
- OS sandbox / cgroup等によるCPU・memory・disk hard limit
- remote service / network transport
- Distributed Execution Fabric経由の実行
- SEI SACSによる親和的な束ねの意味品質
- production latency / throughput

stdout/stderrをtemporary fileへ逃がすことでPython processのcapture memory増大は避けるが、providerが異常量のoutputを生成する場合のdisk hard limitまではこのsliceで実装していない。production supervisionでは別途resource boundaryが必要である。

## 6. Benchmark停止線

本E2Eはsynthetic network / synthetic providerだけを利用した。

`COGNITIVE-ASSOC-01`固定benchmarkにはD1/D2/SACSを適用していない。Human adjudication gate freeze前に意味品質baselineを生成しない。

## 7. 次段階

次は、同じformal request fixtureをSUIとSEI Cognitionの双方で固定し、両repositoryのcontract driftを検出できるcross-repository conformance fixtureを追加する。
