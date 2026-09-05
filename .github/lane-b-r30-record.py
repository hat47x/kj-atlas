from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
heading = "## R30 — groups A2のprovider usageを追加明示opt-inで測定可能にする"
assert heading not in text

section = r'''


## R30 — groups A2のprovider usageを追加明示opt-inで測定可能にする

R29でA2下限候補をcharacterizeした結果、`suggest-card-groups` はA2とBでpromptが異なる一方、`suggest-layout` はA2とBのrendered promptが完全一致した。そこでnamed provider/model実測の公平性を高めつつ、不要なprovider callを増やさないよう、R20/R24/R26の計測ハーネスへ**groups A2だけを追加の明示opt-in**として接続した。

- 既定動作は従来どおり6 requestのまま変更しない。
- CLIへ `--include-groups-a2` を追加した。このflagを指定した場合だけ `suggest-card-groups-a2-lower-bound` を1 request追加し、7 requestになる。
- `--include-groups-a2 --include-layout-c` を両方指定した場合は、既定6 + groups A2 1 + layout C 31 = **38 request**になる。
- layout A2はR29でroute-Bとprompt文字列が完全一致しているため、`suggest-layout-a2-lower-bound` の重複provider requestは追加しない。layout A2のexact input usage比較には既存 `suggest-layout-route-b` のprovider-reported usageをそのまま同一prompt観測として使える。
- groups A2 promptを作る際だけR29のtemporary representative-fit budgetを使い、provider requestを構築する前にproduction定数 `MAX_CARDS=200 / MAX_TEXT_CHARS=12,000 / MAX_RELATIONS=400` へ復元する。
- 外部送信には従来どおり `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` が必要であり、groups A2を送るにはさらに `--include-groups-a2` が必要である。provider/model一致確認、fallback禁止、合成データ限定も維持する。
- groups A2の56,047 UTF-8 bytesはdiagnosticであり、provider usageへ換算しない。fake provider回帰では7件目に任意のreported usage `106` を返し、その値だけが `input_tokens` として記録されることを確認した。usage欠落時は `provider-did-not-report-usage` のままmeasurement incompleteになる。

GitHub Actions run `33948026246` では、既定6 / A2 7 / A2+C 38のdry-run件数、direct CLIのnetwork-free性、provider-reported usageのみを採用する境界、R23〜R29関連を含む **45 test**、ruff、`git diff --check` が成功した。一時workflow/patch helperは成功後に自己削除済みである。

**非主張**: R30でも外部providerは呼んでいない。groups A2のexact token数は未測定であり、layout B/A2やCの実token数も未測定である。A2/B/Cのproduction採択、shared IR cap変更、route変更は行っておらず、本Issueは引き続きIn Progressである。
'''

path.write_text(text.rstrip() + section.rstrip() + "\n", encoding="utf-8")
