from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
heading = "## R29 — A2をproduction cap変更なしで代表入力へcharacterizeする"
assert heading not in text

section = r'''


## R29 — A2をproduction cap変更なしで代表入力へcharacterizeする

R23で方式B、R25/R27でlayout方式Cをmeasurement-only候補として具体化した一方、A2（card上限とtext予算を整合して広げる）はR21の判断基準だけで、同じ代表入力上の具体prompt比較がなかった。そこで `scripts/measure_ai_route_a2_candidate.py` を追加し、production定数を変更せずに、300カード代表入力がshared IRへ**ちょうど収まる下限fixture**をcharacterizeした。

下限fixtureは、sourceを正規化した結果から `MAX_CARDS=300`、`MAX_TEXT_CHARS=13,800` を一時的に適用し、`MAX_RELATIONS=400` は現行値のままとする。これは余裕を持ったproduction cap案ではなく、代表入力についてcard/text由来のtruncationを起こさないための下限に過ぎない。context manager終了時には例外発生時も含め、production定数 `200 / 12,000 / 400` が復元される回帰を固定した。

代表入力での結果は次のとおり。

| route | A2下限候補 | route-B候補 | 観測 |
| --- | ---: | ---: | --- |
| `suggest-card-groups` | 56,047 UTF-8 bytes | 48,791 UTF-8 bytes | 両方とも300/300候補、30/30島、held 1件を保持するがpromptは非同一。A2はshared IR由来の300 relationも保持し、BはR19で必須でないrelationを省く |
| `suggest-layout` | 128,562 UTF-8 bytes | 128,562 UTF-8 bytes | 300座標・300 relation・30島を両方とも保持し、**rendered promptは完全一致** |

A2下限候補はgroups/layoutとも `truncation=false` となり、groupsでは299 groupable + held 1、layoutでは末尾 `c298/c299` 座標と `causal` / `negate` も保持した。これによりA2が「300カードなら一律Bと同じ入力」ではないことが明確になった。groupsではBの意味選択がpromptを実際に小さくする一方、layoutではroute-required構造がほぼshared IR全量に近いため、この代表入力ではA2とBがproviderへ送るpromptとして同じになる。

このlayout同値性はtoken推定ではない。prompt文字列が同一で、既存provider transportが `LLMRequest.inputs` ではなくpromptを送るというR24/R26の測定契約上、同じprovider/model/task/max_tokensならlayout A2のinput token測定をBと別requestで重複させる必要がないことを示す。一方、groups A2はpromptが異なるため、exact token比較が必要ならnamed provider/modelで別途測る必要がある。

GitHub Actions run `33947860553` では、R29とR23/R24/R25/R27関連を含む **39 test**、ruff、`git diff --check` が成功した。一時workflow/patch helperは成功後に自己削除済みである。

**非主張**: `300 / 13,800` はproduction上限案ではなく、代表fixtureをちょうど収める下限値である。bytesはtoken数ではなく、providerの入力上限や費用へ換算しない。外部providerは呼んでおらず、A2/B/Cの採択も行っていない。productionの `MAX_CARDS=200 / MAX_TEXT_CHARS=12,000 / MAX_RELATIONS=400` は変更していない。
'''

path.write_text(text.rstrip() + section.rstrip() + "\n", encoding="utf-8")
