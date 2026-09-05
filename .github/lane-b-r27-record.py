from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
heading = "## R27 — layout C のlocal/global出力合成契約をcharacterizeする"
assert heading not in text

section = r'''


## R27 — layout C のlocal/global出力合成契約をcharacterizeする

R25でlayout Cの入力を30 local + 1 globalへ欠落なく分割し、R26でその31 promptを明示opt-in時だけnamed provider計測へ載せられるようにした。一方、Cを実方式として考えるには「31個のstage出力から、最終的に300カードを1つの座標空間へ戻せるか」という合成契約も必要である。これはprovider/model品質とは独立に決定論的に検証できるため、`scripts/measure_ai_layout_hierarchical_composition.py` で**測定専用のlocal/global合成器**をcharacterizeした。production `/ai/suggest-layout` は変更していない。

合成規則は単純に、各cardについて `finalX = batch.anchorX + card.dx`、`finalY = batch.anchorY + card.dy` とする。local stageはbatch自身の原点まわりのoffsetだけを返し、global stageはbatch anchorだけを返す。viewportのpan/zoomは階層処理が新しく発明せず、source Documentのtransformをそのまま保持する。

300カード・30島のR25代表入力に対して、元の各島centroidをglobal anchor、元座標からcentroidを引いた値をlocal offsetとするsynthetic identity responseを作り、合成した結果は次のとおりだった。

- card ID: 300/300を各1回保持。
- source座標の再構成: x/yとも最大絶対誤差 **0.0**。
- source transform: `panX=0, panY=0, zoom=1` をそのまま保持。
- global translation probe: 全anchorを `(x + 250, y - 125)` とすると、300/300 cardが同じvectorだけ移動し、期待座標との差はx/yとも **0.0**。
- local perturbation probe: `island:i29` 内の `c299` のlocal offsetだけを `(dx + 7.5, dy - 3.25)` とすると、移動したIDは **`c299` だけ**で、期待座標との差はx/yとも **0.0**。
- direct island membershipから外れたcardをR25規則でsingleton batchにした場合も、そのcardを含む300枚全量を再構成できる。

さらに、stage出力を「一部だけ都合よく採用」しないため、合成器は次をfail-closedで固定した。

- local response集合はplan上のbatch集合と完全一致しなければならない。
- 各local responseは、そのbatchのcardを全件・重複なし・未知IDなしでちょうど1回ずつ返さなければならない。
- global responseは全batch anchorを全件・重複なし・未知IDなしでちょうど1回ずつ返さなければならない。
- local offset / global anchor / composed coordinateは有限数だけを受け付ける。
- 最終compositionはsource card集合を全量・各1回覆わなければならない。
- source card / island / edge順を反転してもidentity composition結果は同一になる。

GitHub Actions run `33947383473` では、R27新規回帰にR25/R26/R23系を加えた **33 test**、ruff、`git diff --check` が成功した。一時workflowは成功後に自己削除済みである。

**非主張**: R27で使ったstage出力はすべてsynthetic fixtureであり、外部providerは呼んでいない。したがって、実modelが良いlocal offset / global anchorを返すか、31出力を用いた最終配置がone-shot Bより良いか、token費用・latency・failure rateが許容できるかは未評価である。R27が閉じたのは「有効なstage出力が揃ったなら、意味のある二段座標系を決定論的かつ完全に1配置へ合成できる」という構造契約までであり、Cのproduction採択やA2/B/Cの最終選択ではない。
'''

path.write_text(text.rstrip() + section + "\n", encoding="utf-8")
