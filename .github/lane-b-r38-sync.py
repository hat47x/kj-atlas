from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")

replacements = {
'''- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22以降branch-only GitHub Actionsで関連回帰を繰り返し実行し、R35 run `33952594490` ではR23〜R35関連を含む68 test・ruff・`git diff --check` が成功した。provider実測reportについてもR32/R33/R35でroute/task/provider/model/usage、canonical prompt fingerprint、primary call provenanceのfail-closed検証を固定した。恒久workflowの有無とは分けて記録する。''':
'''- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22以降branch-only GitHub Actionsで関連回帰を繰り返し実行し、R37 run `33953053815` ではR23〜R37関連を含む73 test・ruff・`git diff --check` が成功した。provider実測reportについてもR32/R33/R35/R37でroute/task/provider/model/usage、canonical user prompt fingerprint、primary call provenanceに加え、DeepSeekでは実transportが送るsystem+user message content fingerprintまでfail-closed検証を固定した。恒久workflowの有無とは分けて記録する。''',
'''  - `tests/test_ai_route_provider_call_provenance.py`
  - `tests/test_ai_ir_budget_pressure.py`''':
'''  - `tests/test_ai_route_provider_call_provenance.py`
  - `tests/test_ai_route_provider_transport_input_provenance.py`
  - `tests/test_ai_ir_budget_pressure.py`''',
'''  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usage、canonical prompt SHA-256、primary call provenanceを含むmeasurement reportを保存する。保存reportは `scripts/analyze_ai_route_provider_measurement.py` を通し、route/task/provider/model/usage/fingerprintに加えてtransport/requested_at/trace_id、fallbackなし、primary execution pathが整合した場合だけ方式比較の入力にする。''':
'''  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usage、canonical user prompt SHA-256、primary call provenanceを含むmeasurement reportを保存する。DeepSeekの場合はさらに、実transportと同じbuilderから得たsystem+user message contentのprovider-input SHA-256を保存する。保存reportは `scripts/analyze_ai_route_provider_measurement.py` を通し、route/task/provider/model/usage/user-prompt fingerprint、transport/requested_at/trace_id、fallbackなし、primary execution pathに加え、DeepSeekではprovider-input fingerprintが現在のtransport inputと一致した場合だけ方式比較の入力にする。''',
'''1. **named provider/modelの実入力tokenを測り、保存reportをR32/R33/R35 analyzerへ通す。** R35まで拡張したR20ハーネスを使う。既定はgroups/layoutのcurrent/Bとnarrative/checkの6比較、groups A2も測る場合だけ `--include-groups-a2` で1件追加、layout Cも測る場合だけ `--include-layout-c` で31件追加する。layout A2はR29でroute-Bとrendered promptが完全一致したため、同じprovider/model/task/max_tokens条件では重複requestを送らず `suggest-layout-route-b` のusageを同一prompt観測として扱う。R35以降のreportにはexact UTF-8 promptのSHA-256とprovider call provenanceを含め、現在のcanonical builderと一致しないstale/legacy report、fallback/non-primary call、trace欠落reportは比較根拠へ使わない。''':
'''1. **named provider/modelの実入力tokenを測り、保存reportをR32/R33/R35/R37 analyzerへ通す。** R37まで拡張したR20ハーネスを使う。既定はgroups/layoutのcurrent/Bとnarrative/checkの6比較、groups A2も測る場合だけ `--include-groups-a2` で1件追加、layout Cも測る場合だけ `--include-layout-c` で31件追加する。layout A2はR29でroute-Bとrendered promptが完全一致したため、同じprovider/model/task/max_tokens条件では重複requestを送らず `suggest-layout-route-b` のusageを同一prompt観測として扱う。reportにはexact UTF-8 user promptのSHA-256とprimary provider call provenanceを含め、DeepSeekでは実transportが送るsystem+user message contentのSHA-256も含める。現在のcanonical builder/transport inputと一致しないstale/legacy report、fallback/non-primary call、trace欠落reportは比較根拠へ使わない。''',
}

for old, new in replacements.items():
    assert text.count(old) == 1, old[:80]
    text = text.replace(old, new, 1)

heading = "## R38 — R37後のprovider-input readiness同期"
assert heading not in text
record = r'''
## R38 — R37後のprovider-input readiness同期

R37でDeepSeekのprovider-reported input token観測を、canonical user promptだけでなく実transportが送るsystem+user message contentへも結び付けたため、Issue前半の回帰証拠・検証計画・外部実測条件・次の判断順序を現行実装へ同期した。named DeepSeek実測reportは、R33のuser-prompt fingerprint、R35のprimary call provenance、R37のprovider-input fingerprintがすべて現在のbuilder/transportと一致した場合だけR21の方式比較入力へ進める。

本同期はdocs-onlyであり、外部provider実測・A2/B/C採択・production cap/route変更を行わず、未完了ACを完了へ変更しない。
'''
text = text.rstrip() + "\n\n" + record.strip() + "\n"
path.write_text(text, encoding="utf-8")
