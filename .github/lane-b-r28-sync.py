from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        "| `generate-narrative` | `readingOrder` の完全な順序、および叙述の論理骨格となるcard-to-cardの `causal` / `negate`。明示されたisland-to-island edgeも従来文脈として維持する | `readingOrder` とisland edgeはDocumentからpromptへ。card relationはIRからpromptへ入り、`causal` / `negate` はreading-order上の位置へ写像する | **必要な論理骨格は解消済み。** `AI-IR-NARRATIVE-SPINE-01` / PR #2887で、正規化可能なcard-to-card `causal` / `negate` の両端をrequired cardとして保護し、300カードの末尾関係までIRと最終promptへ残す回帰を固定した。required cardだけで上限を超える場合はfail-closedする。`MAX_RELATIONS` を超える規模やtoken予算は本Issueに残る |",
        "| `generate-narrative` | `readingOrder` の完全な順序、および叙述の論理骨格となるcard-to-cardの `causal` / `negate`。明示されたisland-to-island edgeも従来文脈として維持する | `readingOrder` とisland edgeはDocumentからpromptへ。card relationはIRからpromptへ入り、`causal` / `negate` はreading-order上の位置へ写像する | **必要な論理骨格は解消済み。** `AI-IR-NARRATIVE-SPINE-01` / PR #2887でrequired endpointを保護し、R22 / PR #2939でrequired relation自体も先に予約するようにした。300カードの末尾 `causal` / `negate` はIRと最終promptまで残り、required cardが200件またはrequired relationが400件を超える場合は黙って欠落せずfail-closedする。残るのはnamed provider/model上のtoken余裕と長期方式の判断である |",
    ),
    (
        "- `narrative-late-causal-negate`: reading orderは残るが末尾の `causal` / `negate` は失われる。",
        "- `narrative-late-causal-negate`: R22後はreading orderに加えて末尾のrequired `causal` / `negate` も残る。required card / relation集合そのものがshared budgetを超える場合は黙って縮約せずfail-closedする。",
    ),
    (
        "このprobeを「全IRフィールドの一致率」ではなく、route契約に対するscale regressionのtripwireとして扱う。detect/groupsのように局所的なrequired意味を安全に保護できたrouteは成功条件へ昇格し、narrative/layoutのように未解決なものはcharacterizationとして残す。",
        "このprobeを「全IRフィールドの一致率」ではなく、route契約に対するscale regressionのtripwireとして扱う。detectとnarrativeのrequired意味、groupsのhold判断は成功条件へ昇格している。一方、groupsの候補/島全coverageとlayoutのproduction構造coverageは未解決のままであり、R23以降のB/C候補はproduction採用ではなくcharacterizationとして扱う。",
    ),
    (
        "- `generate-narrative` では、`causal` / `negate` の両端カードやreading order上の論理骨格を先に確保する案が考えられる。ただし、文書全体の叙述骨格を守ろうとするとrequired集合が文書規模へ近づき、A2との差が小さくなる可能性がある。",
        "- `generate-narrative` では、R22までに `causal` / `negate` のrequired relationと両端カードを先に確保する方式を実装済みである。required集合がshared budget内なら末尾骨格も保持し、集合自体が上限を超える場合はfail-closedする。named provider/model上でA2との差を比較する判断は残る。",
    ),
    (
        "`suggest-layout` はさらに難しい。batchごとに局所座標を出しても、それぞれの座標系が独立していれば全体配置にはならない。局所配置の後に、島・代表点・跨り関係を使って全体座標へ整合させる第2段階が必要になる。したがってlayoutの方式Cは、単純な分割処理ではなく階層配置として設計する。",
        "`suggest-layout` はさらに難しい。R25ではこの条件を30 island-local + 1 global alignmentへ具体化し、全300 card / 300 relationを欠落なくpartitionできるmeasurement-only C候補を固定した。R27では `final = global anchor + local offset` の合成契約をcharacterizeし、synthetic identityで300カードを誤差0.0で再構成できること、欠落・重複・未知ID・非有限値をfail-closedできることまで確認した。これはproduction採用ではなく、単純batchではない階層配置Cが構造的に閉じることの候補証拠である。",
    ),
    (
        "- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。GitHub Actionsは現在無効のため、CIで実行成功済みとは扱わない。",
        "- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22〜R27ではbranch-only GitHub Actionsで関連回帰を繰り返し実行し、直近R27 run `33947383473` では33 test・ruff・`git diff --check` が成功した。恒久workflowの有無とは分けて記録する。",
    ),
    (
        "  - `scripts/measure_ai_ir_budget_pressure.py`\n  - `tests/test_llm_input_ir_scale.py`",
        "  - `scripts/measure_ai_ir_budget_pressure.py`\n  - `scripts/measure_ai_route_projection_candidates.py`\n  - `scripts/measure_ai_layout_hierarchical_candidate.py`\n  - `scripts/measure_ai_layout_hierarchical_composition.py`\n  - `tests/test_llm_input_ir_scale.py`",
    ),
    (
        "  - `tests/test_ai_ir_budget_pressure.py`\n  - IR単体テスト、移行対象route統合テスト、backend全体回帰。",
        "  - `tests/test_ai_ir_budget_pressure.py`\n  - `tests/test_ai_route_projection_candidates.py`\n  - `tests/test_ai_layout_hierarchical_candidate.py`\n  - `tests/test_ai_layout_hierarchical_composition.py`\n  - IR単体テスト、移行対象route統合テスト、backend全体回帰。",
    ),
    (
        "1. **named provider/modelの実入力tokenを測る。** R20のハーネスを使い、`suggest-layout` 相当の最重量promptと、座標を使わない `generate-narrative` を同じmodel/providerで比較する。",
        "1. **named provider/modelの実入力tokenを測る。** R24/R26まで拡張したR20ハーネスを使い、既定ではgroups/layoutのcurrent/Bとnarrative/checkの6比較を同じmodel/providerで測る。layout Cも比較する場合だけ `--include-layout-c` を明示し、30 local + 1 globalを追加する。",
    ),
    (
        "3. `generate-narrative` の `causal` / `negate` 両端保護は `AI-IR-NARRATIVE-SPINE-01` で完了した。今後はrequired relationが `MAX_RELATIONS` を超える規模やtoken予算まで含めて、A2/B/Cのどれが必要かを実測後に判断する。",
        "3. `generate-narrative` の `causal` / `negate` はR22までにendpointとrelationの両方をrequired保護した。required card >200 / required relation >400は既にfail-closedであり、今後の判断対象は主にnamed provider/model上のtoken余裕と、文書規模でA2/B/Cのどれが妥当かである。",
    ),
    (
        "4. `suggest-layout` はA2が十分な余裕を持って使えない場合、局所配置と全体整合を分けた階層配置としてCを具体化する。",
        "4. `suggest-layout` のCはR25/R27でmeasurement-only候補として、決定論的partitionとlocal/global合成まで具体化済みである。A2/B/Cの採択は、provider-reported token usageと、必要なら実model出力の配置品質・latency・failure rateを比較してから行う。",
    ),
]

