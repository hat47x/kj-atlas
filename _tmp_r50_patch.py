from __future__ import annotations

import os
from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text()
marker = "## 次の判断順序\n"
assert text.count(marker) == 1
assert "### 外部実測runbook（R50）" not in text

runbook = r'''### 外部実測runbook（R50）

R20〜R49で固定した実測契約を、外部送信前に同じ順序で再現できる最小runbookとして正本化する。以下は `03_Implement/backend` を作業ディレクトリとする。API keyは既存の安全な方法で `KJ_ATLAS_DEEPSEEK_API_KEY` に設定済みであることを前提とし、本runbookからsecret値を表示・保存・再確認しない。

1. **まずnetwork-free dry-runを実行する。** これはproviderを解決せず、6 routeのcanonical prompt/report形状だけを確認する。

   ```bash
   python scripts/measure_ai_route_provider_tokens.py \
     --provider deepseek \
     --model deepseek-v4-flash \
     --deepseek-thinking-mode disabled \
     > ai-ir-scale-deepseek-v4-flash-dry-run.json
   ```

   `executed=false`、6 route、`expected_deepseek_thinking_mode=disabled` を確認する。dry-runの `measurement_complete=false` は正常であり、token evidenceとして扱わない。

2. **明示的に外部実測を許可した場合だけ、production既定相当のcore 6 requestを送る。** `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の二重opt-inに加え、provider/model/thinking modeを環境とCLIで一致させる。

   ```bash
   KJ_ATLAS_LLM_PROVIDER=deepseek \
   KJ_ATLAS_DEEPSEEK_MODEL=deepseek-v4-flash \
   KJ_ATLAS_DEEPSEEK_THINKING_MODE=disabled \
   KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1 \
   python scripts/measure_ai_route_provider_tokens.py \
     --provider deepseek \
     --model deepseek-v4-flash \
     --deepseek-thinking-mode disabled \
     --execute \
     > ai-ir-scale-deepseek-v4-flash.json
   ```

   この段階では既定6 requestだけを送り、A2/Cの追加requestは混ぜない。transport/usage契約が正常に成立することを最小call数で先に確認する。

3. **保存reportをanalyzerへ通す。** provider-reported input usage、prompt/provider-input fingerprint、primary call provenance、DeepSeek `thinking.type` が現在の契約と一致した場合だけ `decision_ready=true` になり得る。

   ```bash
   python scripts/analyze_ai_route_provider_measurement.py \
     ai-ir-scale-deepseek-v4-flash.json \
     > ai-ir-scale-deepseek-v4-flash-analysis.json
   ```

   context-windowのhard-fitも評価する場合だけ、provider/model資料で確認した正の値と監査可能なsourceを `--context-window-tokens` / `--context-window-source` の対で追加する。値を推測して埋めない。

4. **core 6が正常に測れた後でのみ、必要なら候補比較を拡張する。** groups A2は `--include-groups-a2` で計7 request、layout Cは `--include-layout-c` で計37 request、両方同時なら計38 requestとなる。追加call数・費用・latencyを理解したうえで明示的に選ぶ。layout A2はR29どおりroute-Bとprompt同一なので重複送信しない。

`--execute` だけを付け、`KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` を付けない場合は `external-execution-not-opted-in` / exit 2でprovider解決前に停止する。R50のnetwork-free回帰でこの順序も固定する。

### 事前整備の完了境界（R50）

R20〜R49で、代表fixture、current/B/A2/C測定候補、provider-reported usage限定、prompt/provider-input/call provenance、production output reserve、context-window source、DeepSeek V4 model/thinking mode、fail-closed analyzerまで揃った。R50では上記runbookを実CLIでnetwork-free検証したため、**具体的な新欠陥が見つからない限り、外部実測前のscaffolding追加はここで止める**。

以後このIssueで意味のある次の進行は、明示的に許可されたnamed provider/model外部実測からprovider-reported input tokenを取得すること、その結果でhard-fit/十分な余裕/A2-B-Cをrouteごとに判断することである。認証情報や外部実行許可がない状態では、token値を推定せず、方式採択・production cap変更・汎用coverage-loss metadata追加へ先回りしない。

'''
text = text.replace(marker, runbook + marker, 1)

heading = "## R50 — 外部実測runbookと事前整備完了境界を固定"
assert heading not in text
run_id = os.environ["R50_RUN_ID"]
text = text.rstrip() + f"""


{heading}

R20〜R49の実測契約を、`dry-run -> core 6外部実測 -> analyzer -> 必要時だけA2/C追加` のrunbookへまとめた。GitHub Actions run `{run_id}` では実際のCLIを用いてDeepSeek V4 production既定相当のdry-runが6 route・network-freeで成立することと、`--execute` だけでは `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` 不在によりprovider解決前にexit 2で停止することを確認した。

本runで外部providerは呼んでいない。R50を外部実測前scaffoldingの完了境界とし、具体的な欠陥が新たに見つからない限りprovenanceや候補実装を追加しない。未完了AC、provider-reported token、A2/B/C採択、production cap/route、十分な余裕policyは変更しない。
"""
path.write_text(text.rstrip() + "\n")
