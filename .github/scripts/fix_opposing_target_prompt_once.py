from pathlib import Path


def replace_once(path: Path, before: str, after: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(before)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}: {before[:120]!r}")
    path.write_text(text.replace(before, after, 1), encoding="utf-8")


route = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
replace_once(
    route,
    '    if target is None:\n        raise HTTPException(status_code=422, detail="targetCardId does not exist")\n\n    lines = [\n',
    '    if target is None:\n        raise HTTPException(status_code=422, detail="targetCardId does not exist")\n\n'
    '    target_text = target.text\n'
    '    if ir_context is not None:\n'
    '        target_ir = next(\n'
    '            (item for item in ir_context.ir.get("cards", []) if item["id"] == target.id),\n'
    '            None,\n'
    '        )\n'
    '        if target_ir is None:\n'
    '            raise HTTPException(\n'
    '                status_code=422,\n'
    '                detail={\n'
    '                    "code": "required_card_context_mismatch",\n'
    '                    "message": "Task-required target card context did not fit in the IR projection",\n'
    '                },\n'
    '            )\n'
    '        target_text = target_ir["text"]\n\n'
    '    lines = [\n',
)
replace_once(
    route,
    '        f"Target card: {json.dumps({\'id\': target.id, \'text\': target.text})}",\n',
    '        f"Target card: {json.dumps({\'id\': target.id, \'text\': target_text})}",\n',
)

test = Path("03_Implement/backend/tests/test_ai_oppose.py")
replace_once(
    test,
    "from __future__ import annotations\n\nfrom collections.abc import Iterator\n",
    "from __future__ import annotations\n\nimport json\nfrom collections.abc import Iterator\n",
)
replace_once(
    test,
    '    doc = _doc()\n    doc["evidenceLinks"][0]["contradictionState"] = "held"\n    captured = {}\n',
    '    doc = _doc()\n'
    '    raw_target_text = "  alpha\\tbeta  gamma  "\n'
    '    doc["cards"][0]["text"] = raw_target_text\n'
    '    doc["evidenceLinks"][0]["contradictionState"] = "held"\n'
    '    captured = {}\n',
)
replace_once(
    test,
    '    assert request.inputs is not None\n'
    '    assert {card["id"] for card in request.inputs["cards"]} >= {"c-claim", "c-counter"}\n'
    '    assert "contradictionState=held" in request.prompt\n',
    '    assert request.inputs is not None\n'
    '    assert {card["id"] for card in request.inputs["cards"]} >= {"c-claim", "c-counter"}\n'
    '    normalized_target_text = next(\n'
    '        card["text"] for card in request.inputs["cards"] if card["id"] == "c-claim"\n'
    '    )\n'
    '    assert normalized_target_text == "  alphabeta  gamma  "\n'
    '    assert json.dumps({"id": "c-claim", "text": normalized_target_text}) in request.prompt\n'
    '    assert json.dumps({"id": "c-claim", "text": raw_target_text}) not in request.prompt\n'
    '    assert "contradictionState=held" in request.prompt\n',
)

print("opposing-viewpoint target text now follows the actual IR input path")