for old, new in replacements:
    count = text.count(old)
    assert count == 1, (old[:100], count)
    text = text.replace(old, new)

r28 = r'''


## R28 — R22〜R27後のIssue正本整合

R22〜R27で実装・characterizationが進んだ一方、Issue前半には過去時点の「narrative末尾relationが失われる」「required relation >400は未整理」「layout Cは今後具体化」「GitHub Actionsは無効」という記述が残っていた。R28では**production状態や受入条件を前倒しせず**、これらを現在の事実へ同期した。

- narrativeはrequired endpointだけでなくrequired relation自体もR22で保護済みであり、shared budget超過時はsilent lossではなくfail-closedすることへ統一した。
- layout CはR25のpartition、R26の明示opt-in provider計測経路、R27のlocal/global合成までmeasurement-only候補として具体化済みであることを判断順序へ反映した。
- 検証計画へR23/R25/R27のcharacterization script/testを追加した。
- branch-only GitHub Actionsで関連回帰が成功している現在地へCI記述を更新した。ただし恒久workflowの存在やproduction完了を意味しない。
- provider-reported token usage未取得、groups/layoutのproduction scale strategy未採択、A2/B/C未決定という受入条件は変更していない。

**非主張**: R28は文書整合だけであり、production上限・route・IR schema・provider実行境界を変更しない。本IssueのStatusは引き続きIn Progressである。
'''

assert "## R28 — R22〜R27後のIssue正本整合" not in text
text = text.rstrip() + r28.rstrip() + "\n"
path.write_text(text, encoding="utf-8")
