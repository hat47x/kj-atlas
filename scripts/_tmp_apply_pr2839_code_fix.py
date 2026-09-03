from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


route = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
replace_once(
    route,
    "def _build_island_summary_prompt(payload: SuggestIslandSummaryRequest) -> str:\n",
    "def _build_island_summary_prompt(payload: SuggestIslandSummaryRequest, ir_context=None) -> str:\n",
)
replace_once(
    route,
    "    card_lines = [f'- id=\"{card.id}\", text={json.dumps(card.text)}' for card in member_cards]\n",
    "    if ir_context is None:\n"
    "        card_texts_by_id = {card.id: card.text for card in member_cards}\n"
    "    else:\n"
    "        member_ids = {card.id for card in member_cards}\n"
    "        card_texts_by_id = {\n"
    "            item[\"id\"]: item[\"text\"]\n"
    "            for item in ir_context.ir.get(\"cards\", [])\n"
    "            if item[\"id\"] in member_ids\n"
    "        }\n"
    "        if set(card_texts_by_id) != member_ids:\n"
    "            raise HTTPException(\n"
    "                status_code=422,\n"
    "                detail={\n"
    "                    \"code\": \"required_card_context_mismatch\",\n"
    "                    \"message\": \"Task-required card context did not fit in the IR projection\",\n"
    "                },\n"
    "            )\n"
    "    card_lines = [\n"
    "        f'- id=\"{card.id}\", text={json.dumps(card_texts_by_id[card.id])}'\n"
    "        for card in member_cards\n"
    "    ]\n",
)
replace_once(
    route,
    "    except IRGenerationError as exc:\n"
    "        raise HTTPException(status_code=422, detail=exc.to_contract()) from exc\n"
    "    prompt = \"\\n\".join(\n"
    "        [base_prompt, \"\", *island_summary_ir_prompt_lines(ir_context)]\n"
    "    )\n",
    "    except IRGenerationError as exc:\n"
    "        raise HTTPException(status_code=422, detail=exc.to_contract()) from exc\n"
    "    # provider transportはpromptだけを送るため、直接メンバー本文もIRから再描画する。\n"
    "    # 最初のbuilder呼び出しは従来の島不存在・空島エラー境界を保つvalidation-onlyである。\n"
    "    base_prompt = _build_island_summary_prompt(payload, ir_context=ir_context)\n"
    "    prompt = \"\\n\".join(\n"
    "        [base_prompt, \"\", *island_summary_ir_prompt_lines(ir_context)]\n"
    "    )\n",
)


test_path = Path("03_Implement/backend/tests/test_ai_island_summary_ir.py")
replace_once(
    test_path,
    "from types import SimpleNamespace\n\nimport pytest\n",
    "import json\nfrom types import SimpleNamespace\n\nimport pytest\n",
)
marker = "\ndef test_missing_target_island_fails_closed() -> None:\n"
new_test = r'''

def test_route_renders_direct_member_text_from_ir_not_raw_document(monkeypatch) -> None:
    raw_text = "  alpha\tbeta  gamma  "
    base = _payload()
    cards = [
        card.model_copy(update={"text": raw_text}) if card.id == "c1" else card
        for card in base.doc.cards
    ]
    payload = base.model_copy(
        update={
            "doc": base.doc.model_copy(update={"cards": cards}),
            "model": "model-test",
        }
    )
    captured = {}

    monkeypatch.setattr(ai_route, "_assert_model_allowed", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(ai_route, "_resolve_audit_tenant", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(ai_route, "_audit_llm_trace", lambda *_args, **_kwargs: None)

    def _fake_generate(request):
        captured["request"] = request
        return SimpleNamespace(
            raw_text=(
                '{"candidates":[{"summaryText":"確認負担を減らしつつ安全性を保つ必要がある",'
                '"groundingIds":["c1","c2"]}],"warnings":[]}'
            )
        )

    monkeypatch.setattr(ai_route, "generate_with_fallback", _fake_generate)

    ai_route.suggest_island_summary(payload, object(), object())

    llm_request = captured["request"]
    normalized_text = next(
        item["text"] for item in llm_request.inputs["cards"] if item["id"] == "c1"
    )
    # IRのstructured-text正規化はタブ等の制御文字を除去するが、
    # 前後空白や連続空白を別仕様へ勝手に畳み込まない。
    assert normalized_text == raw_text.replace("\t", "")
    assert normalized_text != raw_text
    assert json.dumps(normalized_text) in llm_request.prompt
    assert json.dumps(raw_text) not in llm_request.prompt
'''
replace_once(test_path, marker, new_test + marker)

print("PR #2839 code fix applied: direct member text is rendered from IR before provider transport.")
