from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")

old = "- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22以降branch-only GitHub Actionsで関連回帰を繰り返し実行し、R37 run `33953053815` ではR23〜R37関連を含む73 test・ruff・`git diff --check` が成功した。provider実測reportについてもR32/R33/R35/R37でroute/task/provider/model/usage、canonical user prompt fingerprint、primary call provenanceに加え、DeepSeekでは実transportが送るsystem+user message content fingerprintまでfail-closed検証を固定した。恒久workflowの有無とは分けて記録する。"
new = "- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22以降branch-only GitHub Actionsで関連回帰を繰り返し実行し、R39 run `33954945719` ではR23〜R39関連を含む77 test・ruff・`git diff --check` が成功した。provider実測reportについてもR32/R33/R35/R37でroute/task/provider/model/usage、canonical user prompt fingerprint、primary call provenanceに加え、DeepSeekでは実transportが送るsystem+user message content fingerprintまでfail-closed検証を固定し、R39ではmeasurementの `max_tokens=1` と現行production output reserveを分離したcontext hard-fit計算を固定した。恒久workflowの有無とは分けて記録する。"
assert text.count(old) == 1
text = text.replace(old, new, 1)

old = "  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usage、canonical user prompt SHA-256、primary call provenanceを含むmeasurement reportを保存する。DeepSeekの場合はさらに、実transportと同じbuilderから得たsystem+user message contentのprovider-input SHA-256を保存する。保存reportは `scripts/analyze_ai_route_provider_measurement.py` を通し、route/task/provider/model/usage/user-prompt fingerprint、transport/requested_at/trace_id、fallbackなし、primary execution pathに加え、DeepSeekではprovider-input fingerprintが現在のtransport inputと一致した場合だけ方式比較の入力にする。"
new = "  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usage、canonical user prompt SHA-256、primary call provenanceを含むmeasurement reportを保存する。DeepSeekの場合はさらに、実transportと同じbuilderから得たsystem+user message contentのprovider-input SHA-256を保存する。保存reportは `scripts/analyze_ai_route_provider_measurement.py` を通し、route/task/provider/model/usage/user-prompt fingerprint、transport/requested_at/trace_id、fallbackなし、primary execution pathに加え、DeepSeekではprovider-input fingerprintが現在のtransport inputと一致した場合だけ方式比較の入力にする。named model/providerの文書化されたcontext-window値を確認できる場合は `--context-window-tokens` を明示し、provider-reported input usageに現行production output reserveを加えた最低context必要量がhard-fitするかを別途確認する。hard-fitはR21の「十分な余裕」そのものとは扱わない。"
assert text.count(old) == 1
text = text.replace(old, new, 1)

old = "1. **named provider/modelの実入力tokenを測り、保存reportをR32/R33/R35/R37 analyzerへ通す。** R37まで拡張したR20ハーネスを使う。既定はgroups/layoutのcurrent/Bとnarrative/checkの6比較、groups A2も測る場合だけ `--include-groups-a2` で1件追加、layout Cも測る場合だけ `--include-layout-c` で31件追加する。layout A2はR29でroute-Bとrendered promptが完全一致したため、同じprovider/model/task/max_tokens条件では重複requestを送らず `suggest-layout-route-b` のusageを同一prompt観測として扱う。reportにはexact UTF-8 user promptのSHA-256とprimary provider call provenanceを含め、DeepSeekでは実transportが送るsystem+user message contentのSHA-256も含める。現在のcanonical builder/transport inputと一致しないstale/legacy report、fallback/non-primary call、trace欠落reportは比較根拠へ使わない。\n2. analyzerが `decision_ready=true` と判定したprovider-reported usageだけをR21の判断基準へ当てはめ、A2/B/Cを**ルートごと**に比較する。ここでの `decision_ready` はmeasurement reportの内部整合性だけを意味し、方式採択そのものではない。A1（`MAX_CARDS` だけを300へ上げる案）は比較対象から外す。"
new = "1. **named provider/modelの実入力tokenを測り、保存reportをR32/R33/R35/R37/R39 analyzerへ通す。** R37まで拡張したR20ハーネスを使う。既定はgroups/layoutのcurrent/Bとnarrative/checkの6比較、groups A2も測る場合だけ `--include-groups-a2` で1件追加、layout Cも測る場合だけ `--include-layout-c` で31件追加する。layout A2はR29でroute-Bとrendered promptが完全一致したため、同じprovider/model/task/max_tokens条件では重複requestを送らず `suggest-layout-route-b` のusageを同一prompt観測として扱う。reportにはexact UTF-8 user promptのSHA-256とprimary provider call provenanceを含め、DeepSeekでは実transportが送るsystem+user message contentのSHA-256も含める。現在のcanonical builder/transport inputと一致しないstale/legacy report、fallback/non-primary call、trace欠落reportは比較根拠へ使わない。\n2. analyzerが `decision_ready=true` と判定したprovider-reported usageについて、named model/providerの文書化されたcontext-window値を確認できる場合はR39の `--context-window-tokens` で **input usage + 現行production output reserve** のhard-fitを確認する。layout Cは31件aggregateではなく最大単一requestを対象にする。context-window値が未確認ならhard-fitを推測しない。\n3. hard-fitを満たすこととR21の「十分な余裕」は分ける。安全余裕policyを後付けで捏造せず、provider/modelの制約・実測値・必要なら実model品質を根拠にA2/B/Cを**ルートごと**に比較する。ここでの `decision_ready` と `hard_context_fit` は方式採択そのものではない。A1（`MAX_CARDS` だけを300へ上げる案）は比較対象から外す。"
assert text.count(old) == 1
text = text.replace(old, new, 1)
# Shift the remaining judgment numbers after inserting a new step.
text = text.replace("\n3. `generate-narrative`", "\n4. `generate-narrative`", 1)
text = text.replace("\n4. `suggest-layout`", "\n5. `suggest-layout`", 1)
text = text.replace("\n5. coverage-loss metadata", "\n6. coverage-loss metadata", 1)

heading = "## R40 — R39後のcontext hard-fit手順をIssue前半へ同期"
assert heading not in text
record = r'''

## R40 — R39後のcontext hard-fit手順をIssue前半へ同期

R39でprovider-reported input usageと現行production output reserveを分離し、operatorがnamed model/providerの文書化されたcontext-window値を明示した場合だけhard-fitを計算できるようになったため、Issue前半の受入条件注記・実使用確認・次の判断順序を現行実装へ同期した。

実測後の順序は、(1) R32/R33/R35/R37のmeasurement provenance/identity検証、(2) R39の `input + production output reserve` hard-fit確認、(3) R21の「十分な余裕」と方式比較、の三段階とする。layout Cではaggregate usageをcontext windowへ誤適用せず最大単一requestを使う。hard-fitと安全余裕policyは同一視しない。

本同期はdocs-onlyであり、外部provider実測、context-window値の推測、A2/B/C採択、production cap/route変更、未完了ACの完了化を行わない。
'''
text = text.rstrip() + record.rstrip() + "\n"
path.write_text(text, encoding="utf-8")
