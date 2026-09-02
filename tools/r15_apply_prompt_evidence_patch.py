#!/usr/bin/env python3
"""Temporary R15 helper: apply narrowly checked prompt-evidence fixes.

This file is removed before the PR is merged. Every replacement is fail-closed:
the expected old fragment must occur exactly once.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected fragment exactly once, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


ai = ROOT / "03_Implement/backend/src/kj_atlas_api/routes/ai.py"
replace_once(
    ai,
    '''    relations = ir.get("relations", [])
    if relations:
        context.append("Relations recorded on the canvas (ADR-0048 vocabulary):")
        for relation in relations:
            context.append(
                f'- {relation["type"]}: {relation["from"]} -> {relation["to"]}'
            )

    clusters = [
''',
    '''    relations = ir.get("relations", [])
    if relations:
        context.append("Relations recorded on the canvas (ADR-0048 vocabulary):")
        for relation in relations:
            context.append(
                f'- {relation["type"]}: {relation["from"]} -> {relation["to"]}'
            )

    evidence_links = ir.get("evidence_links", [])
    if evidence_links:
        context.append("Evidence links the human has recorded:")
        for link in evidence_links:
            state = link.get("contradiction_state")
            suffix = f" (contradictionState={state})" if state else ""
            context.append(
                f'- card "{link["from_card_id"]}" --evidence:{link["type"]}--> '
                f'card "{link["to_card_id"]}"{suffix}'
            )

    clusters = [
''',
)

replace_once(
    ai,
    '''        placement_lines = _layout_placement_lines(ir)
        relation_lines = _layout_relation_lines(payload, ir)
        island_relation_lines = _layout_island_relation_lines(ir)
        if placement_lines:
''',
    '''        placement_lines = _layout_placement_lines(ir)
        relation_lines = _layout_relation_lines(payload, ir)
        evidence_lines: list[str] = []
        for link in ir.get("evidence_links", []):
            state = link.get("contradiction_state")
            suffix = f" (contradictionState={state})" if state else ""
            evidence_lines.append(
                f'- card "{link["from_card_id"]}" --evidence:{link["type"]}--> '
                f'card "{link["to_card_id"]}"{suffix}'
            )
        island_relation_lines = _layout_island_relation_lines(ir)
        if placement_lines:
''',
)

replace_once(
    ai,
    '''        context_lines.append("Logical relations (these, not the current positions, say what belongs near what):")
        context_lines.extend(relation_lines or ["- (none)"])
        context_lines.append("Island relations (aggregated from the card relations above):")
''',
    '''        context_lines.append("Logical relations (these, not the current positions, say what belongs near what):")
        context_lines.extend(relation_lines or ["- (none)"])
        if evidence_lines:
            context_lines.append("Evidence links recorded on the canvas:")
            context_lines.extend(evidence_lines)
        context_lines.append("Island relations (aggregated from the card relations above):")
''',
)

test = ROOT / "03_Implement/backend/tests/test_ai_route_prompt_coverage.py"
replace_once(
    test,
    '''    # These two routes carry evidence_links on LLMRequest.inputs but their final
    # prompt builders do not render an evidence section.  The provider transport
    # sends the prompt, so that distinction must stay observable.
    assert groups["coverage"]["visible_in_final_prompt"]["evidence_links"] == 0
    assert layout["coverage"]["visible_in_final_prompt"]["evidence_links"] == 0

    # Narrative explicitly renders every evidence link that survived in the IR.
    assert narrative["coverage"]["visible_in_final_prompt"]["evidence_links"] == 20
''',
    '''    # Evidence that survives the shared IR must reach the actual provider prompt
    # on every migrated route.  Loss from MAX_CARDS remains observable as 20/30;
    # the renderer must not introduce an additional 20 -> 0 loss.
    assert groups["coverage"]["visible_in_final_prompt"]["evidence_links"] == 20
    assert layout["coverage"]["visible_in_final_prompt"]["evidence_links"] == 20
    assert narrative["coverage"]["visible_in_final_prompt"]["evidence_links"] == 20
''',
)

issue = ROOT / "01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md"
replace_once(
    issue,
    '''このため、scale remediationはIR単体の件数だけでなく、**routeごとの最終promptで何が残り、何が欠けるか**を測って判断する。

### なぜ問題か
''',
    '''このため、scale remediationはIR単体の件数だけでなく、**routeごとの最終promptで何が残り、何が欠けるか**を測って判断する。

### 2026-09-03 route別の最終prompt計測

300カード・30島の同じ代表入力を、移行済み3 routeの実prompt builderへ通して測定した。外部LLMは呼ばず、providerへ実際に渡る描画済みpromptだけを決定論的に比較した。

- `suggest-card-groups`: card text 200/300、完全な島membership 20/30、typed relation 199/300。IRの `MAX_CARDS` 境界が候補集合と既存島の文脈へそのまま現れる。
- `suggest-layout`: card textと完全な島membershipはDocument由来の互換節により300/300、30/30を保つ一方、typed relationは199/300、相対座標は200/300に留まる。全カード本文が見えていても構造文脈が完全とは限らない。
- `generate-narrative`: reading order由来でcard text 300/300、完全な島membership 30/30を保つが、typed relationは199/300に留まる。
- evidenceを30件加えた副シナリオでは、IRには20/30件が残った。`generate-narrative` はその20件を最終promptへ描画した一方、計測時点の `suggest-card-groups` / `suggest-layout` は0件だった。これは規模上限による20/30への減少とは別に、rendererで20/20を落とす経路欠落である。

最後の欠落は `AI-IR-PROMPT-EVIDENCE-01` として切り出し、IRに残ったevidenceがprovider promptへ届くよう修正する。ここを直しても `MAX_CARDS` による20/30のcoverage loss自体は解消しないため、本Issueの規模・token判断は継続する。

### なぜ問題か
''',
)

replace_once(
    issue,
    '''- [ ] `suggest-card-groups` / `suggest-layout` / `generate-narrative` について、IR切り詰めが最終promptのどの情報を失わせるかを区別して記録できる。
''',
    '''- [x] `suggest-card-groups` / `suggest-layout` / `generate-narrative` について、IR切り詰めが最終promptのどの情報を失わせるかを区別して記録できる。
''',
)

index = ROOT / "01_Plans/dogfood/cognitive-dogfood-index.md"
needle = '''- `doc_kj_atlas_dogfood_r14.json`
  - R14のKJキャンバス。
'''
replacement = needle + '''- `cognitive-dogfood-continuous-2026-09-03-r9.md`
  - R15。route別の最終prompt計測から、規模切り詰めとは別にevidenceがrendererで失われる経路欠落を分離し、修正へ戻した記録。
- `doc_kj_atlas_dogfood_r15.json`
  - R15のKJキャンバス。
'''
replace_once(index, needle, replacement)

print("R15 prompt-evidence patch applied")
