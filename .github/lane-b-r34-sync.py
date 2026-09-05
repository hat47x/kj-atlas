from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
replacements = {
'''- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22以降branch-only GitHub Actionsで関連回帰を繰り返し実行し、R30 run `33948026246` ではR23〜R30関連を含む45 test・ruff・`git diff --check` が成功した。恒久workflowの有無とは分けて記録する。''':
'''- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22以降branch-only GitHub Actionsで関連回帰を繰り返し実行し、R33 run `33951131455` ではR23〜R33関連を含む62 test・ruff・`git diff --check` が成功した。provider実測reportについてもR32/R33でroute/task/provider/model/usageとcanonical prompt fingerprintのfail-closed検証を固定した。恒久workflowの有無とは分けて記録する。''',
'''  - `scripts/measure_ai_route_provider_tokens.py`\n  - `scripts/measure_ai_ir_budget_pressure.py`''':
'''  - `scripts/measure_ai_route_provider_tokens.py`\n  - `scripts/analyze_ai_route_provider_measurement.py`\n  - `scripts/measure_ai_ir_budget_pressure.py`''',
'''  - `tests/test_ai_route_provider_token_measurement.py`\n  - `tests/test_ai_ir_budget_pressure.py`''':
'''  - `tests/test_ai_route_provider_token_measurement.py`\n  - `tests/test_ai_route_provider_measurement_analysis.py`\n  - `tests/test_ai_route_provider_prompt_fingerprint.py`\n  - `tests/test_ai_ir_budget_pressure.py`''',
'''  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usageを保存する。''':
'''  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usageとcanonical prompt SHA-256を含むmeasurement reportを保存する。保存reportは `scripts/analyze_ai_route_provider_measurement.py` を通し、route/task/provider/model/usage/fingerprintが現在のcanonical builderと一致した場合だけ方式比較の入力にする。''',
'''1. **named provider/modelの実入力tokenを測る。** R30まで拡張したR20ハーネスを使う。既定はgroups/layoutのcurrent/Bとnarrative/checkの6比較、groups A2も測る場合だけ `--include-groups-a2` で1件追加、layout Cも測る場合だけ `--include-layout-c` で31件追加する。layout A2はR29でroute-Bとrendered promptが完全一致したため、同じprovider/model/task/max_tokens条件では重複requestを送らず `suggest-layout-route-b` のusageを同一prompt観測として扱う。\n2. その測定値をR21の判断基準へ当てはめ、A2/B/Cを**ルートごと**に比較する。A1（`MAX_CARDS` だけを300へ上げる案）は比較対象から外す。''':
'''1. **named provider/modelの実入力tokenを測り、保存reportをR32/R33 analyzerへ通す。** R33まで拡張したR20ハーネスを使う。既定はgroups/layoutのcurrent/Bとnarrative/checkの6比較、groups A2も測る場合だけ `--include-groups-a2` で1件追加、layout Cも測る場合だけ `--include-layout-c` で31件追加する。layout A2はR29でroute-Bとrendered promptが完全一致したため、同じprovider/model/task/max_tokens条件では重複requestを送らず `suggest-layout-route-b` のusageを同一prompt観測として扱う。R33以降のreportにはexact UTF-8 promptのSHA-256を含め、現在のcanonical builderと一致しないstale/legacy reportは比較根拠へ使わない。\n2. analyzerが `decision_ready=true` と判定したprovider-reported usageだけをR21の判断基準へ当てはめ、A2/B/Cを**ルートごと**に比較する。ここでの `decision_ready` はmeasurement reportの内部整合性だけを意味し、方式採択そのものではない。A1（`MAX_CARDS` だけを300へ上げる案）は比較対象から外す。''',
}
for old, new in replacements.items():
    assert text.count(old) == 1, old[:80]
    text = text.replace(old, new)
heading = "## R34 — R32/R33後のprovider実測readiness同期"
assert heading not in text
record = r'''

## R34 — R32/R33後のprovider実測readiness同期

R32/R33でprovider measurementの保存・検証境界が強化されたため、Issue前半の受入条件注記・検証計画・次の判断順序を現行実装へ同期した。named provider/model実測後は、usageを直接A2/B/C比較へ持ち込まず、canonical prompt fingerprintを含む保存reportをR32/R33 analyzerへ通し、route/task/provider/model/usage/prompt identityが現在のbuilderと一致した結果だけをR21の比較入力にする。

本同期はdocs-onlyであり、未完了ACを完了へ変更せず、provider実測・A2/B/C採択・production cap/route変更を行わない。
'''
path.write_text(text.rstrip() + record.rstrip() + "\n", encoding="utf-8")
