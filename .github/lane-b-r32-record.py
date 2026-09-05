from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
heading = "## R32 — provider実測結果のfail-closed検証・比較analyzer"
assert heading not in text
record = r'''

## R32 — provider実測結果のfail-closed検証・比較analyzer

R30まででnamed provider/modelへ実測する入力集合は揃ったが、保存したJSONをそのまま人手で読み、dry-runやpartial resultを誤って方式比較の根拠へ昇格させる余地が残っていた。そこで `scripts/analyze_ai_route_provider_measurement.py` と `tests/test_ai_route_provider_measurement_analysis.py` を追加し、R20/R24/R26/R30のmeasurement reportを**provider実測後の判断入力として使えるか**だけを機械的に検証する層を固定した。

- 正本scenario `300-cards-30-islands-ring` とmeasurement kindを要求する。
- 既定6 routeはすべて `status=measured`、expected/actual provider一致、expected/actual model一致、非負整数の `provider_reported.input_tokens` を要求する。dry-run、missing usage、provider/model mismatch、route欠落はfail-closedする。
- groups A2はR30の追加routeが存在するときだけ比較可能とし、current / B / A2のtoken差をprovider-reported値だけから算出する。prompt bytes/charsは一切tokenへ変換しない。
- layout A2はR29の「route-Bとrendered prompt完全一致」契約により、route-B usageを同一prompt観測として再利用することを明示する。重複provider requestは追加しない。
- layout Cが存在する場合はlocal 30 + global 1の**31件全部**がmeasuredでなければaggregate/max tokenを出さない。partial Cを31件相当へ補完・推定しない。
- Cの `max_single_input_tokens` は1 requestあたりの圧力、`aggregate_input_tokens` は31 request総量として別々に保持する。A2/Bの1 request値とC aggregateを同じ意味の数字として扱わない。
- analyzer自身はmodel context limitを知らず、A2/B/Cを選択しない。`decision_ready` は「少なくとも既定6 routeの実測reportが内部整合している」ことだけを表し、方式採択の判定ではない。

branch-only GitHub Actions run `33950682087` で、R32とR23〜R30関連を含む **54 test**、ruff、`git diff --check` が成功した。workflowは同run内で自己削除した。テストではprompt byte値をprovider token値と意図的に無関係な数へ崩し、差分計算が `provider_reported.input_tokens` のみを使うことも固定した。

**非主張**: 外部providerは呼んでいない。実token値、modelの安全余裕、cost、latency、品質は未取得であり、A2/B/Cの採択・production cap・production routeは変更しない。本Issueは引き続きIn Progressである。
'''
path.write_text(text.rstrip() + record + "\n", encoding="utf-8")
