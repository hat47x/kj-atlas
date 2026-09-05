from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        "方式の比較条件はR21を正本とする。要約すると、A1（`MAX_CARDS` だけの引上げ）は候補から外し、A2（カード上限と文字数予算を整合して広げる）・B（ルート別意味保存）・C（分割・階層処理）を、R20の実token測定後にルートごとに比較する。",
        "方式の比較条件はR21を正本とする。要約すると、A1（`MAX_CARDS` だけの引上げ）は候補から外し、A2（カード上限と文字数予算を整合して広げる）・B（ルート別意味保存）・C（分割・階層処理）を、R20系の実token測定後にルートごとに比較する。R29でA2の300カード下限fixture、R23でB、R25/R27でlayout Cをmeasurement-only候補として具体化済みである。",
    ),
    (
        "- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22〜R27ではbranch-only GitHub Actionsで関連回帰を繰り返し実行し、直近R27 run `33947383473` では33 test・ruff・`git diff --check` が成功した。恒久workflowの有無とは分けて記録する。",
        "- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22以降branch-only GitHub Actionsで関連回帰を繰り返し実行し、R30 run `33948026246` ではR23〜R30関連を含む45 test・ruff・`git diff --check` が成功した。恒久workflowの有無とは分けて記録する。",
    ),
    (
        "  - `scripts/measure_ai_route_projection_candidates.py`\n  - `scripts/measure_ai_layout_hierarchical_candidate.py`",
        "  - `scripts/measure_ai_route_projection_candidates.py`\n  - `scripts/measure_ai_route_a2_candidate.py`\n  - `scripts/measure_ai_layout_hierarchical_candidate.py`",
    ),
    (
        "  - `tests/test_ai_route_projection_candidates.py`\n  - `tests/test_ai_layout_hierarchical_candidate.py`",
        "  - `tests/test_ai_route_projection_candidates.py`\n  - `tests/test_ai_route_a2_candidate.py`\n  - `tests/test_ai_layout_hierarchical_candidate.py`",
    ),
    (
        "1. **named provider/modelの実入力tokenを測る。** R24/R26まで拡張したR20ハーネスを使い、既定ではgroups/layoutのcurrent/Bとnarrative/checkの6比較を同じmodel/providerで測る。layout Cも比較する場合だけ `--include-layout-c` を明示し、30 local + 1 globalを追加する。",
        "1. **named provider/modelの実入力tokenを測る。** R30まで拡張したR20ハーネスを使う。既定はgroups/layoutのcurrent/Bとnarrative/checkの6比較、groups A2も測る場合だけ `--include-groups-a2` で1件追加、layout Cも測る場合だけ `--include-layout-c` で31件追加する。layout A2はR29でroute-Bとrendered promptが完全一致したため、同じprovider/model/task/max_tokens条件では重複requestを送らず `suggest-layout-route-b` のusageを同一prompt観測として扱う。",
    ),
]

for old, new in replacements:
    assert text.count(old) == 1, old[:120]
    text = text.replace(old, new)

heading = "## R31 — R29/R30後のprovider実測readiness同期"
assert heading not in text
section = r'''


## R31 — R29/R30後のprovider実測readiness同期

R29でA2下限fixtureをcharacterizeし、R30でgroups A2だけを追加明示opt-inとしてprovider計測ハーネスへ接続したため、Issue前半の方式要約・検証計画・次の判断順序を現在地へ同期した。

- A2/B/Cはいずれもproduction非変更のmeasurement-only候補として比較可能になったことを方式要約へ反映した。
- 検証計画へ `measure_ai_route_a2_candidate.py` / `test_ai_route_a2_candidate.py` を追加した。
- named provider/model実測手順を、既定6件、groups A2追加時7件、layout C追加時37件、両方追加時38件となるR30契約へ更新した。
- layout A2はR29でroute-Bとrendered promptが完全一致したため、重複provider requestを送らない判断を明記した。
- branch-only regressionの記録をR30 run `33948026246` の45 test成功へ更新した。

**非主張**: R31は正本同期のみであり、未完了の受入条件を完了扱いにしない。provider-reported usageは依然未取得で、production strategy、上限値、A2/B/Cの採択、本IssueのIn Progress状態は変更しない。
'''
text = text.rstrip() + section.rstrip() + "\n"
path.write_text(text, encoding="utf-8")
