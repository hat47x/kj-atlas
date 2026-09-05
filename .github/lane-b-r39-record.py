from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
heading = "## R39 — provider input usage と production output reserve を分離してcontext hard-fitを判定する"
assert heading not in text
record = r'''

## R39 — provider input usage と production output reserve を分離してcontext hard-fitを判定する

R20〜R38でnamed provider/modelの入力token実測・prompt/transport provenance・report整合性検証を準備したが、measurement requestは外部費用を抑えるため `max_tokens=1` で送る一方、現行productionの対象routeは `LLMRequest` の既定 `max_tokens=2000` を使う。この2つを混同すると、provider-reported input usageが得られても「productionでcontext windowへ収まるか」を1-token出力予約で過小評価する余地があった。

R39では `analyze_ai_route_provider_measurement.py` にcontext budget summaryを追加し、token推定や方式採択をせず次を固定した。

- measurement harnessのrequestは引き続き `max_tokens=1` であることをcanonical requestから検証し、driftしたreport/builderは比較準備に通さない。
- 現行productionのoutput reserveは数値を別途複製せず、`LLMRequest` の既定 `max_tokens` から取得する。現時点では **2000 tokens** である。
- routeごとの最低context必要量を `provider-reported input_tokens + current production output reserve` として算出する。input token値は従来どおりprovider自身のusageだけを使い、bytes/chars/hashから補わない。
- CLIの `--context-window-tokens` にoperatorがnamed model/providerの文書化されたcontext-window値を明示した場合だけ、残余tokenとhard fit (`minimum <= context window`) を算出する。context window自体をrepo側で推測・固定しない。
- layout Cの31 requestはaggregate input tokenを1つのcontext windowとみなさず、**最大単一requestのinput usage + output reserve** をhard-fit対象にする。aggregateはcost/throughput比較用の別観測として維持する。
- R21の「十分な余裕」はhard-fitと別の設計判断として残し、analyzerは安全余裕率・閾値を新たに発明しない (`sufficient_headroom_policy=null`)。hard-fitしただけでA2/B/Cを採択しない。

branch-only GitHub Actions run `33954945719` でR23〜R39関連を含む **77 test**、ruff、`git diff --check` が成功した。一時patch/workflowは同run内で自己削除した。

**非主張**: R39は実modelのcontext-window値を決めず、外部providerを呼ばず、実token値・cost・latency・品質・安全余裕policyを取得/決定していない。A2/B/C採択、production cap/route、SafeMode・防PII・structured-text-only・proposal-only境界は未変更であり、未完了ACは完了扱いにしない。
'''
path.write_text(text.rstrip() + record.rstrip() + "\n", encoding="utf-8")
